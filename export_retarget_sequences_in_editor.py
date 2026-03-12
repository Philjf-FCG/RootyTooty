"""
Run batch retarget export inside the full Unreal Editor and place the resulting
animation sequences at /Game so the existing C++ load paths continue to work.

Set environment variable RTG_TARGET to Western, Bobrito, or All before launch.
Run from Unreal Editor command line with -ExecutePythonScript.
"""

import os

import unreal


RETARGET_DIR = "/Game/ImportedCharacters/Retarget"
SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple",
]
WESTERN_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer"
BOBRITO_MESH_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy"
SOURCE_ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
]
TARGET_FILTER = os.getenv("RTG_TARGET", "All").strip().lower()


def load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def gather_anim_assets():
    result = []
    seen = set()
    for path in SOURCE_ANIMS:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
        if asset_data and asset_data.is_valid():
            package_name = str(asset_data.package_name)
            if package_name not in seen:
                seen.add(package_name)
                result.append(asset_data)
    return result


def delete_game_root_outputs(prefix):
    for base_name in ["MM_Idle", "MF_Unarmed_Jog_Fwd"]:
        asset_name = f"{prefix}{base_name}"
        object_path = f"/Game/{asset_name}.{asset_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(object_path):
            unreal.EditorAssetLibrary.delete_asset(object_path)
            print(f"deleted {object_path}")


def move_asset_to_game_root(asset_data):
    package_name = str(asset_data.package_name)
    asset_name = package_name.rsplit("/", 1)[-1]
    source_object_path = f"{package_name}.{asset_name}"
    target_object_path = f"/Game/{asset_name}.{asset_name}"

    if source_object_path == target_object_path:
        print(f"already at root: {target_object_path}")
        return target_object_path

    if unreal.EditorAssetLibrary.does_asset_exist(target_object_path):
        unreal.EditorAssetLibrary.delete_asset(target_object_path)

    if not unreal.EditorAssetLibrary.rename_asset(source_object_path, target_object_path):
        raise RuntimeError(f"Failed moving {source_object_path} -> {target_object_path}")

    print(f"moved {source_object_path} -> {target_object_path}")
    return target_object_path


def run_batch(label, prefix, source_mesh, target_mesh, retargeter_path):
    retargeter = unreal.load_asset(retargeter_path)
    if not retargeter:
        raise RuntimeError(f"Missing retargeter: {retargeter_path}")

    delete_game_root_outputs(prefix)

    created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        gather_anim_assets(),
        source_mesh,
        target_mesh,
        retargeter,
        "",
        "",
        prefix,
        "",
        False,
        True,
    )

    print(f"{label} created raw: {[str(asset.package_name) for asset in created]}")
    moved = [move_asset_to_game_root(asset) for asset in created]
    print(f"{label} final: {moved}")


def main():
    source_mesh = load_first(SOURCE_MESH_CANDIDATES)
    western_mesh = unreal.load_asset(WESTERN_MESH_PATH)
    bobrito_mesh = unreal.load_asset(BOBRITO_MESH_PATH)

    if not source_mesh or not western_mesh or not bobrito_mesh:
        raise RuntimeError("Missing source or target meshes")

    anim_assets = gather_anim_assets()
    if len(anim_assets) < 2:
        raise RuntimeError("Could not find the source idle and jog animations")

    if TARGET_FILTER in ("all", "western"):
        run_batch(
            "Western",
            "RTG_Western_",
            source_mesh,
            western_mesh,
            f"{RETARGET_DIR}/RTG_Manny_To_Western",
        )

    if TARGET_FILTER in ("all", "bobrito"):
        run_batch(
            "Bobrito",
            "RTG_Bobrito_",
            source_mesh,
            bobrito_mesh,
            f"{RETARGET_DIR}/RTG_Manny_To_Bobrito",
        )

    unreal.EditorAssetLibrary.save_directory("/Game", False, True)
    print(f"EXPORT_COMPLETE target={TARGET_FILTER}")


if __name__ == "__main__":
    main()