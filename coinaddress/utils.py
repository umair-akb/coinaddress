import typing
from binascii import hexlify

from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from ecdsa.keys import VerifyingKey
from ecdsa.numbertheory import square_root_mod_prime


def int_to_hex(x: int, size) -> bytes:
    """Encode a long value as a hex string, 0-padding to size.

    Note that size is the size of the resulting hex string. So, for a 32Byte
    long size should be 64 (two hex characters per byte"."""
    f_str = "{0:0%sx}" % size
    return f_str.format(x).lower().encode()


def verifying_key_from_hex(key: bytes) -> VerifyingKey:
    """Load the VerifyingKey from a compressed or uncompressed hex public key."""
    id_byte = key[0]
    if not isinstance(id_byte, int):
        id_byte = ord(id_byte)

    if id_byte == 4:
        # Uncompressed public point
        # 1B ID + 32B x coord + 32B y coord = 65 B
        if len(key) != 65:
            raise Exception("Invalid key length")
        return create_verifying_key(
            int(hexlify(key[1:33]), 16), int(hexlify(key[33:]), 16)
        )
    elif id_byte in [2, 3]:
        # Compressed public point
        if len(key) != 33:
            raise Exception("Invalid key length")

        y_odd = bool(id_byte & 0x01)  # 0 even, 1 odd
        x = int(hexlify(key[1:]), 16)
        # The following x-to-pair algorithm was lifted from pycoin
        # I still need to sit down an understand it. It is also described
        # in http://www.secg.org/collateral/sec1_final.pdf
        curve = SECP256k1.curve
        p = curve.p()
        # For SECP256k1, curve.a() is 0 and curve.b() is 7, so this is
        # effectively (x ** 3 + 7) % p, but the full equation is kept
        # for just-in-case-the-curve-is-broken future-proofing
        alpha = (pow(x, 3, p) + curve.a() * x + curve.b()) % p
        beta = square_root_mod_prime(alpha, p)
        y_even = not y_odd

        if y_even == bool(beta & 1):
            return create_verifying_key(x, p - beta)
        else:
            return create_verifying_key(x, beta)

    raise Exception("The given key is not in a known format.")


def create_verifying_key(x: int, y: int) -> VerifyingKey:
    point = Point(SECP256k1.curve, x, y)
    return VerifyingKey.from_public_point(point, curve=SECP256k1)


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


__all__: typing.Final[typing.List[str]] = [
    "int_to_hex",
    "verifying_key_from_hex",
    "create_verifying_key",
    "to_bytes",
]
