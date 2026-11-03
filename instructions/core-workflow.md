---
description: AI coding workflow for changes that touch any core node (hard sensitive rules, runtime-cycle hubs, top risk percentile, core_paths) or that were escalated by aoa-classify --check-diff. Plan first, human approval per step, small diffs, full test suite.
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Core Node Workflow

<ai_meta>
  <parsing_rules>
    - Process XML blocks first for structured data
    - Execute instructions in sequential order
  </parsing_rules>
  <file_conventions>
    - encoding: UTF-8
    - line_endings: LF
    - indent: 2 spaces
    - markdown_headers: no indentation
  </file_conventions>
</ai_meta>

## Overview

<purpose>
  - Core = `class: "core"` in `nodes.json`: a file that hits a core rule — `config_core_path`, `sensitive:<id>` (auth, crypto, secrets, payments, pii, irreversible, db_schema, public_api / package entrypoints), `runtime_cycle` (hub of a runtime cycle), or `score_top` / `score_boundary` (top risk percentile).
  - Mistakes here are expensive and hard to detect, so the human stays in the loop at every step.
  - Also used when @~/agent-os-adaptive/instructions/business-workflow.md or @~/agent-os-adaptive/instructions/leaf-workflow.md escalates (`aoa-classify --check-diff` exits 3).
</purpose>

<applies_when>
  - Any file the task touches is core, OR
  - `aoa-classify --check-diff BASE` exits 3 (`ESCALATE: diff touches core nodes` / `ESCALATE: diff adds N new dependencies`).
</applies_when>

<roles>
  - AI: plans, implements one approved step at a time, runs the full test suite.
  - Human: approves the plan and EACH step before the next one starts; reviews every diff.
  - For the implementation mode (full agent / agent planning / user-led) see @~/agent-os-adaptive/subagents/core-node-agent.md.
</roles>

<process_flow>

<step number="1" name="impact_analysis">
    <action>
      1. LIST the core files involved with their `rules`, `reasons`, `high_risk` and `factors.prod_blast_radius` from `nodes.json`.
      2. LIST their dependents (reverse edges in `graph.json`) that the change could affect, and the tests that reach them (`factors.test_reach`).
      3. LIST any new third-party dependencies and why they are needed.
    </action>
</step>

<step number="2" name="plan_first">
    <action>
      WRITE a numbered plan and ASK for approval before changing any code:
    </action>
    <template>
      **Goal:** [one sentence]
      **Core files and why they are core:** [path — rule ids]
      **Steps:** (each step is one small, reviewable diff that leaves the tests green)
        1. [change] — files: [...] — tests: [new / updated tests] — rollback: [how to undo]
        2. ...
      **Risks:** [what could break, who depends on it, data / security / compatibility concerns]
      **New dependencies:** [none / package — reason]
    </template>
    <rules>
      - Prefer more, smaller steps. A step that touches more than a few core files or mixes refactoring with behavior change should be split.
      - WAIT for explicit approval of the plan.
    </rules>
</step>

<step number="3" name="execute_one_step">
    <action>
      FOR EACH approved step, in order:
      1. IMPLEMENT only that step (small diff; no drive-by refactors).
      2. ADD or update tests for the step's behavior.
      3. RUN the FULL test suite plus lint and typecheck — not only the tests near the change.
      4. RUN `uv run --project ~/agent-os-adaptive aoa-classify . --check-diff BASE` and include its output.
      5. SHOW the human the diff, the test results and the check-diff output, and WAIT for approval before starting the next step.
      6. IF the human asks for changes, redo the step; IF the step turns out bigger than planned, stop and re-plan.
    </action>
</step>

<step number="4" name="final_verification">
    <action>
      1. RUN the full test suite, lint and typecheck once more on the final state.
      2. IF the change altered the dependency structure (new files, moved imports, new cycles), re-run `aoa-graph` + `aoa-classify` and report class changes for the touched files.
      3. SUMMARIZE: steps done, files changed (with classes), tests added, open risks, anything deferred.
    </action>
</step>

</process_flow>

<done_when>
  - Every step was approved by the human before the next one started.
  - Full test suite, lint and typecheck pass on the final state.
  - Human reviewed the final diff.
</done_when>
