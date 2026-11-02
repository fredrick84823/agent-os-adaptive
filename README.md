# Agent OS Adaptive

agent-os-adaptive is my optimized version of agent-os, designed to help AI agents be more "responsible" when collaborating with engineers.

It's an AI development framework that automatically adapts its approach based on code impact analysis. This is a fork of Agent OS with added leaf/core node classification to create optimal development workflows.

## 🧠 Core Innovation

**Dependency-Based Intelligent Classification**: Automatically analyzes actual code dependencies to determine optimal development approach:

- **🔍 Dependency Analysis** → Scans codebase and builds Mermaid dependency graphs  
- **📊 Quantified Classification** → Uses in-degree/out-degree metrics for precise categorization
- **🎯 File-Level Precision** → Classifies individual files/modules (computed by `tools/aoa_graph`), not just features
- **🔄 Mixed Approach Support** → Handles specs spanning multiple node types with phase-based implementation

### Classification Results:
- **Leaf Node** → Autonomous AI development with E2E testing focus
- **Core Node** → Careful oversight with comprehensive testing layers  
- **Business Logic** → Standard TDD with integration testing
- **Mixed Approach** → Selective strategies per component type

Inspired by Erik Schultz's talk on [Vibe Coding](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As), enhanced with data-driven dependency analysis.


## 🚀 Quick Start

### Prerequisites

- **Claude Code CLI** or **Cursor IDE** with Claude integration
- **Git** (recommended)

### Step 1: Clone Agent OS Adaptive

```bash
cd ~
git clone https://github.com/fredrick84823/agent-os-adaptive.git
```

### Step 2: Tool-Specific Setup

> The instructions reference files via `@~/agent-os-adaptive/...`, so keep the clone at `~/agent-os-adaptive` (Step 1). There is no hosted setup script; copy the files directly.

**Claude Code CLI**
```bash
# Instructions as custom slash commands (/plan-product, /analyze-product, /analyze-node-classes, /create-spec, /execute-tasks)
mkdir -p ~/.claude/commands ~/.claude/agents
cp ~/agent-os-adaptive/instructions/*.md ~/.claude/commands/

# Subagents (core-node-agent, leaf-node-agent, and utility agents)
cp ~/agent-os-adaptive/subagents/*.md ~/.claude/agents/
```

**Cursor IDE** (run inside your project)
```bash
mkdir -p .cursor/rules
for f in ~/agent-os-adaptive/instructions/*.md; do
  cp "$f" ".cursor/rules/$(basename "${f%.md}").mdc"
done
```

- Each instruction becomes a `.mdc` rule (e.g. `@plan-product`, `@execute-tasks`); their frontmatter already uses Cursor's `description` / `globs` / `alwaysApply` fields.

### Step 2b: Install the Dependency-Graph Tool (`aoa-graph`)

