import unreal

SRC_DIR = r"C:/Unreal Projects/rooty/RootyTooty/Saved/ImportedCharacters/bobrito-bandito-game-ready-3d-model-free/textures"
DEST_TEX = "/Game/ImportedCharacters/Bobrito/Textures"
MAT_PATH = "/Game/ImportedCharacters/Bobrito"
MAT_NAME = "M_BobritoImported"
MESH_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy"


def import_texture(file_name: str) -> str | None:
    src = f"{SRC_DIR}/{file_name}"
    if not unreal.Paths.file_exists(src):
        unreal.log_warning(f"[BOBRITO_TEX] Missing source: {src}")
        return None

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", src)
    task.set_editor_property("destination_path", DEST_TEX)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("replace_existing_settings", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = task.get_editor_property("imported_object_paths")
    if imported:
        unreal.log(f"[BOBRITO_TEX] Imported {file_name} -> {imported[0]}")
        return imported[0]
    return None


def make_material(base_tex_path: str | None, normal_tex_path: str | None, ao_tex_path: str | None) -> str | None:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = unreal.load_asset(f"{MAT_PATH}/{MAT_NAME}")
    if not mat:
        factory = unreal.MaterialFactoryNew()
        mat = tools.create_asset(MAT_NAME, MAT_PATH, unreal.Material, factory)

    if not mat:
        unreal.log_error("[BOBRITO_TEX] Failed to create/load material")
        return None

    mel = unreal.MaterialEditingLibrary
    mel.delete_all_material_expressions(mat)

    x = -600
    y = -100

    base_tex = unreal.load_asset(base_tex_path) if base_tex_path else None
    normal_tex = unreal.load_asset(normal_tex_path) if normal_tex_path else None
    ao_tex = unreal.load_asset(ao_tex_path) if ao_tex_path else None

    base_node = None
    ao_node = None

    if base_tex:
        base_node = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, x, y)
        base_node.set_editor_property("texture", base_tex)

    if ao_tex:
        ao_node = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, x, y + 240)
        ao_node.set_editor_property("texture", ao_tex)

    if base_node and ao_node:
        mult = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, 20)
        mel.connect_material_expressions(base_node, "RGB", mult, "A")
        mel.connect_material_expressions(ao_node, "RGB", mult, "B")
        mel.connect_material_property(mult, "", unreal.MaterialProperty.MP_BASE_COLOR)
    elif base_node:
        mel.connect_material_property(base_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    if normal_tex:
        normal_node = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, x, y + 480)
        normal_node.set_editor_property("texture", normal_tex)
        mel.connect_material_property(normal_node, "RGB", unreal.MaterialProperty.MP_NORMAL)

    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(f"{MAT_PATH}/{MAT_NAME}", only_if_is_dirty=False)
    return f"{MAT_PATH}/{MAT_NAME}.{MAT_NAME}"


def assign_to_mesh(mat_path: str) -> None:
    mesh = unreal.load_asset(MESH_PATH)
    mat = unreal.load_asset(mat_path) if mat_path else None
    if not mesh or not mat:
        unreal.log_error("[BOBRITO_TEX] Missing mesh or material for assignment")
        return

    mats = mesh.get_editor_property("materials")
    if not mats:
        mats = [unreal.SkeletalMaterial()]

    for i in range(len(mats)):
        skm = mats[i]
        skm.material_interface = mat
        mats[i] = skm

    mesh.set_editor_property("materials", mats)
    unreal.EditorAssetLibrary.save_asset("/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy", only_if_is_dirty=False)
    unreal.log(f"[BOBRITO_TEX] Assigned {mat_path} to {len(mats)} material slot(s)")


def main() -> None:
    base = import_texture("Costume_Base_color.png") or import_texture("Material_baseColor.png")
    normal = import_texture("Costume_Normal_OpenGL.png")
    ao = import_texture("Costume_Mixed_AO.png")

    mat = make_material(base, normal, ao)
    if mat:
        assign_to_mesh(mat)


if __name__ == "__main__":
    main()
