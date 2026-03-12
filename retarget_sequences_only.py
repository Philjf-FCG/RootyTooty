import unreal

SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]
WESTERN_TARGET_MESH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
BOBRITO_TARGET_MESH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy"

ANIM_PATHS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a
    return None


def find_anim_asset_data(paths):
    seen = set()
    out = []
    for p in paths:
        ad = unreal.EditorAssetLibrary.find_asset_data(p)
        if ad and ad.is_valid():
            pkg = str(ad.package_name)
            if pkg in seen:
                continue
            seen.add(pkg)
            out.append(ad)
    return out


def do_batch(prefix, source_mesh, target_mesh, rtg_path):
    rtg = unreal.load_asset(rtg_path)
    if not rtg:
        raise RuntimeError(f"Missing retargeter: {rtg_path}")

    assets = find_anim_asset_data(ANIM_PATHS)
    if not assets:
        raise RuntimeError("No source animation sequences found")

    created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        assets,
        source_mesh,
        target_mesh,
        rtg,
        "",
        "",
        prefix,
        "",
        False,
        True,
    )
    return [str(a.package_name) for a in created]


def main():
    source_mesh = load_first(SOURCE_MESH_CANDIDATES)
    western_mesh = unreal.load_asset(WESTERN_TARGET_MESH)
    bobrito_mesh = unreal.load_asset(BOBRITO_TARGET_MESH)

    if not source_mesh or not western_mesh or not bobrito_mesh:
        raise RuntimeError("Missing source or target skeletal meshes")

    west = do_batch(
        "RTG_Western_",
        source_mesh,
        western_mesh,
        "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Western.RTG_Manny_To_Western",
    )
    bob = do_batch(
        "RTG_Bobrito_",
        source_mesh,
        bobrito_mesh,
        "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Bobrito.RTG_Manny_To_Bobrito",
    )

    unreal.log("RETARGET_SEQ_SUCCESS")
    unreal.log(f"RETARGET_SEQ_WESTERN={west}")
    unreal.log(f"RETARGET_SEQ_BOBRITO={bob}")


if __name__ == "__main__":
    main()
