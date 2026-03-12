import os
import zipfile
import unreal


PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
EXTRACT_ROOT = os.path.join(PROJECT_ROOT, "Saved", "ImportedCharacters")

BOBRITO_ZIP = "bobrito-bandito-game-ready-3d-model-free.zip"
BOBRITO_DEST_PATH = "/Game/ImportedCharacters/Bobrito"

PLAYER_BP = "/Game/Blueprints/BP_WWCharacter"
ENEMY_BP = "/Game/Blueprints/BP_Bandit"
GM_BP = "/Game/Blueprints/BP_WWGameMode"
WESTERN_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _ensure_content_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def _extract_zip(zip_name):
    zip_path = os.path.join(PROJECT_ROOT, zip_name)
    if not os.path.exists(zip_path):
        raise RuntimeError(f"Missing zip: {zip_path}")

    out_dir = os.path.join(EXTRACT_ROOT, os.path.splitext(zip_name)[0])
    _ensure_dir(out_dir)
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(out_dir)
    return out_dir


def _find_first_fbx(root_dir):
    for cur_root, _, files in os.walk(root_dir):
        for name in files:
            if name.lower().endswith(".fbx"):
                return os.path.join(cur_root, name)
    return None


def _import_fbx_automated(fbx_file, destination_path):
    _ensure_content_dir(destination_path)

    data = unreal.AutomatedAssetImportData()
    data.destination_path = destination_path
    data.filenames = [fbx_file]
    data.replace_existing = True
    data.skip_read_only = True

    imported = unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(data)
    for asset in imported:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception:
            pass


def _find_first_skeletal_mesh_under(path):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(path, recursive=True)
    for data in assets:
        if data.asset_class_path.asset_name == "SkeletalMesh" or data.asset_class == "SkeletalMesh":
            loaded = data.get_asset()
            if loaded:
                return loaded
    return None


def _set_if_exists(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception:
        return False


def _assign_mesh_to_blueprint(bp_asset_path, skeletal_mesh):
    bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_asset_path)
    if not bp_cls:
        raise RuntimeError(f"Could not load blueprint class: {bp_asset_path}")

    cdo = unreal.get_default_object(bp_cls)
    mesh_comp = cdo.get_editor_property("mesh")
    if not mesh_comp:
        raise RuntimeError(f"Blueprint has no mesh component: {bp_asset_path}")

    if not _set_if_exists(mesh_comp, "skeletal_mesh_asset", skeletal_mesh):
        _set_if_exists(mesh_comp, "skeletal_mesh", skeletal_mesh)

    _set_if_exists(mesh_comp, "hidden_in_game", False)
    _set_if_exists(mesh_comp, "visible", True)
    _set_if_exists(mesh_comp, "owner_no_see", False)
    _set_if_exists(mesh_comp, "only_owner_see", False)
    _set_if_exists(mesh_comp, "render_in_main_pass", True)
    _set_if_exists(cdo, "actor_hidden_in_game", False)

    unreal.EditorAssetLibrary.save_asset(bp_asset_path)


def _ensure_gamemode_assignments():
    gm_asset = unreal.load_asset(GM_BP)
    player_asset = unreal.load_asset(PLAYER_BP)
    enemy_asset = unreal.load_asset(ENEMY_BP)
    if not gm_asset or not player_asset or not enemy_asset:
        return

    gm_cdo = unreal.get_default_object(gm_asset.generated_class())
    try:
        gm_cdo.set_editor_property("default_pawn_class", player_asset.generated_class())
    except Exception:
        pass

    try:
        gm_cdo.set_editor_property("EnemyClass", enemy_asset.generated_class())
    except Exception:
        try:
            gm_cdo.set_editor_property("enemy_class", enemy_asset.generated_class())
        except Exception:
            pass

    unreal.EditorAssetLibrary.save_asset(GM_BP)


def run_import():
    unreal.log("BOBRITO_IMPORT: Starting bobrito import/assignment")

    western_mesh = unreal.load_asset(WESTERN_MESH_PATH)
    if not western_mesh:
        raise RuntimeError(f"Missing western mesh asset: {WESTERN_MESH_PATH}")

    extracted = _extract_zip(BOBRITO_ZIP)
    fbx = _find_first_fbx(extracted)
    if not fbx:
        raise RuntimeError("No FBX found in bobrito zip")

    unreal.log(f"BOBRITO_IMPORT: Found FBX {fbx}")
    _import_fbx_automated(fbx, BOBRITO_DEST_PATH)

    bobrito_mesh = _find_first_skeletal_mesh_under(BOBRITO_DEST_PATH)
    if not bobrito_mesh:
        raise RuntimeError("No SkeletalMesh found after bobrito import")

    _assign_mesh_to_blueprint(PLAYER_BP, western_mesh)
    _assign_mesh_to_blueprint(ENEMY_BP, bobrito_mesh)
    _ensure_gamemode_assignments()

    unreal.log(f"BOBRITO_IMPORT: Assigned western={western_mesh.get_name()} player, bobrito={bobrito_mesh.get_name()} enemy")


if __name__ == "__main__":
    run_import()
