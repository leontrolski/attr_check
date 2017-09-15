from attr import attrs, attrib
from attr_check import attr_checker, kwarg_checker


@attrs
class Coordinates(object):
    x = attrib()
    y = attrib()


@attr_checker(l=list, coord=Coordinates, coordinate=Coordinates)
@kwarg_checker(Coordinates)
@kwarg_checker({'some.name.space.Coordinates': Coordinates})
def dot_access():
    l.abc()
    coordinate.x = 42
    coordinate.nope = 42

    for coord in some_coordinates:
        coord.no_way = 42

    Coordinates(no_way_jose=42)
    some.name.space.Coordinates(not_gonna_happen=42)
