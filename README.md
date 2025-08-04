# Agent OS Adaptive

An intelligent development framework that automatically adapts its approach based on code impact analysis. Fork of [Agent OS](https://github.com/buildermethods/agent-os) with added leaf/core node classification for optimal development workflows.

## 🧠 Core Innovation

**Intelligent Node Classification**: Automatically detects whether a feature is a:
- **Leaf Node** → Autonomous AI development with E2E testing focus
- **Core Node** → Careful oversight with comprehensive testing layers

Inspired by Erik Schultz's talk on [Vibe Coding](https://youtu.be/fHWFF_pnqDk?si=lzHZFO4TNMKGP7As).

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

## 🎯 Node Classification System

### Leaf Node Indicators
✅ **Autonomous Development Suitable**
- Standalone features with minimal dependencies
- UI components that don't affect core workflows  
- Report generation or data export features
- Utility functions used in limited contexts
- Features with clear boundaries

**Approach**: E2E-focused testing, rapid implementation, acceptable technical debt

### Core Node Indicators  
⚠️ **Oversight Required**
- Database schema changes affecting multiple features
- Authentication/authorization modifications
- Core API changes that other systems depend on
- Framework or architecture modifications
- Performance-critical components

**Approach**: Comprehensive layer testing, architecture-first, multiple implementation modes

## 🔄 Adaptive Workflow

### 1. Code Impact Analysis
Automatically analyzes feature requirements against classification criteria

### 2. User Confirmation
Presents classification and recommended approach for user approval

### 3. Adaptive Planning
- **Leaf Nodes**: E2E test setup → Autonomous implementation → User validation
- **Core Nodes**: Choose implementation mode → Comprehensive testing → Review cycles

### 4. Mode Selection (Core Nodes Only)
- **Full Agent**: AI handles everything with review points
- **Agent Planning**: AI plans, user implements  
- **User-Led**: User implements, AI validates

## 📁 Project Structure

```
agent-os-adaptive/
├── instructions/           # Core workflow instructions
│   ├── plan-product.md    # Product initialization
│   ├── create-spec.md     # Feature specification
│   ├── execute-tasks.md   # Task execution  
│   └── analyze-product.md # Existing codebase analysis
├── standards/             # Development standards
│   ├── tech-stack.md      # Technology preferences
│   ├── code-style.md      # Coding conventions
│   └── best-practices.md  # Workflow guidelines
└── subagents/             # Specialized agent configurations
    ├── leaf-node-agent.md # Autonomous implementation
    ├── core-node-agent.md # Oversight-heavy approach
    └── ...                # Additional utility agents
```

## 🎯 Benefits

### Intelligent Adaptation
- **Right Tool for the Job**: Matches development approach to feature complexity
- **Risk Management**: Prevents technical debt in critical systems
- **Speed Optimization**: Accelerates low-risk feature development

### Quality Assurance
- **Leaf Nodes**: E2E testing ensures user functionality works
- **Core Nodes**: Comprehensive testing catches integration issues
- **Adaptive Standards**: Quality level matches feature importance

### Developer Experience
- **Autonomous Mode**: AI handles routine features independently
- **Collaborative Mode**: Human oversight for critical components  
- **Flexible Control**: Choose your involvement level

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
