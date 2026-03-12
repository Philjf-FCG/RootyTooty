import unreal


def list_assets(folder_path: str):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path(folder_path, recursive=True)
    unreal.log(f"ASSET_DUMP_BEGIN {folder_path} count={len(assets)}")
    for a in assets:
        unreal.log(f"ASSET {a.package_name} class={a.asset_class_path.asset_name}")
    unreal.log(f"ASSET_DUMP_END {folder_path}")


list_assets('/Game/ImportedCharacters/Western')
list_assets('/Game/ImportedCharacters/Bobrito')
