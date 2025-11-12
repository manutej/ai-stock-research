# S&P 500 CSV Generation Test Suite

This document describes the comprehensive test suite for the S&P 500 CSV generation functionality.

## Overview

The test suite consists of **100 tests** covering:
- Unit tests for individual functions
- Integration tests for end-to-end workflows
- Error handling tests for robustness
- Mock tests that run without actual API calls

All tests use mocking to avoid making real API calls, ensuring they run quickly and reliably in any environment.

## Test Files

### 1. Unit Tests: `tests/unit/test_sp500_generation.py`

**48 tests** covering core functionality:

#### Test Coverage Areas:

- **TC-SP500-001: Data fetching functions**
  - Mocked data fetching with async providers
  - Batch processing logic
  - Quote data retrieval

- **TC-SP500-002: Formatting functions**
  - `format_value()` - Currency, billions, millions, percentages
  - `format_number()` - Various numeric formats
  - `safe_get()` - Safe dictionary access with defaults
  - Handling of None, NaN, and invalid values

- **TC-SP500-003: CSV row construction**
  - Valid quote data formatting
  - Missing data handling (N/A values)
  - Partial data scenarios

- **TC-SP500-004: Sector filtering**
  - Case-insensitive filtering
  - Technology, Healthcare, Financials sectors
  - Invalid sector handling

- **TC-SP500-005: Limit options**
  - Limiting to 5, 10, N companies
  - Edge cases (zero, negative, exceeds total)

- **TC-SP500-006: Error handling**
  - Missing data scenarios
  - Empty dictionaries
  - Invalid format handling

- **TC-SP500-007: Batch processing**
  - Batch size calculations
  - Batch slicing logic
  - Last batch detection

### 2. Integration Tests: `tests/integration/test_sp500_csv.py`

**16 tests** covering end-to-end scenarios:

#### Test Coverage Areas:

- **TC-SP500-INT-001: End-to-end CSV generation**
  - Basic CSV generation with mocked provider
  - Advanced CSV with fundamentals
  - Complete workflow validation

- **TC-SP500-INT-002: CSV format validation**
  - Header row presence
  - Proper value quoting
  - Numeric formatting preservation

- **TC-SP500-INT-003: CSV content verification**
  - All rows have tickers
  - Valid timestamps
  - Properly formatted values

- **TC-SP500-INT-004: Sector filtering integration**
  - Technology sector filtering
  - Healthcare sector filtering
  - Combined with mocked data

- **TC-SP500-INT-005: Limit option integration**
  - Limit to 5 companies
  - Limit with sector filter
  - Combined filtering scenarios

- **TC-SP500-INT-006: Error resilience**
  - Partial batch failures
  - Empty results handling
  - Graceful degradation

### 3. Error Handling Tests: `tests/unit/test_sp500_error_handling.py`

**36 tests** covering error scenarios:

#### Test Coverage Areas:

- **TC-SP500-ERR-001: API connection failures**
  - Provider connection errors
  - Get quotes failures
  - Network timeouts

- **TC-SP500-ERR-002: Missing data handling**
  - Safe get with missing keys
  - None and NaN values
  - Default value handling

- **TC-SP500-ERR-003: Malformed data handling**
  - Invalid data types (strings, lists, dicts)
  - NaN in dictionaries
  - Negative values (price, volume)

- **TC-SP500-ERR-004: Rate limit errors**
  - Rate limit exceptions
  - Retry logic

- **TC-SP500-ERR-005: Timeout handling**
  - Async timeout errors
  - Retry mechanisms

- **TC-SP500-ERR-006: Partial batch failures**
  - Continue on batch failure
  - Process available quotes only

- **TC-SP500-ERR-007: Invalid ticker handling**
  - Empty tickers
  - None tickers
  - Invalid ticker format

- **TC-SP500-ERR-008: File I/O errors**
  - Read-only directory
  - Nonexistent directory
  - Malformed CSV reading

## Test Fixtures

### Shared Fixtures (in `tests/conftest.py`)

