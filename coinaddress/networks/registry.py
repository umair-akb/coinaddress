import typing

from coinaddress.networks.base import BaseNetwork


class Registry:
    def __init__(self):
        self.__networks: typing.Dict[str, BaseNetwork] = {}

    def register(self, *names: str):
        def wrapper(cls: typing.Type[BaseNetwork]):
            inst = cls()
            for n in names:
                self.__networks[n] = inst

            return cls

        return wrapper

    def get(
        self, name: str, default: typing.Optional[BaseNetwork] = None
    ) -> typing.Optional[BaseNetwork]:
        return self.__networks.get(name, default)


registry: typing.Final[Registry] = Registry()


__all__: typing.Final[typing.List[str]] = ["registry", "Registry"]
