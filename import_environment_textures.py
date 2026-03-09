import os
import zipfile
import unreal

PROJECT_DIR = unreal.Paths.project_dir()
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
TEMP_EXTRACT_DIR = os.path.join(PROJECT_DIR, "Saved", "ImportedEnvTextures")
ENV_TEXTURE_DEST_ROOT = "/Game/Environment/Textures"
ENV_MATERIAL_DEST_ROOT = "/Game/Environment/Materials"
CHAR_TEXTURE_DEST_ROOT = "/Game/CharacterLooks/Textures"
CHAR_MATERIAL_DEST_ROOT = "/Game/CharacterLooks/Materials"
HAT_TEXTURE_DEST_ROOT = "/Game/HatLooks/Textures"
HAT_MATERIAL_DEST_ROOT = "/Game/HatLooks/Materials"
MAP_PATH = "/Game/Maps/VictoryMap"
ENV_ZIP_HINTS = ["sand", "rock", "boulder", "badlands", "desert", "dune", "ground"]
CHAR_ZIP_HINTS = ["leather", "jeans", "plaid", "cloth", "fabric"]
HAT_ZIP_HINTS = ["velvet", "fabric", "hat"]


def log(msg):
    unreal.log(f"ENV_TEX: {msg}")


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _find_zip_files():
    # Prefer project-local zips so imports are self-contained and reproducible.
    project_zips = [
        os.path.join(PROJECT_DIR, name)
        for name in os.listdir(PROJECT_DIR)
        if name.lower().endswith(".zip") and (name.lower().endswith("-ue.zip") or "1k" in name.lower())
    ]

    candidates = project_zips
    if not candidates and os.path.isdir(DOWNLOADS_DIR):
        candidates = [
            os.path.join(DOWNLOADS_DIR, name)
            for name in os.listdir(DOWNLOADS_DIR)
            if name.lower().endswith(".zip") and (name.lower().endswith("-ue.zip") or "1k" in name.lower())
        ]

    if not candidates:
        return []

    return sorted(candidates)


def _split_zip_groups(zip_files):
    env_zips = []
    char_zips = []
    hat_zips = []
    for zp in zip_files:
        name = os.path.basename(zp).lower()
        if any(h in name for h in ENV_ZIP_HINTS):
            env_zips.append(zp)
            continue
        if any(h in name for h in CHAR_ZIP_HINTS):
            char_zips.append(zp)
            continue
        if any(h in name for h in HAT_ZIP_HINTS):
            hat_zips.append(zp)

    return env_zips, char_zips, hat_zips


def _extract_zip(zip_path):
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    out_dir = os.path.join(TEMP_EXTRACT_DIR, base_name)
    _ensure_dir(out_dir)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)

    return out_dir


def _collect_images(folder):
    collected = []
    for root, _, files in os.walk(folder):
        for f in files:
            lower = f.lower()
            if lower.endswith(".png") or lower.endswith(".jpg"):
                if "preview" in lower:
                    continue
                collected.append(os.path.join(root, f))
    return collected


def _import_images(file_paths, destination_path):
    unreal.EditorAssetLibrary.make_directory(destination_path)

    # Prefer automated bulk import for commandlet runs; this avoids UI/save prompt paths.
    import_data = unreal.AutomatedAssetImportData()
    import_data.destination_path = destination_path
    import_data.filenames = file_paths
    import_data.replace_existing = True
    import_data.skip_read_only = True

    imported_assets = unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(import_data)
    for imported in imported_assets:
        unreal.EditorAssetLibrary.save_loaded_asset(imported)


def _get_pack_key(texture_asset_name):
    name = texture_asset_name.lower()
    for token in ["_albedo", "-albedo", "_normal", "-normal", "_roughness", "-roughness", "_metallic", "-metallic", "_ao", "-ao", "_height", "-height"]:
        if token in name:
            return name.split(token)[0]
    return name


def _classify_texture_role(texture_asset_name):
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


def _create_material(material_name, texture_map, material_dest_root):
    material_path = f"{material_dest_root}/{material_name}"

    # Recreate materials on each run to keep graph wiring deterministic
    # without relying on version-specific graph inspection APIs.
    if unreal.EditorAssetLibrary.does_asset_exist(material_path):
        unreal.EditorAssetLibrary.delete_asset(material_path)

    factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        material_name,
        material_dest_root,
        unreal.Material,
        factory,
    )

    if not material:
        log(f"Failed to create material {material_name}")
        return None

    mel = unreal.MaterialEditingLibrary

    y = -300

    def _add_texture_sample(texture, sampler_type=None):
        nonlocal y
        node = mel.create_material_expression(material, unreal.MaterialExpressionTextureSample, -500, y)
        node.texture = texture
        if sampler_type is not None:
            node.sampler_type = sampler_type
        y += 180
        return node

    base = texture_map.get("base_color")
    if base:
        node = _add_texture_sample(base)
        mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    normal = texture_map.get("normal")
    if normal:
        node = _add_texture_sample(normal, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_NORMAL)

    roughness = texture_map.get("roughness")
    if roughness:
        node = _add_texture_sample(roughness)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_ROUGHNESS)

    metallic = texture_map.get("metallic")
    if metallic:
        node = _add_texture_sample(metallic)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_METALLIC)

    ao = texture_map.get("ao")
    if ao:
        node = _add_texture_sample(ao)
        mel.connect_material_property(node, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)

    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(material_path)
    return material


