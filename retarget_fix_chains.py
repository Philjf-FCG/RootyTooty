"""
Rebuilds IK rig retarget chains with correct explicit bone name mappings
for Mannequin → Western (mixamo-style) → Bobrito (mixamo-style).

The previous run used apply_auto_generated_retarget_definition() which could not
map Mannequin bone names (pelvis, spine_01, upperarm_l, thigh_l …) to the
Mixamo-lowercase names used by these imported meshes (hips, spine, leftarm, leftupleg …).

This script manually defines chains with matching names so auto_map_chains EXACT works.
"""
import unreal

RETARGET_DIR = "/Game/ImportedCharacters/Retarget"

SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple",
]
WESTERN_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer"
BOBRITO_MESH_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy"

# --- Chain definitions ---
# Names must match between source and target so EXACT auto-map succeeds.
# Manny uses UE5 mannequin names; Western/Bobrito use lowercase Mixamo names.
MANNY_CHAINS = [
    ("Root",     "root",       "pelvis"),
    ("Spine",    "spine_01",   "spine_05"),
    ("Head",     "neck_01",    "head"),
    ("LeftArm",  "clavicle_l", "hand_l"),
    ("RightArm", "clavicle_r", "hand_r"),
    ("LeftLeg",  "thigh_l",    "foot_l"),
    ("RightLeg", "thigh_r",    "foot_r"),
]

# Both Western and Bobrito share identical bone names (Mixamo-lowercase).
IMPORTED_CHAINS = [
    ("Root",     "hips",          "spine"),
    ("Spine",    "spine",         "spine2"),
    ("Head",     "neck",          "head"),
    ("LeftArm",  "leftshoulder",  "lefthand"),
    ("RightArm", "rightshoulder", "righthand"),
    ("LeftLeg",  "leftupleg",     "leftfoot"),
    ("RightLeg", "rightupleg",    "rightfoot"),
]

SOURCE_ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a, p
    return None, None


def setup_ik_rig_chains(rig_path, mesh_path, chains, root_bone_name):
    print(f"  Configuring {rig_path} …")
    rig = unreal.load_asset(rig_path)
    if rig is None:
        print(f"  ERROR: could not load {rig_path}")
        return False
    ctrl = unreal.IKRigController.get_controller(rig)
    if ctrl is None:
        print(f"  ERROR: could not get controller for {rig_path}")
        return False

    mesh = unreal.load_asset(mesh_path)
    if mesh is None:
        print(f"  ERROR: could not load mesh {mesh_path}")
        return False
    if not ctrl.set_skeletal_mesh(mesh):
        print(f"  WARNING: set_skeletal_mesh returned False for {mesh_path}")

    # Remove all existing chains so we start fresh.
    try:
        existing = ctrl.get_retarget_chains()
        for c in existing:
            chain_name = c.chain_name if hasattr(c, "chain_name") else str(c)
            ctrl.remove_retarget_chain(unreal.Name(chain_name))
            print(f"    removed chain: {chain_name}")
    except Exception as e:
        print(f"  WARNING removing chains: {e}")

    # Set skeleton root.
    try:
        ctrl.set_retarget_root(unreal.Name(root_bone_name))
        print(f"    root bone set: {root_bone_name}")
    except Exception as e:
        print(f"  WARNING set_retarget_root: {e}")

    # Add chains.  Signature: (chain_name, start_bone, end_bone, goal_name)
    ok = True
    for (name, start, end) in chains:
        try:
            result = ctrl.add_retarget_chain(
                unreal.Name(name), unreal.Name(start), unreal.Name(end), unreal.Name("None")
            )
            print(f"    chain '{name}': {start} → {end}  ok={result}")
            if not result:
                ok = False
        except Exception as e:
            print(f"  ERROR add_retarget_chain '{name}': {e}")
            ok = False

    unreal.EditorAssetLibrary.save_loaded_asset(rig)
    return ok


def rebuild_retargeter(rtg_path, src_rig_path, tgt_rig_path, src_mesh, tgt_mesh):
    print(f"  Rebuilding retargeter {rtg_path} …")
    rtg = unreal.load_asset(rtg_path)
    if rtg is None:
        print(f"  ERROR: could not load retargeter {rtg_path}")
        return False
    rc = unreal.IKRetargeterController.get_controller(rtg)
    if rc is None:
        print(f"  ERROR: no controller for {rtg_path}")
        return False

    src_rig = unreal.load_asset(src_rig_path)
    tgt_rig = unreal.load_asset(tgt_rig_path)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, src_rig)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, tgt_rig)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, src_mesh)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, tgt_mesh)

    # Map chains by exact name — works because we used identical chain names above.
    try:
        rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
        print(f"    auto_map EXACT done")
    except Exception as e:
        print(f"  WARNING EXACT map failed ({e}), trying FUZZY …")
        try:
            rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
            print(f"    auto_map FUZZY done")
        except Exception as e2:
            print(f"  ERROR both map modes failed: {e2}")

    # Auto-align target pose.
    try:
        rc.auto_align_all_bones(
            unreal.RetargetSourceOrTarget.TARGET,
            unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN,
        )
    except Exception as e:
        print(f"  WARNING auto_align: {e}")

    unreal.EditorAssetLibrary.save_loaded_asset(rtg)
    return True


