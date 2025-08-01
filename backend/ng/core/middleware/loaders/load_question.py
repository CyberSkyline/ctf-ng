from collections.abc import Callable
from ._util import LoaderType, generate_loader_decorator


def load_question(source: LoaderType, input_key="question_id", output_key="question") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="Question",
        input_key=input_key,
        output_key=output_key
    )
