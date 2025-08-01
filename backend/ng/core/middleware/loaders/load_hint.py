from collections.abc import Callable
from ._util import LoaderType, generate_loader_decorator


def load_hint(source: LoaderType, input_key="hint_id", output_key="hint") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Hint",
        input_key=input_key,
        output_key=output_key
    )
