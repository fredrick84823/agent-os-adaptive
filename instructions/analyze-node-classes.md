---
description: Runs the aoa-graph tool to compute a file-level dependency graph and metrics, then interprets them to classify nodes.
globs:
alwaysApply: false
version: 1.1
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
  - The numbers (in/out-degree, blast radius, cycles, churn, bug-fix history) are COMPUTED by `tools/aoa_graph`, not estimated by the model.
  - The model's job is to interpret those numbers, resolve what the tool could not (dynamic imports, DI, plugin registration), and justify each classification.
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
  - The tool is the single source of truth for every number. NEVER edit `graph.json`, `metrics.json`, or `unresolved.json` by hand, and NEVER write a degree that is not in `metrics.json` (no "6+", "8+", or rounded values).
  - If you believe the tool is wrong (e.g. a dynamic import it could not see), record it as a model-inferred dependency in Step 4 with evidence; do not change the computed numbers.
  - Field reference: `~/agent-os-adaptive/tools/aoa_graph/README.md`.
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
    <purpose>Render a readable Mermaid map from graph.json</purpose>
    <action>
      1. READ `graph.json` edges. Do not add edges that are not in it (model-inferred edges go to Step 4, drawn dashed if shown).
      2. FOR large graphs (more than ~60 nodes): show the top nodes by `blast_radius` and `fan_in` from `metrics.json`, every member of each `cycles[]` entry, and group the rest by directory; state in a comment which subset is shown.
      3. MARK cycle members (`in_cycle: true`) and keep node labels as file paths.
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

<step number="3" name="dependency_analysis">
    <purpose>Interpret the computed metrics to classify each file</purpose>
    <metric_mapping>
      - In-degree = `fan_in`; Out-degree = `fan_out` (copy the exact integers).
      - "Critical path / if removed, breaks multiple features" = read `blast_radius` (number of files that transitively depend on it).
      - "Bidirectional / circular dependencies" = `in_cycle` / `scc_id`; check `in_runtime_cycle` to see whether the cycle exists at runtime or only through type-only imports.
      - Change risk signals = `churn`, `churn_lines`, `bugfix_count`; hidden coupling = `co_change`.
      - `test_fan_in` tells how many direct dependents are tests (some of `fan_in` / `blast_radius` is test code).
    </metric_mapping>
    <analysis_criteria>
      <core_node_patterns>
        - High in-degree (many components depend on it)
        - Low out-degree (depends on few other components)
        - Critical path components (if removed, breaks multiple features)
        - Infrastructure and shared services
        - Components with bidirectional dependencies
      </core_node_patterns>

      <leaf_node_patterns>
        - Low in-degree (few or no components depend on it)
        - Higher out-degree (depends on other components but not depended upon)
        - UI components with one-way data flow
        - Feature-specific components
        - Report generators and exporters
        - Components that can be removed without breaking other features
      </leaf_node_patterns>

      <business_logic_patterns>
        - Medium in-degree and out-degree
        - Orchestrates between core and leaf nodes
        - Contains domain-specific logic
        - Controllers and service layers
      </business_logic_patterns>
    </analysis_criteria>
    <interpretation_rules>
      - Apply the criteria above to the computed numbers; the criteria themselves are unchanged in this version (rule redesign is tracked separately).
      - Every Justification MUST cite at least one metric value from `metrics.json`.
      - When the numbers and the code's role disagree (e.g. low fan_in but handles auth or payments), say so explicitly in the Justification. When unsure, prefer the stricter class (leaf → business → core).
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
      6. NEVER change the computed metrics; model-inferred dependencies only affect the Justification text and may justify a STRICTER class, never a looser one.
    </action>
</step>

<step number="5" name="classification_documentation">
    <purpose>Document classification results for all files</purpose>
    <creates>agent-os-adaptive/architecture-analysis/node_classification.md</creates>

    <documentation_template>
      # Node Classification Analysis

      > Created: [CURRENT_DATE]
      > Analysis Method: Computed dependency metrics (aoa-graph [GENERATOR_VERSION]) + model interpretation
      > Source: commit [source.commit from metrics.json] (dirty: [source.dirty])
      > Graph: [summary.nodes] files, [summary.edges] edges, [summary.cycles] cycles, [summary.unresolved] unresolved imports
      > History window: [params.window_start] → [params.window_end]

      ## Dependency Map

      See: @agent-os-adaptive/architecture-analysis/dependency_map.mermaid
      Raw data: `graph.json`, `metrics.json`, `unresolved.json` in the same folder.

      ## Component Classifications

      ### Core Nodes (Require Careful Oversight)

      | File | Fan-in | Fan-out | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|--------|---------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [fan_in] | [fan_out] | [blast_radius] | [scc_id or -] | [churn] | [bugfix_count] | [HIGH/MEDIUM/LOW] | [REASONING citing metrics] |

      ### Business Logic Nodes (Standard Development)

      | File | Fan-in | Fan-out | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|--------|---------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [fan_in] | [fan_out] | [blast_radius] | [scc_id or -] | [churn] | [bugfix_count] | [HIGH/MEDIUM/LOW] | [REASONING citing metrics] |

      ### Leaf Nodes (Autonomous Development Candidates)

      | File | Fan-in | Fan-out | Blast radius | Cycle | Churn | Bug-fix | Risk Level | Justification |
      |------|--------|---------|--------------|-------|-------|---------|------------|---------------|
      | [PATH] | [fan_in] | [fan_out] | [blast_radius] | [scc_id or -] | [churn] | [bugfix_count] | [HIGH/MEDIUM/LOW] | [REASONING citing metrics] |

      ## Model-Inferred Dependencies (not in graph.json)

      | From | To | Evidence (file:line) | Effect on classification |
      |------|----|----------------------|--------------------------|
      | [PATH] | [PATH or unknown] | [WHERE] | [none / made stricter] |

    </documentation_template>
</step>

<step number="6" name="final_verification">

### Step 6: Final Verification and Summary

<step_metadata>
  <verifies>analysis completeness</verifies>
  <provides>summary to user</provides>
</step_metadata>

<verification_checklist>
  - [ ] `graph.json`, `metrics.json`, `unresolved.json` generated by the tool (not hand-written)
  - [ ] Every number in `node_classification.md` matches `metrics.json` exactly
  - [ ] Every `dynamic_expression` entry in `unresolved.json` is addressed in the Model-Inferred Dependencies table (or marked unknown)
  - [ ] `dependency_map.mermaid` generated from `graph.json`
  - [ ] `node_classification.md` generated and populated
</verification_checklist>

<summary_template>
  ## ✅ Codebase Architecture Analysis Complete

  Computed with aoa-graph on commit [COMMIT]: [N] files, [M] edges, [C] cycles, [U] unresolved imports.

  - **Raw metrics:** `agent-os-adaptive/architecture-analysis/metrics.json`
  - **Dependency Map:** @agent-os-adaptive/architecture-analysis/dependency_map.mermaid
  - **Node Classification:** @agent-os-adaptive/architecture-analysis/node_classification.md

  These files provide a foundational understanding of the project's structure and will be used to guide future development. Re-run `/analyze-node-classes` after architectural changes; the tool's numbers are reproducible for a given commit.
</summary_template>

<instructions>
  ACTION: Verify all files were created correctly.
  SUMMARIZE: Inform the user that the analysis is complete and what was created using the summary template.
</instructions>

</step>

</process_flow>
