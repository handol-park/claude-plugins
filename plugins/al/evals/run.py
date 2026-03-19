#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "rich"]
# ///
"""
Eval harness for the al (agentic loop) plugin.

Usage:
    uv run run.py [--trials N] [--scenario NAME] [--scenarios-file PATH]

Each trial:
  1. Creates an isolated workdir under /tmp/al-eval/<scenario>/<trial>/
  2. Writes test data from scenario setup
  3. Initializes .al-state.json
  4. Dispatches `claude -p <subagent prompt>` for up to max_iterations
  5. Checks all invariants against ground truth (never agent claims)
  6. Records pass/fail + failure reasons

Reports pass rate per scenario and per invariant.
"""

import argparse
import glob
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

console = Console()

SUBAGENT_PROMPT_TEMPLATE = """\
Goal: {goal}
State file: {state_file}
Iteration: {iteration} of {max_iterations}

{extra_constraints}

Instructions:
1. Read the state file to understand what has been done so far.
2. Do the next unit of work toward the goal.
3. Update the state file when finished with this iteration:
   - If goal fully complete:
     {{"status": "done", "iteration": {iteration}, "goal": "...", "progress": "...", "result": "..."}}
   - If more work remains:
     {{"status": "in_progress", "iteration": {iteration}, "goal": "...", "progress": "..."}}
   - If unrecoverable error:
     {{"status": "failed", "iteration": {iteration}, "goal": "...", "error": "..."}}

Write the state file atomically: write to {state_file}.tmp then rename to {state_file}.
Do NOT signal completion in your text response — the state file is the only signal.
"""


# ── Setup ──────────────────────────────────────────────────────────────────────


def setup_workdir(workdir: Path, files_spec: list[dict]) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    for spec in files_spec:
        repeat = spec.get("repeat", 1)
        for i in range(1, repeat + 1):
            raw_path = spec["path"].replace("{i}", str(i))
            path = workdir / raw_path
            if "lines" in spec:
                path.write_text("\n".join(spec["lines"]) + "\n")
            elif "content" in spec:
                content = spec["content"].replace("{i}", str(i))
                path.write_text(content + "\n")
            else:
                path.write_text("")


def init_state(workdir: Path, goal: str) -> None:
    state = {"status": "pending", "iteration": 0, "goal": goal}
    (workdir / ".al-state.json").write_text(json.dumps(state))


# ── Runner ─────────────────────────────────────────────────────────────────────


def run_iteration(
    workdir: Path,
    goal: str,
    iteration: int,
    max_iterations: int,
    extra_constraints: str = "",
) -> dict:
    state_file = workdir / ".al-state.json"
    prompt = SUBAGENT_PROMPT_TEMPLATE.format(
        goal=goal,
        state_file=state_file,
        iteration=iteration,
        max_iterations=max_iterations,
        extra_constraints=extra_constraints,
    )
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return {"status": "error", "stderr": result.stderr}
    try:
        return json.loads(state_file.read_text())
    except Exception as e:
        return {"status": "error", "error": f"state file unreadable: {e}"}


def run_loop(
    workdir: Path, goal: str, max_iterations: int, extra_constraints: str = ""
) -> tuple[dict, int]:
    """Run up to max_iterations. Return (final_state, iterations_used)."""
    for i in range(1, max_iterations + 1):
        state = run_iteration(workdir, goal, i, max_iterations, extra_constraints)
        if state.get("status") in ("done", "failed", "error"):
            return state, i
    return state, max_iterations


# ── Invariants ─────────────────────────────────────────────────────────────────


def check_invariant(inv: dict, workdir: Path, state: dict) -> tuple[bool, str]:
    t = inv["type"]

    if t == "state_status":
        actual = state.get("status")
        expected = inv["expected"]
        ok = actual == expected
        return ok, f"status={actual!r} (expected {expected!r})"

    if t == "file_exists":
        path = workdir / inv["path"]
        ok = path.exists()
        return ok, f"{'exists' if ok else 'MISSING'}: {inv['path']}"

    if t == "file_not_exists":
        path = workdir / inv["path"]
        ok = not path.exists()
        return ok, f"{'absent' if ok else 'SHOULD NOT EXIST'}: {inv['path']}"

    if t == "json_field":
        path = workdir / inv["path"]
        if not path.exists():
            return False, f"file missing: {inv['path']}"
        try:
            data = json.loads(path.read_text())
        except Exception as e:
            return False, f"invalid JSON in {inv['path']}: {e}"
        actual = data.get(inv["field"])
        expected = inv["expected"]
        ok = actual == expected
        return ok, f"{inv['field']}={actual!r} (expected {expected!r})"

    if t == "state_field_matches_disk":
        field = state.get(inv["state_field"], [])
        disk_files = {Path(p).name for p in glob.glob(str(workdir / inv["disk_glob"]))}
        state_files = {Path(f).name for f in field}
        missing = disk_files - state_files
        extra = state_files - disk_files
        ok = not missing and not extra
        msg = "matches" if ok else f"missing={missing}, extra={extra}"
        return ok, f"state[{inv['state_field']}] vs disk: {msg}"

    return False, f"unknown invariant type: {t!r}"


