---
description: Spec Creation Rules for Agent OS
globs:
alwaysApply: false
version: 1.1
encoding: UTF-8
---

# Spec Creation Rules

<ai_meta>
  <parsing_rules>
    - Process XML blocks first for structured data
    - Execute instructions in sequential order
    - Use templates as exact patterns
    - Request missing data rather than assuming
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
  - Create detailed spec plans for specific features
  - Generate structured documentation for implementation
  - Ensure alignment with product roadmap and mission
</purpose>

<context>
  - Part of Agent OS framework
  - Executed when implementing roadmap items
  - Creates spec-specific documentation
</context>

<prerequisites>
  - Product documentation exists in .agent-os/product/
  - Access to:
    - @.agent-os/product/mission.md,
    - @.agent-os/product/roadmap.md,
    - @.agent-os/product/tech-stack.md
  - User has spec idea or roadmap reference
</prerequisites>

<process_flow>

<step number="1" name="spec_initiation">

### Step 1: Spec Initiation

<step_metadata>
  <trigger_options>
    - option_a: user_asks_whats_next
    - option_b: user_provides_specific_spec
  </trigger_options>
</step_metadata>

<option_a_flow>
  <trigger_phrases>
    - "what's next?"
    - "what should we work on next?"
  </trigger_phrases>
  <actions>
    1. CHECK @.agent-os/product/roadmap.md
    2. FIND next uncompleted item
    3. SUGGEST item to user
    4. WAIT for approval
  </actions>
</option_a_flow>

<option_b_flow>
  <trigger>user describes specific spec idea</trigger>
  <accept>any format, length, or detail level</accept>
  <proceed>to context gathering</proceed>
</option_b_flow>

<instructions>
  ACTION: Identify spec initiation method
  ROUTE: Follow appropriate flow based on trigger
  WAIT: Ensure user agreement before proceeding
</instructions>

</step>

<step number="2" name="context_gathering">

### Step 2: Context Gathering

<step_metadata>
  <reads>
    - @.agent-os/product/mission.md
    - @.agent-os/product/roadmap.md
    - @.agent-os/product/tech-stack.md
  </reads>
  <purpose>understand spec alignment</purpose>
</step_metadata>

<context_analysis>
  <mission>overall product vision</mission>
  <roadmap>current progress and plans</roadmap>
  <tech_stack>technical requirements</tech_stack>
</context_analysis>

<instructions>
  ACTION: Read all three product documents
  ANALYZE: Spec alignment with each document
  NOTE: Consider implications for implementation
</instructions>

</step>

<step number="3" name="requirements_clarification">

### Step 3: Requirements Clarification

<step_metadata>
  <required_clarifications>
    - scope_boundaries: string
    - technical_considerations: array[string]
  </required_clarifications>
</step_metadata>

<clarification_areas>
  <scope>
    - in_scope: what is included
    - out_of_scope: what is excluded (optional)
  </scope>
  <technical>
    - functionality specifics
    - UI/UX requirements
    - integration points
  </technical>
</clarification_areas>

<decision_tree>
  IF clarification_needed:
    ASK numbered_questions
    WAIT for_user_response
  ELSE:
    PROCEED to_date_determination
</decision_tree>

<question_template>
  Based on the spec description, I need clarification on:

  1. [SPECIFIC_QUESTION_ABOUT_SCOPE]
  2. [SPECIFIC_QUESTION_ABOUT_TECHNICAL_APPROACH]
  3. [SPECIFIC_QUESTION_ABOUT_USER_EXPERIENCE]
</question_template>

<instructions>
  ACTION: Evaluate need for clarification
  ASK: Numbered questions if needed
  PROCEED: Only with clear requirements
</instructions>

</step>

<step number="3.5" name="code_impact_analysis">

### Step 3.5: Code Impact Analysis (Dependency-Based Node Classification)

<step_metadata>
  <purpose>Analyze whether spec involves leaf nodes or core architecture using dependency mapping</purpose>
  <enables>vibe_coding_approach</enables>
  <creates>
    - dependency_map.mermaid
    - node_classification.md
  </creates>
</step_metadata>

