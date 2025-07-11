from typing import Callable
from ._util import generate_loader_decorator, LoaderType



def load_role(source : LoaderType, input_key="role_id", output_key="role") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Role",
        input_key=input_key,
        output_key=output_key
    )
