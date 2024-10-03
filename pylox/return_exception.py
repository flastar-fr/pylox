from typing import Any


class Return(RuntimeError):
    def __init__(self, value: Any):
        super().__init__(None, None, False, False)
        self.value = value
