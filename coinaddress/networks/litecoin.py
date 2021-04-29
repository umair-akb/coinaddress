import typing

from coinaddress.networks.base import BaseNetwork
from coinaddress.networks.registry import registry


@registry.register("litecoin", "LTC")
class Litecoin(BaseNetwork):
    pubkey_address_prefix: typing.ClassVar[int] = 0x30
