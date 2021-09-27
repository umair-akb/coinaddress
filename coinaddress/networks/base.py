import hashlib
import typing
from binascii import hexlify, unhexlify

import base58

from coinaddress.keys import PublicKey
from coinaddress.utils import verifying_key_from_hex


class BaseNetwork:
    pubkey_address_prefix: typing.ClassVar[int] = 0x00

    def get_address(self, xpub: str, path: str = "0") -> str:
        node = self.deserialize_xpub(xpub)
        child_node = node.get_child_from_path(path)

        return self.public_key_to_address(child_node)

    def public_key_to_address(self, node: PublicKey) -> str:
        key = unhexlify(node.hex())
        # First get the hash160 of the key
        rh = hashlib.new("ripemd160", hashlib.sha256(key).digest())
        hash160_bytes = rh.digest()
        # Prepend the network address byte
        network_hash160_bytes = bytes([self.pubkey_address_prefix]) + hash160_bytes

        # Return a base58 encoded address with a checksum
        return base58.b58encode_check(network_hash160_bytes).decode()

    def deserialize_xpub(self, key: str) -> PublicKey:
        """Load the ExtendedBip32Key from a hex key."""
        key = base58.b58decode_check(key.encode())
        chain_code, key_data = key[13:45], key[45:]

        point_type = key_data[0]
        if point_type in [2, 3, 4]:
            # Compressed public coordinates
            verifying_key = verifying_key_from_hex(key_data)
        else:
            raise ValueError("Invalid key_data prefix, got %s" % point_type)

        return PublicKey(
            chain_code=hexlify(chain_code),
            verifying_key=verifying_key,
        )

__all__: typing.Final[typing.List[str]] = ["BaseNetwork"]
