import unreal

BASE_TEX = "/Game/ImportedCharacters/Bobrito/Textures/Costume_Base_color.Costume_Base_color"
MAT_PATH = "/Game/ImportedCharacters/Bobrito"
MAT_NAME = "M_BobritoImported"
MESH_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy"


def make_material() -> str | None:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = unreal.load_asset(f"{MAT_PATH}/{MAT_NAME}")
    if not mat:
        mat = tools.create_asset(MAT_NAME, MAT_PATH, unreal.Material, unreal.MaterialFactoryNew())

    base_tex = unreal.load_asset(BASE_TEX)
    if not mat or not base_tex:
        unreal.log_error("[BOBRITO_MAT] Missing material or base texture")
        return None

    mel = unreal.MaterialEditingLibrary
    mel.delete_all_material_expressions(mat)

    tex_node = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -450, 0)
    tex_node.set_editor_property("texture", base_tex)
    mel.connect_material_property(tex_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(f"{MAT_PATH}/{MAT_NAME}", only_if_is_dirty=False)
    return f"{MAT_PATH}/{MAT_NAME}.{MAT_NAME}"


def assign_material(mat_path: str) -> None:
    mesh = unreal.load_asset(MESH_PATH)
    mat = unreal.load_asset(mat_path)
    if not mesh or not mat:
        unreal.log_error("[BOBRITO_MAT] Missing mesh or material for assignment")
        return

    mats = mesh.get_editor_property("materials")
    if not mats:
        mats = [unreal.SkeletalMaterial()]

    for i in range(len(mats)):
        entry = mats[i]
        entry.material_interface = mat
        mats[i] = entry

    mesh.set_editor_property("materials", mats)
    unreal.EditorAssetLibrary.save_asset("/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy", only_if_is_dirty=False)
    unreal.log(f"[BOBRITO_MAT] Assigned {mat_path} to {len(mats)} slot(s)")


def main() -> None:
    mat_path = make_material()
    if mat_path:
        assign_material(mat_path)


if __name__ == "__main__":
    main()
