"""
Repair the IK Rig and IK Retargeter assets used for the imported Western and
Bobrito characters.

This script does not run batch export because that path has been unstable in
this project. It only repairs the rig/retargeter configuration so the user can
open the IK Retargeter in the full editor and export animations from the UI.

Run from Unreal Editor: Tools -> Execute Python Script
"""

import unreal


RETARGET_DIR = "/Game/ImportedCharacters/Retarget"

MANNY_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple",
]
WESTERN_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer"
BOBRITO_MESH_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy"


def load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset, path
    return None, None


def get_chain_summary(ctrl):
    parts = []
    for chain in ctrl.get_retarget_chains():
        chain_name = str(chain.chain_name)
        start_bone = str(ctrl.get_retarget_chain_start_bone(chain.chain_name))
        end_bone = str(ctrl.get_retarget_chain_end_bone(chain.chain_name))
        parts.append(f"{chain_name}={start_bone}->{end_bone}")
    return parts


def clear_all_chains(ctrl):
    for chain in list(ctrl.get_retarget_chains()):
        ctrl.remove_retarget_chain(chain.chain_name)


def add_chain(ctrl, name, start_bone, end_bone):
    created = ctrl.add_retarget_chain(
        unreal.Name(name),
        unreal.Name(start_bone),
        unreal.Name(end_bone),
        unreal.Name("None"),
    )
    print(f"    chain {created}: {start_bone} -> {end_bone}")


def configure_rig(rig_asset_path, mesh_asset_path, retarget_root, chain_defs):
    rig = unreal.load_asset(rig_asset_path)
    mesh = unreal.load_asset(mesh_asset_path)
    if not rig or not mesh:
        raise RuntimeError(f"Failed to load rig or mesh: {rig_asset_path} | {mesh_asset_path}")

    ctrl = unreal.IKRigController.get_controller(rig)
    if not ctrl:
        raise RuntimeError(f"Failed to get IKRigController for {rig_asset_path}")

    ctrl.set_skeletal_mesh(mesh)
    clear_all_chains(ctrl)

    if not ctrl.set_retarget_root(unreal.Name(retarget_root)):
        raise RuntimeError(f"Failed to set retarget root '{retarget_root}' for {rig_asset_path}")

    for name, start_bone, end_bone in chain_defs:
        add_chain(ctrl, name, start_bone, end_bone)

    unreal.EditorAssetLibrary.save_loaded_asset(rig)

    print(f"  rig: {rig_asset_path}")
    print(f"    root={ctrl.get_retarget_root()}")
    for summary in get_chain_summary(ctrl):
        print(f"    {summary}")

    return rig, ctrl


def safe_call(obj, method_name, *args):
    method = getattr(obj, method_name, None)
    if not method:
        return False, None
    try:
        return True, method(*args)
    except TypeError as exc:
        print(f"    {method_name} skipped (signature mismatch): {exc}")
        return False, None
    except Exception as exc:
        print(f"    {method_name} failed: {exc}")
        return False, None


def log_chain_mappings(rc, chain_names):
    for chain_name in chain_names:
        ok, result = safe_call(
            rc,
            "get_source_chain",
            unreal.Name(chain_name),
        )
        if ok:
            print(f"    mapping {chain_name} -> {result}")


