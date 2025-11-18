# Testing Strategy & TDD Workflow

**Date**: 2025-11-10
**Status**: ✅ Production-ready testing framework implemented

---

## Overview

This document describes the comprehensive testing strategy for the AI Stock Research platform. Our testing approach follows industry best practices, including Test-Driven Development (TDD), property-based testing, and multiple layers of validation.

## Testing Philosophy

### Core Principles

1. **No Surface-Level Tests**: Every test validates actual behavior, not just code execution
2. **Meaningful Assertions**: Tests check business requirements, not just "is not None"
3. **Property-Based Testing**: Use Hypothesis to discover edge cases automatically
4. **Test Behavior, Not Implementation**: Tests should survive refactoring
5. **Fast Feedback**: Unit tests run in seconds, integration tests in minutes

### Anti-Patterns to Avoid

❌ **Bad Test** (meaningless):
```python
def test_validate_ticker():
    result = validate_ticker("AAPL")
    assert result is not None  # Meaningless!
```

✅ **Good Test** (validates behavior):
```python
def test_validate_ticker_normalizes_case():
    result = validate_ticker("aapl")
    assert result == "AAPL", "Lowercase should be normalized to uppercase"
    assert len(result) == 4, "Result should preserve length"
    assert result.isalpha(), "Result should contain only letters"
```

---

## Test Pyramid

```
        /\
       /  \
      /E2E \          End-to-End Tests (slow, high value)
     /------\
    /        \
   /Integration\      Integration Tests (medium speed)
  /------------\
 /              \
/   Unit Tests   \    Unit Tests (fast, comprehensive)
------------------
```

### Test Levels

1. **Unit Tests** (`tests/unit/`): 86 tests, ~7s runtime
   - Fast, isolated tests for individual functions and classes
   - Mock external dependencies
   - High coverage (>80% target)

2. **Property Tests** (`tests/property/`): 17 tests, variable runtime
   - Generate hundreds of test cases automatically
   - Find edge cases humans might miss
   - Verify invariants hold across all inputs

3. **Integration Tests** (`tests/integration/`): Planned
   - Test interactions between components
   - Use real dependencies where feasible
   - Verify end-to-end workflows

---

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── test_validation.py      # 39 tests - input validation
│   ├── test_rate_limiter.py    # 28 tests - rate limiting (incl. thread safety)
│   └── test_logging_config.py  # 19 tests - logging (incl. injection prevention)
├── property/                   # Property-based tests
│   └── test_validation_properties.py  # 17 tests - Hypothesis
└── integration/                # Integration tests (future)
    └── test_yfinance_integration.py
```

### Test Organization

Tests are organized by:
1. **Module**: One test file per source module
2. **Feature**: Test classes group related tests
3. **Test Case ID**: Referenced in TEST_SPECIFICATION.md

Example:
```python
class TestTickerValidation:
    """TC-VAL-001: Valid ticker formats"""

    def test_single_letter_ticker(self):
        """Single letter tickers (A, X) should be accepted"""
        assert validate_ticker("A") == "A"
```

---

## Running Tests

### Quick Commands

```bash
# Run all unit tests
make test-unit

# Run property tests
make test-property

# Run all tests
make test-all

# Run tests for specific module
pytest tests/unit/test_validation.py -v

# Run tests with coverage
make coverage

# Watch mode (re-run on file changes)
make test-watch
```

### Test Filters

```bash
# Run fast tests only
make test-fast

# Run tests by marker
pytest -m validation
pytest -m rate_limiter
pytest -m logging

# Run specific test
pytest tests/unit/test_validation.py::TestTickerValidation::test_single_letter_ticker
```

---

## TDD Workflow

### The Red-Green-Refactor Cycle

```
┌─────────────┐
│   🔴 RED    │  Write failing test
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  🟢 GREEN   │  Make test pass (minimal code)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 🔵 REFACTOR │  Improve code (tests stay green)
└──────┬──────┘
       │
       └──────► Repeat
```

### Step-by-Step Workflow

#### 1. RED Phase: Write Failing Test

```bash
# Edit test file
vim tests/unit/test_validation.py

# Write a test that describes desired behavior
def test_new_feature():
    result = new_feature()
    assert result == expected_value

