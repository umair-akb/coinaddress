from coinaddress.networks.base import BaseNetwork
from coinaddress.networks.registry import registry


@registry.register("bitcoin", "BTC")
class Bitcoin(BaseNetwork):
    pass
