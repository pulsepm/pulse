import re
from typing import TypeVar

Url = TypeVar('Url', bound=str)


class UrlType(str):
    def __new__(cls, value: str) -> 'UrlType':
        if not re.compile(r'^(https?://)').match(value):
            raise ValueError('Invalid URL link specified')

        return super().__new__(cls, value)