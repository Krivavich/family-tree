from threading import local
from typing import Any, Optional

_state = local()


def set_current_user(user: Any) -> None:
    _state.user = user


def get_current_user() -> Optional[Any]:
    return getattr(_state, "user", None)
