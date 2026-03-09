import unreal

HAT_TEXTURE_DEST_ROOT = "/Game/HatLooks/Textures"
HAT_MATERIAL_DEST_ROOT = "/Game/HatLooks/Materials"


def log(msg):
    unreal.log(f"HAT_RUNTIME: {msg}")


def classify_texture_role(texture_asset_name):
    n = texture_asset_name.lower()
    if "albedo" in n or "basecolor" in n or "diffuse" in n:
        return "base_color"
    if "normal" in n:
        return "normal"
    if "roughness" in n:
        return "roughness"
    if "metallic" in n:
        return "metallic"
    if n.endswith("_ao") or "-ao" in n or "ambientocclusion" in n:
        return "ao"
    return "other"


def pack_key(texture_asset_name):
    name = texture_asset_name.lower()
    for token in [
        "_albedo",
        "-albedo",
        "_basecolor",
        "-basecolor",
        "_diffuse",
        "-diffuse",
        "_normal",
        "-normal",
        "_roughness",
        "-roughness",
        "_metallic",
        "-metallic",
        "_ao",
        "-ao",
        "_height",
        "-height",
    ]:
        if token in name:
            return name.split(token)[0]
    return name


def scan_hat_texture_packs():
    assets = unreal.EditorAssetLibrary.list_assets(HAT_TEXTURE_DEST_ROOT, recursive=True, include_folder=False)
    packs = {}
    for asset_path in assets:
        tex = unreal.load_asset(asset_path)
        if not isinstance(tex, unreal.Texture):
            continue

        key = pack_key(tex.get_name())
        role = classify_texture_role(tex.get_name())
        if role == "other":
            continue

        if key not in packs:
            packs[key] = {}
        if role not in packs[key]:
            packs[key][role] = tex

    return packs


def create_material(material_name, texture_map, base_color_tint=None):
    unreal.EditorAssetLibrary.make_directory(HAT_MATERIAL_DEST_ROOT)
    material_path = f"{HAT_MATERIAL_DEST_ROOT}/{material_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(material_path):
        unreal.EditorAssetLibrary.delete_asset(material_path)

    factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        material_name,
        HAT_MATERIAL_DEST_ROOT,
        unreal.Material,
        factory,
    )
    if not material:
        log(f"Failed to create {material_name}")
        return None

    mel = unreal.MaterialEditingLibrary
    y = -300

    def add_texture_sample(texture, sampler_type=None):
        nonlocal y
        node = mel.create_material_expression(material, unreal.MaterialExpressionTextureSample, -500, y)
        node.texture = texture
        if sampler_type is not None:
            node.sampler_type = sampler_type
        y += 180
        return node

    base = texture_map.get("base_color")
    if base:
        base_node = add_texture_sample(base)
        if base_color_tint is not None:
            tint = mel.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -250, -260)
            tint.constant = base_color_tint
            mul = mel.create_material_expression(material, unreal.MaterialExpressionMultiply, -80, -260)
            mel.connect_material_expressions(base_node, "RGB", mul, "A")
            mel.connect_material_expressions(tint, "", mul, "B")
            mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
        else:
            mel.connect_material_property(base_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    normal = texture_map.get("normal")
    if normal:
        node = add_texture_sample(normal, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_NORMAL)

    roughness = texture_map.get("roughness")
    if roughness:
        node = add_texture_sample(roughness)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_ROUGHNESS)

    metallic = texture_map.get("metallic")
    if metallic:
        node = add_texture_sample(metallic)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_METALLIC)

    ao = texture_map.get("ao")
    if ao:
        node = add_texture_sample(ao)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)

    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(material_path)
    return material


def choose_pack(packs, required_tokens, fallback_tokens):
    for key in packs.keys():
        k = key.lower()
        if all(t in k for t in required_tokens):
            return key
    for key in packs.keys():
        k = key.lower()
        if any(t in k for t in fallback_tokens):
            return key
    return None


def main():
    packs = scan_hat_texture_packs()
    if not packs:
        unreal.log_error("HAT_RUNTIME: No hat textures found under /Game/HatLooks/Textures")
        return

    player_key = choose_pack(packs, ["fabric", "162"], ["fabric"])
    enemy_key = choose_pack(packs, ["velvet"], ["velvet"])

    if player_key and "base_color" in packs[player_key]:
        create_material(
            "M_PlayerHat_Fabric162_Lilac",
            packs[player_key],
            unreal.LinearColor(0.73, 0.59, 0.83, 1.0),
        )
        log(f"Published M_PlayerHat_Fabric162_Lilac from {player_key}")
    else:
        unreal.log_error("HAT_RUNTIME: Could not resolve player fabric_162 hat pack with base color")

    if enemy_key and "base_color" in packs[enemy_key]:
        create_material(
            "M_EnemyHat_BlackVelvet",
            packs[enemy_key],
            unreal.LinearColor(0.02, 0.02, 0.02, 1.0),
        )
        log(f"Published M_EnemyHat_BlackVelvet from {enemy_key}")
    else:
        unreal.log_error("HAT_RUNTIME: Could not resolve enemy velvet hat pack with base color")

    unreal.EditorAssetLibrary.save_directory(HAT_MATERIAL_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    log("Done")


if __name__ == "__main__":
    main()