# Run test - it should FAIL
pytest tests/unit/test_validation.py::test_new_feature -v
```

Expected output:
```
FAILED tests/unit/test_validation.py::test_new_feature
E   AttributeError: module 'validation' has no attribute 'new_feature'
```

✅ **Test fails as expected** - This is good! It means your test is valid.

#### 2. GREEN Phase: Make Test Pass

```bash
# Edit source file
vim validation.py

# Write minimal code to pass the test
def new_feature():
    return expected_value  # Simplest implementation

# Run test again
make tdd-green
```

Expected output:
```
PASSED tests/unit/test_validation.py::test_new_feature ✓
```

✅ **Test passes** - Now you have working code with proof it works!

#### 3. REFACTOR Phase: Improve Code

```bash
# Improve the implementation
vim validation.py

# Make code cleaner, add error handling, optimize
def new_feature():
    # Better implementation
    ...

# Run all tests to ensure nothing broke
make tdd-refactor
```

Expected output:
```
✓ All tests pass
✓ Linting passed
✓ Type checking passed
```

✅ **Tests still pass** - Your refactoring is safe!

### Makefile Targets for TDD

```bash
make tdd-red       # Reminder: Write failing test first
make tdd-green     # Run last failed test
make tdd-refactor  # Run tests + lint + type-check
```

---

## Test Coverage

### Current Coverage

```
Module                    Stmts   Miss  Cover
-----------------------------------------------
validation.py               70      3    96%
rate_limiter.py            58      0   100%
logging_config.py          28      0   100%
-----------------------------------------------
TOTAL (core modules)      156      3    98%
```

### Coverage Requirements

- **Minimum**: 80% overall coverage (enforced by pytest.ini)
- **Target**: 90%+ for core business logic
- **Critical modules**: 95%+ (validation, rate_limiter, exceptions)

### Coverage Commands

```bash
# Generate coverage report
make coverage

# View HTML report
make coverage-report  # Opens htmlcov/index.html in browser

# Coverage for specific module
pytest tests/unit/test_validation.py --cov=validation --cov-report=term-missing
```

---

## Property-Based Testing

### What is Property-Based Testing?

Instead of writing individual test cases, you write **properties** that should hold for all inputs, and Hypothesis generates hundreds of test cases automatically.

### Example: Traditional vs Property-Based

**Traditional Testing** (manual examples):
```python
def test_ticker_validation():
    assert validate_ticker("AAPL") == "AAPL"
    assert validate_ticker("MSFT") == "MSFT"
    assert validate_ticker("GOOGL") == "GOOGL"
    # What about edge cases we forgot?
```

**Property-Based Testing** (automatic exploration):
```python
@given(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=5))
def test_all_valid_tickers_accepted(ticker: str):
    """Property: Any 1-5 uppercase letter string should be valid"""
    result = validate_ticker(ticker)
    assert result == ticker
    assert result.isupper()
    assert 1 <= len(result) <= 5
    # Hypothesis generates 200 different tickers automatically!
```

### Hypothesis Configuration

Profiles configured in `tests/conftest.py`:

- **default**: 10 examples (fast for local dev)
- **ci**: 100 examples (CI pipeline)
- **thorough**: 1000 examples (release testing)

Set profile via environment variable:
```bash
HYPOTHESIS_PROFILE=thorough pytest tests/property
```

### Property Test Examples

#### Invariant Properties

Properties that should always hold:

```python
@given(valid_ticker_strategy)
def test_idempotent_validation(ticker: str):
    """Property: Validating twice should give same result"""
    once = validate_ticker(ticker)
    twice = validate_ticker(once)
    assert once == twice
```

#### Inverse Properties

Operations that should cancel out:

```python
@given(st.integers(min_value=1, max_value=100))
def test_consume_and_replenish_inverse(rate: int):
    """Property: Consuming then waiting should restore tokens"""
    bucket = TokenBucket(rate=rate, per=1.0)
    bucket.consume(rate)  # Consume all
    time.sleep(1.0)       # Wait for replenishment
    assert bucket.consume(rate)  # Should succeed again
```

#### Boundary Properties

Edge cases at limits:

```python
@given(st.integers(min_value=0, max_value=1000))
def test_rate_limiter_never_exceeds_limit(rate: int):
    """Property: Should never allow more than 'rate' requests"""
    bucket = TokenBucket(rate, 60.0)
    successful = sum(1 for _ in range(rate * 2) if bucket.consume())
    assert successful == rate