def delete_old_sequences(prefix, base_path="/Game"):
    names = ["MM_Idle", "MF_Unarmed_Jog_Fwd"]
    for n in names:
        asset_name = f"{prefix}{n}"
        obj_path = f"{base_path}/{asset_name}.{asset_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(obj_path):
            unreal.EditorAssetLibrary.delete_asset(obj_path)
            print(f"    deleted {obj_path}")


def run_batch(prefix, src_mesh, tgt_mesh, retargeter):
    anim_data = []
    seen = set()
    for p in SOURCE_ANIMS:
        ad = unreal.EditorAssetLibrary.find_asset_data(p)
        if ad and ad.is_valid():
            pkg = str(ad.package_name)
            if pkg not in seen:
                seen.add(pkg)
                anim_data.append(ad)

    if not anim_data:
        print("  ERROR: no source animation assets found")
        return []

    created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        anim_data,
        src_mesh,
        tgt_mesh,
        retargeter,
        "",   # source anim folder override (empty = use source folder)
        "",   # target anim folder override
        prefix,
        "",
        True,  # remap referenced assets
        True,  # allow existing if output exists
    )
    return [str(a.package_name) for a in created]


def main():
    print("=" * 60)
    print("RETARGET CHAIN REBUILD — START")
    print("=" * 60)

    manny_mesh, manny_path = load_first(SOURCE_MESH_CANDIDATES)
    if manny_mesh is None:
        print("ERROR: could not find Mannequin mesh")
        return

    western_mesh = unreal.load_asset(WESTERN_MESH_PATH)
    bobrito_mesh = unreal.load_asset(BOBRITO_MESH_PATH)
    if western_mesh is None or bobrito_mesh is None:
        print("ERROR: could not load imported meshes")
        return

    print("\n--- Setting up IK rigs ---")
    setup_ik_rig_chains(
        f"{RETARGET_DIR}/IKRIG_Manny", manny_path, MANNY_CHAINS, "pelvis"
    )
    setup_ik_rig_chains(
        f"{RETARGET_DIR}/IKRIG_Western", WESTERN_MESH_PATH, IMPORTED_CHAINS, "hips"
    )
    setup_ik_rig_chains(
        f"{RETARGET_DIR}/IKRIG_Bobrito", BOBRITO_MESH_PATH, IMPORTED_CHAINS, "hips"
    )

    print("\n--- Rebuilding retargeters ---")
    rebuild_retargeter(
        f"{RETARGET_DIR}/RTG_Manny_To_Western",
        f"{RETARGET_DIR}/IKRIG_Manny",
        f"{RETARGET_DIR}/IKRIG_Western",
        manny_mesh, western_mesh,
    )
    rebuild_retargeter(
        f"{RETARGET_DIR}/RTG_Manny_To_Bobrito",
        f"{RETARGET_DIR}/IKRIG_Manny",
        f"{RETARGET_DIR}/IKRIG_Bobrito",
        manny_mesh, bobrito_mesh,
    )

    print("\n--- Deleting old (empty) retarget sequences ---")
    delete_old_sequences("RTG_Western_")
    delete_old_sequences("RTG_Bobrito_")

    western_rtg = unreal.load_asset(f"{RETARGET_DIR}/RTG_Manny_To_Western")
    bobrito_rtg = unreal.load_asset(f"{RETARGET_DIR}/RTG_Manny_To_Bobrito")

    print("\n--- Running batch retarget: Western ---")
    west_out = run_batch("RTG_Western_", manny_mesh, western_mesh, western_rtg)
    print(f"  Created: {west_out}")

    print("\n--- Running batch retarget: Bobrito ---")
    bob_out = run_batch("RTG_Bobrito_", manny_mesh, bobrito_mesh, bobrito_rtg)
    print(f"  Created: {bob_out}")

    print("\n" + "=" * 60)
    print(f"DONE  Western sequences: {len(west_out)}  Bobrito sequences: {len(bob_out)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