- `sample_sp500_companies` - Sample company data for testing
- `sample_advanced_companies` - Companies with industry info
- `mock_quote` - Single mock Quote object
- `mock_quotes` - Dictionary of mock quotes
- `mock_stock_provider` - Mocked async provider
- `sample_fundamental_data` - Mock yfinance fundamental data
- `mock_yfinance_ticker` - Comprehensive yfinance mock

## Running the Tests

### Run all S&P 500 tests:
```bash
pytest tests/unit/test_sp500*.py tests/integration/test_sp500*.py -v
```

### Run only unit tests:
```bash
pytest tests/unit/test_sp500_generation.py -v
```

### Run only integration tests:
```bash
pytest tests/integration/test_sp500_csv.py -v
```

### Run only error handling tests:
```bash
pytest tests/unit/test_sp500_error_handling.py -v
```

### Run with coverage:
```bash
pytest tests/unit/test_sp500*.py tests/integration/test_sp500*.py --cov=generate_sp500 --cov-report=html
```

### Run specific test classes:
```bash
pytest tests/unit/test_sp500_generation.py::TestFormatValueFunction -v
pytest tests/unit/test_sp500_generation.py::TestSectorFiltering -v
pytest tests/integration/test_sp500_csv.py::TestCSVGeneration -v
```

## Key Features

### 1. No Real API Calls
All tests use mocks and don't make actual API calls to:
- Polygon.io
- Yahoo Finance
- Any external service

This ensures:
- Fast test execution
- No API key requirements
- No rate limit concerns
- Consistent results

### 2. Comprehensive Coverage
Tests cover:
- Happy path scenarios
- Edge cases
- Error conditions
- Data validation
- Format verification

### 3. Best Practices
- Uses pytest fixtures for reusable test data
- Follows AAA pattern (Arrange, Act, Assert)
- Clear test names describing what is tested
- Organized into logical test classes
- Proper use of async/await for async functions
- Mock isolation - no test affects another

### 4. Test Markers
Tests are marked for easy filtering:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.asyncio` - Async tests

## Test Results

All 100 tests pass successfully:
- 48 unit tests (test_sp500_generation.py)
- 36 error handling tests (test_sp500_error_handling.py)
- 16 integration tests (test_sp500_csv.py)

```
============================= 100 passed =============================
```

## What Each Script Tests

### generate_sp500_test.py
- Basic CSV generation
- Real-time quote fetching
- Simple company list
- Batch processing with rate limiting

### generate_sp500_advanced.py
- Advanced CSV with fundamentals
- yfinance integration
- Sector filtering
- Limit options
- Comprehensive financial metrics

### generate_sp500_standalone.py
- Standalone yfinance implementation
- Retry logic
- Error handling
- Robust data fetching

## Mock Strategy

### Provider Mocking
```python
mock_provider = AsyncMock()
mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
mock_provider.__aexit__ = AsyncMock(return_value=None)
mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)
```

### yfinance Mocking
```python
with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
    data = get_fundamental_data("AAPL")
```

### Quote Object Creation
```python
Quote(
    ticker="AAPL",
    price=150.25,
    timestamp=datetime.now(),
    volume=50000000,
    change=1.25,
    change_percent=0.84,
    provider="mock"
)
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies
- Fast execution (< 20 seconds for all 100 tests)
- Deterministic results
- No network required

## Future Enhancements

Potential additions:
1. Performance tests for large datasets
2. Property-based tests using Hypothesis
3. CSV schema validation tests
4. Data quality checks
5. Concurrent batch processing tests

## Troubleshooting

### Import Errors
If you get import errors, ensure you're running from the project root:
```bash
cd /home/user/ai-stock-research
pytest tests/unit/test_sp500*.py
```

### Async Warnings
The tests use `@pytest.mark.asyncio` for async functions. Make sure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Mock Issues
If mocks aren't working, ensure you're patching the correct module path. Use:
- `generate_sp500_advanced.yf.Ticker` (not `yfinance.Ticker`)
- `generate_sp500_test.ProviderFactory` (not `providers.factory.ProviderFactory`)

## Contact

For questions or issues with the tests, please refer to the project documentation or open an issue.
