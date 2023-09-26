from typing import Any, Callable, Generic, TypeVar

TK = TypeVar("TK")
TV = TypeVar("TV")
TR = TypeVar("TR")
TEffect = Callable[[Any], TR]


class FunctionRegistry(Generic[TK, TV, TR]):
    def __init__(self, factory: Callable[[TEffect], TV]):
        self.registry: dict[TK, TV] = {}
        self.factory = factory

    def register(
        self,
        key: TK,
        **kwargs: Any,
    ) -> Callable[[TEffect], TEffect]:
        def wrapper(f: TEffect) -> TEffect:
            self.registry[key] = self.factory(f, **kwargs)
            return f

        return wrapper

    def get(self, key: TK) -> TV:
        return self.registry[key]
