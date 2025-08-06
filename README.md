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

### 1. Set Up Product Documentation
```bash
# For new projects
@instructions/plan-product.md

# For existing codebases  
@instructions/analyze-product.md
```

### 2. Create Feature Specifications
```bash
@instructions/create-spec.md
```

### 3. Execute Development Tasks
```bash
@instructions/execute-tasks.md
```

## 🏗️ Architecture

### Instructions
- **`plan-product.md`** - Initialize new product with mission, roadmap, and tech stack
- **`analyze-product.md`** - Add Agent OS to existing codebases, triggering a one-time, full-project architecture analysis.
- **`analyze-node-classes.md`** - A reusable instruction that performs a deep, dependency-based analysis of the entire codebase to generate baseline architecture documents.
- **`create-spec.md`** - Plan features by leveraging the existing architecture analysis to determine impact and classify the feature.
- **`execute-tasks.md`** - Execute tasks with adaptive workflows based on the feature's classification.

### Standards  
- **`tech-stack.md`** - Technology preferences and patterns
- **`code-style.md`** - Coding standards and conventions
- **`best-practices.md`** - Development workflow guidelines

### Specialized Agents
- **`leaf-node-agent.md`** - Autonomous implementation for standalone features
- **`core-node-agent.md`** - Careful oversight for critical system components
- **Additional subagents** - Context fetching, git workflow, testing, etc.

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
- **`.agent-os/architecture-analysis/dependency_map.mermaid`**: Visual dependency graph with color-coded node types
- **`.agent-os/architecture-analysis/node_classification.md`**: Detailed analysis table with in-degree/out-degree metrics
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

## 📁 Project Structure

```
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

# Generated during project initialization:
.agent-os/
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

## 🎯 Enhanced Benefits

### 🧠 Data-Driven Intelligence
- **Dependency Analysis**: Makes decisions based on actual code relationships, not just heuristics
- **Visual Documentation**: Mermaid graphs provide clear dependency visualization
- **Quantified Risk**: Uses metrics (in-degree/out-degree) for objective classification
- **Impact Prediction**: Calculates "blast radius" before making changes

### 🎯 Precision Classification & Delegation
- **Component-Level Granularity**: Classifies individual functions/classes, not just features
- **Centralized Decision Making**: Main agent handles all classification and delegation logic
- **Specialized Agent Routing**: Automatically delegates to core-node or leaf-node agents
- **Evidence-Based Decisions**: Shows dependency data to support recommendations
- **Fallback Mechanisms**: Uses legacy indicators when dependency analysis unavailable

### 🚀 Adaptive Development Strategies
- **Intelligent Agent Selection**: Right specialist for each component type
- **Phase-Based Implementation**: Core → Business → Leaf progression for mixed specs
- **Selective Testing**: E2E for leaves, comprehensive for core, standard for business logic
- **Risk-Proportional Quality**: Code quality requirements match component criticality
- **Autonomous vs Oversight**: Right level of AI involvement per component type

### 👥 Developer Experience
- **Transparent Reasoning**: Shows why each classification was made and which agent was selected
- **Visual Dependencies**: Understand system architecture at a glance  
- **Project-Level Persistence**: Architecture analysis reused across all features
- **Flexible Control**: Choose involvement level per component, not just per feature
- **Documentation Artifacts**: Generates reusable dependency maps and classification tables

## 🔧 Configuration

The framework adapts to your project by reading:
- **Product documentation** in `.agent-os/product/`
- **Architecture analysis** in `.agent-os/architecture-analysis/` (auto-generated)
- **Global standards** from `~/.agent-os/standards/`
- **Specialized agents** from `~/.agent-os/subagents/`
- **Project-specific preferences** in local files

## 🆕 Key Architectural Improvements

### Modular & Reusable Node Analysis
- **Standalone Instruction**: The core logic for dependency analysis has been extracted into its own reusable file: `analyze-node-classes.md`.
- **One-Time Analysis**: This analysis is now run once during the `analyze-product.md` phase to create a persistent, project-wide architecture baseline.
- **Efficient Feature Planning**: `create-spec.md` no longer performs a full analysis. Instead, it efficiently leverages the existing baseline to quickly assess the impact of a new feature.

### Centralized Classification Logic
- **Main Agent Decision Making**: All node classification logic centralized in `execute-tasks.md`
- **Specialized Agent Delegation**: Main agent routes to appropriate subagents based on analysis
- **Clean Separation of Concerns**: Subagents focus on execution, main agent handles strategy

### Project-Level Architecture Analysis  
- **Persistent Analysis**: Architecture analysis stored at `.agent-os/architecture-analysis/` (not per-spec)
- **Reusable Across Features**: Single dependency analysis used for all feature development
- **Better File Organization**: Clear separation between project-wide analysis and spec-specific docs

### Enhanced Agent Orchestration
- **Smart Routing**: Main agent automatically selects core-node-agent or leaf-node-agent
- **Transparent Decision Making**: Users see exactly why each delegation decision was made
- **Fallback Mechanisms**: Traditional TDD when specialized approaches not suitable

## 🤝 Contributing

This framework is designed to evolve with your development patterns. Contributions welcome for:
- Additional node classification criteria
- New specialized subagents
- Improved workflow automation
- Better integration patterns

## 📚 Related

- [Original Agent OS](https://github.com/buildermethods/agent-os)
- [Vibe Coding Talk](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As) by Erik Schultz
- [Builder Methods](https://buildermethods.com/agent-os)
