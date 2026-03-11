import unreal

mesh = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple")
if not mesh:
    mesh = unreal.load_asset("/Game/Mannequins/Meshes/SKM_Manny.SKM_Manny")

if mesh:
    bones = [unreal.SkinnedAsset.get_bone_name(mesh, i) for i in range(unreal.SkinnedAsset.get_num_bones(mesh))]
    print("Bones: " + ", ".join([str(b) for b in bones]))
else:
    print("Mesh not found")
