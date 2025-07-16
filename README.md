# Graduating your AI Agents Workshop 🤖

Welcome to the **Graduating your AI Agents Workshop**! This repository contains a comprehensive, hands-on tutorial for building AI agents that are ready for production use.

## 🎯 Workshop Overview

This workshop takes you from a simple toy example to a production-ready AI agent system. You'll learn the essential patterns, tools, and practices needed to build, deploy, and maintain AI agents in real-world scenarios.

### 🚀 What You'll Build

By the end of this workshop, you'll have built:
- A simple coding agent (toy example)
- A multi-agent system with specialized roles
- An agent with state management and memory
- A fully instrumented system with tracing and observability
- A production-ready agent with evaluation and monitoring

### 📋 Prerequisites

- **Python 3.8+** installed on your system
- **OpenAI API Key** (get one from [OpenAI Platform](https://platform.openai.com/api-keys))
- **Basic Python knowledge** (functions, classes, async/await)
- **Git** for version control
- **Terminal/Command Line** familiarity

## 🗺️ Workshop Structure

### 🎬 Introduction & Motivation (30 min)

**What we'll cover:**
- Setting up the development environment
- Understanding what makes an AI agent "production-ready"
- Analyzing existing production systems (e.g., GitHub Copilot)
- Key challenges in agent development

**Learning outcomes:**
- Understand the difference between toy examples and production systems
- Identify the key components of a production AI agent
- Set up your development environment

---

### 🧸 [Module 1: Toy Example](./1-toy-example/) (30 min)

**Build a simple coding agent from scratch**

**What you'll learn:**
- Core agent architecture patterns
- Tool calling and integration
- Basic error handling
- Agent-tool interaction loops

**What you'll build:**
- A coding agent that can write, execute, and test Python code
- Integration with file system operations using Composio's FileTool app
- A simple REPL (Read-Eval-Print Loop) tool

**Key files:**
- `coding_agent.py` - Main agent implementation
- `examples.py` - Demonstration scripts
- `requirements.txt` - Dependencies

[**📚 Start with Module 1 →**](./1-toy-example/README.md)

---

### 👥 [Module 2: Multi-Agent Systems](./2-multi-agent/) (30 min)

**When and how to use multiple agents**

**What you'll learn:**
- Multi-agent design patterns
- Agent coordination and communication
- Task decomposition and specialization
- When to use multiple agents vs. a single agent

**What you'll build:**
- A software development team with specialized agents
- Agent-to-agent communication protocols
- Task orchestration and workflow management

**Key concepts:**
- Agent roles and responsibilities
- Inter-agent communication
- Conflict resolution
- Performance optimization

---

### 🔍 [Module 3: Tracing & Observability](./3-tracing-observability/) (20 min)

**Monitoring, debugging, and performance optimization**

**What you'll learn:**
- Tracing for agent systems
- Performance monitoring and alerting
- Debugging complex agent behaviors
- Integration with observability platforms
- Lifecycle hooks (pre/post execution)

**What you'll build:**
- Comprehensive logging system
- Trace correlation across agent calls
- Error tracking and alerting
- Lifecycle event handlers

**Key concepts:**
- Structured logging
- Performance bottleneck identification
- Real-time monitoring
- Hook-based instrumentation

---

### 🧠 [Module 4: State Management](./4-state-management/) (30 min)

**Memory and context management**

**What you'll learn:**
- State persistence patterns
- Memory management for long-running agents

**What you'll build:**
- Persistent agent memory system
- Context-aware agents

**Key concepts:**
- Short-term vs. long-term memory
- Context retrieval and relevance

---

### 🧪 [Module 5: Evaluation & Testing](./5-evaluation/) (15 min)

**Quality assurance and continuous improvement**

**What you'll learn:**
- Agent evaluation frameworks
- LLM-based evaluation techniques

**What you'll build:**
- Automated evaluation pipeline
- Performance benchmarking system

**Key concepts:**
- Evaluation metrics design

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-agents-workshop.git
cd ai-agents-workshop
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (we'll do this per module)
```

### 3. Get API Keys

You'll need an OpenAI API key for all modules:

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Keep it secure - you'll add it to each module's `.env` file

### 4. Start with Module 1

```bash
cd 1-toy-example
pip install -r requirements.txt
# Follow the README instructions to set up your .env file
python coding_agent.py
```

## 📚 Learning Path

### For Beginners
Start with Module 1 and work through each module sequentially. Each module builds on the previous one.

### For Intermediate Developers
You can jump to specific modules based on your interests:
- **Multi-agent patterns** → Module 2
- **Monitoring** → Module 3
- **State management** → Module 4
- **Testing** → Module 5

### For Advanced Users
Focus on Modules 3-5 for production-ready patterns, or use the repository as a reference implementation.

## 🛠️ Development Environment

### Recommended Setup

- **IDE**: VS Code with Python extension
- **Python**: 3.8+ (3.10+ recommended)
- **Terminal**: Built-in terminal or iTerm2/Windows Terminal
- **Git**: Latest version

### Optional Tools

- **Docker**: For containerized development
- **Poetry**: For dependency management
- **Pre-commit**: For code quality checks

## 📖 Additional Resources

### Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Composio Documentation](https://docs.composio.dev/)
- [LangChain Documentation](https://docs.langchain.com/)

### Community & Support
- [Workshop Discussions](https://github.com/yourusername/ai-agents-workshop/discussions)
- [Report Issues](https://github.com/yourusername/ai-agents-workshop/issues)
- [Join Our Discord](https://discord.gg/your-discord-link)

### Further Learning
- [Production AI Systems](https://www.productionforcasting.com/)
- [Agent Design Patterns](https://github.com/microsoft/autogen)
- [AI Agent Papers](https://arxiv.org/list/cs.AI/recent)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report bugs** or suggest improvements
2. **Add new examples** or exercises
3. **Improve documentation**
4. **Share your agent implementations**

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This workshop is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

- Thanks to the OpenAI team for the excellent APIs and tools
- Thanks to Composio for the comprehensive tool integrations
- Thanks to the open-source community for inspiration and tools

---

**Ready to start building production-ready AI agents?** 

[**🚀 Begin with Module 1: Toy Example →**](./1-toy-example/README.md)

---

*This workshop is designed for educational purposes. Please follow OpenAI's usage policies and best practices when building production systems.*
