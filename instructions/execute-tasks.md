---
description: Task Execution Rules for Agent OS
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Task Execution Rules

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
  - Execute spec tasks systematically
  - Follow TDD development workflow
  - Ensure quality through testing and review
</purpose>

<context>
  - Part of Agent OS framework
  - Executed after spec planning is complete
  - Follows tasks defined in spec tasks.md
</context>

<prerequisites>
  - Spec documentation exists in @.agent-os/specs/
  - Tasks defined in spec's tasks.md
  - Development environment configured
  - Git repository initialized
</prerequisites>

<process_flow>

<step number="1" name="task_assignment">

### Step 1: Task Assignment

<step_metadata>
  <inputs>
    - spec_srd_reference: file path
    - specific_tasks: array[string] (optional)
  </inputs>
  <default>next uncompleted parent task</default>
</step_metadata>

<task_selection>
  <explicit>user specifies exact task(s)</explicit>
  <implicit>find next uncompleted task in tasks.md</implicit>
</task_selection>

<instructions>
  ACTION: Identify task(s) to execute
  DEFAULT: Select next uncompleted parent task if not specified
  CONFIRM: Task selection with user
</instructions>

</step>

<step number="2" name="context_analysis">

### Step 2: Context Analysis

<step_metadata>
  <reads>
    - spec SRD file
- spec tasks.md
- all files in spec sub-specs/ folder
    - @.agent-os/product/mission.md
  </reads>
  <purpose>complete understanding of requirements</purpose>
</step_metadata>

<context_gathering>
  <spec_level>
    - requirements from SRD
    - technical specs
    - test specifications
    - leaf/core node classification
    - implementation mode selection
  </spec_level>
  <product_level>
    - overall mission alignment
    - technical standards
    - best practices
  </product_level>
</context_gathering>

<classification_detection>
  <check_for>
    - Code Impact Assessment results in spec documentation
    - Node classification: leaf_node_candidate vs core_node_requires_oversight
    - Implementation mode selection for core nodes
    - E2E testing data requirements
  </check_for>
  <extract_metadata>
    - node_type: [leaf | core]
    - implementation_mode: [full_agent | agent_planning | user_led] (for core nodes)
    - testing_approach: [e2e_focused | comprehensive_layers]
    - has_user_testing_data: [true | false]
  </extract_metadata>
</classification_detection>

<instructions>
  ACTION: Read all spec documentation thoroughly
  ANALYZE: Requirements and specifications for current task
  EXTRACT: Node classification and implementation mode metadata
  UNDERSTAND: How task fits into overall spec goals and development approach
</instructions>

</step>

<step number="3" name="implementation_planning">

### Step 3: Implementation Planning

<step_metadata>
  <creates>execution plan</creates>
  <requires>user approval</requires>
</step_metadata>

<plan_structure>
  <format>numbered list with sub-bullets</format>
  <includes>
    - all subtasks from tasks.md
    - implementation approach (adapted to node classification)
    - dependencies to install
    - test strategy (E2E focused vs comprehensive)
    - implementation mode handling (for core nodes)
  </includes>
</plan_structure>

