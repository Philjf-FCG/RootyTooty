import unreal

root = "/Game/Weapons/Pickaxe"
out_path = r"C:/Unreal Projects/rooty/RootyTooty/Saved/pickaxe_asset_report.txt"

lines = []
assets = unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False)
lines.append(f"ASSET_COUNT={len(assets)}")
for path in assets:
    obj = unreal.EditorAssetLibrary.load_asset(path)
    cls = obj.get_class().get_name() if obj else "None"
    lines.append(f"{path} :: {cls}")

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

unreal.log(f"WROTE_REPORT={out_path}")
