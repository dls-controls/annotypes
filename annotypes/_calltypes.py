import inspect
import re
import tokenize
from collections import OrderedDict

from ._anno import Anno, NO_DEFAULT, make_repr, anno_with_default
from ._compat import add_metaclass, getargspec
from ._typing import TYPE_CHECKING, GenericMeta, Any

if TYPE_CHECKING:  # pragma: no cover
    from typing import Dict, Callable, Any, Tuple, List

type_re = re.compile('^# type: ([^-]*)( -> (.*))?$')


class CallTypesMeta(GenericMeta):
    def __init__(cls, name, bases, dct, **kwargs):
        f = dct.get('__init__', None)
        if f:
            cls.call_types, _ = make_call_types(f, f.func_globals)
        else:
            cls.call_types = OrderedDict()
        cls.return_type = Anno("Class instance", typ=cls, name="Instance")
        super(CallTypesMeta, cls).__init__(name, bases, dct)


@add_metaclass(CallTypesMeta)
class WithCallTypes(object):
    call_types = None  # type: Dict[str, Anno]
    return_type = None  # type: Anno

    def __repr__(self):
        repr_str = make_repr(self, self.call_types)
        return repr_str


def add_call_types(f):
    f.call_types, f.return_type = make_call_types(f, f.func_globals)
    return f


def make_call_types(f, globals_d):
    # type: (Callable, Dict) -> Tuple[Dict[str, Anno], Anno]
    """Make a call_types dictionary that describes what arguments to pass to f

    Args:
        f: The function to inspect for argument names (without self)
        globals_d: A dictionary of globals to lookup annotation definitions in
    """
    arg_spec = getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]

    defaults = {}  # type: Dict[str, Any]
    if arg_spec.defaults:
        default_args = args[-len(arg_spec.defaults):]
        for a, default in zip(default_args, arg_spec.defaults):
            defaults[a] = default

    if not getattr(f, "__annotations__", None):
        # Make string annotations from the type comment if there is one
        annotations = make_annotations(f, globals_d)
    else:
        annotations = f.__annotations__

    call_types = OrderedDict()  # type: Dict[str, Anno]
    for a in args:
        anno = anno_with_default(annotations[a], defaults.get(a, NO_DEFAULT))
        assert isinstance(anno, Anno), \
            "Argument %r has type %r which is not an Anno" % (a, anno)
        call_types[a] = anno

    return_type = anno_with_default(annotations.get("return", None))
    if return_type is Any:
        return_type = Anno("Any return value", Any, "return")
    assert return_type is None or isinstance(return_type, Anno), \
        "Return has type %r which is not an Anno" % (return_type,)

    return call_types, return_type


def make_annotations(f, globals_d):
    # type: (Callable, Dict) -> Dict[str, Any]
    """Create an annotations dictionary from Python2 type comments

    http://mypy.readthedocs.io/en/latest/python2.html

    Args:
        f: The function to examine for type comments
        globals_d: The globals dictionary to get type idents from
    """
    lines, _ = inspect.getsourcelines(f)
    arg_spec = getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]
    if arg_spec.varargs is not None:
        args.append(arg_spec.varargs)
    if arg_spec.keywords is not None:
        args.append(arg_spec.keywords)
    it = iter(lines)
    types = []  # type: List
    for token in tokenize.generate_tokens(lambda: next(it)):
        typ, string, start, end, line = token
        if typ == tokenize.COMMENT:
            found = type_re.match(string)
            if found:
                parts = found.groups()
                # (...) is used to represent all the args so far
                if parts[0] != "(...)":
                    expr = parts[0].replace("*", "")
                    try:
                        ob = eval(expr, globals_d, {})
                    except Exception as e:
                        raise ValueError(
                            "Error evaluating %r: %s" % (expr, e))
                    if isinstance(ob, tuple):
                        # We got more than one argument
                        types += list(ob)
                    else:
                        # We got a single argument
                        types.append(ob)
                if parts[1]:
                    # Got a return, done
                    try:
                        ob = eval(parts[2], globals_d, {})
                    except Exception as e:
                        raise ValueError(
                            "Error evaluating %r: %s" % (parts[2], e))
                    assert len(args) == len(types), \
                        "Args %r Types %r length mismatch" % (args, types)
                    ret = dict(zip(args, types))
                    ret["return"] = ob
                    return ret
    raise ValueError("Got to the end of the function without seeing ->")
