---
description: Runs aoa-graph (dependency graph + metrics) and aoa-classify (deterministic core/business/leaf rules), then explains the result and records any overrides.
globs:
alwaysApply: false
version: 1.2
encoding: UTF-8
---

# Codebase Node Classification

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
  - To classify the project's files into "Core Nodes," "Business Logic Nodes," and "Leaf Nodes" to inform development strategies.
  - The numbers (fan-in/out, blast radius, cycles, churn, bug-fix history) are COMPUTED by `tools/aoa_graph`, not estimated by the model.
  - The CLASS of every file (core / business / leaf) is DECIDED by `aoa-classify` from versioned rules (`tools/aoa_graph/default_rules.toml` + the project's optional `.aoa.toml`), not by the model.
  - The model's job is to explain the result, resolve what the tools could not see (dynamic imports, DI, plugin registration), and propose overrides in `overrides.jsonl`. Stricter overrides apply automatically; looser ones need a human.
</purpose>

<context>
  - Typically run during the initial setup of Agent OS on a project via `analyze-product.md`; re-run whenever the architecture changes. Same commit → identical tool output, so re-running is cheap and comparable.
  - The output is stored in `agent-os-adaptive/architecture-analysis/` and used by `create-spec.md` to assess the impact of new features.
  - Supported languages: TypeScript / JavaScript and Python. Granularity is fixed at FILE (module) level — do not mix in functions or classes.
</context>

<prerequisites>
  - An existing codebase to analyze (ideally a git repo; history metrics need git).
  - [uv](https://docs.astral.sh/uv/getting-started/installation/) and the aoa-graph dependencies installed (README Step 2b):
    `uv sync --project ~/agent-os-adaptive`
  - Write access to the project root to create `agent-os-adaptive/architecture-analysis/`.
</prerequisites>

<tool_contract>
  - The tools are the single source of truth for every number AND every class. NEVER edit `graph.json`, `metrics.json`, `unresolved.json`, or `nodes.json` by hand, and NEVER write a degree, score, or class that is not in them (no "6+", "8+", or rounded values).
  - If you believe a class is wrong, append an override to `overrides.jsonl` (Step 4) and re-run `aoa-classify`; do not change the class in the document yourself.
  - NEVER set `approved_by` in an override. Only a human may approve a looser class.
  - Field reference: `~/agent-os-adaptive/tools/aoa_graph/README.md` (aoa-graph and aoa-classify sections).
</tool_contract>

<process_flow>

<step number="1" name="run_dependency_graph_tool">
    <purpose>Compute the dependency graph and metrics with the tool</purpose>
    <action>
      1. From the project root, RUN:
         `uv run --project ~/agent-os-adaptive aoa-graph .`
         (equivalent: `uv run --project ~/agent-os-adaptive python ~/agent-os-adaptive/tools/aoa_graph .`)
      2. ADD options only when needed:
         - `--exclude 'GLOB'` for generated or vendored code the tool still picks up
         - `--py-root DIR` when Python code is imported from a non-standard root (not repo root or `src/`)
         - `--since-days N` to change the churn / bug-fix window (default 180, anchored at the HEAD commit)
      3. CONFIRM the summary line printed to stderr (nodes, edges, cycles, unresolved, parse errors).
      4. IF the command fails because dependencies are missing: show the install command from prerequisites and STOP; do not fall back to estimating numbers.
      5. IF the project has no TS/JS or Python files (0 nodes): tell the user the tool does not support this language yet; only then may you analyze manually, and every number in the final document MUST be labeled "estimated (not computed)".
    </action>
    <output>
      agent-os-adaptive/architecture-analysis/graph.json
      agent-os-adaptive/architecture-analysis/metrics.json
      agent-os-adaptive/architecture-analysis/unresolved.json
    </output>
</step>

<step number="2" name="dependency_mapping">
    <purpose>Render a readable Mermaid map from graph.json (colored after Step 3)</purpose>
    <action>
      1. READ `graph.json` edges. Do not add edges that are not in it (model-inferred edges go to Step 4, drawn dashed if shown).
      2. FOR large graphs (more than ~60 nodes): show the top nodes by `blast_radius` and `fan_in` from `metrics.json`, every member of each `cycles[]` entry, and group the rest by directory; state in a comment which subset is shown.
      3. MARK cycle members (`in_cycle: true`) and keep node labels as file paths.
      3a. COLOR nodes by `class` from `nodes.json` (Step 3); if you draw the map before Step 3, come back and apply the classes.
      4. SAVE as agent-os-adaptive/architecture-analysis/dependency_map.mermaid
    </action>

    <mermaid_template>
      ```mermaid
      graph TD
          %% Generated from graph.json (aoa-graph); subset: top 20 by blast_radius + all cycle members
          A["src/auth/session.ts"] --> B["src/db/client.ts"]
          C["src/services/user.ts"] --> A
          C --> B
          D["src/pages/profile.tsx"] --> C
          E["src/report/export.ts"] --> C
          F["src/plugins/loader.ts"] -.->|model-inferred| G["src/plugins/csv.ts"]

          classDef coreNode fill:#ff6b6b,stroke:#000,stroke-width:3px
          classDef businessNode fill:#ffd93d,stroke:#000,stroke-width:2px
          classDef leafNode fill:#6bcf7f,stroke:#000,stroke-width:1px

          class A,B coreNode
          class C businessNode
          class D,E,F,G leafNode
      ```
    </mermaid_template>
</step>

<step number="3" name="rule_based_classification">
    <purpose>Classify every file with the deterministic rules, then explain the result</purpose>
    <action>
      1. From the project root, RUN:
         `uv run --project ~/agent-os-adaptive aoa-classify .`
         (equivalent: `uv run --project ~/agent-os-adaptive aoa-graph classify .`)
      2. ADD options only when needed: `--coverage FILE` (coverage.py JSON or lcov) if the project has a fresh coverage report; `--no-coverage` if the report on disk is stale.
      3. CONFIRM the summary line (core / business / leaf counts, high_risk, overrides applied / pending).
      4. IF it exits with a config or overrides error: show the message to the user and STOP; do not classify by hand.
      5. IF the project has no `.aoa.toml` and the user named sensitive areas the default rules miss (e.g. a billing folder with a generic name), SUGGEST a `.aoa.toml` with `core_paths` and let the user decide; do not write it silently.
    </action>
    <output>agent-os-adaptive/architecture-analysis/nodes.json</output>
    <metric_mapping>
      - Fan-in = `fan_in`, fan-out = `fan_out` (copy the exact integers; fan-out is shown for context only).
      - "If it breaks, how much breaks" = `blast_radius` in metrics.json (includes tests) and `factors.prod_blast_radius` in nodes.json (non-test dependents only; this one drives the score).
      - Circular dependencies = `in_cycle` / `scc_id`; only `in_runtime_cycle` triggers the `runtime_cycle` rule (type-only cycles are noted, not ruled).
      - Change risk signals = `churn`, `churn_lines`, `bugfix_count`; hidden coupling = `co_change` (not scored; mention it in the Justification when relevant).
      - Detectability = `factors.test_fan_in` (direct test importers), `factors.test_reach` (direct or transitive), `factors.coverage`.
    </metric_mapping>
    <classification_criteria>
      Applied by `aoa-classify` in this order (details: tools/aoa_graph/README.md). Out-degree is NOT a criterion: depending on many files does not make a file safer or riskier to change for its dependents.
      1. Test files and example / docs / benchmark code → leaf (`test_file`, `example_code`); they are not ranked.
      2. Hard rules → core:
         - `config_core_path`: matches `core_paths` in the project's `.aoa.toml`
         - `sensitive:<id>`: auth, crypto, secrets, payments, pii, irreversible deletes, db_schema / migrations, public_api (incl. package entrypoints) — matched by path tokens, path globs, or imported packages
         - `runtime_cycle`: member of a runtime cycle (SCC size > 1, ignoring type-only edges) → also `high_risk: true`. This replaces the old "bidirectional dependencies" criterion.
      3. Risk score `risk = impact × cost_of_failure ÷ detectability`, ranked by percentile among non-test, non-example files:
         - impact: blast radius counting only non-test dependents, weighted up by churn
         - cost_of_failure: weighted up by bug-fix commits
         - detectability: tests that import the file directly or transitively, plus line coverage when a report is given (no report → conservative low detectability)
         - top 10% → core (`score_top`); the next 5 points → core (`score_boundary`, leaning stricter)
         - below p35 AND ≤ 2 non-test files depend on it (directly or transitively) → leaf (`score_low`); otherwise business (`leaf_blast_guard`, `leaf_boundary`, `score_mid`)
      4. A leaf with a tree-sitter parse error → business (`parse_error_uncertain`).
      5. Overrides from `overrides.jsonl`: stricter ones apply automatically; looser ones only with a human `approved_by`.
    </classification_criteria>
    <interpretation_rules>
      - Copy `class`, `rules`, `risk_score`, `percentile`, `risk_level` from `nodes.json` exactly.
      - Every Justification MUST cite the rule id(s) and at least one number from `nodes.json` / `metrics.json`, then explain in plain words what the file does and why that rule fits (or does not fit).
      - When the class and the code's role disagree (e.g. a leaf that actually handles payments through a generic filename), do NOT change the class in the document: propose an override in Step 4.
      - Files with `high_risk: true` (runtime cycle members) must be called out in the summary.
    </interpretation_rules>
</step>

<step number="4" name="resolve_unresolved_imports">
    <purpose>Handle what the tool could not see</purpose>
    <action>
      1. READ `unresolved.json`.
      2. FOR each `items[]` entry with reason `dynamic_expression`: open the source line, determine which files it can load (plugin folders, route tables, config-driven imports). If you can name them with evidence, list them as model-inferred dependencies; otherwise mark "unknown".
      3. FOR `not_found` / `*_target_not_found` / `workspace_package_entry_not_found`: decide whether it is generated code, a missing file, or a resolution gap; note it.
      4. FOR files in `parse_errors`: spot-check that their imports in `graph.json` match the file's import lines.
      5. ALSO consider dependencies no import can show: DI containers, framework registration (decorators, entry points), reflection.
      6. NEVER change the computed metrics. Model-inferred dependencies go into the Justification text and, if they make a file riskier, into an override.
    </action>
    <overrides>
      - FILE: agent-os-adaptive/architecture-analysis/overrides.jsonl (one JSON object per line; append, never rewrite earlier lines)
      - FORMAT: `{"node": "<path>", "to": "core|business|leaf", "by": "model", "reason": "<why>", "evidence": "<file:line>"}`
      - STRICTER (leaf → business → core): append it, then re-run `aoa-classify`; it applies automatically.
      - LOOSER (e.g. core → leaf): append it WITHOUT `approved_by`. It stays in `overrides.pending` in `nodes.json` until a human adds `"approved_by": "<name>"`. Tell the user which looser overrides are waiting for approval and why.
      - After appending, RE-RUN `uv run --project ~/agent-os-adaptive aoa-classify .` and confirm the summary line's applied / pending counts.
    </overrides>
</step>

<step number="5" name="classification_documentation">
    <purpose>Document classification results for all files</purpose>
    <creates>agent-os-adaptive/architecture-analysis/node_classification.md</creates>

    <documentation_template>
      # Node Classification Analysis

      > Created: [CURRENT_DATE]
      > Analysis Method: Computed metrics (aoa-graph [GENERATOR_VERSION]) + rule-based classes (aoa-classify, rules [rules_version.default] / repo [rules_version.repo or none]) + model explanation
      > Source: commit [source.commit from metrics.json] (dirty: [source.dirty])
      > Graph: [summary.nodes] files, [summary.edges] edges, [summary.cycles] cycles, [summary.unresolved] unresolved imports
      > History window: [params.window_start] → [params.window_end]
      > Classes: core [summary.core], business [summary.business], leaf [summary.leaf] (ranked [summary.ranked], tests [summary.tests], examples [summary.examples]); high_risk [summary.high_risk]; overrides applied [summary.overrides_applied], pending [summary.overrides_pending]

      ## Dependency Map

      See: @agent-os-adaptive/architecture-analysis/dependency_map.mermaid
      Raw data: `graph.json`, `metrics.json`, `unresolved.json`, `nodes.json`, `overrides.jsonl` in the same folder.

      ## Component Classifications

      ### Core Nodes (Require Careful Oversight)

      | File | Rules | Score (pct) | Fan-in | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|-------|-------------|--------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [rules from nodes.json] | [risk_score] (p[percentile]) | [fan_in] | [blast_radius] | [runtime_scc_id or -] | [churn] | [bugfix_count] | [risk_level] | [REASONING citing rule ids and numbers] |

      ### Business Logic Nodes (Standard Development)

      | File | Rules | Score (pct) | Fan-in | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|-------|-------------|--------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [rules from nodes.json] | [risk_score] (p[percentile]) | [fan_in] | [blast_radius] | [runtime_scc_id or -] | [churn] | [bugfix_count] | [risk_level] | [REASONING citing rule ids and numbers] |

      ### Leaf Nodes (Autonomous Development Candidates)

      | File | Rules | Score (pct) | Fan-in | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|-------|-------------|--------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [rules from nodes.json] | [risk_score] (p[percentile]) | [fan_in] | [blast_radius] | [runtime_scc_id or -] | [churn] | [bugfix_count] | [risk_level] | [REASONING citing rule ids and numbers] |

      For large repos list every core file, and for business / leaf the top 20 by `risk_score` plus any file the user asked about; state the total count of each class from `summary`. Test and example files may be summarized as one line each.

      ## Overrides

      | File | Computed → Final | By | Status (applied / pending approval) | Reason |
      |------|------------------|----|-------------------------------------|--------|
      | [PATH] | [computed_class] → [class or proposed] | [by] | [kind] | [reason] |

      ## Model-Inferred Dependencies (not in graph.json)

      | From | To | Evidence (file:line) | Effect on classification |
      |------|----|----------------------|--------------------------|
      | [PATH] | [PATH or unknown] | [WHERE] | [none / override proposed] |

    </documentation_template>
</step>

<step number="6" name="final_verification">

### Step 6: Final Verification and Summary

<step_metadata>
  <verifies>analysis completeness</verifies>
  <provides>summary to user</provides>
</step_metadata>

<verification_checklist>
  - [ ] `graph.json`, `metrics.json`, `unresolved.json`, `nodes.json` generated by the tools (not hand-written)
  - [ ] Every number in `node_classification.md` matches `metrics.json` / `nodes.json` exactly
  - [ ] Every class in `node_classification.md` matches `class` in `nodes.json` (re-run `aoa-classify` after adding overrides)
  - [ ] No override written by the model has `approved_by`; pending looser overrides are reported to the user
  - [ ] Every `dynamic_expression` entry in `unresolved.json` is addressed in the Model-Inferred Dependencies table (or marked unknown)
  - [ ] `dependency_map.mermaid` generated from `graph.json`
  - [ ] `node_classification.md` generated and populated
</verification_checklist>

<summary_template>
  ## ✅ Codebase Architecture Analysis Complete

  Computed with aoa-graph on commit [COMMIT]: [N] files, [M] edges, [C] cycles, [U] unresolved imports.
  Classified by aoa-classify: core [CORE], business [BUSINESS], leaf [LEAF]; high-risk (runtime cycle) [HIGH_RISK]; overrides pending human approval: [PENDING].

  - **Raw metrics:** `agent-os-adaptive/architecture-analysis/metrics.json`
  - **Classes (rule-based):** `agent-os-adaptive/architecture-analysis/nodes.json`
  - **Dependency Map:** @agent-os-adaptive/architecture-analysis/dependency_map.mermaid
  - **Node Classification:** @agent-os-adaptive/architecture-analysis/node_classification.md

  These files provide a foundational understanding of the project's structure and will be used to guide future development. Re-run `/analyze-node-classes` after architectural changes; the tools' numbers and classes are reproducible for a given commit, rules version, and overrides file.
</summary_template>

<instructions>
  ACTION: Verify all files were created correctly.
  SUMMARIZE: Inform the user that the analysis is complete and what was created using the summary template.
</instructions>

</step>

</process_flow>