<analysis_workflow>
  <substep number="3.5.1" name="codebase_scanning">
    <purpose>Scan existing codebase to identify all functions, classes, and modules</purpose>
    <action>
      1. SCAN project directories (excluding node_modules, .git, etc.)
      2. IDENTIFY all functions, classes, methods, and modules
      3. EXTRACT import/require statements and function calls
      4. BUILD initial inventory of code components
    </action>
    <output>component_inventory.json (temporary working file)</output>
  </substep>

  <substep number="3.5.2" name="dependency_mapping">
    <purpose>Generate comprehensive dependency graph using Mermaid</purpose>
    <action>
      1. ANALYZE import statements and function calls
      2. MAP dependencies between components  
      3. IDENTIFY bidirectional and circular dependencies
      4. GENERATE Mermaid diagram showing dependency relationships
      5. SAVE as sub-specs/dependency_map.mermaid
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
          
          %% UI Components (potential leaf nodes)
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
  </substep>

  <substep number="3.5.3" name="dependency_analysis">
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
  </substep>

  <substep number="3.5.4" name="spec_impact_mapping">
    <purpose>Map spec requirements to affected components</purpose>
    <action>
      1. IDENTIFY which existing components the spec will modify
      2. DETERMINE which new components the spec will create
      3. MAP spec components to dependency graph
      4. ANALYZE impact propagation through dependency chains
      5. CALCULATE "blast radius" of changes
    </action>
    
    <impact_analysis>
      <direct_impact>components directly modified by spec</direct_impact>
      <indirect_impact>components affected through dependencies</indirect_impact>
      <integration_points>interfaces between new and existing components</integration_points>
      <risk_assessment>likelihood of breaking existing functionality</risk_assessment>
    </impact_analysis>
  </substep>

  <substep number="3.5.5" name="classification_documentation">
    <purpose>Document classification results for all affected components</purpose>
    <creates>sub-specs/node_classification.md</creates>
    
    <documentation_template>
      # Node Classification Analysis
      
      > Created: [CURRENT_DATE]
      > Spec: [SPEC_NAME]
      > Analysis Method: Dependency-based classification
      
      ## Dependency Map
      
      See: @sub-specs/dependency_map.mermaid
      
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
      
      ## Spec Impact Analysis
      
      ### Components to be Modified
      - **[COMPONENT]** ([CLASSIFICATION]) - [MODIFICATION_DESCRIPTION]
      
      ### New Components to be Created  
      - **[COMPONENT]** ([PREDICTED_CLASSIFICATION]) - [CREATION_DESCRIPTION]
      
      ### Dependency Chain Impact
      ```
      [SPEC_COMPONENT] → [AFFECTED_COMPONENT_1] → [AFFECTED_COMPONENT_2]
      ```
      
      ## Overall Spec Classification
      
      **Primary Classification:** [LEAF_NODE_CANDIDATE / CORE_NODE_REQUIRES_OVERSIGHT / MIXED_APPROACH]
      
      **Justification:** [DETAILED_REASONING_BASED_ON_DEPENDENCY_ANALYSIS]
      
      **Recommended Development Approach:** [APPROACH_RECOMMENDATION]
    </documentation_template>
  </substep>
</analysis_workflow>

<legacy_indicators>
  <leaf_node_indicators>
    - New standalone features with minimal dependencies
    - UI components that don't affect core workflows
    - Utility functions used in limited contexts
    - End-user facing features without system integrations
    - Features with clear boundaries and limited extension points
    - Report generation or data export features
    - User interface enhancements that don't change data flow
  </leaf_node_indicators>
  
  <core_node_indicators>
    - Database schema changes affecting multiple features
    - Authentication/authorization modifications
    - Core API changes that other systems depend on
    - Framework or architecture modifications
    - Changes to shared utilities used across the system
    - Performance-critical components
    - Security-related infrastructure changes
    - Payment or financial transaction handling
  </core_node_indicators>
</legacy_indicators>