<plan_adaptation_by_classification>
  <leaf_node_plan>
    <focus>
      - E2E testing with user-provided or generated data
      - Rapid autonomous implementation
      - End-user validation emphasis
      - Acceptable technical debt
    </focus>
    <template>
      ## Implementation Plan for [TASK_NAME] (Leaf Node - Autonomous)

      **Classification:** Leaf Node Candidate
      **Approach:** Autonomous AI-driven development with E2E focus

      1. **E2E Testing Setup**
         - [TESTING_DATA_SOURCE: user-provided or generated]
         - Create comprehensive E2E test scenarios
         - Set up user acceptance validation

      2. **Core Implementation**
         - [FEATURE_IMPLEMENTATION_STEPS]
         - Focus on working functionality over perfect architecture
         - Prioritize user-facing behavior

      3. **Integration & Validation**
         - [INTEGRATION_STEPS]
         - End-to-end testing verification
         - User acceptance testing

      **Dependencies to Install:**
      - [LIBRARY_NAME] - [PURPOSE]

      **Test Strategy:** E2E-focused with user validation
    </template>
  </leaf_node_plan>

  <core_node_plan>
    <full_agent_mode>
      <template>
        ## Implementation Plan for [TASK_NAME] (Core Node - Full Agent)

        **Classification:** Core Node Requires Oversight
        **Mode:** Full Agent Implementation with Review Points

        1. **Foundation & Testing**
           - Write comprehensive unit tests
           - Implement core architecture with careful design
           - Integration testing setup

        2. **E2E Testing Setup** 
           - [TESTING_DATA_SOURCE: user-provided or generated]
           - Create E2E test scenarios
           - Performance and security validation

        3. **Implementation & Review**
           - [DETAILED_IMPLEMENTATION_STEPS]
           - Multiple review checkpoints
           - Documentation and code review

        **Dependencies to Install:**
        - [LIBRARY_NAME] - [PURPOSE]

        **Test Strategy:** Comprehensive layer-by-layer + E2E
      </template>
    </full_agent_mode>

    <agent_planning_mode>
      <template>
        ## Implementation Plan for [TASK_NAME] (Core Node - Planning Mode)

        **Classification:** Core Node Requires Oversight  
        **Mode:** Agent Planning + User Implementation

        **I will provide:**
        - Detailed implementation plans and code examples
        - Test specifications and patterns
        - Architecture guidance and best practices
        - Code review after your implementation

        **You will implement:**
        - Copy/paste and adapt the provided code patterns
        - Execute the step-by-step implementation plan
        - Run tests and validation as guided

        **Plan Overview:**
        1. [STEP_1] - I'll provide detailed code examples
        2. [STEP_2] - You implement following the patterns
        3. [STEP_3] - I'll assist with testing and validation

        Would you like me to start with the detailed implementation plans and code examples?
      </template>
    </agent_planning_mode>

    <user_led_mode>
      <template>
        ## Implementation Plan for [TASK_NAME] (Core Node - User Led)

        **Classification:** Core Node Requires Oversight
        **Mode:** User-Led Implementation

        **I will provide:**
        - Testing framework setup
        - Validation criteria and acceptance tests
        - Final implementation review and validation

        **You will handle:**
        - All code implementation
        - Architecture decisions
        - Development approach

        **My role:**
        - Set up E2E testing framework with [TESTING_DATA_SOURCE]
        - Provide test specifications
        - Validate final implementation against requirements

        Ready to set up the testing framework for your implementation?
      </template>
    </user_led_mode>
  </core_node_plan>
</plan_adaptation_by_classification>

<plan_selection_logic>
  IF node_type == "leaf":
    USE leaf_node_plan template
  ELIF node_type == "core" AND implementation_mode == "full_agent":
    USE core_node_plan.full_agent_mode template
  ELIF node_type == "core" AND implementation_mode == "agent_planning":
    USE core_node_plan.agent_planning_mode template
  ELIF node_type == "core" AND implementation_mode == "user_led":
    USE core_node_plan.user_led_mode template
  ELSE:
    USE standard plan_template (fallback)
</plan_selection_logic>

<approval_request>
  I've prepared the above implementation plan based on the [NODE_CLASSIFICATION] and [IMPLEMENTATION_MODE].
  Please review and confirm before I proceed with execution.
</approval_request>

<instructions>
  ACTION: Create execution plan adapted to node classification and mode
  SELECT: Appropriate template based on extracted metadata
  DISPLAY: Plan to user for review
  WAIT: For explicit approval before proceeding
  BLOCK: Do not proceed without affirmative permission
</instructions>

</step>

<step number="4" name="development_server_check">

### Step 4: Check for Development Server

<step_metadata>
  <checks>running development server</checks>
  <prevents>port conflicts</prevents>
</step_metadata>

<server_check_flow>
  <if_running>
    ASK user to shut down
    WAIT for response
  </if_running>
  <if_not_running>
    PROCEED immediately
  </if_not_running>
</server_check_flow>

<user_prompt>
  A development server is currently running.
  Should I shut it down before proceeding? (yes/no)
</user_prompt>

<instructions>
  ACTION: Check for running local development server
  CONDITIONAL: Ask permission only if server is running
  PROCEED: Immediately if no server detected
</instructions>

</step>

<step number="5" name="git_branch_management">

### Step 5: Git Branch Management

<step_metadata>
  <manages>git branches</manages>
  <ensures>proper isolation</ensures>
</step_metadata>

<branch_naming>
  <source>spec folder name</source>
  <format>exclude date prefix</format>
  <example>
    - folder: 2025-03-15-password-reset
    - branch: password-reset
  </example>
</branch_naming>

<branch_logic>
  <case_a>
    <condition>current branch matches spec name</condition>
    <action>PROCEED immediately</action>
  </case_a>
  <case_b>
    <condition>current branch is main/staging/review</condition>
    <action>CREATE new branch and PROCEED</action>
  </case_b>
  <case_c>
    <condition>current branch is different feature</condition>
    <action>ASK permission to create new branch</action>
  </case_c>
</branch_logic>

<case_c_prompt>
  Current branch: [CURRENT_BRANCH]
  This spec needs branch: [SPEC_BRANCH]

  May I create a new branch for this spec? (yes/no)
</case_c_prompt>

<instructions>
  ACTION: Check current git branch
  EVALUATE: Which case applies
  EXECUTE: Appropriate branch action
  WAIT: Only for case C approval
</instructions>

</step>

<step number="6" name="development_execution">

### Step 6: Development Execution

