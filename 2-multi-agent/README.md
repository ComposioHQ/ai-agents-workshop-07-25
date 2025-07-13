# Multi-Agent Systems: When Specialization Beats Generalization

This module demonstrates when and how to use multiple AI agents working together to solve complex coding tasks. You'll learn about agent specialization, cost optimization, and coordination patterns that mirror real-world software development teams.

## 🎯 What You'll Learn

- **When to use multiple agents** vs. a single agent
- **Agent specialization patterns** and separation of concerns
- **Cost optimization** through strategic model selection
- **Handoff mechanisms** for seamless collaboration
- **Workflow orchestration** and dependency management
- **Real-world patterns** from software development teams

## 🚀 Key Concepts

### Agent Specialization

Just like in software development teams, different agents excel at different tasks:

- **🧠 Planner Agent** (GPT-4): Strategic thinking, task decomposition, architecture design
- **💻 Coder Agent** (GPT-4): Complex code generation, algorithm implementation  
- **🔍 Reviewer Agent** (GPT-3.5-turbo): Code review, style checking, bug detection
- **🧪 Tester Agent** (GPT-3.5-turbo): Test creation, validation, regression testing

### Cost Optimization

Strategic model selection can reduce costs by 60-70%:

```python
# Expensive: Using GPT-4 for everything
total_cost = 4 * $0.03 = $0.12 per 1K tokens

# Optimized: GPT-4 for complex tasks, GPT-3.5-turbo for structured tasks
total_cost = 2 * $0.03 + 2 * $0.002 = $0.064 per 1K tokens
# 47% cost reduction!
```

### Handoff Mechanisms

Agents can seamlessly hand off tasks to each other:

```python
# Planner creates a plan, then hands off to Coder
coder_result = planner.handoff_to(coder, "Implement this algorithm")

# Coder completes implementation, then hands off to Reviewer  
review_result = coder.handoff_to(reviewer, "Review this code")
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   MultiAgentSystem                          │
│                   (Orchestrator)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
   ┌───▼───┐         ┌────▼────┐         ┌───▼───┐
   │Planner│  ────▶  │ Coder   │  ────▶  │Tester │
   │(GPT-4)│         │(GPT-4)  │         │(3.5T) │
   └───────┘         └────┬────┘         └───────┘
                          │
                      ┌───▼────┐
                      │Reviewer│
                      │(3.5T)  │
                      └────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Understanding of the toy example (Module 1)

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in this directory:

```env
# OpenAI API Key - Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Composio API Key for enhanced file operations
COMPOSIO_API_KEY=your_composio_api_key_here
```

## 🎮 Usage

### Basic Multi-Agent Workflow

Run the default workflow:

```bash
python multi_agent_system.py
```

Or specify a custom task:

```bash
python multi_agent_system.py "Create a Python function that implements quicksort"
```

### Run Examples

See multiple patterns and use cases:

```bash
python examples.py
```

## 💡 Core Features

### 1. Specialized Agents

Each agent is optimized for its specific role:

#### Planner Agent
- **Role**: Strategic planning and task decomposition
- **Model**: GPT-4 (for complex reasoning)
- **Temperature**: 0.3 (structured planning)
- **Capabilities**: Requirements analysis, architecture design, workflow planning

#### Coder Agent  
- **Role**: Code implementation and development
- **Model**: GPT-4 (for complex code generation)
- **Temperature**: 0.1 (consistent code)
- **Capabilities**: Function/class implementation, debugging, optimization

#### Reviewer Agent
- **Role**: Code review and quality assurance
- **Model**: GPT-3.5-turbo (cost-effective for structured tasks)
- **Temperature**: 0.2 (consistent reviews)
- **Capabilities**: Bug detection, style checking, security review

#### Tester Agent
- **Role**: Test creation and validation
- **Model**: GPT-3.5-turbo (structured test generation)
- **Temperature**: 0.1 (consistent tests)
- **Capabilities**: Unit testing, integration testing, performance testing

### 2. Workflow Orchestration

The system automatically creates optimal workflows:

```python
workflow = [
    WorkflowStep(agent="planner", task="Create implementation plan"),
    WorkflowStep(agent="coder", task="Implement code", depends_on=["planner"]),
    WorkflowStep(agent="reviewer", task="Review code", depends_on=["coder"]),
    WorkflowStep(agent="tester", task="Create tests", depends_on=["coder"])
]
```

### 3. Cost Tracking

Real-time cost estimation and optimization:

```python
# Automatic cost calculation
total_cost = sum(step.cost_estimate for step in workflow_steps)
print(f"Estimated cost: ${total_cost:.4f}")

# Model usage tracking
for agent_name, artifact in result.artifacts.items():
    print(f"{agent_name}: {artifact['model_used']}")
