import os
import warnings


def show_message(old: str, new: str) -> None:
    skip_deprecation = os.environ.get("SPARKAICLIENT_SKIP_DEPRECATION")  # for unit tests etc.
    if skip_deprecation:
        return

    message = (
        f"{old} package is deprecated. Please use {new} package instead. "
        "For more info, go to xfyun.cn"
    )
    warnings.warn(message)
