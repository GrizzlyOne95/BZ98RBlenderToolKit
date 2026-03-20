import os

INNER_COLLISION_NAMES = {
    "inner_col",
    "innercol",
    "inner_collision",
    "innercollision",
}

OUTER_COLLISION_NAMES = {
    "outer_col",
    "outercol",
    "outer_collision",
    "outercollision",
}

SEVERITY_ORDER = {
    "ERROR": 0,
    "WARNING": 1,
    "INFO": 2,
}


def fixgeoname(name, lod):
    geofilename = list(name)
    if len(geofilename) > 8:
        geofilename = geofilename[0:8]
    if lod in (1, 2, 3):
        geofilename[3] = str(lod)
    else:
        geofilename[3] = "3"
    geofilename[4] = "1"
    return "".join(geofilename)


def parse_legacy_geo_name(name):
    lower_name = (name or "").strip().lower()
    if len(lower_name) < 5:
        return {"valid": False, "reason": "too_short", "lod": None}
    if len(lower_name) > 8:
        return {"valid": False, "reason": "too_long", "lod": None}

    lod_char = lower_name[3]
    if lod_char not in {"1", "2", "3"}:
        return {"valid": False, "reason": "invalid_lod", "lod": None}

    return {"valid": True, "reason": None, "lod": int(lod_char)}


def is_collision_helper_name(name):
    lower_name = (name or "").strip().lower()
    return lower_name in INNER_COLLISION_NAMES or lower_name in OUTER_COLLISION_NAMES


def normalized_export_name(name, lod):
    return fixgeoname(name, lod).lower()


def issue_applies(issue, export_mode):
    export_modes = issue.get("export_modes", {"ALL"})
    return "ALL" in export_modes or export_mode in export_modes


def sort_issues(issues):
    return sorted(
        issues,
        key=lambda issue: (
            SEVERITY_ORDER.get(issue["severity"], 99),
            issue.get("target", "").lower(),
            issue.get("message", "").lower(),
        ),
    )


def collect_legacy_validation_issues(context, export_mode="ALL"):
    if export_mode == "GEO":
        return sort_issues(_collect_geo_export_issues(context))
    return sort_issues(_collect_scene_export_issues(context))


def _make_issue(
    severity,
    scope,
    target,
    message,
    export_modes=None,
    object_name="",
    action="",
):
    return {
        "severity": severity,
        "scope": scope,
        "target": target or "",
        "message": message,
        "export_modes": set(export_modes or {"ALL"}),
        "object_name": object_name or "",
        "action": action or "",
    }


def _derive_legacy_texture_name(name):
    base_name = os.path.splitext((name or "").strip())[0]
    base_name = base_name.replace(" ", "_").lower()
    return base_name[:8]


def _get_image_derived_texture_name(material):
    node_tree = getattr(material, "node_tree", None)
    if node_tree is None:
        return ""

    image_nodes = [
        node for node in getattr(node_tree, "nodes", [])
        if getattr(node, "type", "") == 'TEX_IMAGE' and getattr(node, "image", None) is not None
    ]
    if not image_nodes:
        return ""

    active_node = next((node for node in image_nodes if getattr(node, "select", False)), None)
    if active_node is None:
        active_node = image_nodes[0]

    image = active_node.image
    image_name = getattr(image, "name", "") or getattr(image, "filepath", "")
    return _derive_legacy_texture_name(image_name)


def _collect_geo_export_issues(context):
    issues = []
    view_layer = getattr(context, "view_layer", None)
    active_obj = getattr(getattr(view_layer, "objects", None), "active", None)

    if active_obj is None:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Scene",
                    "",
                    "No active object selected. GEO export requires an active mesh object.",
                    {"GEO"},
                    action="select_object",
                )
            )
        return issues

    if getattr(active_obj, "type", None) != "MESH" or getattr(active_obj, "data", None) is None:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    active_obj.name,
                    "Active object is not a mesh. GEO export only supports mesh objects.",
                    {"GEO"},
                    object_name=active_obj.name,
                    action="select_object",
                )
            )
        return issues

    if len(getattr(active_obj.data, "vertices", [])) == 0:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    active_obj.name,
                    "Active mesh has no vertices and cannot be exported as GEO.",
                    {"GEO"},
                    object_name=active_obj.name,
                    action="select_object",
                )
            )

    issues.extend(_collect_material_issues(active_obj, {"GEO"}))
    return issues


