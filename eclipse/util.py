def ceil_div(a:float, b:float) -> int:
    """Returns the ceiling of a / b.

    Args:
        a (float): ...
        b (float): ...

    Returns:
        int: ...
    """
    return -(a // -b)

def clamp(n:float, a:float, b:float) -> float:
    """Clamps n between a and b.

    Args:
        n (float): Number to clamp.
        a (float): Min value.
        b (float): Max value.

    Returns:
        float: The clamped value.
    """
    return min(b, max(a, n))