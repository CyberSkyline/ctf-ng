from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_attempt(source : LoaderType, input_key="attempt_id", output_key="attempt") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Attempt",
        input_key=input_key,
        output_key=output_key
    )
