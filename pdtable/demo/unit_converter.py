"""Demo unit conversion"""
from typing import Tuple, Union, Iterable


def convert_this(
    value, from_unit: str, to_unit: str = "...I guess you want base units"
) -> Tuple[Union[float, Iterable[float]], str]:
    """
    A simple unit converter that hasn't read a lot of books.

    This is an example of how the user could implement a unit converting function.
    Here we define a few unit conversions manually. But the user could also choose to just
    delegate this to some dedicated unit support package like 'pint' or 'unum' or whatever.
    As long as everything is wrapped in a function with the same signature as this one.

    Args:
        value:
            A number or array of numbers. Arrays must support math operators and functions
            operating on it element-wise.
        from_unit:
            Old unit
        to_unit:
            New unit to which to convert

    Returns:
        Number or array converted from old to new unit.

    """
    if to_unit == from_unit:
        # Null conversion. 
        return value, to_unit

    # Here are the base units of the non-base units that I know
    base_units = {"mm": "m", "C": "K", "g": "kg"}
    # Moreover, base units are, of course, their own base units
    base_units.update({bu: bu for bu in base_units.values()})

    if to_unit == "...I guess you want base units":
        if from_unit in base_units:
            to_unit = base_units[from_unit]
        else:
            raise KeyError(f"No base unit defined for this unit.", from_unit)

    requested_conversion = (from_unit, to_unit)
    available_conversions = {
        ("m", "mm"): lambda x: x * 1000,
        ("mm", "m"): lambda x: x / 1000,
        ("C", "K"): lambda x: x + 273.15,
        ("K", "C"): lambda x: x - 273.15,
        ("kg", "g"): lambda x: x * 1000,
        ("g", "kg"): lambda x: x / 1000,
    }
    if requested_conversion not in available_conversions:
        raise KeyError(f"I don't know how to convert from '{from_unit}' to '{to_unit}'")

    return available_conversions[requested_conversion](value), to_unit