<classification_logic>
  <dependency_based_classification>
    IF spec_primarily_affects_leaf_nodes AND dependency_impact_minimal:
      CLASSIFY as "leaf_node_candidate"
      ENABLE vibe_coding_approach
    ELIF spec_affects_core_nodes OR high_dependency_impact:
      CLASSIFY as "core_node_requires_oversight"
      MAINTAIN traditional_development_approach
    ELIF spec_affects_mixed_nodes:
      CLASSIFY as "mixed_approach_required"
      APPLY selective_development_strategies
    ELSE:
      FALL_BACK to legacy_indicator_analysis
  </dependency_based_classification>
</classification_logic>

<user_confirmation_template>
  ## Dependency-Based Code Impact Assessment

  I've analyzed the codebase dependencies and generated:
  - **Dependency Map:** @sub-specs/dependency_map.mermaid
  - **Classification Analysis:** @sub-specs/node_classification.md

  Based on dependency analysis, this spec appears to involve **[CLASSIFICATION]**.

  ### Dependency Analysis Results

  **Components to be Modified:**
  - [COMPONENT_1] ([CLASSIFICATION]) - [IMPACT_DESCRIPTION]
  - [COMPONENT_2] ([CLASSIFICATION]) - [IMPACT_DESCRIPTION]

  **New Components to be Created:**
  - [NEW_COMPONENT_1] ([PREDICTED_CLASSIFICATION]) - [DESCRIPTION]

  **Dependency Chain Impact:**
  - Direct impact: [NUMBER] components
  - Indirect impact: [NUMBER] components  
  - Risk level: [HIGH/MEDIUM/LOW]

  ### Recommendation: [LEAF_NODE_CANDIDATE / CORE_NODE_REQUIRES_OVERSIGHT / MIXED_APPROACH]

  **Justification:** [DETAILED_REASONING_FROM_DEPENDENCY_ANALYSIS]

  If classified as **leaf node candidate**, I can use autonomous development. If **core node**, I'll use traditional careful development. If **mixed approach**, I'll apply different strategies to different components.

  Would you like me to proceed with this classification, or would you like to review the dependency analysis first?
</user_confirmation_template>

<instructions>
  ACTION: Execute dependency-based analysis workflow (substeps 3.5.1 through 3.5.5)
  GENERATE: Mermaid dependency diagram and classification documentation
  ANALYZE: Component dependencies and impact propagation
  CLASSIFY: Spec based on dependency analysis rather than just indicators
  DOCUMENT: All analysis results in sub-specs/ folder
  CONFIRM: Get user agreement on data-driven classification
</instructions>

</step>

<step number="4" name="date_determination">

### Step 4: Date Determination

<step_metadata>
  <purpose>Ensure accurate date for folder naming</purpose>
  <priority>high</priority>
  <creates>temporary file for timestamp</creates>
</step_metadata>

<date_determination_process>
  <primary_method>
    <name>File System Timestamp</name>
    <process>
      1. CREATE directory if not exists: .agent-os/specs/
      2. CREATE temporary file: .agent-os/specs/.date-check
      3. READ file creation timestamp from filesystem
      4. EXTRACT date in YYYY-MM-DD format
      5. DELETE temporary file
      6. STORE date in variable for folder naming
    </process>
  </primary_method>

  <fallback_method>
    <trigger>if file system method fails</trigger>
    <name>User Confirmation</name>
    <process>
      1. STATE: "I need to confirm today's date for the spec folder"
      2. ASK: "What is today's date? (YYYY-MM-DD format)"
      3. WAIT for user response
      4. VALIDATE format matches YYYY-MM-DD
      5. STORE date for folder naming
    </process>
  </fallback_method>
</date_determination_process>

<validation>
  <format_check>^\d{4}-\d{2}-\d{2}$</format_check>
  <reasonableness_check>
    - year: 2024-2030
    - month: 01-12
    - day: 01-31
  </reasonableness_check>
</validation>

<error_handling>
  IF date_invalid:
    USE fallback_method
  IF both_methods_fail:
    ERROR "Unable to determine current date"
</error_handling>

<instructions>
  ACTION: Determine accurate date using file system
  FALLBACK: Ask user if file system method fails
  VALIDATE: Ensure YYYY-MM-DD format
  STORE: Date for immediate use in next step