def _collect_scene_export_issues(context):
    scene = getattr(context, "scene", None)
    if scene is None:
        return [
            _make_issue(
                "ERROR",
                "Scene",
                "",
                "No active scene available for validation.",
                {"VDF", "SDF"},
            )
        ]

    issues = []
    named_candidates = []
    normalized_names = {}
    inner_helpers = []
    outer_helpers = []

    for obj in scene.objects:
        lower_name = obj.name.lower()
        if lower_name in INNER_COLLISION_NAMES:
            inner_helpers.append(obj)
        if lower_name in OUTER_COLLISION_NAMES:
            outer_helpers.append(obj)

        name_info = parse_legacy_geo_name(obj.name)
        geo_props = getattr(obj, "GEOPropertyGroup", None)
        is_spinner_helper = bool(getattr(geo_props, "IsSpinnerHelper", False))
        spinner_like = is_spinner_helper or (int(getattr(geo_props, "GEOType", 0)) == 15)

        if not name_info["valid"]:
            if _looks_like_export_candidate(obj, spinner_like):
                issues.append(
                    _make_issue(
                        "WARNING",
                        "Object",
                        obj.name,
                        _invalid_name_message(name_info["reason"]),
                        {"VDF", "SDF"},
                        object_name=obj.name,
                        action="fix_name",
                    )
                )
            continue

        lod = name_info["lod"]
        normalized_name = normalized_export_name(obj.name, lod)
        named_candidates.append(
            {
                "object": obj,
                "lod": lod,
                "normalized_name": normalized_name,
                "spinner_like": spinner_like,
            }
        )
        normalized_names.setdefault(normalized_name, []).append(obj)

        if getattr(obj, "type", None) != "MESH":
            if spinner_like:
                issues.append(
                    _make_issue(
                        "ERROR",
                        "Object",
                        obj.name,
                        "Spinner/helper empties are VDF-only helpers and will break SDF export if left in a structure scene.",
                        {"SDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )
            else:
                issues.append(
                    _make_issue(
                        "ERROR",
                        "Object",
                        obj.name,
                        "Object has a valid legacy export name but is not a mesh. Legacy VDF/SDF export expects mesh GEO data.",
                        {"VDF", "SDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )
            continue

        if len(getattr(obj.data, "vertices", [])) == 0:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    obj.name,
                    "Mesh has a valid legacy export name but contains no vertices.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        issues.extend(_collect_material_issues(obj, {"VDF", "SDF"}))

    for normalized_name, objects in normalized_names.items():
        if len(objects) < 2:
            continue
        object_names = ", ".join(sorted(obj.name for obj in objects))
        issues.append(
            _make_issue(
                "ERROR",
                "Scene",
                normalized_name,
                f"Multiple objects normalize to the same export name: {object_names}.",
                {"VDF", "SDF"},
            )
        )

    candidate_name_set = set(normalized_names.keys())
    for entry in named_candidates:
        obj = entry["object"]
        parent = getattr(obj, "parent", None)
        if parent is None:
            continue

        parent_info = parse_legacy_geo_name(parent.name)
        if not parent_info["valid"]:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Object",
                    obj.name,
                    f"Parent '{parent.name}' is not legacy-exportable. This object will export with parent WORLD.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        parent_name = normalized_export_name(parent.name, entry["lod"])
        if parent_name not in candidate_name_set:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Object",
                    obj.name,
                    f"Parent '{parent.name}' does not resolve to an exportable object in the same LOD set. This object will likely export with parent WORLD.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )

    issues.extend(_collect_collision_helper_issues(inner_helpers, "inner"))
    issues.extend(_collect_collision_helper_issues(outer_helpers, "outer"))
    return issues


def _collect_collision_helper_issues(helpers, label):
    issues = []
    if not helpers:
        return issues

    if len(helpers) > 1:
        helper_names = ", ".join(sorted(obj.name for obj in helpers))
        issues.append(
            _make_issue(
                "WARNING",
                "Scene",
                label,
                f"Multiple {label} collision helpers are present ({helper_names}). VDF export will use whichever object is encountered last.",
                {"VDF"},
            )
        )

    for helper in helpers:
        if getattr(helper, "type", None) != "MESH" or getattr(helper, "data", None) is None:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    helper.name,
                    "Collision helper is not a mesh object. VDF collision helpers must be meshes.",
                    {"VDF"},
                    object_name=helper.name,
                    action="select_object",
                )
            )
            continue

        if len(getattr(helper.data, "vertices", [])) == 0:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    helper.name,
                    "Collision helper mesh contains no vertices.",
                    {"VDF"},
                    object_name=helper.name,
                    action="select_object",
                )
            )

    return issues


def _collect_material_issues(obj, export_modes):
    issues = []
    mesh = getattr(obj, "data", None)
    materials = getattr(mesh, "materials", None)
    if materials is None:
        return issues

    for index, material in enumerate(materials):
        slot_label = f"{obj.name}:slot{index}"
        if material is None:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    slot_label,
                    "Material slot is empty. Export will fall back to blank texture naming for faces using this slot.",
                    export_modes,
                )
            )
            continue

        material_props = getattr(material, "MaterialPropertyGroup", None)
        raw_texture = ""
        if material_props is not None:
            raw_texture = (getattr(material_props, "MapTexture", "") or "").strip()
        image_texture = _get_image_derived_texture_name(material)

        if raw_texture and len(raw_texture) > 8:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    material.name,
                    f"Legacy texture name '{raw_texture}' exceeds 8 characters and may not round-trip cleanly.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        if raw_texture:
            continue

        if image_texture:
            issues.append(
                _make_issue(
                    "INFO",
                    "Material",
                    material.name,
                    f"Texture name is blank. Export will derive '{image_texture}' from the linked image texture.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        derived_name = _derive_legacy_texture_name(material.name)
        if not derived_name:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    slot_label,
                    "Material has no Battlezone texture name and no usable Blender material name to derive one from.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
        elif len((material.name or "").strip().replace(" ", "_")) > 8:
            issues.append(
                _make_issue(
                    "INFO",
                    "Material",
                    material.name,
                    f"Texture name is blank. Export will auto-derive and truncate this material name to '{derived_name}'.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )

    return issues


def _looks_like_export_candidate(obj, spinner_like):
    if is_collision_helper_name(obj.name):
        return False
    if getattr(obj, "type", None) in {"MESH", "EMPTY"}:
        return True
    if spinner_like:
        return True
    return getattr(obj, "parent", None) is not None


def _invalid_name_message(reason):
    if reason == "too_short":
        return "Object name is shorter than 5 characters and will be skipped by legacy VDF/SDF export."
    if reason == "too_long":
        return "Object name exceeds 8 characters and will be skipped by legacy VDF/SDF export."
    if reason == "invalid_lod":
        return "Object name does not have a valid LOD marker at character 4 and will be skipped by legacy VDF/SDF export."
    return "Object name is not valid for legacy VDF/SDF export."
