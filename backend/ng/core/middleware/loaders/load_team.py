from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_team(source : LoaderType, input_key="team_id", output_key="team") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Team",
        input_key=input_key,
        output_key=output_key
    )
