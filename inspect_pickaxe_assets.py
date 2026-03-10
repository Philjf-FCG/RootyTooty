import unreal

root = "/Game/Weapons/Pickaxe"
assets = unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=True)
unreal.log(f"ASSET_COUNT={len(assets)}")
for path in assets:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        obj = unreal.EditorAssetLibrary.load_asset(path)
        cls = obj.get_class().get_name() if obj else "None"
        unreal.log(f"ASSET {path} :: {cls}")
