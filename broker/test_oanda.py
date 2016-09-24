import requests_mock
import pytest
import os
from .oanda import Oanda
from zipline.assets import Asset


@pytest.fixture
def broker(request):
    id = os.getenv("OANDA_ACCOUNT_ID", "test")
    return Oanda(id)


@pytest.fixture
def asset(request):
    return Asset(1, "forex", symbol="EUR_USD",
                 asset_name="EUR_USD")


def test_create_order_sell_market(broker, asset):
    with requests_mock.mock() as m:
        order_response = {
            "instrument": "EUR_USD",
            "time": "2013-12-06T20:36:06Z",
            "price": 1.37041,
            "tradeOpened": {
                "id": 175517237,
                "units": 2,
                "side": "sell",
                "takeProfit": 0,
                "stopLoss": 0,
                "trailingStop": 0
            },
            "tradesClosed": [],
            "tradeReduced": {}
        }
        m.post("https://api-fxpractice.oanda.com/v1/accounts/{0}/orders".format(broker.id),
               json=order_response)

        order_id = broker.create_order(asset, -2)
        assert order_id == 175517237

        call = m.request_history
        expected_params = ['instrument=EUR_USD', 'side=sell', 'type=market', 'units=-2']
        assert set(call[0].text.split("&")) == set(expected_params)