def _build_materials_from_imported(import_dest_paths, material_dest_root):
    created = {}

    for dest in import_dest_paths:
        assets = unreal.EditorAssetLibrary.list_assets(dest, recursive=True, include_folder=False)
        pack_data = {}

        for asset_path in assets:
            texture = unreal.load_asset(asset_path)
            if not isinstance(texture, unreal.Texture):
                continue

            name = texture.get_name()
            pack_key = _get_pack_key(name)
            role = _classify_texture_role(name)

            if pack_key not in pack_data:
                pack_data[pack_key] = {}
            if role != "other" and role not in pack_data[pack_key]:
                pack_data[pack_key][role] = texture

        for pack_key, tex_map in pack_data.items():
            if "base_color" not in tex_map:
                continue
            mat_name = f"M_{pack_key.replace('-', '_')}"
            mat = _create_material(mat_name, tex_map, material_dest_root)
            if mat:
                created[pack_key] = mat

    return created


def _pick_material(materials, preferred_tokens):
    for token in preferred_tokens:
        for key, mat in materials.items():
            if token in key:
                return mat
    # fallback
    for _, mat in materials.items():
        return mat
    return None


def _apply_materials_to_map(materials):
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        log("Could not load editor world")
        return

    floor_mat = _pick_material(materials, ["wavy", "sand", "desert"])
    rock_mat = _pick_material(materials, ["rock", "boulder", "badlands"])

    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    floor_hits = 0
    rock_hits = 0

    for actor in all_actors:
        label = actor.get_actor_label().lower()

        if not isinstance(actor, unreal.StaticMeshActor):
            continue

        mesh_comp = actor.get_editor_property("static_mesh_component")
        if not mesh_comp:
            continue

        if floor_mat and ("desertfloor" in label or "floor" in label):
            mesh_comp.set_material(0, floor_mat)
            floor_hits += 1
            continue

        if rock_mat and ("desertrock_" in label or "dunemound_" in label):
            mesh_comp.set_material(0, rock_mat)
            rock_hits += 1

    unreal.EditorLevelLibrary.save_current_level()
    log(f"Applied materials: floor actors={floor_hits}, rock/dune actors={rock_hits}")


def _apply_character_materials_to_map(character_materials):
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        log("Could not load editor world for character material assignment")
        return

    jeans_mat = _pick_material(character_materials, ["jeans"])
    plaid_mat = _pick_material(character_materials, ["plaid"])
    leather_mat = _pick_material(character_materials, ["leather"])

    if not (jeans_mat or plaid_mat or leather_mat):
        log("No character materials resolved for player/enemy assignment")
        return

    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    player_hits = 0
    enemy_hits = 0

    for actor in actors:
        label = actor.get_actor_label().lower()
        actor_name = actor.get_name().lower()
        comps = actor.get_components_by_class(unreal.SkeletalMeshComponent)
        if not comps:
            continue

        is_enemy = ("bandit" in label or "enemy" in label or "bandit" in actor_name or "enemy" in actor_name)
        is_player = ("wwcharacter" in label or "player" in label or "wwcharacter" in actor_name or "player" in actor_name)

        if not (is_enemy or is_player):
            continue

        for comp in comps:
            if is_player:
                if jeans_mat:
                    comp.set_material(0, jeans_mat)
                if plaid_mat:
                    comp.set_material(1, plaid_mat)
                elif leather_mat:
                    comp.set_material(1, leather_mat)
                player_hits += 1
            elif is_enemy:
                if leather_mat:
                    comp.set_material(0, leather_mat)
                if plaid_mat:
                    comp.set_material(1, plaid_mat)
                elif jeans_mat:
                    comp.set_material(1, jeans_mat)
                enemy_hits += 1

    unreal.EditorLevelLibrary.save_current_level()
    log(f"Applied character materials: player comps={player_hits}, enemy comps={enemy_hits}")


def _publish_hat_runtime_materials(hat_materials):
    player_hat = _pick_material(hat_materials, ["velvet"])
    enemy_hat = _pick_material(hat_materials, ["fabric"])

    player_dst = f"{HAT_MATERIAL_DEST_ROOT}/M_PlayerHat_Velvet"
    enemy_dst = f"{HAT_MATERIAL_DEST_ROOT}/M_EnemyHat_Fabric"

    if player_hat:
        player_src = player_hat.get_path_name()
        if unreal.EditorAssetLibrary.does_asset_exist(player_dst):
            unreal.EditorAssetLibrary.delete_asset(player_dst)
        unreal.EditorAssetLibrary.duplicate_asset(player_src, player_dst)
        log(f"Published player hat material: {player_dst}")
    else:
        log("Could not resolve velvet material for player hat")

    if enemy_hat:
        enemy_src = enemy_hat.get_path_name()
        if unreal.EditorAssetLibrary.does_asset_exist(enemy_dst):
            unreal.EditorAssetLibrary.delete_asset(enemy_dst)
        unreal.EditorAssetLibrary.duplicate_asset(enemy_src, enemy_dst)
        log(f"Published enemy hat material: {enemy_dst}")
    else:
        log("Could not resolve fabric material for enemy hat")


