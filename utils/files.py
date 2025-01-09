import os
import re
from typing import Tuple


def get_name_and_ext_from_path(path: str) -> Tuple[str, str]:
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    return name, ext

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    name, ext = get_name_and_ext_from_path(filename)
    pattern = r'[^a-zA-Z0-9_\- ]'
    sanitized = re.sub(pattern, '', name)
    sanitized = sanitized.replace(' ', '-')
    return sanitized + ext