`/analyze-node-classes` no longer asks the model to estimate in/out-degrees. It runs `tools/aoa_graph`, a small Python CLI that parses **TypeScript / JavaScript and Python** with [tree-sitter](https://tree-sitter.github.io/) and writes deterministic numbers (same commit → byte-identical output).

Requires Python ≥ 3.10 (tested on 3.13) and `git` (for churn / bug-fix history).

```bash
python3 -m venv ~/agent-os-adaptive/.venv
~/agent-os-adaptive/.venv/bin/pip install -r ~/agent-os-adaptive/requirements.txt
```

Run it from your project root (the instruction does this for you):

```bash
~/agent-os-adaptive/.venv/bin/python ~/agent-os-adaptive/tools/aoa_graph .
# aoa-graph: 83 nodes, 180 edges, 2 cycles (22 nodes; runtime-only: 2 cycles), 2 unresolved, ... in 0.12s → ./agent-os-adaptive/architecture-analysis
```

| Output (in `agent-os-adaptive/architecture-analysis/`) | Contents |
|---|---|
| `graph.json` | File-level nodes (`id`, `language`, `is_test`, `loc`, Python `module`), internal edges with import `kinds`, external packages per file |
| `metrics.json` | Per node: `fan_in`, `fan_out`, `test_fan_in`, `blast_radius` (transitive dependents), `in_cycle` / `scc_id` (Tarjan), `in_runtime_cycle` (ignoring type-only imports), `churn`, `churn_lines`, `bugfix_count`, `co_change` |
| `unresolved.json` | Dynamic / unresolvable imports, files with parse errors — the part the model interprets |

Useful options: `--since-days 180` (history window, anchored at the HEAD commit time), `--bugfix-pattern REGEX`, `--exclude 'docs/**'`, `--py-root DIR`, `--lang ts|py`, `--out DIR`, `--no-git`. Full output format and resolution rules: [`tools/aoa_graph/README.md`](tools/aoa_graph/README.md).

### Step 3: Projects Setup

#### 🆕 For New Projects (0 → 1)

1. **Create your project**
   ```bash
   mkdir my-awesome-project
   cd my-awesome-project
   git init
   ```

2. **Initialize with Agent OS**

   **Claude Code:**
   ```bash
   /plan-product
   I want to build a SaaS tool for tracking customer feedback with AI-powered insights
   ```

   **Cursor:**
   ```bash
   @plan-product
   I want to build a SaaS tool for tracking customer feedback with AI-powered insights
   ```

#### 🔄 For Existing Projects

1. **Navigate to your project**
   ```bash
   cd your-existing-project
   ```

2. **Analyze and install Agent OS**

   **Claude Code:**
   ```bash
   # agent will analyze product -> plan product -> scan codebase to generate docs
   /analyze-product
   Please analyze my codebase and set up Agent OS documentation
   ```

   **Cursor:**
   ```bash
   # agent will analyze product -> plan product -> scan codebase to generate docs
   @analyze-product
   Please analyze my codebase and set up Agent OS documentation
   ```

   **Example**:

   ![Analyze Product](images/step3-analysis-product.png)

### Step 4: Interactive Setup

The AI will guide you through:
- 📝 **Product Mission**: Define your vision and target users
- 🛠️ **Tech Stack**: Detect or configure your technology choices  
- 📋 **Roadmap**: Create development phases and feature priorities
- 🏗️ **Architecture Analysis**: Map dependencies (existing projects only)

   **Example**:

   ![Interactive Setup](images/step4-interactive.png)

### Step 5: Start Building Features

**Claude Code:**
```bash
# Plan a new feature
/create-spec
I want to add user authentication with OAuth and email verification

# Execute development tasks  
/execute-tasks
Let's implement the user registration feature
```

**Cursor:**
```bash
# Plan a new feature
@create-spec
I want to add user authentication with OAuth and email verification

# Execute development tasks
@execute-tasks
Let's implement the user registration feature
```

### Step 6: What Gets Generated

Agent OS creates a complete project structure:

```bash
your-project/
├── agent-os-adaptive/
│   ├── product/                    # Product documentation
│   │   ├── mission.md             # Vision and goals
│   │   ├── roadmap.md             # Development phases
│   │   ├── tech-stack.md          # Technology choices
│   │   └── decisions.md           # Decision history
│   ├── architecture-analysis/     # Dependency analysis (existing projects)
│   │   ├── graph.json / metrics.json / unresolved.json  # Computed by aoa-graph
│   │   ├── dependency_map.mermaid # Visual dependency graph
│   │   └── node_classification.md# Component analysis
│   └── specs/YYYY-MM-DD-feature/  # Feature specifications
│       ├── spec.md                # Requirements
│       ├── tasks.md               # Implementation tasks
│       └── sub-specs/             # Technical details
└── CLAUDE.md                      # Project-specific instructions
```

### 💡 Example Results

See a complete example of Agent OS in action or just see examples folder in this repo:
**[ADK Data Science Agent](https://github.com/fredrick84823/adk-data-science-agent/tree/main/python/agents/data-science)** - A real project built using Agent OS Adaptive showing the complete structure and documentation.

## 🎯 Detail Feature Explanation

### 🔍 Intelligent Analysis Process

The system now performs comprehensive dependency analysis to make precise classifications:

1. **Codebase Scanning** - `tools/aoa_graph` parses TS/JS and Python files with tree-sitter (file/module granularity)
2. **Dependency Mapping** - Writes `graph.json`; the Mermaid map is rendered from it
3. **Impact Analysis** - `metrics.json` computes fan-in/out, "blast radius", cycles, git churn and bug-fix counts
4. **Component Classification** - The model interprets those numbers (it does not estimate them)

### 📊 Classification Categories

#### Leaf Nodes (Autonomous Development)
✅ **Low In-Degree, High Out-Degree**
- Few or no components depend on them
- Can be removed without breaking other features
- UI components with one-way data flow
- Report generators and exporters
- Feature-specific components

**Metrics**: In-degree ≤ 2, Out-degree ≥ 1
**Approach**: E2E-focused testing, rapid implementation, acceptable technical debt

#### Core Nodes (Careful Oversight)
⚠️ **High In-Degree, Low Out-Degree**
- Many components depend on them
- Critical path components
- Infrastructure and shared services
- Components with bidirectional dependencies

**Metrics**: In-degree ≥ 3, Out-degree ≤ 2
**Approach**: Comprehensive layer testing, architecture-first, multiple implementation modes

#### Business Logic Nodes (Standard Development)
🔄 **Medium In-Degree and Out-Degree**
- Orchestrates between core and leaf nodes
- Contains domain-specific logic
- Controllers and service layers

**Metrics**: Balanced dependency relationships
**Approach**: Standard TDD with integration testing focus

#### Mixed Approach (Component-Selective)
🎯 **Multiple Node Types in Single Spec**
- Different components require different approaches
- Phase-based implementation (core → business → leaf)
- Risk-based development prioritization

**Approach**: Selective strategies per component type

## 🔄 Enhanced Adaptive Workflow

### 1. Dependency-Based Code Analysis
- **Codebase Scanning**: `tools/aoa_graph` parses every TS/JS and Python file into a file-level dependency graph
- **Dependency Mapping**: Creates visual Mermaid graphs showing component relationships
- **Impact Calculation**: Measures "blast radius" of proposed changes
- **Component Classification**: Generates detailed classification tables with metrics

### 2. Comprehensive Architecture Analysis & Node Classification
The agent generates a detailed `node_classification.md` file that provides a complete breakdown of your codebase's architecture. This file is crucial for making informed decisions about development strategies.

**Example `node_classification.md`:**

```markdown
# Node Classification Analysis

> Created: 2025-08-05
> Project: ADK Data Science Multi-Agent System

## Component Classifications

### Core Nodes (Require Careful Oversight)

| Component | Type | In-Degree | Out-Degree | Risk Level | Justification |
|-----------|------|-----------|------------|------------|---------------|
| root_agent | CLASS | 8+ | 3 | HIGH | Central orchestrator - all tools and sub-agents depend on it |
| bigquery/tools | MODULE | 6+ | 4 | HIGH | Core BigQuery operations - used by all data access functions |

### Leaf Nodes (Autonomous Development Candidates)

| Component | Type | In-Degree | Out-Degree | Risk Level | Justification |
|-----------|------|-----------|------------|------------|---------------|
| export_query_results_to_csv | FUNCTION | 1 | 3 | LOW | Feature-specific export functionality - minimal dependencies |
| list_available_projects_and_datasets | FUNCTION | 1 | 2 | LOW | Information display feature - no other components depend on it |

## Development Recommendations

### For Core Node Changes
- **Approach:** Traditional careful development with comprehensive testing
- **Testing:** Full integration test suite, performance testing

### For Leaf Node Changes
- **Approach:** Autonomous development with E2E focus
- **Testing:** End-to-end user scenarios, acceptance testing
```

This analysis also includes:
- **Visual Dependency Map**: A link to the `dependency_map.mermaid` graph.
- **Risk Assessment**: Quantified impact levels for each component.
- **Project-Level Persistence**: The analysis is stored at the project level for reuse across all feature specifications.

### 3. Intelligent Agent Delegation
- **Main Agent Analysis**: Reads architecture analysis and classifies task components
- **Smart Delegation**: Routes to specialized subagents based on node types
- **Unified Decision Making**: Centralized classification logic with transparent reasoning

### 4. Specialized Agent Execution
- **Core Node Agent** (`@subagents/core-node-agent.md`): Careful oversight with comprehensive testing
- **Leaf Node Agent** (`@subagents/leaf-node-agent.md`): Autonomous rapid implementation
- **Mixed Approach**: Phase-based delegation to appropriate agents per component

### 5. Mode Selection (Core Nodes Only)
- **Full Agent**: AI handles everything with review points
- **Agent Planning**: AI plans, user implements  
- **User-Led**: User implements, AI validates

### 6. Component-Selective Execution
Main agent delegates different components to appropriate specialized agents based on dependency analysis

## 📁 Overall Folder Structure

```
# Cloned repository structure (~/agent-os-adaptive/):
agent-os-adaptive/
├── instructions/           # Core workflow instructions
│   ├── plan-product.md    # Product initialization
│   ├── analyze-product.md # Existing codebase analysis
│   ├── analyze-node-classes.md # (NEW) Standalone, reusable node classification
│   ├── create-spec.md     # Feature specification (uses analysis)
│   └── execute-tasks.md   # Task execution (adaptive)
├── tools/aoa_graph/       # Dependency-graph CLI (tree-sitter; TS/JS + Python)
├── tests/                 # pytest suite + small TS / Python fixture repos
├── requirements.txt       # Runtime deps for tools/aoa_graph
├── standards/             # Development standards
│   ├── tech-stack.md      # Technology preferences
│   ├── code-style.md      # Coding conventions
│   └── best-practices.md  # Workflow guidelines
└── subagents/             # Specialized agent configurations
    ├── leaf-node-agent.md # Autonomous implementation
    ├── core-node-agent.md # Oversight-heavy approach
    └── ...                # Additional utility agents

# Generated during project initialization (in your project):
agent-os-adaptive/
├── product/                       # Product-level documentation
│   ├── mission.md                # Product vision and goals
│   ├── roadmap.md                # Development phases
│   ├── tech-stack.md             # Technology choices
│   └── decisions.md              # Decision history
├── architecture-analysis/         # Project-wide analysis (NEW)
│   ├── graph.json                # Computed dependency graph (aoa-graph)
│   ├── metrics.json              # Computed per-file metrics (aoa-graph)
│   ├── unresolved.json           # Imports the tool could not resolve
│   ├── dependency_map.mermaid    # Visual dependency graph
│   └── node_classification.md    # Component analysis table
└── specs/YYYY-MM-DD-spec-name/   # Individual feature specs
    ├── spec.md                   # Spec requirements
    ├── tasks.md                  # Implementation tasks
    └── sub-specs/                # Spec-specific technical docs
        ├── technical-spec.md     # Technical requirements
        ├── api-spec.md           # API specifications (if needed)
        ├── database-schema.md    # Database changes (if needed)
        └── tests.md              # Testing specifications
```

## 🤝 Contributing

This framework is designed to evolve with your development patterns. Contributions welcome for:
- Additional node classification criteria
- New specialized subagents
- Improved workflow automation
- New idea of workflow

Before opening a PR, run:

```bash
python3 scripts/lint-instructions.py          # frontmatter, absolute paths, @~/agent-os-adaptive/ references
pip install -r requirements-dev.txt && pytest  # aoa-graph resolution, cycles, blast radius, git metrics, determinism
```

## 📚 Related

- [Original Agent OS](https://github.com/buildermethods/agent-os) by Brian Casel
- [Builder Methods](https://buildermethods.com/agent-os) by Brian Casel
- [Vibe Coding Talk](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As) by Erik Schultz