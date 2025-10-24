from collections.abc import Callable
from ._util import LoaderType, generate_loader_decorator

def load_sponsor(source: LoaderType, input_key="sponsor_id", output_key="sponsor") -> Callable:
    """
    Load sponsor by ID from the request context.
    """
    return generate_loader_decorator(
        source=source,
        model_name="Sponsor",
        input_key=input_key,
        output_key=output_key,
    )