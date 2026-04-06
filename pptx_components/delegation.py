from __future__ import annotations


class GetAttr:
    """Minimal attribute delegation mixin inspired by fastcore.GetAttr.

    Subclasses set `_default` to the attribute name holding the delegate object.
    Missing attributes are looked up on that delegate object.
    """

    _default: str = ""

    def _default_obj(self):
        if not self._default:
            raise AttributeError(f"{self.__class__.__name__} has no delegate target")
        return object.__getattribute__(self, self._default)

    def __getattr__(self, key: str):
        # Called only when normal lookup fails.
        if key.startswith("__"):
            raise AttributeError(key)

        target = self._default_obj()
        try:
            return getattr(target, key)
        except AttributeError as exc:
            raise AttributeError(f"{self.__class__.__name__!s} has no attribute {key!r}") from exc


def get_first_attr(obj, *names: str, default=None):
    """Return the first existing attribute value from *names* on *obj*."""
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default
