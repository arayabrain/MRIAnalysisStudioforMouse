import re


def camel_to_snake(name, is_plural=False):
    """Convert camel string to snake string

    Args:
        name (_type_): An string
        is_plural (bool, optional):plural or singular. Defaults to False.

    Returns:
        _type_: snake string
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    return f'{name}s' if is_plural else name
