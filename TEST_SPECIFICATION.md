# Test Specification - AI Stock Research Platform

**Version**: 1.0
**Date**: 2025-11-10
**Purpose**: Define comprehensive testing strategy with measurable success criteria

---

## Philosophy

### Testing Principles

1. **Behavior over Implementation**: Test what the code does, not how it does it
2. **Meaningful Assertions**: Every assertion must validate a business requirement
3. **Isolation**: Unit tests must be fast and independent
4. **Integration Reality**: Integration tests must use real scenarios
5. **Property-Based**: Use property testing to find edge cases
6. **No Coverage Theater**: 80% coverage is baseline, not goal

### Anti-Patterns to Avoid

❌ **Surface-Level Tests**
```python
# BAD: Just testing that code runs
def test_get_quote():
    result = provider.get_quote("AAPL")
    assert result is not None  # Meaningless!
```

✅ **Meaningful Tests**
```python
# GOOD: Testing actual behavior
def test_get_quote_returns_valid_price_data():
    result = provider.get_quote("AAPL")
    assert result.ticker == "AAPL"
    assert result.price > 0, "Price must be positive"
    assert result.timestamp is not None
    assert isinstance(result.provider, str)
```

---

## Test Coverage Matrix

### Module: `validation.py`

#### Success Criteria
- ✅ Rejects all invalid ticker formats
- ✅ Accepts all valid ticker formats
- ✅ Normalizes input correctly
- ✅ Provides clear error messages
- ✅ Handles edge cases (None, empty, special chars)

#### Test Cases

**TC-VAL-001: Valid Ticker Formats**
```yaml
Objective: Validate that all legitimate ticker formats are accepted
Success Criteria:
  - Single letter tickers (A, X) accepted
  - Multi-letter tickers (AAPL, MSFT, GOOGL) accepted
  - 5-letter tickers (AMZNN) accepted
  - Lowercase input normalized to uppercase
  - Whitespace trimmed
Property Test: Any string matching /^[A-Z]{1,5}$/ should be valid
```

**TC-VAL-002: Invalid Ticker Formats**
```yaml
Objective: Reject invalid ticker formats with clear error messages
Success Criteria:
  - Tickers > 5 letters rejected
  - Numeric tickers rejected
  - Special characters rejected
  - Empty string rejected
  - None rejected
  - Mixed alphanumeric rejected (ABC123)
Edge Cases:
  - "": ValueError with message "Ticker cannot be empty"
  - "TOOLONG": ValueError with message "must be 1-5"
  - "123": ValueError with message "must be 1-5 uppercase letters"
  - "ABC-D": ValueError with message "must be 1-5 uppercase letters"
```

**TC-VAL-003: Batch Validation**
```yaml
Objective: Validate ticker lists with correct error propagation
Success Criteria:
  - Valid list accepted and normalized
  - List with one invalid ticker rejected entirely
  - Empty list rejected
  - List > 50 tickers rejected (business rule)
  - Duplicate tickers preserved (or deduplicated based on spec)
```

**TC-VAL-004: Date Range Validation**
```yaml
Objective: Ensure date ranges are logically valid
Success Criteria:
  - end_date must be after start_date
  - Dates cannot be in the future (for historical data)
  - Dates must be valid datetime objects
Property Test: For any two dates where end > start, validation passes
```

---

### Module: `logging_config.py`

#### Success Criteria
- ✅ Logs written to correct outputs
- ✅ Log levels filter correctly
- ✅ JSON format valid and parseable
- ✅ Human format readable
- ✅ No log injection vulnerabilities

#### Test Cases

**TC-LOG-001: Log Level Filtering**
```yaml
Objective: Verify log levels filter messages correctly
Success Criteria:
  - DEBUG level shows all messages
  - INFO level hides DEBUG
  - WARNING level hides INFO and DEBUG
  - ERROR level shows only ERROR and CRITICAL
Test Method: Capture logs, verify counts match expectations
```

**TC-LOG-002: Structured JSON Logging**
```yaml
Objective: Ensure JSON logs are valid and complete
Success Criteria:
  - Every log line is valid JSON
  - Required fields present: time, level, module, function, line, message
  - Timestamps in ISO 8601 format
  - Exception info included when exc_info=True
Validation: Parse each JSON line, verify schema
```

**TC-LOG-003: Log Injection Prevention**
```yaml
Objective: Prevent log injection attacks
Success Criteria:
  - Newlines in log messages escaped
  - Special characters sanitized
  - No code execution possible via log messages
Test Cases:
  - logger.info("Hello\nInjected") -> single line
  - logger.info("'; DROP TABLE--") -> escaped
```

