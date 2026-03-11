import unreal


CHAR_BP_PATH = "/Game/Blueprints/BP_WWCharacter"
GM_BP_PATH = "/Game/Blueprints/BP_WWGameMode"
PLAYER_MESH_CANDIDATES = [
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]


def _load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _set_if_exists(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception:
        return False


def _fix_character_blueprint_visibility():
    bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(CHAR_BP_PATH)
    if not bp_cls:
        unreal.log_error(f"VIS_FIX: Could not load blueprint class {CHAR_BP_PATH}")
        return False

    cdo = unreal.get_default_object(bp_cls)
    mesh_comp = None
    try:
        mesh_comp = cdo.get_editor_property("mesh")
    except Exception:
        pass

    if not mesh_comp:
        unreal.log_error("VIS_FIX: Character blueprint has no mesh component")
        return False

    player_mesh = _load_first(PLAYER_MESH_CANDIDATES)
    if player_mesh:
        if not _set_if_exists(mesh_comp, "skeletal_mesh_asset", player_mesh):
            _set_if_exists(mesh_comp, "skeletal_mesh", player_mesh)
        unreal.log(f"VIS_FIX: Ensured skeletal mesh is set to {player_mesh.get_name()}")
    else:
        unreal.log_warning("VIS_FIX: Could not find a Manny mesh asset; leaving current mesh unchanged")

    _set_if_exists(mesh_comp, "hidden_in_game", False)
    _set_if_exists(mesh_comp, "visible", True)
    _set_if_exists(mesh_comp, "owner_no_see", False)
    _set_if_exists(mesh_comp, "only_owner_see", False)
    _set_if_exists(mesh_comp, "cast_shadow", True)
    _set_if_exists(mesh_comp, "render_in_main_pass", True)

    _set_if_exists(cdo, "hidden", False)
    _set_if_exists(cdo, "actor_hidden_in_game", False)

    unreal.EditorAssetLibrary.save_asset(CHAR_BP_PATH)
    unreal.log("VIS_FIX: Saved BP_WWCharacter with explicit visible mesh settings")
    return True


def _fix_gamemode_default_pawn():
    gm_bp = unreal.load_asset(GM_BP_PATH)
    char_bp = unreal.load_asset(CHAR_BP_PATH)
    if not gm_bp or not char_bp:
        unreal.log_error("VIS_FIX: Could not load BP_WWGameMode or BP_WWCharacter")
        return False

    gm_cdo = unreal.get_default_object(gm_bp.generated_class())
    char_class = char_bp.generated_class()
    try:
        gm_cdo.set_editor_property("default_pawn_class", char_class)
        unreal.EditorAssetLibrary.save_asset(GM_BP_PATH)
        unreal.log(f"VIS_FIX: Set GameMode default_pawn_class to {char_class.get_name()}")
        return True
    except Exception as exc:
        unreal.log_error(f"VIS_FIX: Failed to set GameMode default pawn class: {exc}")
        return False


def run_fix():
    unreal.log("VIS_FIX: Starting player visibility repair...")
    char_ok = _fix_character_blueprint_visibility()
    gm_ok = _fix_gamemode_default_pawn()

    if char_ok and gm_ok:
        unreal.log("VIS_FIX: Complete. Press Play to verify player is visible.")
    else:
        unreal.log_warning("VIS_FIX: Completed with warnings. Review log for details.")


if __name__ == "__main__":
    run_fix()
