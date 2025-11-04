from collections.abc import Callable
from ._util import generate_loader_decorator, LoaderType

def load_file_upload(source: LoaderType, input_key="file_upload_id", output_key="file_upload") -> Callable:
    return generate_loader_decorator(
        source=source,
        model_name="FileUpload",
        input_key=input_key,
        output_key=output_key
    )