</instructions>

</step>

<step number="5" name="spec_folder_creation">

### Step 5: Spec Folder Creation

<step_metadata>
  <creates>
    - directory: .agent-os/specs/YYYY-MM-DD-spec-name/
  </creates>
  <uses>date from step 4</uses>
</step_metadata>

<folder_naming>
  <format>YYYY-MM-DD-spec-name</format>
  <date>use stored date from step 4</date>
  <name_constraints>
    - max_words: 5
    - style: kebab-case
    - descriptive: true
  </name_constraints>
</folder_naming>

<example_names>
  - 2025-03-15-password-reset-flow
  - 2025-03-16-user-profile-dashboard
  - 2025-03-17-api-rate-limiting
</example_names>

<instructions>
  ACTION: Create spec folder using stored date
  FORMAT: Use kebab-case for spec name
  LIMIT: Maximum 5 words in name
  VERIFY: Folder created successfully
</instructions>

</step>

<step number="6" name="create_spec_md">

### Step 6: Create spec.md

<step_metadata>
  <creates>
    - file: .agent-os/specs/YYYY-MM-DD-spec-name/spec.md
  </creates>
</step_metadata>

<file_template>
  <header>
    # Spec Requirements Document

    > Spec: [SPEC_NAME]
    > Created: [CURRENT_DATE]
    > Status: Planning
  </header>
  <required_sections>
    - Overview
    - User Stories
    - Spec Scope
    - Out of Scope
    - Expected Deliverable
  </required_sections>
</file_template>

<section name="overview">
  <template>
    ## Overview

    [1-2_SENTENCE_GOAL_AND_OBJECTIVE]
  </template>
  <constraints>
    - length: 1-2 sentences
    - content: goal and objective
  </constraints>
  <example>
    Implement a secure password reset functionality that allows users to regain account access through email verification. This feature will reduce support ticket volume and improve user experience by providing self-service account recovery.
  </example>
</section>

<section name="user_stories">
  <template>
    ## User Stories

    ### [STORY_TITLE]

    As a [USER_TYPE], I want to [ACTION], so that [BENEFIT].

    [DETAILED_WORKFLOW_DESCRIPTION]
  </template>
  <constraints>
    - count: 1-3 stories
    - include: workflow and problem solved
    - format: title + story + details
  </constraints>
</section>

<section name="spec_scope">
  <template>
    ## Spec Scope

    1. **[FEATURE_NAME]** - [ONE_SENTENCE_DESCRIPTION]
    2. **[FEATURE_NAME]** - [ONE_SENTENCE_DESCRIPTION]
  </template>
  <constraints>
    - count: 1-5 features
    - format: numbered list
    - description: one sentence each
  </constraints>
</section>

<section name="out_of_scope">
  <template>
    ## Out of Scope

    - [EXCLUDED_FUNCTIONALITY_1]
    - [EXCLUDED_FUNCTIONALITY_2]
  </template>
  <purpose>explicitly exclude functionalities</purpose>
</section>

<section name="expected_deliverable">
  <template>
    ## Expected Deliverable

    1. [TESTABLE_OUTCOME_1]
    2. [TESTABLE_OUTCOME_2]
  </template>
  <constraints>
    - count: 1-3 expectations
    - focus: browser-testable outcomes
  </constraints>
</section>

<instructions>
  ACTION: Create spec.md with all sections
  FILL: Use spec details from steps 1-3
  MAINTAIN: Clear, concise descriptions
</instructions>

</step>

<step number="7" name="create_technical_spec">

### Step 7: Create Technical Specification

<step_metadata>
  <creates>
    - directory: sub-specs/
    - file: sub-specs/technical-spec.md
  </creates>
</step_metadata>

<file_template>
  <header>
    # Technical Specification

    This is the technical specification for the spec detailed in @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md

    > Created: [CURRENT_DATE]
    > Version: 1.0.0
  </header>
</file_template>

<spec_sections>
  <technical_requirements>
    - functionality details
    - UI/UX specifications
    - integration requirements
    - performance criteria
  </technical_requirements>
  <approach_options>
    - multiple approaches (if applicable)
    - selected approach
    - rationale for selection
  </approach_options>
  <external_dependencies>
    - new libraries/packages
    - justification for each
    - version requirements
  </external_dependencies>
