# CodeFixAgent Evaluation Tools

This directory contains simple testing tools for evaluating the repair capabilities of CodeFixAgent.

## Simple Evaluation Tools

### `test_code_fix.py`

An all-in-one CodeFixAgent evaluation script that provides simple and direct testing methods.

#### Features

- **Built-in Test Cases**: Contains common Python code problems
- **Automated Verification**: Verifies fix effectiveness by running the repaired files
- **Simple Reporting**: Outputs clear success/failure results
- **Single File Solution**: No complex configuration needed, one file handles all functionality

#### Built-in Test Cases

1. **Syntax Error Test** (`syntax_error`)
   - Problem: Missing colon in function definition
   - Verification: Can execute normally after repair

2. **Logic Error Test** (`logic_error`)
   - Problem: Division by zero error
   - Verification: Can handle division by zero properly after repair

3. **Indentation Error Test** (`indentation_error`)
   - Problem: Incorrect Python code indentation
   - Verification: Can execute normally after repair

#### Usage

```bash
# View all available test cases
python test_code_fix.py --list

# Run individual test cases
python test_code_fix.py --test syntax_error
python test_code_fix.py --test logic_error
python test_code_fix.py --test indentation_error

# Run all test cases
python test_code_fix.py
```

#### Verification Strategy

**Test Process:**
1. Create Python files containing problems
2. Verify that original files indeed have problems (syntax or runtime errors)
3. Call CodeFixAgent for repair
4. Verify repair results:
   - Syntax check: `python -m py_compile filename.py`
   - Execution test: `python filename.py`
5. Determine success (0) or failure (non-0) based on exit code

**Success Criteria:**
- Repaired files can pass Python syntax check
- Repaired files can execute normally without errors

#### Output Example

```
🧪 Starting test: Syntax Error Test
📋 Description: Missing colon in function definition

🔍 Step 1: Verifying original file has problems...
   Syntax check: ❌ Failed
   Execution test: ❌ Failed

🤖 Step 2: Using CodeFixAgent for repair...
[CodeFixAgent repair process...]

✅ Step 3: Verifying repair results...
   Post-repair syntax check: ✅ Passed
   Post-repair execution test: ✅ Success

🎉 Test syntax_error completed successfully!
```

#### Test Report

After running all tests, a simple test report is generated:

```
📊 Test Report
============================================================
Total Tests: 3
Passed Tests: 3
Failed Tests: 0
Success Rate: 100.0%

📋 Detailed Results:
  ✅ Passed Syntax Error Test
  ✅ Passed Logic Error Test
  ✅ Passed Indentation Error Test
```

## Dependencies

- Python 3.7+
- CodeFixAgent related modules in project root directory
- Standard libraries: `subprocess`, `tempfile`, `argparse`

## Extending Tests

To add new test cases, simply add new entries to the `TEST_CASES` dictionary:

```python
"your_test_case": {
    "name": "Test Name",
    "description": "Problem Description",
    "code": '''Problematic Python code''',
    "expected_to_run": True
}
```
