# Toy Example: Simple Coding Agent

This is the first example in our AI Agents Workshop series. We'll build a minimal coding agent from scratch that can write, execute, and manage Python code.

## 🎯 What You'll Learn

- How to create a basic AI agent using OpenAI's API
- How to implement tool calling with custom tools
- How to integrate file operations using Composio
- How to create a simple REPL (Read-Eval-Print Loop) for code execution
- Basic agent-tool interaction patterns

## 🚀 What Our Agent Can Do

The coding agent in this example can:

1. **Write Python code** based on natural language requests
2. **Execute Python code** using a built-in REPL tool
3. **Create and manage files** using Composio's file tools
4. **Test and validate code** by running it and showing results
5. **Iterate and improve** code based on execution results

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Basic understanding of Python

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in this directory with your API keys:

```env
# OpenAI API Key - Required for the coding agent
OPENAI_API_KEY=your_openai_api_key_here

# Composio API Key - Optional, for enhanced file operations
COMPOSIO_API_KEY=your_composio_api_key_here
```

### 3. Get Your API Keys

- **OpenAI API Key**: Get it from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Composio API Key**: Get it from [Composio Dashboard](https://app.composio.dev/) (optional)

## 🎮 Usage

### Basic Usage

Run the agent with the default example:

```bash
python coding_agent.py
```

This will ask the agent to create a prime number checker function and test it.

### Custom Requests

You can provide your own coding request:

```bash
python coding_agent.py "Create a Python function that calculates the factorial of a number"
```

```bash
python coding_agent.py "Write a function to find the longest word in a sentence and save it to a file"
```

### Example Session

Here's what a typical session looks like:

```
🚀 Starting Coding Agent - Toy Example
==================================================
🤖 Agent: Processing request: Create a Python function that checks if a number is prime and test it on the number 7
==================================================

--- Iteration 1 ---
🔧 Agent is calling tools...
   Calling: run_python_code
   Code executed:
   def is_prime(n):
       if n < 2:
           return False
       for i in range(2, int(n**0.5) + 1):
           if n % i == 0:
               return False
       return True
   
   # Test the function
   test_number = 7
   result = is_prime(test_number)
   print(f"Is {test_number} prime? {result}")
   
   Result: Output: Is 7 prime? True

🎉 Agent: I've created a function called `is_prime()` that checks if a number is prime...
```

## 🔍 Code Walkthrough

### Key Components

1. **Python REPL Tool** (`run_python_code`): Executes Python code safely and returns results
2. **Composio File Tools**: Provides file operations (create, edit, read, list, delete)
3. **Agent Loop**: Manages the conversation between user, agent, and tools
4. **Error Handling**: Catches and reports execution errors

### Agent Architecture

```
User Request → Agent (gpt-4.1) → Tool Calls → Tool Results → Agent Response
                    ↑                            ↓
                    ←──── Iterative Loop ────────
```

### Tool Integration

The agent has access to:
- `run_python_code`: Execute Python code
- `FILETOOL_CREATE_FILE`: Create new files
- `FILETOOL_EDIT_FILE`: Edit existing files
- `FILETOOL_READ_FILE`: Read file contents
- `FILETOOL_LIST_FILES`: List directory contents
- `FILETOOL_DELETE_FILE`: Delete files

## 🧪 Try These Examples

1. **Basic Function Creation**:
   ```bash
   python coding_agent.py "Create a function to reverse a string"
   ```

2. **File Operations**:
   ```bash
   python coding_agent.py "Create a function to count words in a text file and save the result to output.txt"
   ```

3. **Data Processing**:
   ```bash
   python coding_agent.py "Write a function to find the average of a list of numbers and test it with [1, 2, 3, 4, 5]"
   ```

4. **Error Handling**:
   ```bash
   python coding_agent.py "Create a function that handles division by zero gracefully"
   ```

## 🎓 Learning Points

### What Makes This Agent "Toy"?

This is a simplified agent that demonstrates core concepts but lacks production features:

- **No memory** between sessions
- **Simple error handling** 
- **No state persistence**
- **Limited security** in code execution
- **No advanced planning** or reasoning

### Next Steps

In the subsequent workshop modules, we'll add:
- Multi-agent collaboration (Module 2)
- State management and memory (Module 3)
- Tracing and observability (Module 4)
- Evaluation and testing (Module 5)

## 🐛 Troubleshooting

**Common Issues:**

1. **"OPENAI_API_KEY not found"**: Make sure you've created a `.env` file with your API key
2. **"Module not found"**: Run `pip install -r requirements.txt`
3. **"Code execution failed"**: Check if your Python environment is properly set up

**Need Help?**

- Check the error messages in the console
- Verify your API keys are correct
- Ensure all dependencies are installed
- Try running with the default example first

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Composio Documentation](https://docs.composio.dev/)
- [Python REPL Best Practices](https://realpython.com/python-repl/)

---

**Next**: Ready to move on? Check out `../2-multi-agent/` to learn when and how to use multiple agents! 