import os
import subprocess
from langchain_community.llms import Ollama

# === Initialize Ollama LLM ===
llm = Ollama(model="llama3")

# === Agent 1: Code Writer ===
def code_writer(task: str) -> str:
    prompt = f"Write clean Python code for the following task:\n\n{task}\n\nReturn only the code."
    return llm.invoke(prompt)

# === Agent 2: Code Reviewer ===
def code_reviewer(code: str) -> str:
    prompt = f"""Review the following Python code. Identify bugs, inefficiencies, or issues. Provide suggestions for improvement.\n\n```python\n{code}\n```"""
    return llm.invoke(prompt)

# === Agent 3: Test Writer ===
def test_writer(code: str) -> str:
    prompt = f"""Write pytest-based unit tests for the following Python code.\n\n```python\n{code}\n```\nReturn only the test code."""
    return llm.invoke(prompt)

# === Agent 4: Test Runner ===
def run_tests(code_file: str, test_file: str) -> str:
    try:
        exec_output = subprocess.getoutput(f"python {code_file}")
        test_output = subprocess.getoutput(f"pytest {test_file} --tb=short -v")
        return f"=== Code Output ===\n{exec_output}\n\n=== Test Results ===\n{test_output}"
    except Exception as e:
        return f"Error while running tests: {str(e)}"

# === Agent 5: Refiner ===
def refiner(code: str, test_results: str, suggestions: str) -> str:
    prompt = f"""Based on the following test results and code review suggestions, refine and improve the given code.

            Test Results:
            {test_results}

            Suggestions:
            {suggestions}

            Original Code:
            {code}
            Return only the improved Python code.
            """
    return llm.invoke(prompt)


### === File Helpers ===
def save_to_file(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)

### === Coordinator ===
def run_agent_loop(task: str, max_loops: int = 3):
    code_file = "main_code.py"
    test_file = "test_main_code.py"
    code = ""

for i in range(max_loops):
    print(f"\n--- Iteration {i+1} ---")

    # Step 1: Write Code
    code = code_writer(task)
    save_to_file(code_file, code)
    print(f"\n[CodeWriter] Code:\n{code}")

    # Step 2: Review Code
    suggestions = code_reviewer(code)
    print(f"\n[CodeReviewer] Suggestions:\n{suggestions}")

    # Step 3: Write Tests
    test_code = test_writer(code)
    save_to_file(test_file, test_code)
    print(f"\n[TestWriter] Tests:\n{test_code}")

    # Step 4: Run Code and Tests
    results = run_tests(code_file, test_file)
    print(f"\n[TestRunner] Results:\n{results}")

    # Step 5: Analyze and Decide
    if "failed" in results.lower() or "error" in results.lower():
        print("\n[Refiner] Refining code based on feedback...")
        code = refiner(code, results, suggestions)
    else:
        print("\n✅ Code and tests passed. No further refinement needed.")
        break

save_to_file(code_file, code)
print(f"\n🎉 Final code written to {code_file}")

### === Entry Point ===
if __name__ == "main":
user_task = input("Enter the task for the agent to solve: ")
run_agent_loop(user_task)
