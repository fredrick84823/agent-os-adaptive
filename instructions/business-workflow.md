---
description: AI coding workflow for changes whose strictest touched class is business (the default class — not core, not leaf). AI restates intent for human confirmation, writes tests first as the spec, iterates autonomously until tests/lint/typecheck pass; the human reviews tests, intent and scope. Auto-escalates to the core workflow when the diff touches core nodes or adds dependencies.
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Business Node Workflow

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
  - Business is the DEFAULT class in `nodes.json`: a file that hits no core rule and does not meet the leaf conditions (`rules: ["default"]`, reason `default: not core, not leaf — not leaf because …`). Most domain logic, services and controllers end up here.
  - The human's time goes to WHAT the change should do (intent, rules, edge cases, tests), not to line-by-line review. The AI does the implementation loop on its own.
</purpose>

<applies_when>
  - The strictest class among the files the task touches is business, AND
  - `aoa-classify --check-diff` has no `ESCALATE` line (no core node touched, no new dependencies beyond `--max-new-deps`).
  - If ANY core node is touched, or the change adds third-party dependencies, use @~/agent-os-adaptive/instructions/core-workflow.md instead.
</applies_when>

<roles>
  - AI: restates intent, writes tests, implements, iterates, runs the escalation check.
  - Human: confirms the restated intent (Step 2), then reviews tests + intent + scope at the end (Step 6). The human does not need to approve each edit.
</roles>

<process_flow>

<step number="1" name="scope_and_classes">
    <action>
      1. LIST the files you expect to change or create and look each one up in `nodes.json` (`class`, `rules`, `reasons`).
      2. IF any of them is core → STOP and use @~/agent-os-adaptive/instructions/core-workflow.md.
      3. NOTE the business files' `reasons` (e.g. "not leaf because 7 non-test files depend on it"): those dependents are what your tests must protect.
    </action>
</step>

<step number="2" name="restate_intent">
    <action>
      WRITE a short restatement and ASK the human to confirm or correct it before writing code:
    </action>
    <template>
      **Intent:** [one or two sentences: what changes for the user / caller]
      **Rules:** [the business rules the code must follow, as bullet points]
      **Edge cases:** [empty / invalid input, limits, concurrency, error paths that matter here]
      **Out of scope:** [what this change will NOT do]
      **Files:** [planned files with their class from nodes.json]
    </template>
    <rules>
      - Keep it brief (≤ 15 lines). This is a check of understanding, not a design document.
      - WAIT for confirmation. Corrections from the human replace your version.
    </rules>
</step>

<step number="3" name="tests_first_as_spec">
    <action>
      1. WRITE tests that encode the confirmed rules and edge cases (one test per rule / edge case where practical), next to the project's existing tests and in their style.
      2. RUN them and confirm they FAIL for the right reason (missing behavior, not import errors).
      3. Do NOT weaken or delete these tests later to make the implementation pass; if a test turns out to be wrong, say so in the Step 6 report.
    </action>
</step>

<step number="4" name="iterate_autonomously">
    <action>
      1. IMPLEMENT and iterate on your own until ALL of these pass: the new tests, the existing test suite, lint, typecheck (whatever the project has configured).
      2. KEEP the diff inside the scope from Step 2. Do not refactor unrelated code.
      3. No human check-ins are needed during this loop unless the confirmed intent turns out to be impossible or contradictory — then stop and ask.
    </action>
</step>

<step number="5" name="escalation_check">
    <action>
      1. RUN from the project root, with BASE = the branch you will merge into:
         `uv run --project ~/agent-os-adaptive aoa-classify . --check-diff BASE`
      2. IF it exits 3 with `ESCALATE: diff touches core nodes` or `ESCALATE: diff adds N new dependencies` → AUTO-ESCALATE: stop, tell the human which core files / dependencies are involved, and continue under @~/agent-os-adaptive/instructions/core-workflow.md (plan + per-step approval) for the remaining work. Do not merge.
      3. Files marked `*` (new file, inferred from path) are classified by path only; if one of them is imported by core code or handles sensitive data, treat it as core.
      4. IF it prints a staleness WARNING → re-run `aoa-graph` + `aoa-classify` and repeat.
      5. IF it exits 0 with strictest class business (or lower) → continue.
    </action>
</step>

<step number="6" name="human_review">
    <action>
      PRESENT for review, in this order:
      1. The tests added in Step 3 (the human reviews them as the spec).
      2. The confirmed intent from Step 2, and any place the implementation deviates from it.
      3. Scope: the changed files with their classes (paste the check-diff output) and the diff size.
      4. Test / lint / typecheck results.
    </action>
</step>

</process_flow>

<done_when>
  - Human confirmed the restated intent.
  - New tests + existing tests, lint and typecheck pass.
  - `aoa-classify --check-diff BASE` exits 0 (no core touched, no new dependencies).
  - Human reviewed tests, intent and scope.
</done_when>