def main():
    zip_files = _find_zip_files()
    if not zip_files:
        unreal.log_error("ENV_TEX: No *-ue.zip files found in Downloads")
        return

    env_zips, char_zips, hat_zips = _split_zip_groups(zip_files)
    log(f"Found {len(zip_files)} texture zip files (env={len(env_zips)}, char={len(char_zips)}, hat={len(hat_zips)})")

    if not env_zips and not char_zips and not hat_zips:
        unreal.log_error("ENV_TEX: Found zip files but none match environment, character, or hat pack names")
        return

    _ensure_dir(TEMP_EXTRACT_DIR)
    unreal.EditorAssetLibrary.make_directory(ENV_TEXTURE_DEST_ROOT)
    unreal.EditorAssetLibrary.make_directory(ENV_MATERIAL_DEST_ROOT)
    unreal.EditorAssetLibrary.make_directory(CHAR_TEXTURE_DEST_ROOT)
    unreal.EditorAssetLibrary.make_directory(CHAR_MATERIAL_DEST_ROOT)
    unreal.EditorAssetLibrary.make_directory(HAT_TEXTURE_DEST_ROOT)
    unreal.EditorAssetLibrary.make_directory(HAT_MATERIAL_DEST_ROOT)

    env_import_paths = []
    char_import_paths = []
    hat_import_paths = []

    for zip_path in env_zips:
        extracted = _extract_zip(zip_path)
        images = _collect_images(extracted)
        if not images:
            log(f"No images found in {os.path.basename(zip_path)}")
            continue

        pack_name = os.path.splitext(os.path.basename(zip_path))[0].replace("-ue", "")
        dest = f"{ENV_TEXTURE_DEST_ROOT}/{pack_name}"
        _import_images(images, dest)
        env_import_paths.append(dest)
        log(f"Imported {len(images)} textures from {os.path.basename(zip_path)} -> {dest}")

    for zip_path in char_zips:
        extracted = _extract_zip(zip_path)
        images = _collect_images(extracted)
        if not images:
            log(f"No images found in {os.path.basename(zip_path)}")
            continue

        pack_name = os.path.splitext(os.path.basename(zip_path))[0].replace("-ue", "")
        dest = f"{CHAR_TEXTURE_DEST_ROOT}/{pack_name}"
        _import_images(images, dest)
        char_import_paths.append(dest)
        log(f"Imported {len(images)} textures from {os.path.basename(zip_path)} -> {dest}")

    for zip_path in hat_zips:
        extracted = _extract_zip(zip_path)
        images = _collect_images(extracted)
        if not images:
            log(f"No images found in {os.path.basename(zip_path)}")
            continue

        pack_name = os.path.splitext(os.path.basename(zip_path))[0].replace("-ue", "")
        dest = f"{HAT_TEXTURE_DEST_ROOT}/{pack_name}"
        _import_images(images, dest)
        hat_import_paths.append(dest)
        log(f"Imported {len(images)} textures from {os.path.basename(zip_path)} -> {dest}")

    env_materials = _build_materials_from_imported(env_import_paths, ENV_MATERIAL_DEST_ROOT)
    char_materials = _build_materials_from_imported(char_import_paths, CHAR_MATERIAL_DEST_ROOT)
    hat_materials = _build_materials_from_imported(hat_import_paths, HAT_MATERIAL_DEST_ROOT)
    log(f"Created materials: env={len(env_materials)}, char={len(char_materials)}, hat={len(hat_materials)}")

    if env_materials:
        _apply_materials_to_map(env_materials)

    if char_materials:
        _apply_character_materials_to_map(char_materials)

    if hat_materials:
        _publish_hat_runtime_materials(hat_materials)

    unreal.EditorAssetLibrary.save_directory(ENV_TEXTURE_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    unreal.EditorAssetLibrary.save_directory(ENV_MATERIAL_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    unreal.EditorAssetLibrary.save_directory(CHAR_TEXTURE_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    unreal.EditorAssetLibrary.save_directory(CHAR_MATERIAL_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    unreal.EditorAssetLibrary.save_directory(HAT_TEXTURE_DEST_ROOT, only_if_is_dirty=False, recursive=True)
    unreal.EditorAssetLibrary.save_directory(HAT_MATERIAL_DEST_ROOT, only_if_is_dirty=False, recursive=True)

    if env_materials or char_materials or hat_materials:
        log("Texture import and material assignment complete")
    else:
        unreal.log_warning("ENV_TEX: No materials were created from imported textures")


if __name__ == "__main__":
    main()