</spec_sections>

<example_template>
  ## Technical Requirements

  - [SPECIFIC_TECHNICAL_REQUIREMENT]
  - [SPECIFIC_TECHNICAL_REQUIREMENT]

  ## Approach Options

  **Option A:** [DESCRIPTION]
  - Pros: [LIST]
  - Cons: [LIST]

  **Option B:** [DESCRIPTION] (Selected)
  - Pros: [LIST]
  - Cons: [LIST]

  **Rationale:** [EXPLANATION]

  ## External Dependencies

  - **[LIBRARY_NAME]** - [PURPOSE]
  - **Justification:** [REASON_FOR_INCLUSION]
</example_template>

<instructions>
  ACTION: Create sub-specs folder and technical-spec.md
  DOCUMENT: All technical decisions and requirements
  JUSTIFY: Any new dependencies
</instructions>

</step>

<step number="8" name="create_database_schema">

### Step 8: Create Database Schema (Conditional: ignore unless user asks to create)

<step_metadata>
  <creates>
    - file: sub-specs/database-schema.md
  </creates>
  <condition>only if database changes needed</condition>
</step_metadata>

<decision_tree>
  IF spec_requires_database_changes:
    CREATE sub-specs/database-schema.md
  ELSE:
    SKIP this_step
</decision_tree>

<file_template>
  <header>
    # Database Schema

    This is the database schema implementation for the spec detailed in @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md

    > Created: [CURRENT_DATE]
    > Version: 1.0.0
  </header>
</file_template>

<schema_sections>
  <changes>
    - new tables
    - new columns
    - modifications
    - migrations
  </changes>
  <specifications>
    - exact SQL or migration syntax
    - indexes and constraints
    - foreign key relationships
  </specifications>
  <rationale>
    - reason for each change
    - performance considerations
    - data integrity rules
  </rationale>
</schema_sections>

<instructions>
  ACTION: Check if database changes needed
  CREATE: database-schema.md only if required
  INCLUDE: Complete SQL/migration specifications
</instructions>

</step>

<step number="9" name="create_api_spec">

### Step 9: Create API Specification (Conditional: ignore unless user asks to create)

<step_metadata>
  <creates>
    - file: sub-specs/api-spec.md
  </creates>
  <condition>only if API changes needed</condition>
</step_metadata>

<decision_tree>
  IF spec_requires_api_changes:
    CREATE sub-specs/api-spec.md
  ELSE:
    SKIP this_step
</decision_tree>

<file_template>
  <header>
    # API Specification

    This is the API specification for the spec detailed in @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md

    > Created: [CURRENT_DATE]
    > Version: 1.0.0
  </header>
</file_template>

<api_sections>
  <routes>
    - HTTP method
    - endpoint path
    - parameters
    - response format
  </routes>
  <controllers>
    - action names
    - business logic
    - error handling
  </controllers>
  <purpose>
    - endpoint rationale
    - integration with features
  </purpose>
</api_sections>

<endpoint_template>
  ## Endpoints

  ### [HTTP_METHOD] [ENDPOINT_PATH]

  **Purpose:** [DESCRIPTION]
  **Parameters:** [LIST]
  **Response:** [FORMAT]
  **Errors:** [POSSIBLE_ERRORS]
</endpoint_template>

<instructions>
  ACTION: Check if API changes needed
  CREATE: api-spec.md only if required
  DOCUMENT: All endpoints and controllers
</instructions>

</step>

<step number="10" name="create_tests_spec">

### Step 10: Create Tests Specification

<step_metadata>
  <creates>
    - file: sub-specs/tests.md
  </creates>
</step_metadata>

<file_template>
  <header>
    # Tests Specification

    This is the tests coverage details for the spec detailed in @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md

    > Created: [CURRENT_DATE]
    > Version: 1.0.0
  </header>
</file_template>

