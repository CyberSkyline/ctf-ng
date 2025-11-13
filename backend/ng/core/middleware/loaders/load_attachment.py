from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_attachment(source: LoaderType, input_key="attachment_id", output_key="attachment") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="TicketAttachment",
        input_key=input_key,
        output_key=output_key
    )