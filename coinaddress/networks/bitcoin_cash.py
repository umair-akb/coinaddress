import typing

from base58 import b58decode_check

from coinaddress.keys import PublicKey
from coinaddress.networks.base import BaseNetwork
from coinaddress.networks.registry import registry

CHARSET: typing.Final[str] = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
GENERATOR: typing.Final[typing.List[typing.Tuple[int, int]]] = [
    (0x01, 0x98F2BC8E61),
    (0x02, 0x79B76D99E2),
    (0x04, 0xF33E5FB3C4),
    (0x08, 0xAE2EABE2A8),
    (0x10, 0x1E4F43E470),
]


def b32encode(inputs: typing.Iterable[int]) -> str:
    return "".join(CHARSET[cc] for cc in inputs)


def polymod(values: typing.Iterable[int]) -> int:
    chk = 1
    for value in values:
        top = chk >> 35
        chk = ((chk & 0x07FFFFFFFF) << 5) ^ value
        for i in GENERATOR:
            if top & i[0] != 0:
                chk ^= i[1]

    return chk ^ 1


def prefix_expand(prefix: str) -> typing.List[int]:
    return [ord(x) & 0x1F for x in prefix] + [0]


def calculate_checksum(prefix: str, payload: typing.List[int]) -> typing.List[int]:
    poly = polymod(prefix_expand(prefix) + payload + [0, 0, 0, 0, 0, 0, 0, 0])
    return [poly >> 5 * (7 - i) & 0x1F for i in range(8)]


def convertbits(
    data: typing.Iterable[int], frombits: int, tobits: int, pad: bool = True
) -> typing.Optional[typing.List[int]]:
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1

    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)

    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None

    return ret


@registry.register("bitcoin_cash", "BCH")
class BitcoinCash(BaseNetwork):
    pubkey_address_prefix: typing.ClassVar[int] = 0x1C
    prefix: typing.ClassVar[str] = "bitcoincash"

    def public_key_to_address(self, public_key: PublicKey):
        version_int = 0

        pub_key = super().public_key_to_address(public_key)
        payload = list(b58decode_check(pub_key)[1:])

        payload = [version_int] + payload
        payload = convertbits(payload, 8, 5)
        if payload is None:
            raise RuntimeError("Invalid pubkey!")

        checksum = calculate_checksum(prefix, payload)

        return prefix + ":" + b32encode(payload + checksum)


__all__: typing.Final[typing.List[str]] = [
    "CHARSET",
    "GENERATOR",
    "b32encode",
    "polymod",
    "prefix_expand",
    "calculate_checksum",
    "convertbits",
    "BitcoinCash",
]