<step_metadata>
  <follows>approved implementation plan</follows>
  <adheres_to>all spec standards</adheres_to>
</step_metadata>

<execution_standards>
  <follow_exactly>
    - approved implementation plan
    - spec specifications
    - @.agent-os/product/code-style.md
    - @.agent-os/product/dev-best-practices.md
  </follow_exactly>
  <approach>adapted based on node classification and mode</approach>
</execution_standards>

<execution_modes>
  <leaf_node_execution>
    <characteristics>
      - E2E-first testing approach
      - Rapid autonomous implementation
      - Focus on working functionality
      - Acceptable technical debt
      - Larger implementation chunks
    </characteristics>
    <workflow>
      1. Set up E2E tests with user data or generated mock data
      2. Implement features in larger, autonomous chunks
      3. Verify E2E functionality continuously
      4. Focus on user-facing behavior over perfect architecture
      5. Validate with user acceptance criteria
    </workflow>
  </leaf_node_execution>

  <core_node_full_agent>
    <characteristics>
      - Comprehensive layer-by-layer testing
      - Detailed step-by-step implementation
      - Multiple review checkpoints
      - High code quality standards
    </characteristics>
    <workflow>
      1. Write comprehensive unit tests first
      2. Implement core architecture with careful design
      3. Add integration tests at each layer
      4. Set up E2E tests with user data
      5. Performance and security validation
      6. Code review and documentation
    </workflow>
  </core_node_full_agent>

  <core_node_planning_mode>
    <characteristics>
      - Agent provides detailed plans and examples
      - User implements following patterns
      - Agent assists with testing and review
    </characteristics>
    <workflow>
      1. Generate detailed implementation plans
      2. Provide code examples and patterns
      3. Guide user through step-by-step implementation
      4. Assist with testing setup and validation
      5. Review user implementation and provide feedback
    </workflow>
  </core_node_planning_mode>

  <core_node_user_led>
    <characteristics>
      - User handles all implementation
      - Agent provides testing framework only
      - Agent validates final result
    </characteristics>
    <workflow>
      1. Set up testing framework and E2E tests
      2. Provide validation criteria and acceptance tests
      3. User implements independently
      4. Agent validates final implementation
      5. Assist with any testing or deployment issues
    </workflow>
  </core_node_user_led>
</execution_modes>

<mode_selection_execution>
  IF node_type == "leaf":
    EXECUTE leaf_node_execution workflow
  ELIF node_type == "core" AND implementation_mode == "full_agent":
    EXECUTE core_node_full_agent workflow
  ELIF node_type == "core" AND implementation_mode == "agent_planning":
    EXECUTE core_node_planning_mode workflow
  ELIF node_type == "core" AND implementation_mode == "user_led":
    EXECUTE core_node_user_led workflow
  ELSE:
    EXECUTE traditional TDD workflow (fallback)
</mode_selection_execution>

<traditional_tdd_workflow>
  1. Write failing tests first
  2. Implement minimal code to pass
  3. Refactor while keeping tests green
  4. Repeat for each feature
</traditional_tdd_workflow>

<instructions>
  ACTION: Execute development plan using mode-appropriate workflow
  SELECT: Execution mode based on node classification and implementation mode
  FOLLOW: All coding standards and specifications
  ADAPT: Testing and implementation approach based on classification
  MAINTAIN: Appropriate code quality level for node type
</instructions>

</step>

<step number="7" name="task_status_updates">

### Step 7: Task Status Updates

<step_metadata>
  <updates>tasks.md file</updates>
  <timing>immediately after completion</timing>
</step_metadata>

<update_format>
  <completed>- [x] Task description</completed>
  <incomplete>- [ ] Task description</incomplete>
  <blocked>
    - [ ] Task description
    ⚠️ Blocking issue: [DESCRIPTION]
  </blocked>
</update_format>

<blocking_criteria>
  <attempts>maximum 3 different approaches</attempts>
  <action>document blocking issue</action>
  <emoji>⚠️</emoji>
</blocking_criteria>

<instructions>
  ACTION: Update tasks.md after each task completion
  MARK: [x] for completed items immediately
  DOCUMENT: Blocking issues with ⚠️ emoji
  LIMIT: 3 attempts before marking as blocked
</instructions>

</step>

<step number="8" name="test_suite_verification">

### Step 8: Run All Tests

<step_metadata>
  <runs>entire test suite</runs>
  <ensures>no regressions</ensures>
</step_metadata>

<test_execution>
  <order>
    1. Verify new tests pass
    2. Run entire test suite
    3. Fix any failures
  </order>
  <requirement>100% pass rate</requirement>
</test_execution>

<failure_handling>
  <action>troubleshoot and fix</action>
  <priority>before proceeding</priority>
</failure_handling>

