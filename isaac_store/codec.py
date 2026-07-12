"""Plain-data codec: any Isaac state <-> JSON-safe structures.

The keep-every-measurement guarantee lives here: encoding must be
COMPLETE (every attribute survives) and LOUD (anything it cannot
faithfully encode raises CodecError with the exact path — never a
silent drop).

Every real dict is encoded in wrapped form {"__t": "dict", ...} so a
plain JSON object in the output is always one of our type markers —
no ambiguity, keys of any hashable type survive.

Shared and cyclic structure survives: mutable containers (dict,
defaultdict, obj) carry an "oid" on first encounter; later encounters
encode as {"__t": "ref"}. Decode registers each oid before filling
children, so cycles and aliasing rebuild exactly.
"""
import base64
import json
import types

from collections import defaultdict

try:
    import numpy as np
except ImportError:  # storage layer itself has no hard numpy need
    np = None

_MODULES = {}  # canonical name -> module, for class/function resolution
_ALIASES = {}  # runtime module __name__ -> canonical name


def register_module(mod, as_name=None):
    """Register a module for encode/decode. as_name pins the CANONICAL
    name written into files, so a mind saved while the engine ran as
    __main__ still decodes where the engine is imported as 'isaac'."""
    name = as_name or mod.__name__
    _MODULES[name] = mod
    _ALIASES[mod.__name__] = name


class CodecError(Exception):
    pass


_DD_FACTORIES = {"set": set, "dict": dict, "int": int, "list": list, "float": float}


def _factory_name(f):
    for name, fac in _DD_FACTORIES.items():
        if f is fac:
            return name
    return None


class _Encoder:
    def __init__(self):
        self.memo = {}      # id(x) -> oid, for dict/defaultdict/obj
        self.next_oid = 0
        self.in_stack = set()  # id()s of lists currently being encoded

    def _oid_for(self, x):
        oid = self.next_oid
        self.memo[id(x)] = oid
        self.next_oid += 1
        return oid

    def enc(self, x, path="$"):
        if x is None or isinstance(x, (bool, int, str, float)):
            return x  # json emits NaN/Infinity; json.loads reads them back
        if isinstance(x, bytes):
            return {"__t": "bytes", "b64": base64.b64encode(x).decode("ascii")}
        if id(x) in self.memo:
            return {"__t": "ref", "oid": self.memo[id(x)]}
        if isinstance(x, list):
            if id(x) in self.in_stack:
                raise CodecError(f"{path}: cycle through a bare list — wrap it in an object")
            self.in_stack.add(id(x))
            try:
                return [self.enc(v, f"{path}[{i}]") for i, v in enumerate(x)]
            finally:
                self.in_stack.discard(id(x))
        if isinstance(x, tuple):
            return {"__t": "tup", "items": [self.enc(v, f"{path}[{i}]") for i, v in enumerate(x)]}
        if isinstance(x, (set, frozenset)):
            items = [self.enc(v, f"{path}{{}}") for v in x]
            items.sort(key=lambda e: json.dumps(e, sort_keys=True))
            return {"__t": "fset" if isinstance(x, frozenset) else "set", "items": items}
        if isinstance(x, defaultdict):
            fac = _factory_name(x.default_factory)
            if fac is None and x.default_factory is not None:
                raise CodecError(f"{path}: defaultdict with unknown factory {x.default_factory!r}")
            oid = self._oid_for(x)
            return {"__t": "dd", "oid": oid, "f": fac,
                    "items": [[self.enc(k, f"{path}.key"), self.enc(v, f"{path}[{k!r}]")]
                              for k, v in x.items()]}
        if isinstance(x, dict):
            oid = self._oid_for(x)
            return {"__t": "dict", "oid": oid,
                    "items": [[self.enc(k, f"{path}.key"), self.enc(v, f"{path}[{k!r}]")]
                              for k, v in x.items()]}
        if np is not None:
            if isinstance(x, np.ndarray):
                a = np.ascontiguousarray(x)
                return {"__t": "nd", "dt": str(a.dtype), "sh": list(a.shape),
                        "b64": base64.b64encode(a.tobytes()).decode("ascii")}
            if isinstance(x, np.generic):
                return {"__t": "npv", "dt": str(x.dtype), "v": x.item()}
        # module-level function or class: stored by qualified name
        if isinstance(x, (types.FunctionType, types.BuiltinFunctionType,
                          types.MethodType, type)):
            qn = getattr(x, "__qualname__", "")
            mod = _ALIASES.get(getattr(x, "__module__", None))
            if mod is not None and "<lambda>" not in qn and "<locals>" not in qn \
                    and not isinstance(x, types.MethodType):
                return {"__t": "fn", "mod": mod, "qn": qn}
            raise CodecError(f"{path}: cannot encode callable {x!r} "
                             f"(lambda/closure/bound method, or module not registered)")
        # generic object with instance state (incl. callable instances)
        if hasattr(x, "__dict__"):
            cls = type(x)
            mod = _ALIASES.get(cls.__module__)
            if mod is None:
                raise CodecError(f"{path}: object of unregistered class "
                                 f"{cls.__module__}.{cls.__qualname__}")
            oid = self._oid_for(x)
            return {"__t": "obj", "oid": oid, "mod": mod, "cls": cls.__qualname__,
                    "d": self.enc(dict(x.__dict__), f"{path}.<{cls.__qualname__}>")}
        raise CodecError(f"{path}: cannot encode {type(x).__name__}: {x!r}")


def _resolve(mod, qualname):
    if mod not in _MODULES:
        raise CodecError(f"module {mod!r} not registered for decode")
    obj = _MODULES[mod]
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


class _Decoder:
    def __init__(self):
        self.memo = {}  # oid -> live object

    def dec(self, x):
        if x is None or isinstance(x, (bool, int, float, str)):
            return x
        if isinstance(x, list):
            return [self.dec(v) for v in x]
        t = x["__t"]
        if t == "ref":
            return self.memo[x["oid"]]
        if t == "bytes":
            return base64.b64decode(x["b64"])
        if t == "tup":
            return tuple(self.dec(v) for v in x["items"])
        if t == "set":
            return set(self.dec(v) for v in x["items"])
        if t == "fset":
            return frozenset(self.dec(v) for v in x["items"])
        if t == "dd":
            d = defaultdict(_DD_FACTORIES.get(x["f"]))
            self.memo[x["oid"]] = d
            for k, v in x["items"]:
                d[self.dec(k)] = self.dec(v)
            return d
        if t == "dict":
            d = {}
            self.memo[x["oid"]] = d
            for k, v in x["items"]:
                d[self.dec(k)] = self.dec(v)
            return d
        if t == "nd":
            a = np.frombuffer(base64.b64decode(x["b64"]), dtype=np.dtype(x["dt"]))
            return a.reshape(x["sh"]).copy()
        if t == "npv":
            return np.dtype(x["dt"]).type(x["v"])
        if t == "fn":
            return _resolve(x["mod"], x["qn"])
        if t == "obj":
            cls = _resolve(x["mod"], x["cls"])
            inst = cls.__new__(cls)
            self.memo[x["oid"]] = inst
            inst.__dict__.update(self.dec(x["d"]))
            return inst
        raise CodecError(f"unknown type tag {t!r}")


def enc(x, path="$"):
    return _Encoder().enc(x, path)


def dec(x):
    return _Decoder().dec(x)