<test_categories>
  <unit_tests>
    - model tests
    - service tests
    - helper tests
  </unit_tests>
  <integration_tests>
    - controller tests
    - API tests
    - workflow tests
  </integration_tests>
  <feature_tests>
    - end-to-end scenarios
    - user workflows
  </feature_tests>
  <mocking_requirements>
    - external services
    - API responses
    - time-based tests
  </mocking_requirements>
</test_categories>

<test_template>
  ## Test Coverage

  ### Unit Tests

  **[CLASS_NAME]**
  - [TEST_DESCRIPTION]
  - [TEST_DESCRIPTION]

  ### Integration Tests

  **[FEATURE_NAME]**
  - [SCENARIO_DESCRIPTION]
  - [SCENARIO_DESCRIPTION]

  ### Mocking Requirements

  - **[SERVICE_NAME]:** [MOCK_STRATEGY]
</test_template>

<instructions>
  ACTION: Create comprehensive test specification
  ENSURE: All new functionality has test coverage
  SPECIFY: Mock requirements for external services
</instructions>

</step>

<step number="11" name="user_review">

### Step 11: User Review

<step_metadata>
  <action>request user review</action>
  <reviews>
    - spec.md
    - all sub-specs files
  </reviews>
</step_metadata>

<review_request>
  I've created the spec documentation:

  - Spec Requirements: @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md
  - Technical Spec: @.agent-os/specs/YYYY-MM-DD-spec-name/sub-specs/technical-spec.md
  [LIST_OTHER_CREATED_SPECS]

  Please review and let me know if any changes are needed before I create the task breakdown.
</review_request>

<instructions>
  ACTION: Request user review of all documents
  WAIT: For approval or revision requests
  REVISE: Make requested changes if any
</instructions>

</step>

<step number="12" name="create_tasks">

### Step 12: Create tasks.md

<step_metadata>
  <creates>
    - file: tasks.md
  </creates>
  <depends_on>user approval from step 11</depends_on>
</step_metadata>

<file_template>
  <header>
    # Spec Tasks

    These are the tasks to be completed for the spec detailed in @.agent-os/specs/YYYY-MM-DD-spec-name/spec.md

    > Created: [CURRENT_DATE]
    > Status: Ready for Implementation
  </header>
</file_template>

<task_structure>
  <major_tasks>
    - count: 1-5
    - format: numbered checklist
    - grouping: by feature or component
  </major_tasks>
  <subtasks>
    - count: up to 8 per major task
    - format: decimal notation (1.1, 1.2)
    - first_subtask: typically write tests
    - last_subtask: verify all tests pass
  </subtasks>
</task_structure>

<task_template>
  ## Tasks

  - [ ] 1. [MAJOR_TASK_DESCRIPTION]
    - [ ] 1.1 Write tests for [COMPONENT]
    - [ ] 1.2 [IMPLEMENTATION_STEP]
    - [ ] 1.3 [IMPLEMENTATION_STEP]
    - [ ] 1.4 Verify all tests pass

  - [ ] 2. [MAJOR_TASK_DESCRIPTION]
    - [ ] 2.1 Write tests for [COMPONENT]
    - [ ] 2.2 [IMPLEMENTATION_STEP]
</task_template>

<ordering_principles>
  - Consider technical dependencies
  - Follow TDD approach
  - Group related functionality
  - Build incrementally
</ordering_principles>

