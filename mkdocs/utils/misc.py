from typing import MutableMapping


def dict_merge_inplace(original: MutableMapping, extra: MutableMapping) -> MutableMapping:
    """Merge `extra` to `original` in place recursively, without overriding and deep copy."""
    for key in extra:
        if isinstance(original.get(key), MutableMapping) and isinstance(extra[key], MutableMapping):
            dict_merge_inplace(original[key], extra[key])
        elif key not in original:
            original[key] = extra[key]

    return original
