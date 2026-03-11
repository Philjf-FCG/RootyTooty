import os
import unreal

PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
DEST_PATH = "/Game/Audio"

AUDIO_IMPORTS = [
    {
        "source": "back_drop-ragtime-piano-honky-tonk-swipesy-354895.mp3",
        "dest": "BGM_Ragtime",
        "looping": True,
    },
    {
        "source": "magiaz-revolver_shots-407314.mp3",
        "dest": "SFX_PlayerRevolver",
        "looping": False,
    },
]


def ensure_folder(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def import_audio_assets():
    ensure_folder(DEST_PATH)
    for item in AUDIO_IMPORTS:
        source_file = os.path.join(PROJECT_ROOT, item["source"])
        dest_name = item["dest"]
        should_loop = item["looping"]

        if not os.path.exists(source_file):
            unreal.log_error(f"AUDIO_IMPORT: Source file missing: {source_file}")
            continue

        task = unreal.AssetImportTask()
        task.set_editor_property("filename", source_file)
        task.set_editor_property("destination_path", DEST_PATH)
        task.set_editor_property("destination_name", dest_name)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        imported_asset_path = f"{DEST_PATH}/{dest_name}.{dest_name}"
        asset = unreal.EditorAssetLibrary.load_asset(imported_asset_path)
        if not asset:
            unreal.log_error(f"AUDIO_IMPORT: Failed to import asset at {imported_asset_path}")
            continue

        if isinstance(asset, unreal.SoundWave):
            try:
                asset.set_editor_property("looping", should_loop)
            except Exception:
                pass

        unreal.EditorAssetLibrary.save_asset(imported_asset_path)
        unreal.log(f"AUDIO_IMPORT: Imported and saved {imported_asset_path}")


if __name__ == "__main__":
    import_audio_assets()