# ── Trial ──────────────────────────────────────────────────────────────────────


def run_trial(scenario: dict, trial_idx: int) -> dict:
    name = scenario["name"]
    workdir = Path(tempfile.mkdtemp(prefix=f"al-eval-{name}-{trial_idx}-"))
    try:
        goal_template = scenario["goal"]
        goal = goal_template.replace("{workdir}", str(workdir))

        setup_workdir(workdir, scenario.get("setup", {}).get("files", []))
        init_state(workdir, goal)

        extra = scenario.get("extra_constraints", "")
        max_iter = scenario.get("max_iterations", 10)

        state, iters_used = run_loop(workdir, goal, max_iter, extra)

        results = []
        for inv in scenario.get("invariants", []):
            ok, msg = check_invariant(inv, workdir, state)
            results.append({"invariant": inv["type"], "passed": ok, "detail": msg})

        passed = all(r["passed"] for r in results)
        return {
            "trial": trial_idx,
            "passed": passed,
            "iterations_used": iters_used,
            "state_status": state.get("status"),
            "invariants": results,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ── Report ─────────────────────────────────────────────────────────────────────


def report(scenario_name: str, trials: list[dict]) -> None:
    n = len(trials)
    passed = sum(1 for t in trials if t["passed"])
    console.print(
        f"\n[bold]{scenario_name}[/bold]  {passed}/{n} passed "
        f"([{'green' if passed == n else 'yellow' if passed > 0 else 'red'}]"
        f"{passed / n:.0%}[/])"
    )

    # per-invariant breakdown
    inv_types = [inv["invariant"] for inv in trials[0]["invariants"]]
    table = Table(show_header=True, header_style="bold")
    table.add_column("invariant")
    table.add_column("pass rate")
    table.add_column("sample failure")
    for inv_type in inv_types:
        inv_trials = [
            next(i for i in t["invariants"] if i["invariant"] == inv_type)
            for t in trials
        ]
        inv_pass = sum(1 for i in inv_trials if i["passed"])
        failures = [i["detail"] for i in inv_trials if not i["passed"]]
        sample = failures[0] if failures else ""
        rate_color = "green" if inv_pass == n else "yellow" if inv_pass > 0 else "red"
        table.add_row(
            inv_type,
            f"[{rate_color}]{inv_pass}/{n}[/]",
            sample,
        )
    console.print(table)


# ── Main ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="al plugin eval harness")
    parser.add_argument("--trials", type=int, default=3, help="runs per scenario")
    parser.add_argument("--scenario", help="run only this scenario by name")
    parser.add_argument(
        "--scenarios-file",
        default=Path(__file__).parent / "scenarios.yaml",
        help="path to scenarios YAML",
    )
    args = parser.parse_args()

    with open(args.scenarios_file) as f:
        data = yaml.safe_load(f)

    scenarios = data["scenarios"]
    if args.scenario:
        scenarios = [s for s in scenarios if s["name"] == args.scenario]
        if not scenarios:
            console.print(f"[red]Scenario {args.scenario!r} not found[/]")
            sys.exit(1)

    overall_pass = 0
    overall_total = 0

    for scenario in scenarios:
        console.print(
            f"\n[dim]Running {args.trials} trials: {scenario['name']} — "
            f"{scenario['description']}[/dim]"
        )
        trials = []
        for i in range(1, args.trials + 1):
            console.print(f"  trial {i}/{args.trials}...", end=" ")
            t = run_trial(scenario, i)
            console.print(
                "[green]PASS[/]" if t["passed"] else "[red]FAIL[/]",
                f"({t['iterations_used']} iter, status={t['state_status']})",
            )
            trials.append(t)

        report(scenario["name"], trials)
        overall_pass += sum(1 for t in trials if t["passed"])
        overall_total += len(trials)

    console.print(
        f"\n[bold]Overall: {overall_pass}/{overall_total} trials passed[/bold]"
    )


if __name__ == "__main__":
    main()
