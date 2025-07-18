import inspect
import sys

from util.authUtil import create_access_token, examine_password, get_password_hash, verify_password, verify_token
from util.log import log, log_clean, log_init


def auto_export(module_name: str = None):
    module_name = sys._getframe(1).f_globals.get('__name__') if module_name is None else module_name
    module = sys.modules[module_name]
    names = []

    for name, obj in vars(module).items():
        if name.startswith('_') or name == auto_export.__name__:
            continue
        if inspect.isfunction(obj) or inspect.isclass(obj):
            names.append(name)
        else:
            if not inspect.ismodule(obj):
                names.append(name)
    return names


__all__ = [auto_export]
__all__ += auto_export(__name__)
