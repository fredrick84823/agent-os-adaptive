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
- **`analyze-product.md`** - Add Agent OS to existing codebases 
- **`create-spec.md`** - Plan features with intelligent node classification
- **`execute-tasks.md`** - Execute tasks with adaptive workflows

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

### 2. Comprehensive Documentation
- **`dependency_map.mermaid`**: Visual dependency graph with color-coded node types
- **`node_classification.md`**: Detailed analysis table with in-degree/out-degree metrics
- **Risk Assessment**: Quantified impact levels for each component

### 3. User Confirmation with Data
Presents dependency analysis results and classification with supporting evidence

### 4. Adaptive Planning by Node Type
- **Leaf Nodes**: E2E test setup → Autonomous implementation → User validation
- **Core Nodes**: Choose implementation mode → Comprehensive testing → Review cycles  
- **Mixed Approach**: Phase-based implementation (core → business → leaf)

### 5. Mode Selection (Core Nodes Only)
- **Full Agent**: AI handles everything with review points
- **Agent Planning**: AI plans, user implements  
- **User-Led**: User implements, AI validates

### 6. Component-Selective Execution
For mixed approach specs, applies different development strategies to different components based on their individual classifications

## 📁 Project Structure

```
agent-os-adaptive/
├── instructions/           # Core workflow instructions
│   ├── plan-product.md    # Product initialization
│   ├── create-spec.md     # Feature specification (enhanced with dependency analysis)
│   ├── execute-tasks.md   # Task execution (supports mixed approach)
│   └── analyze-product.md # Existing codebase analysis
├── standards/             # Development standards
│   ├── tech-stack.md      # Technology preferences
│   ├── code-style.md      # Coding conventions
│   └── best-practices.md  # Workflow guidelines
└── subagents/             # Specialized agent configurations
    ├── leaf-node-agent.md # Autonomous implementation
    ├── core-node-agent.md # Oversight-heavy approach
    └── ...                # Additional utility agents

# Generated during spec creation:
.agent-os/specs/YYYY-MM-DD-spec-name/
├── spec.md                # Spec requirements
├── tasks.md               # Implementation tasks
└── sub-specs/
    ├── dependency_map.mermaid      # Visual dependency graph
    ├── node_classification.md      # Component analysis table
    ├── technical-spec.md           # Technical requirements
    └── tests.md                    # Testing specifications
```

## 🎯 Enhanced Benefits

### Data-Driven Intelligence
- **Dependency Analysis**: Makes decisions based on actual code relationships, not just heuristics
- **Visual Documentation**: Mermaid graphs provide clear dependency visualization
- **Quantified Risk**: Uses metrics (in-degree/out-degree) for objective classification
- **Impact Prediction**: Calculates "blast radius" before making changes

### Precision Classification
- **Component-Level Granularity**: Classifies individual functions/classes, not just features
- **Mixed Approach Support**: Handles specs that span multiple node types
- **Evidence-Based Decisions**: Shows dependency data to support recommendations
- **Fallback Mechanisms**: Uses legacy indicators when dependency analysis unavailable

### Adaptive Development Strategies
- **Phase-Based Implementation**: Core → Business → Leaf progression for mixed specs
- **Selective Testing**: E2E for leaves, comprehensive for core, standard for business logic
- **Risk-Proportional Quality**: Code quality requirements match component criticality
- **Autonomous vs Oversight**: Right level of AI involvement per component type

### Developer Experience
- **Transparent Reasoning**: Shows why each classification was made
- **Visual Dependencies**: Understand system architecture at a glance
- **Flexible Control**: Choose involvement level per component, not just per feature
- **Documentation Artifacts**: Generates reusable dependency maps and classification tables

## 🔧 Configuration

The framework adapts to your project by reading:
- Product documentation in `.agent-os/product/`
- Global standards from `~/.agent-os/standards/`
- Project-specific preferences in local files

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
