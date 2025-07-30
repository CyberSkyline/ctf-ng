from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_ticket(source : LoaderType, input_key="ticket_id", output_key="ticket") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Ticket",
        input_key=input_key,
        output_key=output_key
    )
