import binascii
import hashlib
import typing

from coinaddress import keys, networks, bech32
from coinaddress.networks.registry import registry


HRP: typing.Final[str] = "bc"
WITVER: typing.Final[int] = 0


@registry.register("bitcoin_bech32", "BTC-bech32")
class BitcoinBech32(networks.BaseNetwork):
    def public_key_to_address(self, node: keys.PublicKey) -> typing.Optional[str]:
        key = binascii.unhexlify(node.hex())
        rh = hashlib.new("ripemd160", hashlib.sha256(key).digest()).digest()
        return bech32.encode(HRP, WITVER, rh) 


__all__: typing.Final[typing.List[str]] = ["HRP", "WITVER", "BitcoinBech32"]
