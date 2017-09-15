import attr_check
import example_imports


def test_checkers():
    attrs = set(e._attr for e in attr_check.yield_exceptions(example_imports))
    assert attrs == {'abc', 'no_way_jose', 'not_gonna_happen', 'no_way', 'nope'}
