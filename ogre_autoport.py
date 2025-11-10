# ogre_autoport.py
from pathlib import Path
import traceback

# Import the model porter library from the embedded subpackage
from .bzrmodelporter import port_models
from .bzrmodelporter.bzportmodels import port_bwd2, port_geo


def _load_config_for_porter():
    """
    Mimic port_models.py's config.cfg behavior:
      - First line: path to .act palette
      - Subsequent lines: resource search directories
    """
    script_dir = Path(port_models.__file__).parent
    config_path = script_dir / "config.cfg"

    resource_dir_list = []
    act_path = None

    try:
        with open(config_path, 'rt') as stream:
            first = stream.readline().rstrip("\n")
            if first:
                act_path = Path(first)
            for line in stream:
                line = line.rstrip("\n")
                if line:
                    resource_dir_list.append(Path(line))
    except OSError:
        # No config; that's fine – the porter will still work for non-indexed .map
        pass

    return act_path, resource_dir_list


def auto_port_bz98_to_ogre(exported_path: str):
    """
    Called by the Blender exporters after a successful VDF/SDF/GEO export.

    Will emit:
      - <name>.mesh
      - <name>.skeleton
      - <name>_port.material
      - <name>_port_D.dds textures (etc.)
    into the same directory as exported_path.
    """
    filepath = Path(exported_path)
    ext = filepath.suffix.lower()

    if ext not in {".vdf", ".sdf", ".geo"}:
        print(f"[bz98tools] Ogre auto-port: skipping unsupported type {ext}")
        return {'CANCELLED'}

    act_path, resource_dir_list = _load_config_for_porter()

    asset_resolver = port_models.AssetResolver(
        input_dirpath=filepath.parent,
        dest_dirpath=filepath.parent,
        resource_dir_list=resource_dir_list,
        act_path=act_path,
    )

    settings = port_models.SettingsController(
        name=None,              # fall back to stem inside port_bwd2/port_geo
        suffix="_port",         # matches CLI default, e.g. mytank_port.material
        headlights=False,
        person=None,
        turret=None,
        cockpit=None,
        skeletalanims=None,
        scope=port_models.ScopeSettings(),
        no_pov_rots=False,
        flat_colors=False,
        boundingbox_scale_factors=None,
        nowrite=False,
        verbose=False,
    )

    print(f"[bz98tools] Ogre auto-port: {filepath.name}")

    try:
        if ext in {".vdf", ".sdf"}:
            # BWD2 (VDF/SDF) port
            port_bwd2(filepath, asset_resolver, settings)
        elif ext == ".geo":
            # GEO port
            port_geo(filepath, asset_resolver, settings)

    except Exception:
        print("[bz98tools] Ogre auto-port FAILED:")
        print(traceback.format_exc())
        return {'CANCELLED'}

    print("[bz98tools] Ogre auto-port complete.")
    return {'FINISHED'}