```

## 📊 Example Session

Here's what a typical multi-agent session looks like:

```
🚀 Starting Multi-Agent Workflow
Task: Create a Python function that implements binary search
============================================================
💰 Estimated cost: $0.0740

🤖 Planner Agent: Creating workflow plan
🤖 Planner Agent: Executing step
✅ Completed: planner

🤖 Coder Agent: Executing step  
🤖 Coder Agent: Implementing code based on plan
✅ Completed: coder

🤖 Reviewer Agent: Executing step
🤖 Reviewer Agent: Reviewing code for quality and bugs
✅ Completed: reviewer

🤖 Tester Agent: Executing step
🤖 Tester Agent: Creating comprehensive test suite
✅ Completed: tester

============================================================
🎉 Workflow completed successfully!
⏱️  Execution time: 45.67 seconds
💰 Estimated cost: $0.0740

📊 Model Usage & Cost Optimization
- Planner: gpt-4
- Coder: gpt-4  
- Reviewer: gpt-3.5-turbo
- Tester: gpt-3.5-turbo
```

## 🔍 Advanced Features

### Custom Workflows

Create specialized workflows for specific use cases:

```python
system = MultiAgentSystem()

# Custom workflow for performance-critical code
workflow = system.create_workflow(
    task="Optimize this sorting algorithm",
    requirements={"performance": "O(n log n)", "memory": "in-place"}
)
```

### Individual Agent Usage

Use agents independently for specialized tasks:

```python
# Use just the reviewer for code review
reviewer = ReviewerAgent()
review_result = reviewer.review_code(code, requirements)

# Use just the tester for test creation
tester = TesterAgent()
test_result = tester.create_test_suite(code)
```

### Handoff Demonstrations

See how agents collaborate:

```python
system = MultiAgentSystem()
result = system.demonstrate_handoff("Create a hash table implementation")
```

## 🧪 Available Examples

The `examples.py` script includes:

1. **Simple Algorithm Implementation** - Basic workflow demonstration
2. **Data Structure Implementation** - Complex task requiring careful design
3. **Algorithm with Requirements** - Handling detailed specifications
4. **Utility Function Creation** - Practical programming tasks
5. **File Processing Function** - I/O operations and error handling
6. **Handoff Pattern Demo** - Agent collaboration patterns
7. **Cost Optimization Demo** - Model selection strategies

## 🎓 Learning Objectives

By the end of this module, you'll understand:

### When to Use Multiple Agents

✅ **Use multiple agents when:**
- Task complexity benefits from specialization
- Different steps require different expertise
- Cost optimization is important
- Quality assurance is critical
- Workflow needs to be reproducible

❌ **Stick with single agent when:**
- Task is simple and straightforward
- Overhead of coordination exceeds benefits
- Real-time response is critical
- Context switching costs are high

### Agent Design Patterns

1. **Separation of Concerns**: Each agent has a clear, focused responsibility
2. **Pipeline Pattern**: Sequential workflow with dependencies
3. **Review Pattern**: Independent validation by specialized agents
4. **Handoff Pattern**: Seamless task transfer between agents
5. **Cost Optimization**: Strategic model selection based on task complexity

### Production Considerations

- **Error Handling**: Graceful failure and recovery mechanisms
- **Performance**: Parallel execution where possible
- **Monitoring**: Cost tracking and performance metrics
- **Scalability**: Adding new agents and capabilities
- **Quality**: Consistent output through specialization

## 🚀 Next Steps

Ready to continue? Here's what's coming next:

1. **State Management** (Module 3): Learn how agents remember context and maintain state
2. **Tracing & Observability** (Module 4): Monitor and debug multi-agent systems
3. **Evaluation** (Module 5): Measure and improve agent performance

## 🐛 Troubleshooting

**Common Issues:**

1. **"Agent initialization failed"**
   - Check your OpenAI API key
   - Verify model availability
   - Ensure sufficient API credits

2. **"Workflow step failed"**
   - Check agent dependencies
   - Verify task complexity isn't too high
   - Review error messages for specific issues

3. **"Cost estimation inaccurate"**
   - Estimates are approximations
   - Actual costs depend on input/output lengths
   - Monitor real usage in OpenAI dashboard

## 🤝 Key Takeaways

- **Specialization improves quality**: Each agent excels at its specific role
- **Cost optimization is crucial**: Strategic model selection can reduce costs significantly
- **Coordination patterns matter**: Proper handoffs and dependencies ensure success
- **Real-world applicability**: These patterns mirror actual software development teams
- **Scalability benefits**: Adding new agents and capabilities is straightforward

---

**Next**: Ready to add memory and state management? Check out [Module 3: State Management](../3-state-management/README.md)! 