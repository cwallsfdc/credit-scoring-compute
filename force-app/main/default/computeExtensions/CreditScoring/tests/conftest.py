import sys
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Create a mock object that will act as our fake 'heroku_applink' module
mock_sdk = MagicMock()


# Define a dummy middleware class that has the same structure as the real one.
class DummyIntegrationAsgiMiddleware:
    def __init__(self, app, config=None):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


# Define a dummy Record class matching the real SDK's Record interface.
class DummyRecord:
    def __init__(self, *, type: str, fields: dict):
        self.type = type
        self.fields = fields

# Attach the DUMMY classes to our FAKE module.
mock_sdk.IntegrationAsgiMiddleware = DummyIntegrationAsgiMiddleware
mock_sdk.Record = DummyRecord

# Now, put the fake module in place.
sys.modules["heroku_applink"] = mock_sdk


def pytest_configure(config):
    """
    This function is called by pytest during startup.
    It programmatically disables the 'anyio' plugin, which
    conflicts with the 'pytest-asyncio' plugin we need.
    """
    config.addinivalue_line("markers", "asyncio: mark a test as being asyncio-driven.")
    if "anyio" in config.pluginmanager.list_name_plugin():
        config.pluginmanager.unregister(name="anyio")


@pytest.fixture
def mock_context():
    """
    Returns a fully-mocked AppLink client context with data_api, org, and logger.
    """
    import heroku_applink as sdk

    context = MagicMock()
    context.data_api = AsyncMock()
    context.org = MagicMock()
    context.org.data_api = AsyncMock()
    context.logger = MagicMock()

    sdk.get_client_context = MagicMock(return_value=context)
    return context


@pytest.fixture
def client(mock_context):
    """
    A TestClient wired to the FastAPI app with the SDK fully mocked.
    """
    from main import app

    with TestClient(app) as c:
        yield c


def _make_account_record(
    name="Acme Corporation",
    working_capital=500000,
    total_assets=1000000,
    retained_earnings=200000,
    ebit=150000,
    market_value_equity=800000,
    total_liabilities=400000,
    sales=900000,
):
    """
    Helper to build a mock Salesforce Account record with financial fields.
    """
    record = MagicMock()
    fields = {
        "Id": "001XX000003GYQXYA4",
        "Name": name,
        "WorkingCapital__c": working_capital,
        "TotalAssets__c": total_assets,
        "RetainedEarnings__c": retained_earnings,
        "EBIT__c": ebit,
        "MarketValueEquity__c": market_value_equity,
        "TotalLiabilities__c": total_liabilities,
        "Sales__c": sales,
    }
    record.fields = fields
    return record
