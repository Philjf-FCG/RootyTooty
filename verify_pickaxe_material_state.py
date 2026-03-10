import unreal

editor_lib = unreal.EditorAssetLibrary
mesh = editor_lib.load_asset('/Game/Weapons/Pickaxe/stylized_pickaxe_SM.stylized_pickaxe_SM')
mat = editor_lib.load_asset('/Game/Weapons/Pickaxe/M_StylizedPickaxe.M_StylizedPickaxe')
assets = editor_lib.list_assets('/Game/Weapons/Pickaxe/Textures', recursive=True, include_folder=False)

lines = []
lines.append(f"MATERIAL_EXISTS={mat is not None}")
lines.append(f"TEXTURE_COUNT={len(assets)}")
for a in assets:
    lines.append(f"TEXTURE={a}")

if mesh:
    slot0 = mesh.get_material(0)
    lines.append(f"MESH_SLOT0={(slot0.get_path_name() if slot0 else 'None')}")
else:
    lines.append('MESH_SLOT0=NO_MESH')

out_path = r"C:/Unreal Projects/rooty/RootyTooty/Saved/pickaxe_material_state.txt"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

unreal.log('Wrote pickaxe material state report')
