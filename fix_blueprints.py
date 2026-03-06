import unreal


def _load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _find_animation_asset_by_keywords(keywords):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_class("AnimSequence", True)
    wanted = [k.lower() for k in keywords]
    for data in assets:
        name = data.asset_name.lower()
        pkg = str(data.package_name).lower()
        if all(k in f"{name} {pkg}" for k in wanted):
            loaded = data.get_asset()
            if loaded:
                return loaded
    return None


def _resolve_player_mesh():
    return _load_first([
        "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
        "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    ])


def _resolve_enemy_mesh():
    return _load_first([
        "/Game/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple",
        "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple",
    ])


def _resolve_idle_anim():
    return _load_first([
        "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
        "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    ]) or _find_animation_asset_by_keywords(["idle"])


def _resolve_move_anim():
    return _load_first([
        "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
        "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    ]) or _find_animation_asset_by_keywords(["jog", "fwd"])


def _restore_mesh_animation(mesh_comp, mesh_asset, idle_anim):
    if not mesh_comp:
        return False

    if mesh_asset:
        try:
            mesh_comp.set_editor_property("skeletal_mesh_asset", mesh_asset)
        except Exception:
            pass

    try:
        mesh_comp.set_editor_property("animation_blueprint_generated_class", None)
    except Exception:
        pass
    try:
        mesh_comp.set_editor_property("anim_class", None)
    except Exception:
        pass

    try:
        mesh_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        try:
            mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        except Exception:
            pass

    if idle_anim:
        try:
            mesh_comp.set_animation(idle_anim)
        except Exception:
            pass
        try:
            mesh_comp.play_animation(idle_anim, True)
        except Exception:
            pass

    return True


def _restore_bp(bp_asset_path, mesh_asset, idle_anim):
    bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_asset_path)
    if not bp_cls:
        unreal.log_error(f"ANIM_FIX: Could not load blueprint class for {bp_asset_path}")
        return False

    cdo = unreal.get_default_object(bp_cls)
    mesh_comp = cdo.get_editor_property("mesh")
    ok = _restore_mesh_animation(mesh_comp, mesh_asset, idle_anim)
    unreal.EditorAssetLibrary.save_asset(bp_asset_path)
    return ok


def restore_character_and_enemy_animations():
    unreal.log("ANIM_FIX: Restoring player and enemy animation setup...")

    player_mesh = _resolve_player_mesh()
    enemy_mesh = _resolve_enemy_mesh()
    idle_anim = _resolve_idle_anim()
    move_anim = _resolve_move_anim()

    if not idle_anim:
        unreal.log_error("ANIM_FIX: Idle animation asset not found.")
    if not move_anim:
        unreal.log_warning("ANIM_FIX: Move animation asset not found; character can still idle.")

    player_ok = _restore_bp("/Game/Blueprints/BP_WWCharacter", player_mesh, idle_anim)
    enemy_ok = _restore_bp("/Game/Blueprints/BP_Bandit", enemy_mesh, idle_anim)

    if player_ok and enemy_ok:
        unreal.log("ANIM_FIX: Player and enemy animations restored.")
    else:
        unreal.log_warning("ANIM_FIX: Completed with warnings. Check blueprint load errors.")


if __name__ == "__main__":
    restore_character_and_enemy_animations()

