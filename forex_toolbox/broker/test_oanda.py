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


def test_get_positions(broker):
    response = {
        "positions" : [
            {
                "instrument" : "EUR_USD",
                "units" : 4741,
                "side" : "buy",
                "avgPrice" : 1.3626
            },
            {
                "instrument" : "USD_CAD",
                "units" : 30,
                "side" : "sell",
                "avgPrice" : 1.11563
            }
        ]
    }

    with requests_mock.mock() as m:
        m.get("https://api-fxpractice.oanda.com/v1/accounts/{0}/positions".format(broker.id),
               json=response)
        positions = broker.get_positions(broker.id)
        assert 'positions' in positions

def order_response():
    return {"instrument": "EUR_USD",
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
            "tradeReduced": {}}


def test_create_order_sell_market(broker, asset):
    with requests_mock.mock() as m:
        m.post("https://api-fxpractice.oanda.com/v1/accounts/{0}/orders".format(broker.id),
               json=order_response())

        order_id = broker.create_order(asset, -2)
        assert order_id == 175517237

        call = m.request_history
        expected_params = ['instrument=EUR_USD', 'side=sell', 'type=market', 'units=2']
        assert set(call[0].text.split("&")) == set(expected_params)


def test_create_order_sell_tp_sl(broker, asset):
    with requests_mock.mock() as m:
        m.post("https://api-fxpractice.oanda.com/v1/accounts/{0}/orders".format(broker.id),
               json=order_response())

        order_id = broker.create_order(asset, -2, trailling=10.5, stop_loss=1.2345, take_profit=2.3456)
        assert order_id == 175517237

        call = m.request_history
        expected_params = ['instrument=EUR_USD', 'side=sell',
                           'type=market', 'units=2',
                           'trailingStop=10.5',
                           'takeProfit=2.34560', 'stopLoss=1.23450']
        assert set(call[0].text.split("&")) == set(expected_params)

def test_create_order_stop(broker, asset):
    with requests_mock.mock() as m:
        m.post("https://api-fxpractice.oanda.com/v1/accounts/{0}/orders".format(broker.id),
               json=order_response())

        order_id = broker.create_order(asset, -2, price=2.3456, order_type='stop')
        assert order_id == 175517237

        call = m.request_history
        expected_params = ['instrument=EUR_USD', 'side=sell',
                           'type=stop', 'units=2',
                           'price=2.34560']
        assert set(call[0].text.split("&")) == set(expected_params)