---

### Module: `rate_limiter.py`

#### Success Criteria
- ✅ Rate limits enforced accurately
- ✅ Token bucket algorithm correct
- ✅ Thread-safe under concurrent access
- ✅ Time-based replenishment works
- ✅ Burst capacity correct

#### Test Cases

**TC-RATE-001: Basic Rate Limiting**
```yaml
Objective: Verify rate limiter enforces limits
Success Criteria:
  - First N requests succeed (where N = rate)
  - Request N+1 raises RateLimitExceededError
  - After time window, requests succeed again
Test Setup:
  - Create limiter with rate=5, per=60
  - Make 5 requests -> all succeed
  - Make 6th request -> raises exception
  - Wait 60 seconds
  - Make request -> succeeds
```

**TC-RATE-002: Token Replenishment**
```yaml
Objective: Verify tokens replenish correctly over time
Success Criteria:
  - Tokens added proportional to time passed
  - Tokens capped at maximum rate
  - Fractional tokens handled correctly
Test Method:
  - Consume all tokens
  - Wait half the time window
  - Should have ~half tokens available
Property Test: tokens_available = min(rate, initial + (time_passed * rate / window))
```

**TC-RATE-003: Thread Safety**
```yaml
Objective: Ensure thread-safe under concurrent access
Success Criteria:
  - No race conditions when multiple threads access
  - Total requests across all threads = rate
  - No deadlocks
Test Method:
  - Spawn 100 threads
  - Each tries to consume a token
  - Exactly 'rate' threads should succeed
```

**TC-RATE-004: Multiple Providers**
```yaml
Objective: Different providers have independent limits
Success Criteria:
  - Polygon limit doesn't affect YFinance
  - Each provider tracked separately
  - Limits configurable per provider
```

---

### Module: `exceptions.py`

#### Success Criteria
- ✅ Exception hierarchy correct
- ✅ All exceptions inherit from base
- ✅ Error messages clear and actionable
- ✅ Custom attributes accessible

#### Test Cases

**TC-EXC-001: Exception Hierarchy**
```yaml
Objective: Verify exception inheritance
Success Criteria:
  - All exceptions inherit from AIStockResearchError
  - AIStockResearchError inherits from Exception
  - isinstance checks work correctly
Validation:
  - isinstance(ProviderError(), AIStockResearchError) == True
  - isinstance(InvalidTickerError(), ProviderError) == False
  - isinstance(InvalidTickerError(), AIStockResearchError) == True
```

**TC-EXC-002: Custom Attributes**
```yaml
Objective: Custom exception attributes accessible
Success Criteria:
  - InvalidTickerError.ticker available
  - ProviderRateLimitError.retry_after available
  - Attributes set correctly in constructor
Test:
  - e = InvalidTickerError("XYZ")
  - assert e.ticker == "XYZ"
  - assert "XYZ" in str(e)
```

---

### Module: `providers/yfinance_provider.py`

#### Success Criteria
- ✅ All methods log operations
- ✅ Invalid input rejected with clear errors
- ✅ Network errors handled gracefully
- ✅ Rate limiting enforced
- ✅ Data validation performed
- ✅ Provider name accurate

#### Test Cases

**TC-YF-001: Quote Retrieval Success**
```yaml
Objective: Verify get_quote returns valid data
Success Criteria:
  - Quote object returned
  - All required fields populated (ticker, price, timestamp)
  - Price is positive float
  - Timestamp is recent (within 1 hour)
  - Provider field = "yfinance"
Mock Setup:
  - Mock yfinance.Ticker to return valid data
  - Verify rate limiter called
  - Verify logger called with INFO
Validation:
  - assert quote.ticker == "AAPL"
  - assert quote.price > 0
  - assert datetime.now() - quote.timestamp < timedelta(hours=1)
```

**TC-YF-002: Invalid Ticker Rejection**
```yaml
Objective: Verify invalid tickers rejected before API call
Success Criteria:
  - InvalidTickerError raised for invalid format
  - No API call made (mock not called)
  - Error logged with WARNING level
Test Cases:
  - get_quote("") -> InvalidTickerError
  - get_quote("123") -> InvalidTickerError
  - get_quote("TOOLONG") -> InvalidTickerError
Validation:
  - Exception type correct
  - Exception message contains ticker
  - Mock yf.Ticker not called (efficiency check)
```

