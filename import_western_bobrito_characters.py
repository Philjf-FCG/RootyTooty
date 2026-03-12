import os
import zipfile
import unreal


PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
EXTRACT_ROOT = os.path.join(PROJECT_ROOT, "Saved", "ImportedCharacters")

WESTERN_ZIP = "western-cowboy-rigged.zip"
BOBRITO_ZIP = "bobrito-bandito-game-ready-3d-model-free.zip"

WESTERN_DEST_PATH = "/Game/ImportedCharacters/Western"
BOBRITO_DEST_PATH = "/Game/ImportedCharacters/Bobrito"

WESTERN_ASSET_NAME = "SK_WesternPlayer"
BOBRITO_ASSET_NAME = "SK_BobritoEnemy"

PLAYER_BP = "/Game/Blueprints/BP_WWCharacter"
ENEMY_BP = "/Game/Blueprints/BP_Bandit"
GM_BP = "/Game/Blueprints/BP_WWGameMode"


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


def _build_skeletal_import_options():
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property("import_animations", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("create_physics_asset", False)

    sk_data = options.get_editor_property("skeletal_mesh_import_data")
    if sk_data:
        try:
            sk_data.set_editor_property("import_meshes_in_bone_hierarchy", True)
        except Exception:
            pass
    return options


def _import_fbx_as_skeletal(fbx_file, destination_path, destination_name):
    _ensure_content_dir(destination_path)
    options = _build_skeletal_import_options()

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fbx_file)
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("destination_name", destination_name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("options", options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    asset_path = f"{destination_path}/{destination_name}.{destination_name}"
    asset = unreal.load_asset(asset_path)
    if not asset:
        raise RuntimeError(f"Failed to import skeletal mesh: {asset_path}")
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log(f"CHAR_IMPORT: Imported {asset_path}")
    return asset


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
    unreal.log(f"CHAR_IMPORT: Assigned {skeletal_mesh.get_name()} -> {bp_asset_path}")


def _ensure_gamemode_assignments():
    gm_asset = unreal.load_asset(GM_BP)
    player_asset = unreal.load_asset(PLAYER_BP)
    enemy_asset = unreal.load_asset(ENEMY_BP)
    if not gm_asset or not player_asset or not enemy_asset:
        unreal.log_warning("CHAR_IMPORT: Could not load game mode or blueprint assets for final class assignment")
        return

    gm_cdo = unreal.get_default_object(gm_asset.generated_class())

    try:
        gm_cdo.set_editor_property("default_pawn_class", player_asset.generated_class())
    except Exception as exc:
        unreal.log_warning(f"CHAR_IMPORT: Failed to set default_pawn_class: {exc}")

    # Custom game mode property used in this project.
    try:
        gm_cdo.set_editor_property("EnemyClass", enemy_asset.generated_class())
    except Exception:
        try:
            gm_cdo.set_editor_property("enemy_class", enemy_asset.generated_class())
        except Exception as exc:
            unreal.log_warning(f"CHAR_IMPORT: Failed to set enemy class property: {exc}")

    unreal.EditorAssetLibrary.save_asset(GM_BP)
    unreal.log("CHAR_IMPORT: GameMode class references refreshed")


def run_import_and_assign():
    unreal.log("CHAR_IMPORT: Starting western/bobrito character import")
    _ensure_dir(EXTRACT_ROOT)

    western_dir = _extract_zip(WESTERN_ZIP)
    bobrito_dir = _extract_zip(BOBRITO_ZIP)

    western_fbx = _find_first_fbx(western_dir)
    bobrito_fbx = _find_first_fbx(bobrito_dir)

    if not western_fbx:
        raise RuntimeError("No FBX found in western zip")
    if not bobrito_fbx:
        raise RuntimeError("No FBX found in bobrito zip")

    unreal.log(f"CHAR_IMPORT: Western FBX -> {western_fbx}")
    unreal.log(f"CHAR_IMPORT: Bobrito FBX -> {bobrito_fbx}")

    western_mesh = _import_fbx_as_skeletal(western_fbx, WESTERN_DEST_PATH, WESTERN_ASSET_NAME)
    bobrito_mesh = _import_fbx_as_skeletal(bobrito_fbx, BOBRITO_DEST_PATH, BOBRITO_ASSET_NAME)

    _assign_mesh_to_blueprint(PLAYER_BP, western_mesh)
    _assign_mesh_to_blueprint(ENEMY_BP, bobrito_mesh)
    _ensure_gamemode_assignments()

    unreal.log("CHAR_IMPORT: Complete. Western assigned to player, Bobrito assigned to enemy")


if __name__ == "__main__":
    run_import_and_assign()
