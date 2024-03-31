def ceil_div(a:float, b:float) -> int:
    """Returns the ceiling of a / b.

    Args:
        a (float): ...
        b (float): ...

    Returns:
        int: ...
    """
    return -(a // -b)