**TC-YF-003: Network Error Handling**
```yaml
Objective: Network errors handled gracefully
Success Criteria:
  - ProviderError raised (not raw exception)
  - Error logged with ERROR level and stack trace
  - Original error preserved in exception chain
Mock Setup:
  - Mock yf.Ticker to raise ConnectionError
Expected:
  - ProviderError raised
  - str(exc) contains "Failed to fetch quote"
  - logger.error called with exc_info=True
```

**TC-YF-004: Data Validation**
```yaml
Objective: Invalid API responses detected
Success Criteria:
  - Missing price data raises DataNotFoundError
  - Empty response raises DataNotFoundError
  - Malformed data raises ProviderError
Mock Scenarios:
  - info = {} -> DataNotFoundError
  - info = {"currentPrice": None} -> DataNotFoundError
  - info = {"currentPrice": "invalid"} -> ProviderError
```

**TC-YF-005: Batch Quote Handling**
```yaml
Objective: Batch quotes handle partial failures correctly
Success Criteria:
  - Valid tickers return quotes
  - Invalid tickers logged but don't stop batch
  - Result dict contains only successful quotes
Test:
  - get_quotes(["AAPL", "INVALID", "MSFT"])
  - Result: {"AAPL": Quote(...), "MSFT": Quote(...)}
  - logger.warning called for "INVALID"
```

**TC-YF-006: Historical Data Validation**
```yaml
Objective: Historical data meets business requirements
Success Criteria:
  - Bars returned in chronological order
  - All OHLCV fields populated
  - Volume is non-negative integer
  - High >= Low for each bar
  - High >= Open, Close
  - Low <= Open, Close
Property Test: For any valid date range, returned data is valid
```

**TC-YF-007: Rate Limiting Integration**
```yaml
Objective: Rate limiter called for each operation
Success Criteria:
  - rate_limiter.check_limit("yfinance") called
  - RateLimitExceededError propagated if raised
  - Operation aborted if rate limited (no API call)
Mock:
  - Mock rate_limiter to raise RateLimitExceededError
  - Verify yf.Ticker not called
```

---

## Integration Tests

### INT-001: End-to-End Quote Flow

```yaml
Objective: Validate complete flow from request to response
Components: validation -> rate_limiter -> provider -> logging
Success Criteria:
  - Input validated
  - Rate limit checked
  - API called
  - Response validated
  - Result logged
  - Metrics recorded
Test Flow:
  1. Call get_quote("AAPL")
  2. Verify validate_ticker called
  3. Verify rate_limiter called
  4. Verify yf.Ticker called with "AAPL"
  5. Verify Quote object returned
  6. Verify logger.info called with success message
Failure Cases:
  - Invalid ticker -> no API call, error logged
  - Rate limited -> no API call, exception raised
  - API error -> error logged, exception raised
```

### INT-002: Provider Failover

```yaml
Objective: Verify fallback behavior when provider fails
Components: HybridProvider, YFinance, Polygon
Success Criteria:
  - Primary provider tried first
  - Fallback provider used on failure
  - Both attempts logged
  - Final result or error returned
Test Scenarios:
  - YFinance succeeds -> use YFinance result
  - YFinance fails, no fallback -> exception
  - Hybrid: Polygon fails -> YFinance used
```

### INT-003: Logging Pipeline

```yaml
Objective: Verify logs flow correctly through system
Success Criteria:
  - All operations logged
  - Log levels correct
  - Logs parseable (JSON)
  - No sensitive data in logs (API keys, etc.)
Test Method:
  - Capture all log output
  - Parse each line as JSON
  - Verify required fields present
  - Verify no API keys in messages
```

---

## Property-Based Tests

### PROP-001: Ticker Validation Properties

```python
from hypothesis import given, strategies as st

@given(st.text(alphabet=st.characters(whitelist_categories=('Lu',)), min_size=1, max_size=5))
def test_valid_ticker_always_accepted(ticker: str):
    """Any 1-5 uppercase letter string should be valid"""
    result = validate_ticker(ticker)
    assert result == ticker
    assert result.isupper()

@given(st.text(min_size=6))
def test_long_ticker_always_rejected(ticker: str):
    """Any string > 5 characters should be rejected"""
    with pytest.raises(ValueError):
        validate_ticker(ticker)
```

### PROP-002: Rate Limiter Properties

