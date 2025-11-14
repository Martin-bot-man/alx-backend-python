# Parameterized Testing with Python

A comprehensive guide to using `@parameterized.expand` for writing efficient, maintainable test suites in Python.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Examples](#examples)
- [Contributing](#contributing)

## Overview

Parameterized testing allows you to run the same test logic with multiple sets of input data, eliminating code duplication and making your test suite more maintainable. Instead of writing dozens of similar test methods, you write one test and provide it with different parameters.

### Why Use Parameterized Tests?

- **Reduce Code Duplication**: Write test logic once, apply it to many scenarios
- **Improve Maintainability**: Update logic in one place instead of multiple methods
- **Increase Test Coverage**: Easily add new test cases without writing new functions
- **Better Readability**: Separate test data from test logic
- **Faster Development**: Add edge cases and boundary conditions quickly

## Installation

Install the `parameterized` library using pip:

```bash
pip install parameterized
```

For development with additional testing tools:

```bash
pip install parameterized pytest unittest2
```

## Quick Start

Here's a simple example to get you started:

```python
import unittest
from parameterized import parameterized

class TestMath(unittest.TestCase):
    @parameterized.expand([
        (2, 3, 5),
        (5, 5, 10),
        (10, -3, 7),
    ])
    def test_addition(self, a, b, expected):
        self.assertEqual(a + b, expected)

if __name__ == '__main__':
    unittest.main()
```

This creates three separate test cases automatically!

## Basic Usage

### Simple List of Tuples

The most straightforward approach:

```python
@parameterized.expand([
    (1, 1, 2),
    (2, 2, 4),
    (3, 3, 6),
])
def test_multiplication(self, a, b, expected):
    self.assertEqual(a * b, expected)
```

### Named Test Cases

Make test names more descriptive:

```python
@parameterized.expand([
    ("positive_numbers", 2, 3, 5),
    ("negative_numbers", -2, -3, -5),
    ("mixed_signs", 2, -3, -1),
])
def test_addition(self, name, a, b, expected):
    self.assertEqual(a + b, expected)
```

### Dictionary Parameters

Use dictionaries for clearer parameter mapping:

```python
@parameterized.expand([
    {"username": "alice", "age": 30, "valid": True},
    {"username": "bob", "age": 17, "valid": False},
    {"username": "charlie", "age": 25, "valid": True},
])
def test_user_validation(self, username, age, valid):
    result = validate_user(username, age)
    self.assertEqual(result, valid)
```

## Advanced Features

### Custom Test Name Generation

Control how test names appear in output:

```python
def custom_name_func(testcase_func, param_num, param):
    return f"{testcase_func.__name__}_case_{param_num}_{param.args[0]}"

@parameterized.expand([
    (2, 3, 5),
    (5, 5, 10),
], name_func=custom_name_func)
def test_addition(self, a, b, expected):
    self.assertEqual(a + b, expected)
```

### Using `param()` Helper

For more control over individual test cases:

```python
from parameterized import param

@parameterized.expand([
    param(2, 3, expected=5),
    param(5, 5, expected=10, doc="Testing equal numbers"),
    param(10, -3, expected=7, doc="Testing negative operand"),
])
def test_addition(self, a, b, expected):
    self.assertEqual(a + b, expected)
```

### Dynamic Test Case Generation

Use generators or functions to create test cases:

```python
def generate_fibonacci_tests():
    fibonacci = [(0, 0), (1, 1), (2, 1), (3, 2), (4, 3), (5, 5)]
    for n, expected in fibonacci:
        yield (n, expected)

@parameterized.expand(generate_fibonacci_tests())
def test_fibonacci(self, n, expected):
    self.assertEqual(fibonacci(n), expected)
```

### Loading Test Cases from Files

Separate test data from test code:

```python
import json

def load_test_cases(filename):
    with open(filename) as f:
        return json.load(f)

@parameterized.expand(load_test_cases('test_data.json'))
def test_from_file(self, input_val, expected_output):
    self.assertEqual(process(input_val), expected_output)
```

### Combining with Mocks and Patches

Stack decorators for complex scenarios:

```python
from unittest.mock import patch

@parameterized.expand([
    ("success", 200, True),
    ("not_found", 404, False),
    ("server_error", 500, False),
])
@patch('requests.get')
def test_api_call(self, mock_get, scenario, status_code, expected):
    mock_get.return_value.status_code = status_code
    result = check_api_status()
    self.assertEqual(result, expected)
```

## Best Practices

### 1. Keep Test Cases Simple

Each test case should test one specific scenario:

```python
# Good
@parameterized.expand([
    ([], 0),
    ([1], 1),
    ([1, 2, 3], 3),
])
def test_list_length(self, input_list, expected_length):
    self.assertEqual(len(input_list), expected_length)
```

### 2. Use Descriptive Names

Make it easy to understand what failed:

```python
@parameterized.expand([
    ("empty_string", "", False),
    ("valid_email", "user@example.com", True),
    ("missing_at_sign", "userexample.com", False),
    ("missing_domain", "user@", False),
])
def test_email_validation(self, case_name, email, is_valid):
    self.assertEqual(validate_email(email), is_valid)
```

### 3. Group Related Test Cases

Organize test data logically:

```python
# Boundary conditions
boundary_cases = [
    ("min_value", 0, True),
    ("max_value", 100, True),
    ("below_min", -1, False),
    ("above_max", 101, False),
]

# Normal cases
normal_cases = [
    ("typical_value", 50, True),
    ("another_value", 75, True),
]

@parameterized.expand(boundary_cases + normal_cases)
def test_range_validation(self, name, value, expected):
    self.assertEqual(is_in_range(value, 0, 100), expected)
```

### 4. Use External Data for Large Test Suites

Keep your test files clean:

```python
# test_data.json
# [
#   {"input": "hello", "output": "HELLO"},
#   {"input": "world", "output": "WORLD"}
# ]

@parameterized.expand(load_test_cases('test_data.json'))
def test_uppercase_conversion(self, input_str, expected_output):
    self.assertEqual(input_str.upper(), expected_output)
```

## Common Pitfalls

### Pitfall 1: Mutable Default Arguments

```python
# Bad - list is shared across all test cases
@parameterized.expand([
    ([1, 2, 3]),
    ([4, 5, 6]),
])
def test_list_modification(self, numbers=[]):  # Don't do this!
    numbers.append(0)
    # Tests will interfere with each other

# Good - create new instances
@parameterized.expand([
    ([1, 2, 3]),
    ([4, 5, 6]),
])
def test_list_modification(self, numbers):
    numbers = numbers.copy()  # Create a copy
    numbers.append(0)
```

### Pitfall 2: Too Many Parameters

```python
# Bad - hard to read and maintain
@parameterized.expand([
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
])
def test_complex(self, a, b, c, d, e, f, g, h, i, j, expected):
    pass

# Good - use dictionaries or objects
@parameterized.expand([
    {"config": Config(a=1, b=2, c=3), "expected": 10},
])
def test_with_config(self, config, expected):
    pass
```

### Pitfall 3: Ignoring Test Isolation

Each test case should be independent:

```python
# Bad - tests depend on execution order
class TestCounter(unittest.TestCase):
    counter = 0
    
    @parameterized.expand([(1,), (2,), (3,)])
    def test_increment(self, amount):
        self.counter += amount  # Don't do this!
        
# Good - each test is isolated
class TestCounter(unittest.TestCase):
    @parameterized.expand([(1, 1), (2, 2), (3, 3)])
    def test_increment(self, amount, expected):
        counter = 0
        counter += amount
        self.assertEqual(counter, expected)
```

## Examples

### Example 1: Testing String Operations

```python
@parameterized.expand([
    ("lowercase", "hello", "HELLO"),
    ("uppercase", "WORLD", "WORLD"),
    ("mixed_case", "HeLLo", "HELLO"),
    ("with_numbers", "hello123", "HELLO123"),
    ("empty_string", "", ""),
])
def test_to_uppercase(self, name, input_str, expected):
    self.assertEqual(input_str.upper(), expected)
```

### Example 2: Testing API Response Parsing

```python
@parameterized.expand([
    ({"status": "success", "data": {"id": 1}}, True, 1),
    ({"status": "error", "message": "Not found"}, False, None),
    ({"status": "success", "data": {}}, True, None),
])
def test_parse_response(self, response, is_success, expected_id):
    result = parse_api_response(response)
    self.assertEqual(result.success, is_success)
    self.assertEqual(result.id, expected_id)
```

### Example 3: Testing Mathematical Functions

```python
import math

@parameterized.expand([
    ("positive", 4, 2.0),
    ("zero", 0, 0.0),
    ("fraction", 0.25, 0.5),
    ("large_number", 10000, 100.0),
])
def test_square_root(self, name, input_val, expected):
    self.assertAlmostEqual(math.sqrt(input_val), expected)
```

### Example 4: Testing Edge Cases

```python
@parameterized.expand([
    ("null_input", None, ""),
    ("empty_string", "", ""),
    ("whitespace_only", "   ", ""),
    ("normal_string", "  hello  ", "hello"),
    ("multiple_spaces", "hello   world", "hello world"),
])
def test_string_normalization(self, name, input_str, expected):
    result = normalize_string(input_str)
    self.assertEqual(result, expected)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Please ensure your code is formatted properly:

```bash
black .
flake8 .
```

## License

MIT License - See LICENSE file for details

## Resources

- [Official parameterized Documentation](https://github.com/wolever/parameterized)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Parameterization](https://docs.pytest.org/en/stable/parametrize.html)

## Support

If you encounter any issues or have questions, please open an issue on GitHub or reach out to the maintainers.

---

**Happy Testing!** 🚀