dumb dumb import-time attribute access checking for python.

Given `./test/example_imports.py`:

```
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
```

On running `./test/attr-check`, the following warnings will be printed to STDERR:


```
Import Warning: function 'attr_check.test.example_imports.dot_access' (line 23) will access non-existent attr 'not_gonna_happen' of <class 'example_imports.Coordinates'>
Import Warning: function 'attr_check.test.example_imports.dot_access' (line 22) will access non-existent attr 'no_way_jose' of <class 'example_imports.Coordinates'>
Import Warning: function 'attr_check.test.example_imports.dot_access' (line 17) will access non-existent attr 'nope' of <class 'example_imports.Coordinates'>
Import Warning: function 'attr_check.test.example_imports.dot_access' (line 15) will access non-existent attr 'abc' of <type 'list'>
Import Warning: function 'attr_check.test.example_imports.dot_access' (line 20) will access non-existent attr 'no_way' of <class 'example_imports.Coordinates'>
```