```

---

## Test Quality: Mutation Testing

### What is Mutation Testing?

Mutation testing validates that your tests are actually catching bugs, not just executing code. It modifies your source code (creates "mutants") and checks if tests fail.

### Running Mutation Tests

```bash
# Run mutation testing
make mutation-test

# View results
make mutation-results
```

### Interpreting Results

- **Killed**: Test caught the mutation ✅ Good!
- **Survived**: Test didn't catch the mutation ❌ Weak test!
- **Timeout**: Mutation caused infinite loop
- **Incompetent**: Mutation broke syntax

**Target**: >80% mutation score

---

## Pre-Commit Checks

### Before Every Commit

Run this command:
```bash
make pre-commit
```

This runs:
1. ✅ Code formatting check (black, isort)
2. ✅ Linting (flake8, pylint)
3. ✅ Type checking (mypy)
4. ✅ Unit tests with coverage
5. ✅ Security checks (bandit, safety)

### CI Pipeline Simulation

Test locally what will run in CI:
```bash
make ci
```

This runs the full pipeline:
- Format check
- Linting
- Type checking
- **All tests** (unit + integration + property)
- Security scanning

---

## Writing Good Tests

### Test Naming Convention

Format: `test_<what>_<condition>_<expected>`

Examples:
- ✅ `test_ticker_validation_lowercase_normalizes_to_uppercase`
- ✅ `test_rate_limiter_concurrent_access_respects_limit`
- ❌ `test_function` (too vague)
- ❌ `test1`, `test2` (meaningless)

### Test Structure: Arrange-Act-Assert

```python
def test_token_bucket_consumes_tokens():
    # Arrange: Set up test data
    bucket = TokenBucket(rate=5, per=60.0)

    # Act: Perform the action
    result = bucket.consume(tokens=3)

    # Assert: Verify the outcome
    assert result is True
    assert bucket.allowance == 2
```

### Meaningful Assertions

❌ **Bad** (vague):
```python
assert result  # What are we checking?
assert result is not None  # Why should it not be None?
```

✅ **Good** (explicit):
```python
assert result == "AAPL", "Lowercase ticker should normalize to uppercase"
assert result.isupper(), "Result must be uppercase"
assert len(result) == 4, "Result should preserve ticker length"
```

### Testing Error Cases

Always test both happy path and error cases:

```python
class TestTickerValidation:
    def test_valid_ticker_accepted(self):
        """Happy path: Valid ticker should be accepted"""
        assert validate_ticker("AAPL") == "AAPL"

    def test_empty_ticker_rejected(self):
        """Error case: Empty string should raise ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("")
        assert "cannot be empty" in str(exc_info.value)

    def test_too_long_ticker_rejected(self):
        """Error case: Ticker >5 chars should raise ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("TOOLONG")
        assert "must be 1-5" in str(exc_info.value)
```

---

## Fixtures and Mocking

### Common Fixtures

Defined in `tests/conftest.py`:

```python
@pytest.fixture
def sample_quote_data():
    """Sample quote data for testing"""
    return {
        "currentPrice": 185.04,
        "volume": 45678900,
        ...
    }

@pytest.fixture
def mock_yfinance_ticker(sample_quote_data):
    """Mock yfinance Ticker object"""
    ticker = Mock()
    ticker.info = sample_quote_data
    return ticker
```

### Using Fixtures

```python
def test_quote_extraction(mock_yfinance_ticker):
    """Fixtures are automatically injected by pytest"""
    provider = YFinanceProvider()
    quote = await provider.get_quote("AAPL")
    assert quote.price == 185.04
```

### Mocking Best Practices

1. **Mock at boundaries**: Mock external services, not internal logic
2. **Verify behavior**: Check that mocks were called correctly
3. **Use realistic data**: Mock responses should match real API responses

```python
def test_rate_limiter_used(mocker):
    """Verify that rate limiter is called"""
    mock_limiter = mocker.patch('provider.rate_limiter')

    provider.get_quote("AAPL")

    mock_limiter.check_limit.assert_called_once_with("yfinance")
```

---

## Continuous Integration

### GitHub Actions Workflow

When you push code, CI automatically runs:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    steps:
      - Run linting (flake8, pylint)
      - Run type checking (mypy)
      - Run unit tests
      - Run property tests
      - Run integration tests
      - Upload coverage report
      - Run security scan
```

