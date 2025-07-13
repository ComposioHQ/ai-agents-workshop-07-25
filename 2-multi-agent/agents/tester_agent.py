"""
Tester Agent

This agent specializes in creating and running tests for code validation.
It uses GPT-3.5-turbo for cost optimization since test creation is a more structured task.
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent
from ..utils.python_repl import create_python_repl_tool


class TesterAgent(BaseAgent):
    """
    Agent that specializes in creating and running tests for code validation.
    
    This agent:
    - Creates comprehensive test suites
    - Runs unit tests and integration tests
    - Validates code functionality
    - Generates test reports
    - Identifies test coverage gaps
    
    Uses GPT-3.5-turbo for cost optimization.
    """
    
    def __init__(self, **kwargs):
        # Use GPT-3.5-turbo for cost-effective test creation
        kwargs.setdefault('model', 'gpt-3.5-turbo')
        kwargs.setdefault('name', 'Tester')
        kwargs.setdefault('temperature', 0.1)  # Lower temperature for consistent test creation
        
        super().__init__(**kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are a Tester Agent, specialized in creating and running comprehensive tests.

Your role is to:
1. CREATE comprehensive test suites for code validation
2. DESIGN test cases that cover normal, edge, and error conditions
3. RUN tests and validate functionality
4. GENERATE clear test reports with results
5. IDENTIFY test coverage gaps and missing scenarios
6. ENSURE code meets quality and reliability standards

Testing Strategies:
1. UNIT TESTS: Test individual functions and methods
2. INTEGRATION TESTS: Test component interactions
3. EDGE CASE TESTS: Test boundary conditions and limits
4. ERROR HANDLING TESTS: Test exception and error scenarios
5. PERFORMANCE TESTS: Test execution time and resource usage
6. REGRESSION TESTS: Ensure existing functionality isn't broken

Test Case Design:
- Test typical use cases (happy path)
- Test edge cases and boundary conditions
- Test error conditions and exception handling
- Test invalid inputs and malformed data
- Test performance with large datasets
- Test concurrent access (if applicable)

Test Implementation:
- Use clear, descriptive test names
- Include both positive and negative test cases
- Test one thing at a time
- Use appropriate assertions
- Include setup and teardown when needed
- Document test purpose and expected behavior

Always run tests using the Python REPL tool to verify results.
Provide clear test reports with pass/fail status and explanations."""
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Tester agent needs Python REPL for running tests and file tools for test management"""
        from composio_openai import Action
        
        # Get file tools for test file management
        file_tools = self.composio_toolset.get_tools(actions=[
            Action.FILETOOL_CREATE_FILE,
            Action.FILETOOL_READ_FILE,
            Action.FILETOOL_LIST_FILES,
        ])
        
        # Add Python REPL tool for running tests
        python_repl = create_python_repl_tool()
        
        return [python_repl] + file_tools
    
    def create_test_suite(self, code: str, function_name: str = None) -> Dict[str, Any]:
        """
        Create a comprehensive test suite for the given code.
        
        Args:
            code: The code to create tests for
            function_name: Optional specific function name to focus on
            
        Returns:
            Dictionary containing test suite and results
        """
        test_prompt = f"""
        Code to create tests for:
        ```python
        {code}
        ```
        
        Function focus: {function_name or 'All functions in the code'}
        
        Create a comprehensive test suite that includes:
        
        1. TEST STRUCTURE:
           - Import necessary modules
           - Set up test functions with descriptive names
           - Include docstrings explaining what each test does
        
        2. TEST CATEGORIES:
           - Normal operation tests (happy path)
           - Edge case tests (boundary conditions)
           - Error handling tests (invalid inputs)
           - Type validation tests
           - Performance tests (if applicable)
        
        3. TEST IMPLEMENTATION:
           - Use assert statements for validation
           - Include multiple test cases per function
           - Test both expected successes and expected failures
           - Use try/except blocks for error testing
        
        4. TEST EXECUTION:
           - Run all tests using the run_python_code tool
           - Report results for each test
           - Identify any failures and explain why
        
        Create the test suite and run it immediately to verify functionality.
        """
        
        result = self.run(test_prompt)
        return {
            "test_suite": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def run_specific_tests(self, code: str, test_scenarios: List[str]) -> Dict[str, Any]:
        """
        Run specific test scenarios for the given code.
        
        Args:
            code: The code to test
            test_scenarios: List of specific scenarios to test
            
        Returns:
            Dictionary containing test results
        """
        test_prompt = f"""
        Code to test:
        ```python
        {code}
        ```
        
        Test scenarios to validate:
        {chr(10).join(f"- {scenario}" for scenario in test_scenarios)}
        
        For each scenario:
        1. Create appropriate test cases
        2. Run the tests using the run_python_code tool
        3. Report the results (pass/fail)
        4. Explain any failures
        
        Focus on validating that the code handles each scenario correctly.
        """
        
        result = self.run(test_prompt)
        return {
            "test_results": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def validate_against_requirements(self, code: str, requirements: str) -> Dict[str, Any]:
        """
        Validate code against specific requirements.
        
        Args:
            code: The code to validate
            requirements: The requirements to validate against
            
        Returns:
            Dictionary containing validation results
        """
        validation_prompt = f"""
        Code to validate:
        ```python
        {code}
        ```
        
        Requirements to validate against:
        {requirements}
        
        Create and run tests that specifically validate:
        1. Each requirement is met
        2. Code behaves as specified
        3. Edge cases mentioned in requirements
        4. Any performance or quality criteria
        
        For each requirement:
        - Create targeted test cases
        - Run tests using the run_python_code tool
        - Report compliance status
        - Identify any gaps or failures
        
        Provide a clear compliance report.
        """
        
        result = self.run(validation_prompt)
        return {
            "validation_results": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def performance_testing(self, code: str, performance_criteria: str = None) -> Dict[str, Any]:
        """
        Run performance tests on the given code.
        
        Args:
            code: The code to performance test
            performance_criteria: Optional specific performance criteria
            
        Returns:
            Dictionary containing performance test results
        """
        performance_prompt = f"""
        Code to performance test:
        ```python
        {code}
        ```
        
        Performance criteria: {performance_criteria or 'General performance benchmarking'}
        
        Create and run performance tests that measure:
        1. Execution time for typical inputs
        2. Memory usage patterns
        3. Performance with large datasets
        4. Scalability characteristics
        5. Resource utilization
        
        Use the run_python_code tool to:
        - Import time module for timing
        - Run code with different input sizes
        - Measure execution times
        - Test with edge case inputs
        
        Report performance metrics and identify any bottlenecks.
        """
        
        result = self.run(performance_prompt)
        return {
            "performance_results": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def regression_testing(self, original_code: str, modified_code: str) -> Dict[str, Any]:
        """
        Run regression tests to ensure modifications don't break existing functionality.
        
        Args:
            original_code: The original working code
            modified_code: The modified code to test
            
        Returns:
            Dictionary containing regression test results
        """
        regression_prompt = f"""
        Original code:
        ```python
        {original_code}
        ```
        
        Modified code:
        ```python
        {modified_code}
        ```
        
        Create and run regression tests that:
        1. Test the same functionality in both versions
        2. Ensure existing behavior is preserved
        3. Validate that modifications work correctly
        4. Identify any breaking changes
        
        For each test:
        - Run on original code to establish baseline
        - Run on modified code to check for regressions
        - Compare results and report differences
        - Explain any changes in behavior
        
        Use the run_python_code tool to test both versions.
        """
        
        result = self.run(regression_prompt)
        return {
            "regression_results": result.content,
            "success": result.success,
            "model_used": self.model
        }
    
    def generate_test_report(self, code: str, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive test report.
        
        Args:
            code: The code that was tested
            test_results: List of test results from various test runs
            
        Returns:
            Dictionary containing comprehensive test report
        """
        report_prompt = f"""
        Code that was tested:
        ```python
        {code}
        ```
        
        Test results to summarize:
        {chr(10).join(str(result) for result in test_results)}
        
        Generate a comprehensive test report that includes:
        1. Executive summary of testing
        2. Test coverage analysis
        3. Pass/fail statistics
        4. Issue summary with severity levels
        5. Performance metrics (if available)
        6. Recommendations for improvement
        7. Risk assessment
        
        Format as a professional test report.
        """
        
        result = self.run(report_prompt)
        return {
            "test_report": result.content,
            "success": result.success,
            "model_used": self.model
        } 