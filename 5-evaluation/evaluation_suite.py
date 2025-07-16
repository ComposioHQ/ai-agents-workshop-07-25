#!/usr/bin/env python3
"""
Simple Evaluation Suite for Multi-Agent System

This demonstrates how to evaluate agent performance by:
1. Loading tasks from a JSONL file
2. Running the agent system for each task
3. Using an LLM as a judge to compare outputs
4. Generating a simple evaluation report

Keep it simple and educational for workshop purposes.
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import openai
from dotenv import load_dotenv

# Import the state management system
from state_multi_agent_system import run_multi_agent_system_with_state

# Load environment variables
load_dotenv()

@dataclass
class EvaluationTask:
    """Represents a single evaluation task"""
    name: str
    prompt: str
    expected_outcome: str

@dataclass
class EvaluationResult:
    """Represents the result of evaluating a single task"""
    task_name: str
    agent_output: str
    expected_outcome: str
    judge_score: float
    judge_reasoning: str
    passed: bool

class SimpleEvaluator:
    """Simple evaluator using LLM as a judge"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def load_tasks(self, tasks_file: str) -> List[EvaluationTask]:
        """Load evaluation tasks from JSONL file"""
        tasks = []
        try:
            with open(tasks_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        task_data = json.loads(line)
                        tasks.append(EvaluationTask(
                            name=task_data['name'],
                            prompt=task_data['prompt'],
                            expected_outcome=task_data['expected_outcome']
                        ))
        except FileNotFoundError:
            print(f"❌ Tasks file {tasks_file} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSONL file: {e}")
            return []
        
        return tasks
    
    async def run_agent_for_task(self, task: EvaluationTask) -> str:
        """Run the agent system for a single task"""
        try:
            # Create a unique session ID for each evaluation
            session_id = f"eval_{task.name.replace(' ', '_')}"
            
            # Run the agent system
            result = await run_multi_agent_system_with_state(
                user_request=task.prompt,
                project_name=f"EvalProject_{task.name}",
                session_id=session_id
            )
            
            return result
        except Exception as e:
            return f"Error running agent: {str(e)}"
    
    def judge_output(self, task: EvaluationTask, agent_output: str) -> tuple[float, str]:
        """Use LLM as a judge to compare agent output with expected outcome"""
        
        judge_prompt = f"""
        You are an expert evaluator tasked with comparing an AI agent's output with an expected outcome.
        
        Task: {task.name}
        Original Prompt: {task.prompt}
        
        Expected Outcome: {task.expected_outcome}
        
        Agent Output: {agent_output}
        
        Please evaluate how well the agent's output matches the expected outcome on a scale of 0.0 to 1.0:
        - 1.0: Perfect match or exceeds expectations
        - 0.8-0.9: Very good match with minor differences
        - 0.6-0.7: Good match but missing some aspects
        - 0.4-0.5: Partial match with significant gaps
        - 0.2-0.3: Poor match with major issues
        - 0.0-0.1: Complete failure or irrelevant output
        
        Consider:
        - Did the agent address the main requirements?
        - Are the key functionalities present?
        - Is the output practical and usable?
        - Are there any critical missing elements?
        
        Respond with a JSON object containing:
        {{
            "score": <float between 0.0 and 1.0>,
            "reasoning": "<brief explanation of your evaluation>"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the response
            judge_response = json.loads(response.choices[0].message.content)
            score = float(judge_response.get("score", 0.0))
            reasoning = judge_response.get("reasoning", "No reasoning provided")
            
            return score, reasoning
            
        except Exception as e:
            print(f"❌ Error in LLM judge: {e}")
            return 0.0, f"Judge error: {str(e)}"
    
    async def evaluate_task(self, task: EvaluationTask) -> EvaluationResult:
        """Evaluate a single task"""
        print(f"🔍 Evaluating: {task.name}")
        
        # Run the agent
        agent_output = await self.run_agent_for_task(task)
        
        # Judge the output
        score, reasoning = self.judge_output(task, agent_output)
        
        # Determine if passed (simple threshold)
        passed = score >= 0.6
        
        return EvaluationResult(
            task_name=task.name,
            agent_output=agent_output,
            expected_outcome=task.expected_outcome,
            judge_score=score,
            judge_reasoning=reasoning,
            passed=passed
        )
    
    async def run_evaluation(self, tasks_file: str = "tasks.jsonl") -> List[EvaluationResult]:
        """Run evaluation on all tasks"""
        print(f"🚀 Starting Evaluation Suite")
        print(f"📋 Loading tasks from: {tasks_file}")
        print("=" * 60)
        
        # Load tasks
        tasks = self.load_tasks(tasks_file)
        if not tasks:
            print("❌ No tasks found to evaluate")
            return []
        
        print(f"📝 Found {len(tasks)} evaluation tasks")
        
        # Evaluate each task
        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n📊 Task {i}/{len(tasks)}: {task.name}")
            result = await self.evaluate_task(task)
            results.append(result)
            
            # Print immediate result
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"   {status} (Score: {result.judge_score:.2f})")
        
        return results
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        """Generate a simple evaluation report"""
        if not results:
            return "No evaluation results to report"
        
        # Calculate summary statistics
        total_tasks = len(results)
        passed_tasks = sum(1 for r in results if r.passed)
        average_score = sum(r.judge_score for r in results) / total_tasks
        
        report = f"""
🎯 EVALUATION REPORT
{'=' * 50}
📊 Summary:
   Total Tasks: {total_tasks}
   Passed: {passed_tasks}
   Failed: {total_tasks - passed_tasks}
   Success Rate: {(passed_tasks/total_tasks)*100:.1f}%
   Average Score: {average_score:.2f}

📋 Detailed Results:
"""
        
        for result in results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            report += f"""
{status} {result.task_name}
   Score: {result.judge_score:.2f}
   Reasoning: {result.judge_reasoning}
   Expected: {result.expected_outcome[:100]}...
   Agent Output: {result.agent_output[:100]}...
"""
        
        return report
    
    def save_results(self, results: List[EvaluationResult], filename: str = "evaluation_results.json"):
        """Save evaluation results to JSON file"""
        results_data = []
        for result in results:
            results_data.append({
                "task_name": result.task_name,
                "agent_output": result.agent_output,
                "expected_outcome": result.expected_outcome,
                "judge_score": result.judge_score,
                "judge_reasoning": result.judge_reasoning,
                "passed": result.passed,
                "timestamp": datetime.now().isoformat()
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Results saved to {filename}")

async def main():
    """Main evaluation function"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        return
    
    # Create evaluator
    evaluator = SimpleEvaluator()
    
    # Run evaluation
    results = await evaluator.run_evaluation("tasks.jsonl")
    
    if results:
        # Generate and print report
        report = evaluator.generate_report(results)
        print(report)
        
        # Save results
        evaluator.save_results(results)
        
        print(f"\n🎉 Evaluation completed!")
        print(f"📁 Check evaluation_results.json for detailed results")
    else:
        print("❌ No evaluation results generated")

if __name__ == "__main__":
    asyncio.run(main()) 