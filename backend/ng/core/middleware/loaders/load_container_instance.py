from typing import Callable
from ._util import generate_loader_decorator, LoaderType

def load_container_instance(source : LoaderType, input_key="container_instance_id", output_key="container_instance") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="ContainerInstance",
        input_key=input_key,
        output_key=output_key
    )