```python
@given(st.integers(min_value=1, max_value=1000), st.floats(min_value=1.0, max_value=3600.0))
def test_rate_limiter_never_exceeds_limit(rate: int, window: float):
    """Rate limiter should never allow more than 'rate' requests in 'window'"""
    limiter = TokenBucket(rate, window)

    successful = 0
    for _ in range(rate * 2):
        if limiter.consume():
            successful += 1

    assert successful == rate, f"Expected {rate}, got {successful}"
```

### PROP-003: OHLCV Data Properties

```python
@given(st.lists(st.floats(min_value=0.01, max_value=10000), min_size=4, max_size=4))
def test_ohlcv_invariants(prices: List[float]):
    """OHLCV data must satisfy: High >= max(O,C) and Low <= min(O,C)"""
    open_price, high, low, close = sorted(prices), max(prices), min(prices), prices[2]

    # Construct valid OHLCV
    bar = OHLCV(
        timestamp=datetime.now(),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=1000
    )

    # Validate invariants
    assert bar.high >= bar.open
    assert bar.high >= bar.close
    assert bar.low <= bar.open
    assert bar.low <= bar.close
```

---

## Performance Tests

### PERF-001: Rate Limiter Performance

```yaml
Objective: Rate limiter overhead < 1ms per call
Success Criteria:
  - 10,000 calls complete in < 10 seconds
  - Mean latency < 1ms
  - P95 latency < 2ms
  - Thread-safe under load
Test Method:
  - Benchmark 10,000 sequential calls
  - Benchmark 100 threads × 100 calls
  - Measure latency distribution
```

### PERF-002: Logging Performance

```yaml
Objective: Logging doesn't significantly impact performance
Success Criteria:
  - Logging 1,000 messages < 100ms
  - Async logging (if implemented) doesn't block
  - No memory leaks over time
```

---

## Test Execution Strategy

### Unit Tests
```bash
pytest tests/unit/ -v --cov=. --cov-report=term-missing
```

**Requirements**:
- All tests independent (no order dependency)
- No network calls
- Fast (<1s total for unit tests)
- Deterministic (no flaky tests)

### Integration Tests
```bash
pytest tests/integration/ -v --slow
```

**Requirements**:
- May use network (mocked or stubbed)
- Test real integrations
- Slower (<30s total)

### Property Tests
```bash
pytest tests/property/ -v --hypothesis-profile=ci
```

**Requirements**:
- Use Hypothesis library
- Generate edge cases automatically
- Find bugs through fuzzing

---

## Success Metrics

### Coverage Metrics
- **Line Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 75%
- **Function Coverage**: ≥ 90%

### Quality Metrics
- **Mutation Score**: ≥ 70% (using mutmut)
- **Flaky Test Rate**: 0% (no flaky tests tolerated)
- **Test Execution Time**: <5s for unit, <30s for all

### Behavioral Metrics
- **Edge Cases Covered**: 100% of known edge cases
- **Error Paths Tested**: All error handlers tested
- **Integration Points**: All module boundaries tested

---

## TDD Workflow

### Red-Green-Refactor Cycle

1. **RED**: Write failing test first
   ```python
   def test_validate_ticker_rejects_numbers():
       with pytest.raises(ValueError):
           validate_ticker("123")
   ```

2. **GREEN**: Write minimal code to pass
   ```python
   def validate_ticker(ticker: str) -> str:
       if ticker.isdigit():
           raise ValueError("Ticker cannot be all numbers")
       return ticker.upper()
   ```

3. **REFACTOR**: Improve code quality
   ```python
   def validate_ticker(ticker: str) -> str:
       if not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
           raise ValueError(
               f"Invalid ticker format: {ticker}. "
               "Ticker must be 1-5 uppercase letters"
           )
       return ticker.upper()
   ```

### Before Committing

```bash
# Run all checks
make test           # All tests
make lint           # Code quality
make type-check     # Type checking
make security       # Security scan

# If all pass, commit
git commit -m "feat: add ticker validation"
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Run property tests
        run: pytest tests/property/ -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Anti-Pattern Detection

### Code Review Checklist

- [ ] Test names describe behavior, not implementation
- [ ] Each test has clear success criteria
- [ ] Mocks are minimal and necessary
- [ ] Property tests used where applicable
- [ ] Edge cases explicitly tested
- [ ] Error messages validated
- [ ] No "test everything" tests
- [ ] No duplicate test logic
- [ ] Fast execution (<1s per test)
- [ ] Deterministic (no randomness without seed)

---

**Status**: SPECIFICATION COMPLETE
**Next**: Implement tests following this specification
**Review**: Required before implementation
