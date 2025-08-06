---
description: Analyzes the entire codebase to classify nodes based on dependency mapping.
globs:
alwaysApply: false
version: 1.0
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
  - To conduct a comprehensive, one-time analysis of the entire project's codebase.
  - To generate a dependency map and a node classification document that will serve as a baseline for all future feature development.
  - This process categorizes code components into "Core Nodes," "Business Logic Nodes," and "Leaf Nodes" to inform development strategies.
</purpose>

<context>
  - This is a foundational step, typically run once during the initial setup of Agent OS on a project via `analyze-product.md`.
  - It can be re-run if the core architecture undergoes significant changes.
  - The output is stored in `.agent-os/architecture-analysis/` and used by `create-spec.md` to assess the impact of new features.
</context>

<prerequisites>
  - An existing codebase to analyze.
  - Write access to the project root to create the `.agent-os/architecture-analysis/` directory and its contents.
</prerequisites>

<process_flow>

<step number="1" name="codebase_scanning">
    <purpose>Scan existing codebase to identify all functions, classes, and modules</purpose>
    <action>
      1. SCAN project directories (excluding node_modules, .git, etc.)
      2. IDENTIFY all functions, classes, methods, and modules
      3. EXTRACT import/require statements and function calls
      4. BUILD initial inventory of code components
    </action>
    <output>component_inventory.json (temporary working file)</output>
</step>

<step number="2" name="dependency_mapping">
    <purpose>Generate comprehensive dependency graph using Mermaid</purpose>
    <action>
      1. ANALYZE import statements and function calls
      2. MAP dependencies between components  
      3. IDENTIFY bidirectional and circular dependencies
      4. GENERATE Mermaid diagram showing dependency relationships
      5. SAVE as .agent-os/architecture-analysis/dependency_map.mermaid
    </action>
    
    <mermaid_template>
      ```mermaid
      graph TD
          %% Core Infrastructure Nodes
          A[Authentication] --> B[UserService]
          A --> C[Database]
          
          %% Business Logic Nodes
          B --> D[ProfileController]
          B --> E[OrderController]
          
          %% Leaf Nodes (minimal dependencies)
          F[ReportGenerator] --> B
          G[EmailNotifier] --> H[EmailService]
          
          %% UI Components (potential leaf nodes, it could be other Nodes depends on project)
          I[UserDashboard] --> D
          J[OrderHistory] --> E
          
          %% Styling and classification
          classDef coreNode fill:#ff6b6b,stroke:#000,stroke-width:3px
          classDef businessNode fill:#ffd93d,stroke:#000,stroke-width:2px
          classDef leafNode fill:#6bcf7f,stroke:#000,stroke-width:1px
          
          class A,C coreNode
          class B,D,E businessNode  
          class F,G,I,J leafNode
      ```
    </mermaid_template>
</step>

<step number="3" name="dependency_analysis">
    <purpose>Analyze dependency patterns to classify components</purpose>
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
</step>

<step number="4" name="classification_documentation">
    <purpose>Document classification results for all affected components</purpose>
    <creates>.agent-os/architecture-analysis/node_classification.md</creates>
    
    <documentation_template>
      # Node Classification Analysis
      
      > Created: [CURRENT_DATE]
      > Analysis Method: Dependency-based classification
      
      ## Dependency Map
      
      See: @.agent-os/architecture-analysis/dependency_map.mermaid
      
      ## Component Classifications
      
      ### Core Nodes (Require Careful Oversight)
      
      | Component | Type | In-Degree | Out-Degree | Risk Level | Justification |
      |-----------|------|-----------|------------|------------|---------------|
      | [COMPONENT] | [CLASS/FUNCTION] | [NUMBER] | [NUMBER] | [HIGH/MEDIUM/LOW] | [REASONING] |
      
      ### Business Logic Nodes (Standard Development)
      
      | Component | Type | In-Degree | Out-Degree | Risk Level | Justification |
      |-----------|------|-----------|------------|------------|---------------|
      | [COMPONENT] | [CLASS/FUNCTION] | [NUMBER] | [NUMBER] | [HIGH/MEDIUM/LOW] | [REASONING] |
      
      ### Leaf Nodes (Autonomous Development Candidates)
      
      | Component | Type | In-Degree | Out-Degree | Risk Level | Justification |
      |-----------|------|-----------|------------|------------|---------------|
      | [COMPONENT] | [CLASS/FUNCTION] | [NUMBER] | [NUMBER] | [HIGH/MEDIUM/LOW] | [REASONING] |
      
    </documentation_template>
</step>

<step number="5" name="final_verification">

### Step 5: Final Verification and Summary

<step_metadata>
  <verifies>analysis completeness</verifies>
  <provides>summary to user</provides>
</step_metadata>

<verification_checklist>
  - [ ] `.agent-os/architecture-analysis/` directory created
  - [ ] `dependency_map.mermaid` generated
  - [ ] `node_classification.md` generated and populated
</verification_checklist>

<summary_template>
  ## ✅ Codebase Architecture Analysis Complete

  I have successfully analyzed the entire codebase and generated the following architecture documents:

  - **Dependency Map:** @.agent-os/architecture-analysis/dependency_map.mermaid
  - **Node Classification:** @.agent-os/architecture-analysis/node_classification.md

  These files provide a foundational understanding of the project's structure and will be used to guide future development.
</summary_template>

<instructions>
  ACTION: Verify all files were created correctly.
  SUMMARIZE: Inform the user that the analysis is complete and what was created using the summary template.
</instructions>

</step>

</process_flow>
