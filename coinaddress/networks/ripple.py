import hashlib
import typing
from binascii import hexlify

from coinaddress.keys import PublicKey
from coinaddress.networks.base import BaseNetwork
from coinaddress.networks.registry import registry


def get_ripple_from_pubkey(pubkey: bytes) -> str:
    """Given a public key, determine the Ripple address."""
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(hashlib.sha256(pubkey).digest())

    return RippleBaseDecoder.encode(ripemd160.digest())


def to_bytes(
    number: int, length: typing.Optional[int] = None, endianess: str = "big"
) -> bytes:
    """Will take an integer and serialize it to a string of bytes.
    Python 3 has this, this is originally a backport to Python 2, from:
        http://stackoverflow.com/a/16022710/15677
    We use it for Python 3 as well, because Python 3's builtin version
    needs to be given an explicit length, which means our base decoder
    API would have to ask for an explicit length, which just isn't as nice.
    Alternative implementation here:
       https://github.com/nederhoed/python-bitcoinaddress/blob/c3db56f0a2d4b2a069198e2db22b7f607158518c/bitcoinaddress/__init__.py#L26
    """
    h = hex(number)
    s = "0" * (len(h) % 2) + h
    if length:
        if len(s) > length * 2:
            raise ValueError("Length too large for {} bytes".format(length))

        s = s.zfill(length * 2)

    s = bytes.fromhex(s)
    return s if endianess == "big" else s[::-1]


@registry.register("ripple", "XRP")
class Ripple(BaseNetwork):
    def public_key_to_address(self, node: PublicKey):
        return get_ripple_from_pubkey(bytes.fromhex(node.hex().decode()))


class RippleBaseDecoder(object):
    """Decodes Ripple's base58 alphabet.
    This is what ripple-lib does in ``base.js``.
    """

    alphabet: typing.ClassVar[
        str
    ] = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"
    version: typing.ClassVar[bytes] = b"\x00"

    @classmethod
    def decode(cls, encoded: str, pad_length: typing.Optional[int] = None):
        """Apply base58 decode, verify checksum, return payload."""
        decoded = cls.decode_base(encoded, pad_length)
        assert cls.verify_checksum(decoded)

        # 1 -> remove first byte, a version number
        # -4 -> remove the checksum
        return decoded[1:-4]

    @classmethod
    def decode_base(cls, encoded: str, pad_length: typing.Optional[int] = None):
        """Decode a base encoded string with the Ripple alphabet."""
        n = 0
        base = len(cls.alphabet)
        for char in encoded:
            n = n * base + cls.alphabet.index(char)

        return to_bytes(n, pad_length, "big")

    @classmethod
    def verify_checksum(cls, bytes_: bytes) -> bool:
        """These ripple byte sequences have a checksum builtin."""
        calculated = hashlib.sha256(hashlib.sha256(bytes_[:-4]).digest())
        valid = bytes_[-4:] == calculated.digest()[:4]

        return valid

    @staticmethod
    def as_ints(bytes_: str) -> typing.List[int]:
        return [ord(c) for c in bytes_]

    @classmethod
    def encode(cls, data: bytes) -> str:
        """Apply base58 encode including version, checksum."""
        bytes_ = cls.version + data
        # checksum
        bytes_ += hashlib.sha256(hashlib.sha256(bytes_).digest()).digest()[:4]
        return cls.encode_base(bytes_)

    @classmethod
    def encode_base(cls, data: bytes) -> str:
        # https://github.com/jgarzik/python-bitcoinlib/blob/master/bitcoin/base58.py  # noqa
        # Convert big-endian bytes to integer
        n = int(hexlify(data).decode(), 16)

        # Divide that integer into base58
        res = []
        while n > 0:
            n, r = divmod(n, len(cls.alphabet))
            res.append(cls.alphabet[r])

        res = "".join(res[::-1])
        # Encode leading zeros as base58 zeros
        pad = data.find(0)

        return cls.alphabet[0] * pad + res


__all__: typing.Final[typing.List[str]] = [
    "get_ripple_from_pubkey",
    "to_bytes",
    "RippleBaseDecoder",
    "Ripple",
]
