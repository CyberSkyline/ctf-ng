from collections.abc import Callable

from ._util import LoaderType, generate_loader_decorator


def load_challenge(source: LoaderType, input_key="challenge_id", output_key="challenge") -> Callable:
    return generate_loader_decorator(source=source, model_name="Challenge", input_key=input_key, output_key=output_key)
