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

## 📦 Installation & Setup

### Prerequisites

Before using Agent OS, ensure you have:
- **Claude Code CLI** or **Cursor IDE**
- **Git** initialized project (recommended)
- **Node.js** 18+ (if building web applications)
- Write access to your project directory

### Must Do: Clone repo to your environment
```bash
cd ~
git clone https://github.com/fredrick84823/agent-os-adaptive.git
```

### 🆕 Option 1: New Project (0 → 1)

For starting a fresh project with Agent OS:

1. **Create & Initialize Project**
   ```bash
   mkdir my-new-project
   cd my-new-project
   git init
   ```

2. **Initialize Agent OS Product Documentation**
    - In Claude Code
   ```bash
   /plan-product
   I want to build a ...
   ```
   - In Cursor
   ```bash
   @plan-product
   I want to build a ...
   ```

   You'll be prompted for:
   - Main product idea
   - Key features (minimum 3)
   - Target users
   - Tech stack preferences

3. **Review Generated Documentation**
   ```bash
   # Agent OS creates these files under project folder:
   agent-os-adaptive/product/
   ├── mission.md          # Product vision
   ├── roadmap.md          # Development phases  
   ├── tech-stack.md       # Technology choices
   └── decisions.md        # Decision history
   ```

4. **Start Building Features**
    - In Claude Code
   ```bash
   /create-spec
   I want to add a feature, ...
   ```
   - In Cursor
   ```bash
   @create-spec
   I want to add a feature, ...
   ```

### 🔄 Option 2: Existing Project Integration

For adding Agent OS to an existing codebase:

1. **Navigate to Your Project**
   ```bash
   cd your-existing-project
   ```

2. **Analyze & Install Agent OS**
   ```bash
   /analyze-product
   Analyze project and creating agent os documents
   ```
   - In Cursor
   ```bash
   @analyze-product
   Analyze project and creating agent os documents
   ```

    **Tips: Chat with the agent to clarify the features you want to build**
   
3. **Review Analysis Results**
   Agent OS will:
   - ✅ Scan your codebase structure
   - ✅ Detect technology stack
   - ✅ Identify completed features
   - ✅ Generate architecture documentation

4. **Verify Generated Documentation**
   ```bash
   # Check generated files:
   agent-os-adaptive/
   ├── product/                    # Product documentation
   ├── architecture-analysis/      # Dependency analysis
   └── specs/                      # Future specs will go here
   ```

### ⚙️ Configuration

#### Global Standards (Optional)
Set up personal development standards:

```bash
# Create global Agent OS configuration
mkdir -p ~/agent-os-adaptive/standards
mkdir -p ~/agent-os-adaptive/instructions  
mkdir -p ~/agent-os-adaptive/subagents
```

Copy standard files from this repository to your global config.

#### Project-Specific Customization
Agent OS adapts by reading:
- `agent-os-adaptive/product/` - Your product documentation
- `agent-os-adaptive/architecture-analysis/` - Auto-generated dependency analysis
- `~/agent-os-adaptive/standards/` - Your global preferences

### Method 1: Direct Repository Clone (Recommended)

1. **Clone Agent OS Adaptive to your home directory**
   ```bash
   # Clone to root directory
   cd ~
   git clone https://github.com/fredrick84823/agent-os-adaptive.git
   ```

2. **Initialize with AI Agent conversation**
   
   **For New Projects:**
   ```
   🤖 Ask your AI: "I want to set up Agent OS for a new project. 
   Please use @~/agent-os-adaptive/instructions/plan-product.md to help me create 
   product documentation."
   ```
   
   **For Existing Projects:**
   ```
   🤖 Ask your AI: "I want to add Agent OS to my existing codebase. 
   Please use @~/agent-os-adaptive/instructions/analyze-product.md to analyze 
   my project and set up the documentation."
   ```

3. **Follow the Interactive Setup**
   
   The AI will guide you through:
   - 📝 Product mission and vision
   - 🎯 Key features and target users  
   - 🛠️ Technology stack detection/selection
   - 🗂️ Project structure analysis (for existing projects)
   - 📋 Development roadmap creation

4. **Start Feature Development**
   ```
   🤖 Ask your AI: "What should we work on next?" 
   or
   🤖 Ask your AI: "I want to build [feature description]. 
   Please use @~/agent-os-adaptive/instructions/create-spec.md to plan this feature."
   ```

### Method 2: Direct Command Usage

Once Agent OS is set up, use these commands directly:

```bash
# Plan your product (first time setup)
@~/agent-os-adaptive/instructions/plan-product.md

# Analyze existing codebase 
@~/agent-os-adaptive/instructions/analyze-product.md

# Create feature specifications
@~/agent-os-adaptive/instructions/create-spec.md

# Execute development tasks
@~/agent-os-adaptive/instructions/execute-tasks.md
```

### 💬 Sample AI Conversations

**Initial Setup:**
> **You:** "Help me set up Agent OS for my e-commerce project"
> 
> **AI:** "I'll help you set up Agent OS! Let me use the plan-product instruction to create your product documentation. What's your main product idea?"

**Feature Planning:**
> **You:** "I need to add user authentication to my app"
> 
> **AI:** "I'll create a spec for user authentication. Let me analyze your codebase first to determine if this affects core or leaf nodes, then plan accordingly."

**Development:**
> **You:** "Let's implement the user registration feature"
> 
> **AI:** "Based on the dependency analysis, user registration affects core authentication nodes. I'll use careful oversight mode and comprehensive testing for this implementation."

## 📋 What's Created During Setup

| File/Directory | New Project | Existing Project | Purpose |
|----------------|-------------|------------------|----------|
| `agent-os-adaptive/product/mission.md` | ✅ | ✅ | Product vision & goals |
| `agent-os-adaptive/product/roadmap.md` | ✅ | ✅ | Development phases |
| `agent-os-adaptive/product/tech-stack.md` | ✅ | ✅ | Technology choices |  
| `agent-os-adaptive/product/decisions.md` | ✅ | ✅ | Decision history |
| `agent-os-adaptive/architecture-analysis/` | ❌ | ✅ | Dependency analysis |
| `CLAUDE.md` | ✅ | ✅ | Project-specific instructions |

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
- **Additional subagents** - Context fetching, git workflow, testing, etc. This is original subagents from agent-os

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

## 📁 Project Structure

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
- **Product documentation** in `agent-os-adaptive/product/`
- **Architecture analysis** in `agent-os-adaptive/architecture-analysis/` (auto-generated)
- **Global standards** from `~/agent-os-adaptive/standards/`
- **Specialized agents** from `~/agent-os-adaptive/subagents/`
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
- **Persistent Analysis**: Architecture analysis stored at `agent-os-adaptive/architecture-analysis/` (not per-spec)
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
- New idea of workflow

## 📚 Related

- [Original Agent OS](https://github.com/buildermethods/agent-os) by Brian Casel
- [Builder Methods](https://buildermethods.com/agent-os) by Brian Casel
- [Vibe Coding Talk](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As) by Erik Schultz