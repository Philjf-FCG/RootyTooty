import unreal

editor_lib = unreal.EditorAssetLibrary
mat_lib = unreal.MaterialEditingLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

tex_base = editor_lib.load_asset(
    "/Game/Weapons/Pickaxe/Textures/T_pickaxe_BaseColor.T_pickaxe_BaseColor"
)
tex_normal = editor_lib.load_asset(
    "/Game/Weapons/Pickaxe/Textures/T_pickaxe_Normal.T_pickaxe_Normal"
)
tex_orm = editor_lib.load_asset(
    "/Game/Weapons/Pickaxe/Textures/T_pickaxe_OcclusionRoughnessMetallic.T_pickaxe_OcclusionRoughnessMetallic"
)

if not tex_base or not tex_normal or not tex_orm:
    raise RuntimeError("Required pickaxe textures are missing.")

tex_normal.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
tex_normal.set_editor_property("srgb", False)
tex_orm.set_editor_property("srgb", False)

mat_path = "/Game/Weapons/Pickaxe"
mat_name = "M_StylizedPickaxe"
material_asset_path = f"{mat_path}/{mat_name}.{mat_name}"
material = editor_lib.load_asset(material_asset_path)
if not material:
    material = asset_tools.create_asset(mat_name, mat_path, unreal.Material, unreal.MaterialFactoryNew())

if not material:
    raise RuntimeError("Failed to create/load pickaxe material.")

mat_lib.delete_all_material_expressions(material)

base_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, -260)
base_sample.texture = tex_base

normal_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, 0)
normal_sample.texture = tex_normal
normal_sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)

orm_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, 280)
orm_sample.texture = tex_orm

ao_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -320, 200)
ao_mask.set_editor_property("r", True)
rough_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -320, 280)
rough_mask.set_editor_property("g", True)
metal_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -320, 360)
metal_mask.set_editor_property("b", True)

mat_lib.connect_material_expressions(orm_sample, "RGB", ao_mask, "Input")
mat_lib.connect_material_expressions(orm_sample, "RGB", rough_mask, "Input")
mat_lib.connect_material_expressions(orm_sample, "RGB", metal_mask, "Input")

mat_lib.connect_material_property(base_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
mat_lib.connect_material_property(normal_sample, "RGB", unreal.MaterialProperty.MP_NORMAL)
mat_lib.connect_material_property(ao_mask, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
mat_lib.connect_material_property(rough_mask, "G", unreal.MaterialProperty.MP_ROUGHNESS)
mat_lib.connect_material_property(metal_mask, "B", unreal.MaterialProperty.MP_METALLIC)

mat_lib.layout_material_expressions(material)
mat_lib.recompile_material(material)

mesh = editor_lib.load_asset("/Game/Weapons/Pickaxe/stylized_pickaxe_SM.stylized_pickaxe_SM")
if not mesh:
    raise RuntimeError("Failed to load stylized pickaxe mesh")

mesh.set_material(0, material)

for asset in [tex_base, tex_normal, tex_orm, material, mesh]:
    editor_lib.save_loaded_asset(asset)

with open(r"C:/Unreal Projects/rooty/RootyTooty/Saved/pickaxe_material_report.txt", "w", encoding="utf-8") as f:
    f.write("Material assigned to stylized_pickaxe_SM slot 0\n")

unreal.log("Pickaxe material assignment complete.")
