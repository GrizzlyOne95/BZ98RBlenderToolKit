from pathlib import Path
import traceback

from .bzrmodelporter import port_models
from .bzrmodelporter.bzportmodels import port_bwd2, port_geo


def _ternary_from_enum(val: str):
    """
    Map Blender enum values "AUTO"/"YES"/"NO" to the ternary expected by SettingsController:
      AUTO or empty -> None
      YES          -> True
      NO           -> False
    """
    if not val or val == 'AUTO':
        return None
    if val == 'YES':
        return True
    if val == 'NO':
        return False
    return None


def _load_config_for_porter(config_path_str, act_override_str):
    """
    Mimic the CLI config behaviour:

    - If config_path_str given, use that.
    - Otherwise, look for 'config.cfg' next to port_models.py.
    - First line: .act palette path (unless overridden by act_override_str)
    - Remaining non-empty lines: resource search directories.
    """
    script_dir = Path(port_models.__file__).parent
    config_path = Path(config_path_str) if config_path_str else (script_dir / "config.cfg")

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
        # No config; that's OK – caller may still give an explicit ACT path or rely on non-indexed maps
        pass

    if act_override_str:
        act_path = Path(act_override_str)

    return act_path, resource_dir_list


def auto_port_bz98_to_ogre(exported_path: str, options: dict | None = None):
    """
    Called by the Blender exporters after a successful VDF/SDF/GEO export.

    'options' is a dict coming from the Blender operator containing fields
    that correspond roughly to the CLI arguments in port_models.py.

    Common options (all file types):
      name, suffix, flat_colors, bounds_mult, act_path, config_path,
      only_once, nowrite, dest_dir

    VDF-only extras:
      headlights, person_mode, turret_mode, cockpit_mode, skeletalanims_mode,
      scope_mode, scope_type, scope_nation, scope_screen, scope_gun,
      scope_transform, scope_texture, no_pov_rots
    """
    options = options or {}
    filepath = Path(exported_path)
    ext = filepath.suffix.lower()

    if ext not in {".vdf", ".sdf", ".geo"}:
        print(f"[bz98tools] Ogre auto-port: skipping unsupported type {ext}")
        return {'CANCELLED'}

    # Destination directory
    dest_dir_str = options.get("dest_dir") or None
    dest_dirpath = Path(dest_dir_str) if dest_dir_str else filepath.parent

    # --onlyonce: skip if a mesh already exists in the destination
    if options.get("only_once"):
        mesh_path = dest_dirpath / (filepath.stem + ".mesh")
        if mesh_path.exists():
            print(f"[bz98tools] Ogre auto-port: skipping, mesh already exists and only-once is enabled: {mesh_path}")
            return {'CANCELLED'}

    # ACT / resource dirs via config (or override)
    act_path, resource_dir_list = _load_config_for_porter(
        options.get("config_path"),
        options.get("act_path"),
    )

    asset_resolver = port_models.AssetResolver(
        input_dirpath=filepath.parent,
        dest_dirpath=dest_dirpath,
        resource_dir_list=resource_dir_list,
        act_path=act_path,
    )

    # ----- SettingsController core fields -----

    name = (options.get("name") or None) or None
    suffix = options.get("suffix")
    if suffix is None or suffix == "":
        suffix = "_port"

    flat_colors = bool(options.get("flat_colors", False))
    nowrite = bool(options.get("nowrite", False))

    bounds_mult = options.get("bounds_mult")
    if isinstance(bounds_mult, (list, tuple)) and len(bounds_mult) == 3:
        boundingbox_scale_factors = tuple(float(x) for x in bounds_mult)
    else:
        boundingbox_scale_factors = None

    # VDF/person-only-ish settings (safe to pass even if not used)
    headlights = bool(options.get("headlights", False))
    no_pov_rots = bool(options.get("no_pov_rots", False))

    person = _ternary_from_enum(options.get("person_mode"))
    turret = _ternary_from_enum(options.get("turret_mode"))
    cockpit = _ternary_from_enum(options.get("cockpit_mode"))
    skeletalanims = _ternary_from_enum(options.get("skeletalanims_mode"))

    # ----- ScopeSettings -----
    scope_mode = _ternary_from_enum(options.get("scope_mode"))
    scope_type = (options.get("scope_type") or "AUTO").upper()

    scope_nation = options.get("scope_nation") or None

    scope_screen_vals = options.get("scope_screen")
    if isinstance(scope_screen_vals, (list, tuple)) and len(scope_screen_vals) == 5:
        scope_screen = tuple(float(x) for x in scope_screen_vals)
    else:
        scope_screen = None

    scope_gun = options.get("scope_gun") or None
    scope_texture = options.get("scope_texture") or None

    scope_transform_vals = options.get("scope_transform")
    if isinstance(scope_transform_vals, (list, tuple)) and len(scope_transform_vals) == 12:
        transform = port_models.Transform.from_array_rufp_xyz(
            [float(x) for x in scope_transform_vals]
        )
    else:
        transform = None

    scope_settings = port_models.ScopeSettings(
        scope=scope_mode,
        type=scope_type,
        nation=scope_nation,
        screen=scope_screen,
        gun_name=scope_gun,
        transform=transform,
        texture=scope_texture,
    )

    settings = port_models.SettingsController(
        name=name,
        suffix=suffix,
        headlights=headlights,
        person=person,
        turret=turret,
        cockpit=cockpit,
        skeletalanims=skeletalanims,
        scope=scope_settings,
        no_pov_rots=no_pov_rots,
        flat_colors=flat_colors,
        boundingbox_scale_factors=boundingbox_scale_factors,
        nowrite=nowrite,
        verbose=False,
    )

    print(f"[bz98tools] Ogre auto-port: {filepath.name}")

    try:
        if ext in {".vdf", ".sdf"}:
            port_bwd2(filepath, asset_resolver, settings)
        else:  # ".geo"
            port_geo(filepath, asset_resolver, settings)

    except Exception:
        print("[bz98tools] Ogre auto-port FAILED:")
        print(traceback.format_exc())
        return {'CANCELLED'}

    print("[bz98tools] Ogre auto-port complete.")
    return {'FINISHED'}
