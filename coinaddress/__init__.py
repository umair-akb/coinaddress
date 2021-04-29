"""Top-level package for coinaddress."""
import typing

__author__: typing.Final[str] = """Roman Tolkachyov"""
__email__: typing.Final[str] = "roman@tolkachyov.name"
__version__: typing.Final[str] = "0.1.1"

from .coinaddress import address_from_xpub

__all__: typing.Final[typing.List[str]] = ["address_from_xpub"]
