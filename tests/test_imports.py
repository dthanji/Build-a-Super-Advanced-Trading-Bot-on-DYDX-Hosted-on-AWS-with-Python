def test_runtime_module_imports():
    from src.dydx.client import DydxClient
    from src.dydx.market_data import MarketData
    from src.dydx.orders import Orders
    from src.dydx.positions import Positions

    assert DydxClient and MarketData and Orders and Positions
