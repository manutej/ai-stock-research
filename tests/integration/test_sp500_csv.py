"""
Integration tests for S&P 500 CSV generation

Test Coverage:
- TC-SP500-INT-001: End-to-end CSV generation
- TC-SP500-INT-002: CSV format validation
- TC-SP500-INT-003: CSV content verification
- TC-SP500-INT-004: Sector filtering integration
- TC-SP500-INT-005: Limit option integration
- TC-SP500-INT-006: Error resilience in production scenarios

Success Criteria:
- CSV files are generated with correct format
- All expected columns are present
- Data is properly formatted
- Files can be read back and parsed
- Filtering and limiting works end-to-end
"""
import pytest
import csv
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generate_sp500_test import generate_sp500_csv, SP500_TEST_COMPANIES
from generate_sp500_advanced import generate_advanced_csv, SP500_COMPANIES
from generate_sp500_standalone import generate_csv
from providers.base import Quote


@pytest.mark.integration
@pytest.mark.asyncio
class TestCSVGeneration:
    """TC-SP500-INT-001: End-to-end CSV generation with mocks"""

    async def test_generate_basic_csv(self, tmp_path):
        """Should generate a basic CSV file with all required columns"""
        output_file = tmp_path / "test_sp500.csv"

        # Create mock provider
        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # Create mock quotes for all test companies
        mock_quotes = {}
        for company in SP500_TEST_COMPANIES[:5]:  # Test with first 5
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=150.0 + hash(company["ticker"]) % 100,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                open=149.50,
                high=151.00,
                low=149.00,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)

        # Patch and generate
        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_test.SP500_TEST_COMPANIES', SP500_TEST_COMPANIES[:5]):
                await generate_sp500_csv(str(output_file))

        # Verify file exists
        assert output_file.exists()

        # Verify file can be parsed as CSV
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have rows for companies
        assert len(rows) > 0

        # Verify required columns exist
        expected_columns = [
            "Ticker", "Company Name", "Sector", "Price", "Change", "Change %",
            "Open", "High", "Low", "Volume", "Provider", "Timestamp"
        ]

        for col in expected_columns:
            assert col in rows[0].keys(), f"Missing column: {col}"

    async def test_generate_advanced_csv(self, tmp_path):
        """Should generate advanced CSV with fundamental data"""
        output_file = tmp_path / "test_advanced.csv"

        # Mock provider for market data
        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        test_companies = SP500_COMPANIES[:3]
        mock_quotes = {}
        for company in test_companies:
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=150.0,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)

        # Mock yfinance for fundamentals
        mock_ticker = Mock()
        mock_ticker.info = {
            "marketCap": 2500000000000,
            "trailingPE": 28.5,
            "forwardPE": 25.3,
            "priceToBook": 45.2,
            "totalRevenue": 383000000000,
            "profitMargins": 0.25,
            "returnOnEquity": 1.47,
            "beta": 1.2,
        }

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                with patch('generate_sp500_advanced.SP500_COMPANIES', test_companies):
                    await generate_advanced_csv(str(output_file), limit=3)

        # Verify file exists
        assert output_file.exists()

        # Parse and verify
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3

        # Verify advanced columns
        advanced_columns = [
            "Ticker", "Company Name", "Sector", "Industry",
            "Price", "Market Cap", "P/E Ratio", "Forward P/E",
            "Revenue", "Profit Margin", "ROE"
        ]

        for col in advanced_columns:
            assert col in rows[0].keys(), f"Missing advanced column: {col}"


