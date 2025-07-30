from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_ticket_tag(source : LoaderType, input_key="ticket_tag_id", output_key="ticket_tag") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="TicketTag",
        input_key=input_key,
        output_key=output_key
    )
