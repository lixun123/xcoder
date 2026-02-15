#!/usr/bin/env python3
"""
Simple CodeFixAgent evaluation test

This script provides a simple method to test CodeFixAgent's repair capabilities:
1. Use built-in problematic test cases
2. Call CodeFixAgent for repairs
3. Verify if repairs are successful by running Python files
4. Output simple test reports

Usage:
    python evaluation/test_code_fix.py
    python evaluation/test_code_fix.py --test syntax_error
"""

import os
import sys
import tempfile
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agents.code_fix_agent import CodeFixAgent

# Built-in test cases
TEST_CASES = {
    "syntax_error": {
        "name": "Syntax Error Test",
        "description": "Missing colon in function definition",
        "code": '''#!/usr/bin/env python3
def hello_world()
    print("Hello, World!")
    return True

if __name__ == "__main__":
    result = hello_world()
    print(f"Function returned: {result}")
''',
        "expected_to_run": True
    },

    "logic_error": {
        "name": "Logic Error Test",
        "description": "Division by zero error",
        "code": '''#!/usr/bin/env python3
def divide_numbers():
    a = 10
    b = 0
    return a / b

if __name__ == "__main__":
    try:
        result = divide_numbers()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
''',
        "expected_to_run": True
    },

    "indentation_error": {
        "name": "Indentation Error Test",
        "description": "Incorrect indentation",
        "code": '''#!/usr/bin/env python3
def calculate():
print("calculating...")
result = 2 + 2
return result

if __name__ == "__main__":
    result = calculate()
    print(f"Calculation result: {result}")
''',
        "expected_to_run": True
    }
}


class SimpleCodeFixTester:
    """Simple CodeFixAgent tester"""

    def __init__(self):
        """Initialize tester"""
        self.agent = CodeFixAgent()
        self.temp_dir = tempfile.mkdtemp(prefix="codefix_test_")
        print(f"📁 Test temporary directory: {self.temp_dir}")

    def create_test_file(self, test_case_name: str, test_case: dict) -> str:
        """Create problematic test files"""
        filename = f"{test_case_name}_test.py"
        file_path = os.path.join(self.temp_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_case["code"])

        print(f"📝 Created test file: {file_path}")
        print(f"🔍 Problem description: {test_case['description']}")

        return file_path

    def check_syntax(self, file_path: str) -> bool:
        """Check if Python file syntax is correct"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_file(self, file_path: str) -> tuple:
        """Run Python file and return results"""
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(file_path)
            )

            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Execution timeout"
        except Exception as e:
            return False, "", str(e)

    def test_codefix_agent(self, test_case_name: str) -> dict:
        """Test CodeFixAgent repair for specific test case"""
        if test_case_name not in TEST_CASES:
            return {
                "success": False,
                "error": f"Unknown test case: {test_case_name}",
                "test_case": test_case_name
            }

        test_case = TEST_CASES[test_case_name]

        print(f"\n{'='*60}")
        print(f"🧪 Starting test: {test_case['name']}")
        print(f"📋 Description: {test_case['description']}")
        print(f"{'='*60}")

        # Step 1: Create problematic file
        problem_file = self.create_test_file(test_case_name, test_case)

        # Step 2: Verify file indeed has problems
        print(f"\n🔍 Step 1: Verifying original file has problems...")
        syntax_ok = self.check_syntax(problem_file)
        run_ok, stdout, stderr = self.run_file(problem_file)

        print(f"   Syntax check: {'✅ Passed' if syntax_ok else '❌ Failed'}")
        print(f"   Execution test: {'✅ Success' if run_ok else '❌ Failed'}")

        if syntax_ok and run_ok:
            print("⚠️ Warning: Original file seems to have no problems, skipping repair test")
            return {
                "success": True,
                "test_case": test_case_name,
                "message": "Original file has no problems",
                "original_syntax_ok": syntax_ok,
                "original_run_ok": run_ok
            }

        # Step 3: Use CodeFixAgent for repair
        print(f"\n🤖 Step 2: Using CodeFixAgent for repair...")
        try:
            problem_description = f"Fix problems in file {problem_file}. The file has {test_case['description']}."
            fix_result = self.agent.fix_problem(problem_description)

            if not fix_result.get("success"):
                return {
                    "success": False,
                    "error": "CodeFixAgent repair failed",
                    "test_case": test_case_name,
                    "fix_result": fix_result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Repair process exception: {str(e)}",
                "test_case": test_case_name
            }

        # Step 4: Verify repair results
        print(f"\n✅ Step 3: Verifying repair results...")

        # Check repaired file
        if os.path.exists(problem_file):
            fixed_syntax_ok = self.check_syntax(problem_file)
            fixed_run_ok, fixed_stdout, fixed_stderr = self.run_file(problem_file)

            print(f"   Post-repair syntax check: {'✅ Passed' if fixed_syntax_ok else '❌ Failed'}")
            print(f"   Post-repair execution test: {'✅ Success' if fixed_run_ok else '❌ Failed'}")

            if fixed_stderr:
                print(f"   Error message: {fixed_stderr}")

            success = fixed_syntax_ok and fixed_run_ok

            return {
                "success": success,
                "test_case": test_case_name,
                "original_syntax_ok": syntax_ok,
                "original_run_ok": run_ok,
                "fixed_syntax_ok": fixed_syntax_ok,
                "fixed_run_ok": fixed_run_ok,
                "fixed_stdout": fixed_stdout,
                "fixed_stderr": fixed_stderr,
                "fix_result": fix_result
            }
        else:
            return {
                "success": False,
                "error": "Repaired file does not exist",
                "test_case": test_case_name
            }

    def run_all_tests(self) -> dict:
        """Run all test cases"""
        print("🚀 Starting to run all CodeFixAgent tests...")

        results = {}
        total_tests = len(TEST_CASES)
        passed_tests = 0

        for test_name in TEST_CASES.keys():
            result = self.test_codefix_agent(test_name)
            results[test_name] = result

            if result["success"]:
                passed_tests += 1

        # Generate test report
        print(f"\n{'='*60}")
        print("📊 Test Report")
        print(f"{'='*60}")
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Failed tests: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

        print(f"\n📋 Detailed results:")
        for test_name, result in results.items():
            status = "✅ Passed" if result["success"] else "❌ Failed"
            test_case = TEST_CASES[test_name]
            print(f"  {status} {test_case['name']}")
            if not result["success"]:
                print(f"     Error: {result.get('error', 'Unknown error')}")

        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": passed_tests/total_tests,
            "results": results
        }

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Failed to clean up temporary directory: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple CodeFixAgent evaluation test")
    parser.add_argument(
        "--test",
        choices=list(TEST_CASES.keys()),
        help="Run specified test case"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test cases"
    )

    args = parser.parse_args()

    if args.list:
        print("📋 Available test cases:")
        for name, case in TEST_CASES.items():
            print(f"  {name}: {case['name']} - {case['description']}")
        return

    # Create tester
    tester = SimpleCodeFixTester()

    try:
        if args.test:
            # Run single test
            result = tester.test_codefix_agent(args.test)
            if result["success"]:
                print(f"\n🎉 Test {args.test} completed successfully!")
            else:
                print(f"\n❌ Test {args.test} failed: {result.get('error')}")
                sys.exit(1)
        else:
            # Run all tests
            results = tester.run_all_tests()

            # Determine exit code based on success rate
            if results["success_rate"] < 1.0:
                sys.exit(1)
            else:
                print(f"\n🎉 All tests completed successfully!")

    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