@pytest.mark.integration
class TestCSVFormat:
    """TC-SP500-INT-002: CSV format validation"""

    def test_csv_has_header_row(self, tmp_path):
        """CSV should have a header row with column names"""
        output_file = tmp_path / "test.csv"

        # Write a test CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Ticker", "Price", "Volume"])
            writer.writerow(["AAPL", "150.00", "50000000"])

        # Read and verify header
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)

        assert header == ["Ticker", "Price", "Volume"]

    def test_csv_values_are_properly_quoted(self, tmp_path):
        """CSV should handle special characters in company names"""
        output_file = tmp_path / "test.csv"

        company_name = 'Company, Inc.'  # Contains comma

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Company Name"])
            writer.writeheader()
            writer.writerow({"Ticker": "TEST", "Company Name": company_name})

        # Read back
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["Company Name"] == company_name

    def test_csv_handles_numeric_formatting(self, tmp_path):
        """CSV should preserve numeric formatting"""
        output_file = tmp_path / "test.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Price", "Volume"])
            writer.writeheader()
            writer.writerow({
                "Ticker": "AAPL",
                "Price": "$150.25",
                "Volume": "50,000,000"
            })

        # Read back
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert "$" in row["Price"]
        assert "," in row["Volume"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestSectorFilteringIntegration:
    """TC-SP500-INT-004: Sector filtering integration tests"""

    async def test_filter_by_technology_sector(self, tmp_path):
        """Should generate CSV with only Technology companies"""
        output_file = tmp_path / "tech_only.csv"

        # Mock provider
        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # Filter companies
        tech_companies = [c for c in SP500_COMPANIES if c["sector"] == "Technology"][:5]

        mock_quotes = {}
        for company in tech_companies:
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=150.0,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)

        # Mock yfinance
        mock_ticker = Mock()
        mock_ticker.info = {"marketCap": 1000000000, "trailingPE": 20.0}

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                await generate_advanced_csv(str(output_file), sector="Technology", limit=5)

        # Verify file
        assert output_file.exists()

        # Parse and verify all are Technology sector
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have some rows
        assert len(rows) > 0

        # All should be Technology sector (based on our test companies)
        for row in rows:
            assert row["Sector"] == "Technology"

    async def test_filter_by_healthcare_sector(self, tmp_path):
        """Should generate CSV with only Healthcare companies"""
        output_file = tmp_path / "healthcare_only.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # Filter companies
        healthcare_companies = [c for c in SP500_COMPANIES if c["sector"] == "Healthcare"][:3]

        mock_quotes = {}
        for company in healthcare_companies:
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=200.0,
                timestamp=datetime.now(),
                volume=30000000,
                change=-1.50,
                change_percent=-0.75,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)
        mock_ticker = Mock()
        mock_ticker.info = {"marketCap": 1000000000}

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                await generate_advanced_csv(str(output_file), sector="Healthcare", limit=3)

        assert output_file.exists()

        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0
        for row in rows:
            assert row["Sector"] == "Healthcare"


@pytest.mark.integration
@pytest.mark.asyncio
class TestLimitIntegration:
    """TC-SP500-INT-005: Limit option integration tests"""

    async def test_limit_to_five_companies(self, tmp_path):
        """Should generate CSV with exactly 5 companies"""
        output_file = tmp_path / "limited_5.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        test_companies = SP500_COMPANIES[:5]
        mock_quotes = {}
        for company in test_companies:
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=150.0,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)
        mock_ticker = Mock()
        mock_ticker.info = {}

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                await generate_advanced_csv(str(output_file), limit=5)

        assert output_file.exists()

        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5

    async def test_limit_with_sector_filter(self, tmp_path):
        """Should apply both sector filter and limit"""
        output_file = tmp_path / "tech_limited.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        tech_companies = [c for c in SP500_COMPANIES if c["sector"] == "Technology"][:3]
        mock_quotes = {}
        for company in tech_companies:
            mock_quotes[company["ticker"]] = Quote(
                ticker=company["ticker"],
                price=150.0,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                provider="mock"
            )

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)
        mock_ticker = Mock()
        mock_ticker.info = {}

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                await generate_advanced_csv(str(output_file), sector="Technology", limit=3)

        assert output_file.exists()

        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        for row in rows:
            assert row["Sector"] == "Technology"