def rebuild_retargeter(retargeter_path, source_rig, target_rig, source_mesh, target_mesh):
    retargeter = unreal.load_asset(retargeter_path)
    if not retargeter:
        raise RuntimeError(f"Failed to load retargeter: {retargeter_path}")

    rc = unreal.IKRetargeterController.get_controller(retargeter)
    if not rc:
        raise RuntimeError(f"Failed to get IKRetargeterController for {retargeter_path}")

    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)

    safe_call(rc, "remove_all_ops")
    safe_call(rc, "add_default_ops")
    safe_call(rc, "assign_ik_rig_to_all_ops", unreal.RetargetSourceOrTarget.SOURCE)
    safe_call(rc, "assign_ik_rig_to_all_ops", unreal.RetargetSourceOrTarget.TARGET)

    num_ok, num_ops = safe_call(rc, "get_num_retarget_ops")
    if num_ok and isinstance(num_ops, int):
        print(f"    op count={num_ops}")
        for index in range(num_ops):
            safe_call(rc, "run_op_initial_setup", index)

    rc.auto_map_chains(unreal.AutoMapChainType.CLEAR, True)
    rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    log_chain_mappings(
        rc,
        ["Root", "Spine", "Head", "LeftArm", "RightArm", "LeftLeg", "RightLeg"],
    )

    unreal.EditorAssetLibrary.save_loaded_asset(retargeter)

    print(f"  retargeter: {retargeter_path}")
    print(f"    source rig={rc.get_ik_rig(unreal.RetargetSourceOrTarget.SOURCE)}")
    print(f"    target rig={rc.get_ik_rig(unreal.RetargetSourceOrTarget.TARGET)}")

    return retargeter, rc


def main():
    manny_mesh, manny_mesh_path = load_first(MANNY_MESH_CANDIDATES)
    western_mesh = unreal.load_asset(WESTERN_MESH_PATH)
    bobrito_mesh = unreal.load_asset(BOBRITO_MESH_PATH)

    if not manny_mesh or not western_mesh or not bobrito_mesh:
        raise RuntimeError("Missing Manny, Western, or Bobrito skeletal mesh")

    print("=== Repairing IK Rigs ===")
    manny_rig, _ = configure_rig(
        f"{RETARGET_DIR}/IKRIG_Manny",
        manny_mesh_path,
        "pelvis",
        [
            ("Root", "root", "pelvis"),
            ("Spine", "spine_01", "spine_05"),
            ("Head", "neck_01", "head"),
            ("LeftArm", "clavicle_l", "hand_l"),
            ("RightArm", "clavicle_r", "hand_r"),
            ("LeftLeg", "thigh_l", "foot_l"),
            ("RightLeg", "thigh_r", "foot_r"),
        ],
    )
    western_rig, _ = configure_rig(
        f"{RETARGET_DIR}/IKRIG_Western",
        WESTERN_MESH_PATH,
        "hips",
        [
            ("Root", "hips", "spine"),
            ("Spine", "spine", "spine2"),
            ("Head", "neck", "head"),
            ("LeftArm", "leftshoulder", "lefthand"),
            ("RightArm", "rightshoulder", "righthand"),
            ("LeftLeg", "leftupleg", "leftfoot"),
            ("RightLeg", "rightupleg", "rightfoot"),
        ],
    )
    bobrito_rig, _ = configure_rig(
        f"{RETARGET_DIR}/IKRIG_Bobrito",
        BOBRITO_MESH_PATH,
        "hips",
        [
            ("Root", "hips", "spine"),
            ("Spine", "spine", "spine2"),
            ("Head", "neck", "head"),
            ("LeftArm", "leftshoulder", "lefthand"),
            ("RightArm", "rightshoulder", "righthand"),
            ("LeftLeg", "leftupleg", "leftfoot"),
            ("RightLeg", "rightupleg", "rightfoot"),
        ],
    )

    print("=== Repairing IK Retargeters ===")
    rebuild_retargeter(
        f"{RETARGET_DIR}/RTG_Manny_To_Western",
        manny_rig,
        western_rig,
        manny_mesh,
        western_mesh,
    )
    rebuild_retargeter(
        f"{RETARGET_DIR}/RTG_Manny_To_Bobrito",
        manny_rig,
        bobrito_rig,
        manny_mesh,
        bobrito_mesh,
    )

    print("=== COMPLETE ===")
    print("Open each RTG asset in the editor and verify the preview mesh animates.")
    print("Then export MM_Idle and MF_Unarmed_Jog_Fwd from the IK Retarget Editor.")


if __name__ == "__main__":
    main()