"""Main module."""
import typing

from .networks import registry
from .networks.base import BaseNetwork


def get_network(name: str) -> typing.Optional[BaseNetwork]:
    """Returns the registered network with the given name, None otherwise.
    """
    return registry.get(name)


def address_from_xpub(network: str, xpub: str, path: str = "0") -> str:
    """Get address derived from xpub.
    """
    net = get_network(network)
    return net.get_address(xpub=xpub, path=path)


__all__: typing.Final[typing.List[str]] = [
        "get_network",
        "address_from_xpub",
]