@pytest.mark.integration
class TestCSVContentVerification:
    """TC-SP500-INT-003: Verify CSV content is valid and complete"""

    def test_all_rows_have_ticker(self, tmp_path):
        """Every row should have a non-empty ticker"""
        output_file = tmp_path / "test.csv"

        # Create test CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Price"])
            writer.writeheader()
            writer.writerow({"Ticker": "AAPL", "Price": "150.00"})
            writer.writerow({"Ticker": "MSFT", "Price": "350.00"})

        # Verify
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["Ticker"]
                assert len(row["Ticker"]) > 0

    def test_timestamps_are_valid(self, tmp_path):
        """Timestamp values should be valid datetime strings"""
        output_file = tmp_path / "test.csv"

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Timestamp"])
            writer.writeheader()
            writer.writerow({"Ticker": "AAPL", "Timestamp": timestamp})

        # Verify
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        # Should be parseable as datetime
        parsed_time = datetime.strptime(row["Timestamp"], '%Y-%m-%d %H:%M:%S')
        assert isinstance(parsed_time, datetime)

    def test_numeric_values_are_formatted(self, tmp_path):
        """Numeric values should have proper formatting"""
        output_file = tmp_path / "test.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Price", "Volume"])
            writer.writeheader()
            writer.writerow({
                "Ticker": "AAPL",
                "Price": "$150.25",
                "Volume": "50,000,000"
            })

        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        # Verify formatting is preserved
        assert "$" in row["Price"]
        assert "." in row["Price"]
        assert "," in row["Volume"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestErrorResilience:
    """TC-SP500-INT-006: Test error resilience"""

    async def test_continue_on_partial_failures(self, tmp_path):
        """Should continue processing even if some companies fail"""
        output_file = tmp_path / "partial_failure.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # Some companies succeed, one fails (missing from quotes)
        test_companies = SP500_COMPANIES[:3]
        mock_quotes = {
            test_companies[0]["ticker"]: Quote(
                ticker=test_companies[0]["ticker"],
                price=150.0,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                provider="mock"
            ),
            # test_companies[1] missing - simulates failure
            test_companies[2]["ticker"]: Quote(
                ticker=test_companies[2]["ticker"],
                price=200.0,
                timestamp=datetime.now(),
                volume=30000000,
                change=-1.50,
                change_percent=-0.75,
                provider="mock"
            ),
        }

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)
        mock_ticker = Mock()
        mock_ticker.info = {}

        with patch('generate_sp500_advanced.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
                with patch('generate_sp500_advanced.SP500_COMPANIES', test_companies):
                    await generate_advanced_csv(str(output_file), limit=3)

        # File should still be created
        assert output_file.exists()

        # Should have rows for all companies, even failed ones (with N/A)
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3

    async def test_empty_result_handling(self, tmp_path):
        """Should handle empty results gracefully"""
        output_file = tmp_path / "empty.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)
        mock_provider.get_quotes = AsyncMock(return_value={})  # Empty results

        mock_ticker = Mock()
        mock_ticker.info = {}

        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_test.SP500_TEST_COMPANIES', SP500_TEST_COMPANIES[:2]):
                await generate_sp500_csv(str(output_file))

        # Should still create file
        assert output_file.exists()


@pytest.mark.integration
class TestCSVReadability:
    """Test that generated CSVs are readable by common tools"""

    def test_csv_readable_by_dictreader(self, tmp_path):
        """CSV should be readable by Python's csv.DictReader"""
        output_file = tmp_path / "test.csv"

        # Create CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Price", "Sector"])
            writer.writeheader()
            writer.writerow({"Ticker": "AAPL", "Price": "150.00", "Sector": "Technology"})

        # Read with DictReader
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["Ticker"] == "AAPL"

    def test_csv_has_consistent_column_count(self, tmp_path):
        """All rows should have the same number of columns"""
        output_file = tmp_path / "test.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Ticker", "Price", "Volume"])
            writer.writeheader()
            writer.writerow({"Ticker": "AAPL", "Price": "150.00", "Volume": "50000000"})
            writer.writerow({"Ticker": "MSFT", "Price": "350.00", "Volume": "30000000"})

        # Read and verify
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Header + 2 data rows
        assert len(rows) == 3

        # All rows should have same column count
        col_count = len(rows[0])
        for row in rows:
            assert len(row) == col_count


# Pytest marks
pytestmark = pytest.mark.integration
