from src.paper.exchange import PaperExchange


def test_paper_long_profit_and_close():
    exchange = PaperExchange(1000)
    exchange.market_order("BTC-USD", "BUY", 1, 100)
    assert exchange.portfolio.gross_exposure({"BTC-USD": 110}) == 110
    pnl = exchange.close("BTC-USD", 110)
    assert pnl == 10
    assert exchange.portfolio.realized_pnl == 10


def test_paper_short_profit_and_close():
    exchange = PaperExchange(1000)
    exchange.market_order("BTC-USD", "SELL", 2, 100)
    pnl = exchange.portfolio.close_position("BTC-USD", 90)
    assert pnl == 20


def test_invalid_order_rejected():
    exchange = PaperExchange()
    try:
        exchange.market_order("BTC-USD", "BUY", 0, 100)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid size should be rejected")
