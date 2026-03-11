import unreal


PLAYER_BP = "/Game/Blueprints/BP_WWCharacter"
ENEMY_BP = "/Game/Blueprints/BP_Bandit"
GM_BP = "/Game/Blueprints/BP_WWGameMode"

WESTERN_MESH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
BOBRITO_MESH_CANDIDATES = [
    "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy",
    "/Game/ImportedCharacters/Bobrito/Offensive_Idle.Offensive_Idle",
]


def _set_if_exists(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception:
        return False


def _load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _assign_mesh_to_bp(bp_path, mesh_asset):
    bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
    if not bp_cls:
        raise RuntimeError(f"Could not load blueprint class: {bp_path}")

    cdo = unreal.get_default_object(bp_cls)
    mesh_comp = cdo.get_editor_property("mesh")
    if not mesh_comp:
        raise RuntimeError(f"No mesh component on blueprint: {bp_path}")

    if not _set_if_exists(mesh_comp, "skeletal_mesh_asset", mesh_asset):
        _set_if_exists(mesh_comp, "skeletal_mesh", mesh_asset)

    _set_if_exists(mesh_comp, "hidden_in_game", False)
    _set_if_exists(mesh_comp, "visible", True)
    _set_if_exists(mesh_comp, "owner_no_see", False)
    _set_if_exists(mesh_comp, "only_owner_see", False)
    _set_if_exists(mesh_comp, "render_in_main_pass", True)
    _set_if_exists(cdo, "actor_hidden_in_game", False)

    unreal.EditorAssetLibrary.save_asset(bp_path)


def _assign_gamemode_classes():
    gm = unreal.load_asset(GM_BP)
    player_bp = unreal.load_asset(PLAYER_BP)
    enemy_bp = unreal.load_asset(ENEMY_BP)
    if not gm or not player_bp or not enemy_bp:
        raise RuntimeError("Could not load game mode or character blueprints")

    gm_cdo = unreal.get_default_object(gm.generated_class())
    gm_cdo.set_editor_property("default_pawn_class", player_bp.generated_class())

    try:
        gm_cdo.set_editor_property("EnemyClass", enemy_bp.generated_class())
    except Exception:
        _set_if_exists(gm_cdo, "enemy_class", enemy_bp.generated_class())

    unreal.EditorAssetLibrary.save_asset(GM_BP)


def run_assignment():
    western = unreal.load_asset(WESTERN_MESH)
    bobrito = _load_first(BOBRITO_MESH_CANDIDATES)

    if not western:
        raise RuntimeError(f"Missing western mesh: {WESTERN_MESH}")
    if not bobrito:
        raise RuntimeError("Missing bobrito mesh under /Game/ImportedCharacters/Bobrito")

    _assign_mesh_to_bp(PLAYER_BP, western)
    _assign_mesh_to_bp(ENEMY_BP, bobrito)
    _assign_gamemode_classes()

    unreal.log(f"CHAR_ASSIGN: Player mesh={western.get_name()}, Enemy mesh={bobrito.get_name()}")


if __name__ == "__main__":
    run_assignment()
