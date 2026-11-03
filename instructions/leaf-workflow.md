---
description: AI coding workflow for changes that only touch leaf nodes (tests, examples/docs, low-risk files with ≤ 2 non-test dependents). AI edits directly, runs the existing tests, human review of the result is optional.
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Leaf Node Workflow

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
  - Let the AI make low-risk changes end to end with minimal ceremony.
  - Leaf = `class: "leaf"` in `agent-os-adaptive/architecture-analysis/nodes.json`: test files, example / docs / benchmark code, or ranked files with a low risk score AND ≤ 2 non-test files depending on them (rule `score_low`). Nothing important breaks if a leaf breaks.
</purpose>

<applies_when>
  - EVERY file the task touches is leaf (or not a classified source file, e.g. README, CSS, images), AND
  - `aoa-classify --check-diff` reports `strictest class: leaf` (or none) with no `ESCALATE` line.
  - Otherwise use @~/agent-os-adaptive/instructions/business-workflow.md or @~/agent-os-adaptive/instructions/core-workflow.md.
</applies_when>

<roles>
  - AI: edits, runs tests, reports.
  - Human: OPTIONAL review of the final result. No approval is needed before or during the change.
</roles>

<process_flow>

<step number="1" name="confirm_scope">
    <action>
      1. LIST the files you plan to change and look each one up in `nodes.json` (`class`, `rules`).
      2. IF any planned file is business or core → STOP and switch to the stricter workflow.
      3. IF you plan to create new source files, keep them in leaf locations (tests, examples, or a file nothing else imports yet).
    </action>
</step>

<step number="2" name="edit_directly">
    <action>
      1. MAKE the change directly. No plan approval, no test-first requirement.
      2. KEEP the diff limited to the files from Step 1. Do not add third-party dependencies (that escalates to core, see Step 4).
    </action>
</step>

<step number="3" name="run_existing_tests">
    <action>
      1. RUN the project's existing test suite (at least the tests that import the changed files, `factors.test_reach` in `nodes.json` says how many there are) plus lint / typecheck if the project has them.
      2. FIX failures and re-run until green. Add a test only when it is cheap and obviously useful; it is not required.
    </action>
</step>

<step number="4" name="escalation_check">
    <action>
      1. RUN from the project root, with BASE = the branch you will merge into (usually `main` or `origin/main`):
         `uv run --project ~/agent-os-adaptive aoa-classify . --check-diff BASE`
      2. IF it prints `strictest class: leaf` (or none) and exits 0 → continue.
      3. IF it reports business → switch to @~/agent-os-adaptive/instructions/business-workflow.md from its Step 1 (restate intent) for the business files.
      4. IF it exits 3 (`ESCALATE`: core touched or new dependencies) → STOP and switch to @~/agent-os-adaptive/instructions/core-workflow.md. Do not push or merge.
      5. IF it prints `WARNING: nodes.json was built at …, which is not an ancestor of HEAD` → re-run `aoa-graph` + `aoa-classify` (see @~/agent-os-adaptive/instructions/analyze-node-classes.md) and repeat the check.
    </action>
</step>

<step number="5" name="report">
    <action>
      SUMMARIZE for the human (review optional): files changed, tests / lint run and their result, and the check-diff output line `strictest class: …`.
    </action>
</step>

</process_flow>

<done_when>
  - Existing tests, lint and typecheck pass.
  - `aoa-classify --check-diff BASE` exits 0 with strictest class leaf (or none).
</done_when>