<instructions>
  ACTION: Run complete test suite
  VERIFY: All tests pass including new ones
  FIX: Any test failures before continuing
  BLOCK: Do not proceed with failing tests
</instructions>

</step>

<step number="9" name="git_workflow">

### Step 9: Git Workflow

<step_metadata>
  <creates>
    - git commit
    - github push
    - pull request
  </creates>
</step_metadata>

<commit_process>
  <commit>
    <message>descriptive summary of changes</message>
    <format>conventional commits if applicable</format>
  </commit>
  <push>
    <target>spec branch</target>
    <remote>origin</remote>
  </push>
  <pull_request>
    <title>descriptive PR title</title>
    <description>functionality recap</description>
  </pull_request>
</commit_process>

<pr_template>
  ## Summary

  [BRIEF_DESCRIPTION_OF_CHANGES]

  ## Changes Made

  - [CHANGE_1]
  - [CHANGE_2]

  ## Testing

  - [TEST_COVERAGE]
  - All tests passing ✓
</pr_template>

<instructions>
  ACTION: Commit all changes with descriptive message
  PUSH: To GitHub on spec branch
  CREATE: Pull request with detailed description
</instructions>

</step>

<step number="10" name="roadmap_progress_check">

### Step 10: Roadmap Progress Check

<step_metadata>
  <checks>@.agent-os/product/roadmap.md</checks>
  <updates>if spec completes roadmap item</updates>
</step_metadata>

<roadmap_criteria>
  <update_when>
    - spec fully implements roadmap feature
    - all related tasks completed
    - tests passing
  </update_when>
  <caution>only mark complete if absolutely certain</caution>
</roadmap_criteria>

<instructions>
  ACTION: Review roadmap.md for related items
  EVALUATE: If current spec completes roadmap goals
  UPDATE: Mark roadmap items complete if applicable
  VERIFY: Certainty before marking complete
</instructions>

</step>

<step number="11" name="completion_notification">

### Step 11: Task Completion Notification

<step_metadata>
  <plays>system sound</plays>
  <alerts>user of completion</alerts>
</step_metadata>

<notification_command>
  afplay /System/Library/Sounds/Glass.aiff
</notification_command>

<instructions>
  ACTION: Play completion sound
  PURPOSE: Alert user that task is complete
</instructions>

</step>

<step number="12" name="completion_summary">

### Step 12: Completion Summary

<step_metadata>
  <creates>summary message</creates>
  <format>structured with emojis</format>
</step_metadata>

<summary_template>
  ## ✅ What's been done

  1. **[FEATURE_1]** - [ONE_SENTENCE_DESCRIPTION]
  2. **[FEATURE_2]** - [ONE_SENTENCE_DESCRIPTION]

  ## ⚠️ Issues encountered

  [ONLY_IF_APPLICABLE]
  - **[ISSUE_1]** - [DESCRIPTION_AND_REASON]

  ## 👀 Ready to test in browser

  [ONLY_IF_APPLICABLE]
  1. [STEP_1_TO_TEST]
  2. [STEP_2_TO_TEST]

  ## 📦 Pull Request

  View PR: [GITHUB_PR_URL]
</summary_template>

<summary_sections>
  <required>
    - functionality recap
    - pull request info
  </required>
  <conditional>
    - issues encountered (if any)
    - testing instructions (if testable in browser)
  </conditional>
</summary_sections>

<instructions>
  ACTION: Create comprehensive summary
  INCLUDE: All required sections
  ADD: Conditional sections if applicable
  FORMAT: Use emoji headers for scannability
</instructions>

</step>

</process_flow>

## Development Standards

<standards>
  <code_style>
    <follow>@.agent-os/product/code-style.md</follow>
    <enforce>strictly</enforce>
  </code_style>
  <best_practices>
    <follow>@.agent-os/product/dev-best-practices.md</follow>
    <apply>all directives</apply>
  </best_practices>
  <testing>
    <coverage>comprehensive</coverage>
    <approach>test-driven development</approach>
  </testing>
  <documentation>
    <commits>clear and descriptive</commits>
    <pull_requests>detailed descriptions</pull_requests>
  </documentation>
</standards>

## Error Handling

<error_protocols>
  <blocking_issues>
    - document in tasks.md
    - mark with ⚠️ emoji
    - include in summary
  </blocking_issues>
  <test_failures>
    - fix before proceeding
    - never commit broken tests
  </test_failures>
  <technical_roadblocks>
    - attempt 3 approaches
    - document if unresolved
    - seek user input
  </technical_roadblocks>
</error_protocols>

<final_checklist>
  <verify>
    - [ ] Task implementation complete
    - [ ] All tests passing
    - [ ] tasks.md updated
    - [ ] Code committed and pushed
    - [ ] Pull request created
    - [ ] Roadmap checked/updated
    - [ ] Summary provided to user
  </verify>
</final_checklist>
