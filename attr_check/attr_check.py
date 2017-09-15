import ast
from functools import wraps


def obj_to_ast_and_module_name(obj):
    func_code = obj.__code__
    filename = func_code.co_filename
    lineno = func_code.co_firstlineno
    if hasattr(obj, '_co_firstlineno'):  # provided from _checker_wrapper
        lineno = obj._co_firstlineno
    if hasattr(obj, '_co_filename'):
        filename = obj._co_filename
    module_name = filename.replace('/', '.')[:-3]  # approximately
    with open(filename, 'r') as f:
        file_str = f.read()

    tree = ast.parse(file_str, filename=filename)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.lineno == lineno:
                return node, module_name

    raise ReferenceError("couldn't see {}.{} at line {}".format(
        module_name, obj, lineno))


class CheckException(ImportError):
    def __init__(self, module_name, func_name, lineno, attr, class_):
        self._module_name = module_name
        self._func_name = func_name
        self._lineno = lineno
        self._attr = attr
        self._class = class_
        message = ("Import Warning: function '{}.{}' (line {}) will access "
                   "non-existent attr '{}' of {}")
        super(CheckException, self).__init__(message.format(
            module_name, func_name, lineno, attr, class_))


def walker(f, node_checker):
    tree, module_name = obj_to_ast_and_module_name(f)
    for node in ast.walk(tree):
        for class_, attr in node_checker(node):
            yield CheckException(
                module_name, f.func_name, node.lineno, attr, class_)


def attr_check(node, name_to_class):
    if isinstance(node, ast.Attribute):
        attr = None
        try:
            instance_name = node.value.id
            class_ = name_to_class[instance_name]
            attr = node.attr
        except (AttributeError, KeyError):
            pass

        if attr is not None and attr not in dir(class_):
            yield class_, attr


def kwarg_check(node, call_to_class):
    if isinstance(node, ast.Call):
        for call_name, class_ in call_to_class.iteritems():
            split = call_name.split('.')
            is_match = False
            parts = []
            try:
                current = node.func
                for _ in range(len(split) - 1):
                    parts.append(current.attr)
                    current = current.value
                parts.append(current.id)
                is_match = parts[::-1] == split
            except AttributeError:
                pass

            if is_match:
                for attr in [kw.arg for kw in node.keywords]:
                    if attr not in dir(class_):
                        yield class_, attr


def _checker_wrapper(function_checker):
    def outer(f):
        if not hasattr(f, '_function_checkers'):
            f._function_checkers = []
        f._function_checkers.append(lambda: function_checker(f))

        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        # add properties for stacked decorators
        if hasattr(f, '_co_firstlineno'):
            inner._co_firstlineno = f._co_firstlineno
            inner._co_filename = f._co_filename
        else:
            inner._co_firstlineno = f.__code__.co_firstlineno
            inner._co_filename = f.__code__.co_filename

        return inner
    return outer


def attr_checker(**name_to_class):
    def function_checker(f):
        return walker(f, lambda node: attr_check(node, name_to_class))

    return _checker_wrapper(function_checker)


def kwarg_checker(_call_to_class):
    if not isinstance(_call_to_class, dict):
        _call_to_class = {_call_to_class.__name__: _call_to_class}

    def function_checker(f):
        return walker(f, lambda node: kwarg_check(node, _call_to_class))

    return _checker_wrapper(function_checker)


def yield_exceptions(*modules):
    for module_ in modules:
        for module_attr in dir(module_):
            thing = getattr(module_, module_attr)
            if hasattr(thing, '_function_checkers'):
                for _function_checker in thing._function_checkers:
                    for exception in _function_checker():
                        yield exception
