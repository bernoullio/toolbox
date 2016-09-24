""" Meta wrapper for oanda apis
See http://developer.oanda.com/rest-live

TODO: Benchmark latency
"""
from __future__ import absolute_import
import os
import oandapy

import logging


class Oanda(object):
    PRECISION = {'EUR_USD': '%.5f',
                 'USD_JPY': '%.3f',
                 'EUR_JPY': '%.3f',
                 'GBP_USD': '%.5f'}

    def __init__(self, id):
        self.id = id
        self.oanda = oandapy.API(environment=os.getenv("OANDA_ENV", "practice"),
                                 access_token=os.getenv("OANDA_ACCESS_TOKEN", "xxx"))

    def create_order(self, instrument, amount,
                     limit=None, stop=None, expiry=None,
                     stop_loss=None, take_profit=None, trailling=None):
        """
        Creates an order with Oanda rest api.

        Default expiry is 1 month from now, for limit, stop
        and marketIfTouch order types.

        Return
        ------
        order_id: string
            Oanda order id string
        """

        if amount < 0:
            side = "sell"
            lower_bound = stop
            upper_bound = limit
            touch_price = upper_bound
        else:
            side = "buy"
            lower_bound = limit
            upper_bound = stop
            touch_price = lower_bound

        order_type = ""
        if stop and limit:
            # For oanda, there's no explicit "stop limit order" type
            # So we use "market if touch", but set upper and lower bound
            order_type = "marketIfTouched"
        elif stop:
            order_type = "stop"
            touch_price = stop
        elif limit:
            order_type = "limit"
            touch_price = limit
        else:
            order_type = "market"
            touch_price = None

        params = {"account_id": self.id,
                  "instrument": instrument.symbol,
                  "units":      amount,
                  "side":       side,
                  "type":       order_type}

        if touch_price:
            params["price"] = touch_price

        if expiry is not None:
            expiry_string = expiry.strftime("%Y-%m-%dT%H:%M:%S")
            params["expiry"] = expiry_string

        precision = Oanda.PRECISION[instrument.symbol]
        if lower_bound:
            params["lowerBound"] = precision % lower_bound

        if upper_bound:
            params["upperBound"] = precision % upper_bound

        if stop_loss:
            params["stopLoss"] = precision % stop_loss

        if take_profit:
            params["takeProfit"] = precision % take_profit

        try:
            response = self.oanda.create_order(**params)
            logging.info("#create_order params=%s response=%s" % (params, response))
        except oandapy.exceptions.OandaError as e:
            logging.exception(e)

        return response["tradeOpened"]["id"]
