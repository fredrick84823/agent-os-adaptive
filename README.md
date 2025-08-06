# Agent OS Adaptive

An intelligent development framework that automatically adapts its approach based on code impact analysis. Fork of [Agent OS](https://github.com/buildermethods/agent-os) with added leaf/core node classification for optimal development workflows.

## 🧠 Core Innovation

**Dependency-Based Intelligent Classification**: Automatically analyzes actual code dependencies to determine optimal development approach:

- **🔍 Dependency Analysis** → Scans codebase and builds Mermaid dependency graphs  
- **📊 Quantified Classification** → Uses in-degree/out-degree metrics for precise categorization
- **🎯 Component-Level Precision** → Classifies individual functions/classes, not just features
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
- **Node.js** 18+ (for web applications)
- Write access to your project directory

### Step 1: Clone Agent OS Adaptive

```bash
cd ~
git clone https://github.com/fredrick84823/agent-os-adaptive.git
```

### Step 2: Tool-Specific Setup
**Claude Code CLI**
```bash
curl -sSL https://raw.githubusercontent.com/buildermethods/agent-os/main/setup.sh | bash
```

- Copies the commands from the GitHub Repo to use as custom slash commands in your ~/.claude/commands/ folder.
- Optionally installs specialized subagent files from the GitHub Repo to your ~/.claude/agents/ folder for enhanced performance.

**Cursor IDE**
```bash
curl -sSL https://raw.githubusercontent.com/buildermethods/agent-os/main/setup-cursor.sh | bash
```

- Creates the .cursor/rules/ directory in your project.
- Copies the commands from the GitHub repo to your .cursor/rules/ folder with .mdc extensions.



### Step 3: Choose Your Path

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
   /analyze-product
   Please analyze my codebase and set up Agent OS documentation
   ```

   **Cursor:**
   ```bash
   @analyze-product
   Please analyze my codebase and set up Agent OS documentation
   ```

### Step 4: Interactive Setup

The AI will guide you through:
- 📝 **Product Mission**: Define your vision and target users
- 🛠️ **Tech Stack**: Detect or configure your technology choices  
- 📋 **Roadmap**: Create development phases and feature priorities
- 🏗️ **Architecture Analysis**: Map dependencies (existing projects only)

### Step 5: Start Building Features

**Claude Code:**
```bash
# Plan a new feature
/create-spec
I want to add user authentication with OAuth and email verification

# Execute development tasks  
/execute-task
Let's implement the user registration feature
```

**Cursor:**
```bash
# Plan a new feature
@create-spec
I want to add user authentication with OAuth and email verification

# Execute development tasks
@execute-task
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

### 💬 Sample Conversations

**Initial Setup:**
> **You:** "Help me set up Agent OS for my e-commerce project"
>
> **AI:** "I'll set up Agent OS for your e-commerce project. Let me create comprehensive product documentation. What's your main product idea and target market?"

**Feature Development:**
> **You:** "I need to add a recommendation engine"
>
> **AI:** "I'll analyze your codebase first to classify this as a leaf or core node, then create a spec with the appropriate development approach. Let me start by examining your architecture..."

**Smart Development:**
> **AI:** "Based on dependency analysis, the recommendation engine is a leaf node component. I'll use autonomous development with E2E testing focus for rapid implementation."

## 🎯 Advanced Dependency-Based Classification

### 🔍 Intelligent Analysis Process

The system now performs comprehensive dependency analysis to make precise classifications:

1. **Codebase Scanning** - Identifies all functions, classes, and modules
2. **Dependency Mapping** - Generates visual Mermaid dependency graphs
3. **Impact Analysis** - Calculates "blast radius" of changes
4. **Component Classification** - Uses in-degree/out-degree metrics for precise categorization

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
- **Codebase Scanning**: Scans all project files for functions and classes
- **Dependency Mapping**: Creates visual Mermaid graphs showing component relationships
- **Impact Calculation**: Measures "blast radius" of proposed changes
- **Component Classification**: Generates detailed classification tables with metrics

### 2. Comprehensive Architecture Analysis
- **`agent-os-adaptive/architecture-analysis/dependency_map.mermaid`**: Visual dependency graph with color-coded node types
- **`agent-os-adaptive/architecture-analysis/node_classification.md`**: Detailed analysis table with in-degree/out-degree metrics
- **Risk Assessment**: Quantified impact levels for each component
- **Project-Level Persistence**: Analysis stored at project level for reuse across all specs

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

## 📚 Related

- [Original Agent OS](https://github.com/buildermethods/agent-os) by Brian Casel
- [Builder Methods](https://buildermethods.com/agent-os) by Brian Casel
- [Vibe Coding Talk](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As) by Erik Schultz