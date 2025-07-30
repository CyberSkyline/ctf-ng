from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_user(source : LoaderType, input_key="user_id", output_key="user") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="User",
        input_key=input_key,
        output_key=output_key
    )