### Branch Protection

- ✅ All tests must pass before merge
- ✅ Code coverage must be ≥80%
- ✅ No security vulnerabilities allowed
- ✅ Code must pass linting

---

## Test Performance

### Performance Targets

- **Unit tests**: <10 seconds total
- **Property tests**: <60 seconds total
- **Integration tests**: <5 minutes total
- **Full CI pipeline**: <10 minutes

### Performance Tips

1. **Parallel execution**: Use pytest-xdist
   ```bash
   pytest -n auto  # Run tests in parallel
   ```

2. **Fast fixtures**: Use session-scoped fixtures for expensive setup
   ```python
   @pytest.fixture(scope="session")
   def expensive_resource():
       # Created once per test session
       return setup_expensive_resource()
   ```

3. **Skip slow tests locally**:
   ```bash
   pytest -k "not slow"  # Skip tests marked with @pytest.mark.slow
   ```

---

## Debugging Failed Tests

### Running Single Test

```bash
# Run specific test with full output
pytest tests/unit/test_validation.py::test_specific_case -vv -s

# -vv: Very verbose
# -s: Show print statements
```

### Using Debugger

```python
import ipdb  # Interactive Python Debugger

def test_something():
    result = function_under_test()
    ipdb.set_trace()  # Debugger stops here
    assert result == expected
```

Or use pytest's built-in debugger:
```bash
pytest --pdb  # Drop into debugger on failure
```

### Viewing Test Output

```bash
# Show captured stdout/stderr
pytest -v -s

# Show test summary
pytest --tb=short  # Short traceback
pytest --tb=line   # One line per failure
pytest --tb=no     # No traceback
```

---

## Best Practices Summary

### ✅ Do This

1. **Write tests first** (TDD red-green-refactor)
2. **Test behavior, not implementation**
3. **Use meaningful assertions** with clear messages
4. **Test error cases** as thoroughly as happy paths
5. **Use property-based testing** for edge case discovery
6. **Mock at boundaries** (external services only)
7. **Run `make pre-commit` before every commit**
8. **Keep tests fast** (<10s for unit tests)
9. **Document complex test logic**
10. **Maintain >80% coverage**

### ❌ Don't Do This

1. ❌ Skip writing tests ("I'll add them later")
2. ❌ Write tests just for coverage numbers
3. ❌ Test implementation details (private methods)
4. ❌ Use vague assertions (`assert result`)
5. ❌ Mock everything (makes tests brittle)
6. ❌ Write slow unit tests (use integration tests instead)
7. ❌ Ignore failing tests
8. ❌ Commit without running tests
9. ❌ Copy-paste test code
10. ❌ Test only happy paths

---

## Test Metrics

### Current Status

| Metric                | Target | Current | Status |
|-----------------------|--------|---------|--------|
| Unit Test Count       | 50+    | 86      | ✅     |
| Property Test Count   | 10+    | 17      | ✅     |
| Test Coverage         | 80%    | 98%*    | ✅     |
| Unit Test Runtime     | <10s   | 7.08s   | ✅     |
| Mutation Score        | 80%    | TBD     | 🔄     |

*Coverage for core modules (validation, rate_limiter, logging_config)

---

## Resources

### Tools Used

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **Hypothesis**: Property-based testing
- **mutmut**: Mutation testing
- **Coverage.py**: Coverage measurement

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [Property-Based Testing Guide](https://hypothesis.works/articles/what-is-property-based-testing/)

### Project Files

- [TEST_SPECIFICATION.md](TEST_SPECIFICATION.md) - Detailed test cases with success criteria
- [Makefile](Makefile) - Test automation commands
- [pytest.ini](pytest.ini) - Test configuration
- [tests/conftest.py](tests/conftest.py) - Shared fixtures

---

## Conclusion

This testing strategy ensures that the AI Stock Research platform is:

1. **Reliable**: Comprehensive tests catch bugs before production
2. **Maintainable**: Tests document expected behavior
3. **Robust**: Property-based testing finds edge cases
4. **Fast**: Quick feedback loop encourages frequent testing
5. **Professional**: Industry-standard practices and tools

**Remember**: Tests are not a burden - they are your safety net, documentation, and specification all in one!

---

**Last Updated**: 2025-11-10
**Maintained By**: Development Team
