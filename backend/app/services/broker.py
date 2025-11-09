from abc import ABC, abstractmethod
from typing import Any, Dict


class BrokerAdapter(ABC):
    @abstractmethod
    def place_order(self, symbol: str, side: str, volume: float) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        raise NotImplementedError


class PaperBroker(BrokerAdapter):
    def __init__(self):
        self.orders = []

    def place_order(self, symbol: str, side: str, volume: float) -> Dict[str, Any]:
        order = {"symbol": symbol, "side": side, "volume": volume, "status": "filled"}
        self.orders.append(order)
        return order

    def get_positions(self) -> Dict[str, Any]:
        return {"positions": [], "orders": self.orders}


class ExnessMT5Broker(BrokerAdapter):
    def __init__(self, login: str, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server

    def place_order(self, symbol: str, side: str, volume: float) -> Dict[str, Any]:
        raise NotImplementedError("Exness MT5 integration not implemented yet")

    def get_positions(self) -> Dict[str, Any]:
        raise NotImplementedError("Exness MT5 integration not implemented yet")
