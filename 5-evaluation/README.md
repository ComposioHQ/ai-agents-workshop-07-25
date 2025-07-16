# Multi-Agent System Evaluation Module

This module demonstrates how to evaluate multi-agent systems using **LLM-as-a-Judge** methodology. It's designed for educational purposes to show the core concepts of agent evaluation in a simple, understandable way.

## 🎯 What This Module Teaches

This evaluation system demonstrates:

1. **LLM-as-a-Judge**: How to use language models to evaluate agent outputs
2. **Systematic Testing**: How to run multiple evaluation tasks automatically
3. **Structured Evaluation**: How to define tasks and expected outcomes
4. **Performance Metrics**: How to score and analyze agent performance
5. **Evaluation Reporting**: How to generate comprehensive evaluation reports

## 🔧 How It Works

### 1. Define Evaluation Tasks

Tasks are defined in a simple JSONL format with three key components:

```json
{
  "name": "Task Name",
  "prompt": "What you want the agent to do",
  "expected_outcome": "What you expect the agent to produce"
}
```

**Example:**
```json
{"name": "Simple Calculator", "prompt": "Create a basic Python calculator with functions for addition, subtraction, multiplication, and division. Include error handling for division by zero.", "expected_outcome": "A Python file with calculator functions (add, subtract, multiply, divide) and proper error handling for division by zero."}
```

### 2. Run Agent System

For each task, the evaluation system:
- Runs the multi-agent system with the task prompt
- Captures the complete agent output
- Handles any errors gracefully

```python
# Run the agent system for evaluation
result = await run_multi_agent_system_with_state(
    user_request=task.prompt,
    project_name=f"EvalProject_{task.name}",
    session_id=session_id
)
```

### 3. LLM Judge Evaluation

The system uses an LLM to compare agent output with expected outcomes:

```python
def judge_output(self, task: EvaluationTask, agent_output: str) -> tuple[float, str]:
    """Use LLM as a judge to compare agent output with expected outcome"""
    
    judge_prompt = f"""
    You are an expert evaluator. Compare the agent's output with the expected outcome.
    
    Task: {task.name}
    Expected: {task.expected_outcome}
    Agent Output: {agent_output}
    
    Score 0.0-1.0 based on how well the output matches expectations.
    """
    
    # Call OpenAI API to get score and reasoning
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": judge_prompt}]
    )
```

### 4. Generate Reports

The system compiles results into comprehensive reports:

```
🎯 EVALUATION REPORT
==================================================
📊 Summary:
   Total Tasks: 5
   Passed: 4
   Failed: 1
   Success Rate: 80.0%
   Average Score: 0.75
```

## 📋 Sample Evaluation Tasks

The module includes 5 sample tasks that demonstrate different types of coding challenges:

1. **Simple Calculator** - Basic arithmetic operations with error handling
2. **To-Do List App** - CLI application with file persistence
3. **Password Generator** - Security-focused utility with customization
4. **File Organizer** - File system manipulation and organization
5. **Unit Converter** - Multi-category conversion system

## 🚀 Running the Evaluation

### Quick Start

1. **Install dependencies:**
```bash
pip install openai-agents composio-openai-agents python-dotenv openai
```

2. **Set up environment:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. **Run evaluation:**
```bash
python evaluation_suite.py
```

### What Happens

1. **Task Loading**: Reads tasks from `tasks.jsonl`
2. **Agent Execution**: Runs each task through the multi-agent system
3. **LLM Judging**: Compares outputs with expected outcomes
4. **Scoring**: Assigns scores (0.0-1.0) with pass threshold of 0.6
5. **Reporting**: Generates detailed evaluation report

## 🎓 Educational Value

### Core Concepts Demonstrated

**LLM-as-a-Judge Pattern:**
- Shows how to use LLMs for evaluation instead of rigid metrics
- Demonstrates flexible, context-aware evaluation
- Provides reasoning along with scores

**Systematic Evaluation:**
- Automated testing of agent performance
- Reproducible evaluation methodology
- Structured task definition and execution

**Performance Analysis:**
- Scoring mechanisms and thresholds
- Success/failure analysis
- Detailed reporting and insights

### Learning Outcomes

After working with this module, you'll understand:

1. How to design evaluation tasks for AI agents
2. How to implement LLM-as-a-Judge evaluation
3. How to systematically test agent performance
4. How to interpret and analyze evaluation results
5. How to create reproducible evaluation pipelines

## 🔧 Customization

### Adding New Tasks

Simply add lines to `tasks.jsonl`:

```json
{"name": "Web Scraper", "prompt": "Build a web scraper that extracts titles", "expected_outcome": "Python script using requests/BeautifulSoup"}
```

### Modifying Evaluation Criteria

Change the judge prompt in `evaluation_suite.py`:

```python
judge_prompt = f"""
Your custom evaluation criteria here...
Consider: functionality, code quality, error handling, etc.
"""
```

### Adjusting Scoring

Modify the pass threshold or scoring scale:

```python
# Change pass threshold
passed = score >= 0.7  # More strict

# Add custom scoring logic
if "comprehensive error handling" in agent_output:
    score += 0.1  # Bonus for good practices
```

## 📁 File Structure

```
5-evaluation/
├── evaluation_suite.py          # Main evaluation system
├── tasks.jsonl                  # Evaluation tasks definition
├── state_multi_agent_system.py  # The agent system being evaluated
├── README.md                    # This documentation
├── requirements.txt             # Dependencies
└── evaluation_results.json      # Results (generated)
```

## 🎯 Key Design Principles

**Simplicity**: Intentionally kept simple for educational purposes
**Flexibility**: Easy to modify tasks, scoring, and evaluation criteria
**Transparency**: Clear scoring with reasoning from LLM judge
**Reproducibility**: Consistent evaluation methodology across runs
**Extensibility**: Easy to add new evaluation dimensions

## 📊 Understanding Results

### Scoring Scale

- **0.9-1.0**: Excellent - Exceeds expectations
- **0.7-0.8**: Good - Meets most requirements
- **0.5-0.6**: Acceptable - Basic requirements met
- **0.3-0.4**: Poor - Significant gaps
- **0.0-0.2**: Failed - Major issues or irrelevant output

### Pass Threshold

- **0.6**: Default threshold for considering a task "passed"
- Balances being permissive enough for learning while maintaining standards
- Can be adjusted based on evaluation goals

## 🚀 Next Steps

This simple evaluation system can be extended with:

1. **Multiple Judge Models**: Compare different LLM judges
2. **Human Evaluation**: Add human-in-the-loop validation
3. **Advanced Metrics**: Code quality, security, performance metrics
4. **Automated Generation**: Generate evaluation tasks automatically
5. **Continuous Evaluation**: Set up automated evaluation pipelines

The goal is to provide a foundation for understanding agent evaluation while keeping the implementation simple and educational. 