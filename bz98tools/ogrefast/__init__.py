import importlib
import os
import platform
import sys

_VENDOR_ROOT = os.path.join(os.path.dirname(__file__), "vendor")
_NATIVE_ROOT = os.path.join(_VENDOR_ROOT, "kenshi_blender_tool")
_DLL_DIR_HANDLE = None
_PROBE_RESULT = None


def _prepare_native_import():
    global _DLL_DIR_HANDLE

    if _VENDOR_ROOT not in sys.path:
        sys.path.insert(0, _VENDOR_ROOT)

    if os.name == "nt" and os.path.isdir(_NATIVE_ROOT):
        if hasattr(os, "add_dll_directory"):
            if _DLL_DIR_HANDLE is None:
                _DLL_DIR_HANDLE = os.add_dll_directory(_NATIVE_ROOT)
        else:
            os.environ["PATH"] = _NATIVE_ROOT + os.pathsep + os.environ.get("PATH", "")


def probe_native_backend(force=False):
    global _PROBE_RESULT

    if _PROBE_RESULT is not None and not force:
        return _PROBE_RESULT

    if os.name != "nt":
        _PROBE_RESULT = (False, "native Ogre backend is currently bundled for Windows only")
        return _PROBE_RESULT

    if platform.machine().lower() not in {"amd64", "x86_64"}:
        _PROBE_RESULT = (False, "native Ogre backend requires a 64-bit Python runtime")
        return _PROBE_RESULT

    if sys.version_info[:2] != (3, 11):
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        _PROBE_RESULT = (False, f"native Ogre backend requires Python 3.11, found {version}")
        return _PROBE_RESULT

    try:
        importlib.import_module("numpy")
    except Exception as exc:
        _PROBE_RESULT = (False, f"numpy is unavailable: {exc}")
        return _PROBE_RESULT

    try:
        _prepare_native_import()
        importlib.import_module("kenshi_blender_tool")
        _PROBE_RESULT = (True, None)
    except Exception as exc:
        _PROBE_RESULT = (False, str(exc))

    return _PROBE_RESULT
