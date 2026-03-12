import unreal

RETARGET_DIR = "/Game/ImportedCharacters/Retarget"

SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]

WESTERN_TARGET_MESH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
BOBRITO_TARGET_MESH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy"

SOURCE_ANIM_CANDIDATES = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Pistol/MM_Pistol_Fire_Montage.MM_Pistol_Fire_Montage",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a, p
    return None, None


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def load_or_create(asset_name, package_path, asset_class, factory):
    obj_path = f"{package_path}/{asset_name}.{asset_name}"
    existing = unreal.load_asset(obj_path)
    if existing:
        return existing
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    return tools.create_asset(asset_name, package_path, asset_class, factory)


def configure_ik_rig(ik_rig, skeletal_mesh):
    ctrl = unreal.IKRigController.get_controller(ik_rig)
    if not ctrl:
        raise RuntimeError(f"Could not get IKRigController for {ik_rig.get_name()}")
    if not ctrl.set_skeletal_mesh(skeletal_mesh):
        raise RuntimeError(f"Could not set skeletal mesh {skeletal_mesh.get_name()} on {ik_rig.get_name()}")
    ctrl.apply_auto_generated_retarget_definition()
    return ctrl


def build_retargeter(name, source_ik_rig, target_ik_rig, source_mesh, target_mesh):
    retargeter = load_or_create(name, RETARGET_DIR, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(retargeter)
    if not rc:
        raise RuntimeError(f"Could not get IKRetargeterController for {name}")

    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_ik_rig)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_ik_rig)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)
    rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET, unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)

    unreal.EditorAssetLibrary.save_loaded_asset(retargeter)
    unreal.EditorAssetLibrary.save_loaded_asset(source_ik_rig)
    unreal.EditorAssetLibrary.save_loaded_asset(target_ik_rig)
    return retargeter


def gather_source_anim_asset_data():
    out = []
    seen_packages = set()
    for p in SOURCE_ANIM_CANDIDATES:
        ad = unreal.EditorAssetLibrary.find_asset_data(p)
        if ad and ad.is_valid():
            pkg = str(ad.package_name)
            if pkg not in seen_packages:
                seen_packages.add(pkg)
                out.append(ad)
    return out


def run_batch(prefix, source_mesh, target_mesh, retargeter):
    anim_assets = gather_source_anim_asset_data()
    if not anim_assets:
        raise RuntimeError("No source mannequin animation assets found to retarget")

    created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        anim_assets,
        source_mesh,
        target_mesh,
        retargeter,
        "",
        "",
        prefix,
        "",
        True,
        True,
    )

    return [str(a.package_name) for a in created]


def main():
    ensure_dir(RETARGET_DIR)

    source_mesh, source_path = load_first(SOURCE_MESH_CANDIDATES)
    if not source_mesh:
        raise RuntimeError("Could not load source Manny mesh")

    western_mesh = unreal.load_asset(WESTERN_TARGET_MESH)
    bobrito_mesh = unreal.load_asset(BOBRITO_TARGET_MESH)
    if not western_mesh or not bobrito_mesh:
        raise RuntimeError("Missing western or bobrito target skeletal mesh")

    src_ik = load_or_create("IKRIG_Manny", RETARGET_DIR, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    west_ik = load_or_create("IKRIG_Western", RETARGET_DIR, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    bob_ik = load_or_create("IKRIG_Bobrito", RETARGET_DIR, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())

    configure_ik_rig(src_ik, source_mesh)
    configure_ik_rig(west_ik, western_mesh)
    configure_ik_rig(bob_ik, bobrito_mesh)

    west_rtg = build_retargeter("RTG_Manny_To_Western", src_ik, west_ik, source_mesh, western_mesh)
    bob_rtg = build_retargeter("RTG_Manny_To_Bobrito", src_ik, bob_ik, source_mesh, bobrito_mesh)

    west_created = run_batch("RTG_Western_", source_mesh, western_mesh, west_rtg)
    bob_created = run_batch("RTG_Bobrito_", source_mesh, bobrito_mesh, bob_rtg)

    unreal.log("RETARGET_SUCCESS")
    unreal.log(f"RETARGET_SOURCE_MESH={source_path}")
    unreal.log(f"RETARGET_WESTERN_CREATED={west_created}")
    unreal.log(f"RETARGET_BOBRITO_CREATED={bob_created}")


if __name__ == "__main__":
    main()
