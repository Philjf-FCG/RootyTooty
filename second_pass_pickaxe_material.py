import unreal

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
editor_lib = unreal.EditorAssetLibrary
mat_lib = unreal.MaterialEditingLibrary

src_tex_dir = r"C:/Unreal Projects/rooty/RootyTooty/Assets/StylizedPickaxe/Stylized Pickaxe Asset/Textures/Unreal"
dest_tex_path = "/Game/Weapons/Pickaxe/Textures"
mat_path = "/Game/Weapons/Pickaxe"
mat_name = "M_StylizedPickaxe"
mesh_path = "/Game/Weapons/Pickaxe/stylized_pickaxe_SM.stylized_pickaxe_SM"

# 1) Import textures.
texture_files = [
    "T_pickaxe_BaseColor.tga",
    "T_pickaxe_Normal.tga",
    "T_pickaxe_OcclusionRoughnessMetallic.tga",
]

tasks = []
for tex in texture_files:
    task = unreal.AssetImportTask()
    task.filename = f"{src_tex_dir}/{tex}"
    task.destination_path = dest_tex_path
    task.automated = True
    task.save = True
    task.replace_existing = True
    task.replace_existing_settings = True
    tasks.append(task)

asset_tools.import_asset_tasks(tasks)

# 2) Load textures.
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
    raise RuntimeError("Failed to import/load one or more pickaxe textures.")

# Configure import-sensitive texture settings.
tex_normal.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
tex_normal.set_editor_property("srgb", False)
tex_orm.set_editor_property("srgb", False)

# 3) Create or load material.
material_asset_path = f"{mat_path}/{mat_name}.{mat_name}"
material = editor_lib.load_asset(material_asset_path)
if not material:
    material = asset_tools.create_asset(mat_name, mat_path, unreal.Material, unreal.MaterialFactoryNew())

if not material:
    raise RuntimeError("Failed to create/load material asset.")

# Rebuild graph from scratch.
mat_lib.delete_all_material_expressions(material)

base_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, -260)
base_sample.texture = tex_base

normal_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, 10)
normal_sample.texture = tex_normal
normal_sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)

orm_sample = mat_lib.create_material_expression(material, unreal.MaterialExpressionTextureSample, -600, 280)
orm_sample.texture = tex_orm

ao_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -330, 210)
ao_mask.set_editor_property("r", True)
ao_mask.set_editor_property("g", False)
ao_mask.set_editor_property("b", False)
ao_mask.set_editor_property("a", False)

rough_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -330, 290)
rough_mask.set_editor_property("r", False)
rough_mask.set_editor_property("g", True)
rough_mask.set_editor_property("b", False)
rough_mask.set_editor_property("a", False)

metal_mask = mat_lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -330, 370)
metal_mask.set_editor_property("r", False)
metal_mask.set_editor_property("g", False)
metal_mask.set_editor_property("b", True)
metal_mask.set_editor_property("a", False)

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

# 4) Assign material to mesh slot 0.
mesh = editor_lib.load_asset(mesh_path)
if not mesh:
    raise RuntimeError(f"Failed to load mesh: {mesh_path}")

mesh.set_material(0, material)

# 5) Save all touched assets.
for asset in [tex_base, tex_normal, tex_orm, material, mesh]:
    unreal.EditorAssetLibrary.save_loaded_asset(asset)

unreal.log("Second pass complete: stylized pickaxe material assigned.")
