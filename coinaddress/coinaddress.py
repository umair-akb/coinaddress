"""Main module."""
import typing

from coinaddress.networks import BaseNetwork, registry


def get_network(name: str) -> typing.Optional[BaseNetwork]:
    """Returns the registered network with the given name, None otherwise."""
    return registry.get(name)


def address_from_xpub(network: str, xpub: str, path: str = "0") -> str:
    """Get address derived from xpub."""
    return get_network(network).get_address(xpub=xpub, path=path)


__all__: typing.Final[typing.List[str]] = [
    "get_network",
    "address_from_xpub",
]
