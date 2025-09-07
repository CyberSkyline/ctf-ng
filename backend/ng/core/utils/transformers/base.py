from abc import ABCMeta, abstractmethod

class Success[T]:
    def __init__(self, value: T):
        self.value = value

class Failure:
    def __init__(self, message: str, **kwargs: str) -> None:
        self.message = message
        self.kwargs = kwargs

    def format_map(self, mapping: dict[str, str]) -> str:
        self.kwargs.update(mapping)
        return self.message.format_map(self.kwargs)

type Result[T, E] = Success[T] | E
type ValidatorResult[T] = Result[T, Failure]

# Validator base classes
class HasTransform[*T](metaclass=ABCMeta):
    @abstractmethod
    def transform(self, *args: *T) -> ValidatorResult[T]: ...