<task_strategy_by_classification>
  <leaf_node_approach>
    <characteristics>
      - Detailed sub-task planning still required
      - Focus primarily on E2E testing over layer-by-layer testing
      - Autonomous implementation with comprehensive sub-tasks
      - Emphasis on end-user validation
    </characteristics>
    <task_template>
      - [ ] 1. [FEATURE_NAME] - Implementation
        - [ ] 1.1 Request E2E testing data from user
        - [ ] 1.2 Create E2E tests (with user data or generated)
        - [ ] 1.3 Implement core functionality
        - [ ] 1.4 Implement UI/UX components (if needed, since sometimes the projects don't have UI/UX)
        - [ ] 1.5 Integration with existing systems
        - [ ] 1.6 Verify E2E tests pass
        - [ ] 1.7 User acceptance validation
    </task_template>
  </leaf_node_approach>
  
  <core_node_approach>
    <characteristics>
      - Detailed step-by-step implementation required
      - Comprehensive testing at each layer
      - User consultation on implementation approach
      - More granular review points
    </characteristics>
    <task_template>
      - [ ] 1. [COMPONENT_NAME] - Core Implementation
        - [ ] 1.1 Consult user on implementation approach
        - [ ] 1.2 Request E2E testing data from user
        - [ ] 1.3 Write unit tests for core logic
        - [ ] 1.4 Implement core architecture/logic
        - [ ] 1.5 Write integration tests
        - [ ] 1.6 Create E2E tests (with user data or generated)
        - [ ] 1.7 Performance and security validation
        - [ ] 1.8 Documentation and code review
        - [ ] 1.9 Full test suite verification
    </task_template>
  </core_node_approach>
</task_strategy_by_classification>

<e2e_testing_data_requirements>
  <priority_order>
    1. Request testing data from user first
    2. Generate mock data if user cannot provide
    3. Document data source in tasks
  </priority_order>
  
  <user_request_template>
    ## E2E Testing Data Required

    For comprehensive end-to-end testing of this feature, I need realistic test data.

    **Required Data Types:**
    - [LIST_SPECIFIC_DATA_NEEDED]

    **Options:**
    1. **Preferred**: Provide sample/mock data that represents real usage
    2. **Alternative**: I can generate realistic mock data based on the spec

    Please provide the test data, or let me know if you'd like me to generate it.
  </user_request_template>
</e2e_testing_data_requirements>

<core_node_implementation_modes>
  <mode_selection_prompt>
    ## Core Node Implementation Approach

    This spec involves core system components that require careful handling.

    **Available Implementation Modes:**

    1. **Full Agent Implementation** - I handle all code changes with detailed review points
    2. **Agent Planning + User Implementation** - I provide detailed plans and code examples, you implement
    3. **User-Led Implementation** - You implement independently, I assist with testing and validation

    Which approach would you prefer for this core system work?
  </mode_selection_prompt>
  
  <mode_implications>
    <full_agent>
      - Agent writes all code
      - Multiple review checkpoints
      - Detailed testing at each layer
      - Comprehensive documentation
    </full_agent>
    <agent_planning>
      - Agent provides implementation plans
      - Code examples and patterns
      - User copies/implements manually
      - Agent assists with testing after implementation
    </agent_planning>
    <user_led>
      - User implements independently
      - Agent provides testing framework
      - Agent validates final implementation
      - Minimal code generation by agent
    </user_led>
  </mode_implications>
</core_node_implementation_modes>

<instructions>
  ACTION: Create task breakdown based on node classification
  STRATEGY: Use appropriate template for leaf vs core nodes
  REQUEST: E2E testing data from user first
  CONSULT: User for core node implementation approach
  STRUCTURE: Major tasks with detailed subtasks
  ORDER: Consider dependencies and testing requirements
</instructions>

</step>

<step number="13" name="update_cross_references">

### Step 13: Documentation Cross-References

<step_metadata>
  <updates>
    - file: spec.md
  </updates>
  <adds>references to all spec files</adds>
</step_metadata>

<reference_template>
  ## Spec Documentation

  - Tasks: @.agent-os/specs/YYYY-MM-DD-spec-name/tasks.md
  - Technical Specification: @.agent-os/specs/YYYY-MM-DD-spec-name/sub-specs/technical-spec.md
  - API Specification: @.agent-os/specs/YYYY-MM-DD-spec-name/sub-specs/api-spec.md
  - Database Schema: @.agent-os/specs/YYYY-MM-DD-spec-name/sub-specs/database-schema.md
  - Tests Specification: @.agent-os/specs/YYYY-MM-DD-spec-name/sub-specs/tests.md
</reference_template>

<reference_format>
  - Use @ prefix for clickable paths
  - Include full path from project root
  - Only list files that were created
</reference_format>

<instructions>
  ACTION: Update spec.md with references
  FORMAT: Use @ prefix for all paths
  INCLUDE: Only files actually created
</instructions>

</step>

<step number="14" name="decision_documentation">

### Step 14: Decision Documentation

<step_metadata>
  <evaluates>strategic impact</evaluates>
  <updates>decisions.md if needed</updates>
</step_metadata>

<decision_analysis>
  <review_against>
    - @.agent-os/product/mission.md
    - @.agent-os/product/decisions.md
  </review_against>
  <criteria>
    - changes product direction
    - impacts roadmap priorities
    - introduces new technical patterns
    - affects user experience significantly
  </criteria>
</decision_analysis>

<decision_tree>
  IF spec_impacts_mission_or_roadmap:
    IDENTIFY key_decisions (max 3)
    DOCUMENT decision_details
    ASK user_for_approval
    IF approved:
      UPDATE decisions.md
  ELSE:
    STATE "This spec is inline with the current mission and roadmap, so no need to post anything to our decisions log at this time."
</decision_tree>

<decision_template>
  ## [CURRENT_DATE]: [DECISION_TITLE]

  **ID:** DEC-[NEXT_NUMBER]
  **Status:** Accepted
  **Category:** [technical/product/business/process]
  **Related Spec:** @.agent-os/specs/YYYY-MM-DD-spec-name/

  ### Decision

  [DECISION_SUMMARY]

  ### Context

  [WHY_THIS_DECISION_WAS_NEEDED]

  ### Consequences

  **Positive:**
  - [EXPECTED_BENEFITS]

  **Negative:**
  - [KNOWN_TRADEOFFS]
</decision_template>

<instructions>
  ACTION: Analyze spec for strategic decisions
  IDENTIFY: Up to 3 key decisions if any
  REQUEST: User approval before updating
  UPDATE: Add to decisions.md if approved
</instructions>

</step>

<step number="15" name="execution_readiness">

### Step 15: Execution Readiness Check

<step_metadata>
  <evaluates>readiness to begin implementation</evaluates>
  <depends_on>completion of all previous steps</depends_on>
</step_metadata>

<readiness_summary>
  <present_to_user>
    - Spec name and description
    - First task summary from tasks.md
    - Estimated complexity/scope
    - Key deliverables for task 1
  </present_to_user>
</readiness_summary>

<execution_prompt>
  PROMPT: "The spec planning is complete. The first task is:

  **Task 1:** [FIRST_TASK_TITLE]
  [BRIEF_DESCRIPTION_OF_TASK_1_AND_SUBTASKS]

  Would you like me to proceed with implementing Task 1? I will follow the execution guidelines in @~/.agent-os/instructions/execute-tasks.md and focus only on this first task and its subtasks unless you specify otherwise.

  Type 'yes' to proceed with Task 1, or let me know if you'd like to review or modify the plan first."
</execution_prompt>

<execution_flow>
  IF user_confirms_yes:
    REFERENCE: @~/.agent-os/instructions/execute-tasks.md
    FOCUS: Only Task 1 and its subtasks
    CONSTRAINT: Do not proceed to additional tasks without explicit user request
  ELSE:
    WAIT: For user clarification or modifications
</execution_flow>

<instructions>
  ACTION: Summarize first task and request user confirmation
  REFERENCE: Use execute-tasks.md for implementation
  SCOPE: Limit to Task 1 only unless user specifies otherwise
</instructions>

</step>

</process_flow>

## Execution Standards

<standards>
  <follow>
    - @.agent-os/product/code-style.md
    - @.agent-os/product/dev-best-practices.md
    - @.agent-os/product/tech-stack.md
  </follow>
  <maintain>
    - Consistency with product mission
    - Alignment with roadmap
    - Technical coherence
  </maintain>
  <create>
    - Comprehensive documentation
    - Clear implementation path
    - Testable outcomes
  </create>
</standards>

<final_checklist>
  <verify>
    - [ ] Accurate date determined via file system
    - [ ] Spec folder created with correct date prefix
    - [ ] spec.md contains all required sections
    - [ ] All applicable sub-specs created
    - [ ] User approved documentation
    - [ ] tasks.md created with TDD approach
    - [ ] Cross-references added to spec.md
    - [ ] Strategic decisions evaluated
  </verify>
</final_checklist>
