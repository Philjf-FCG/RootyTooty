import unreal
import random


def _load_first_asset(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _set_static_mesh(actor, mesh):
    if not actor or not mesh:
        return False
    mesh_comp = actor.get_editor_property("static_mesh_component")
    if not mesh_comp:
        return False
    mesh_comp.set_editor_property("static_mesh", mesh)
    return True


def _spawn_static(mesh, label, location, rotation=None, scale=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location)
    if not actor:
        return None
    actor.set_actor_label(label)
    if rotation:
        actor.set_actor_rotation(rotation, False)
    if scale:
        actor.set_actor_scale3d(scale)
    _set_static_mesh(actor, mesh)
    return actor


def _find_static_mesh_by_keywords(keywords):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    all_meshes = registry.get_assets_by_class("StaticMesh", True)
    wanted = [k.lower() for k in keywords]
    for asset_data in all_meshes:
        name = asset_data.asset_name.lower()
        path = str(asset_data.package_name).lower()
        if any(k in name or k in path for k in wanted):
            loaded = asset_data.get_asset()
            if loaded:
                return loaded
    return None


def _configure_player_view():
    bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Blueprints/BP_WWCharacter")
    if not bp_cls:
        unreal.log_warning("FIX_WARNING: Could not load BP_WWCharacter for view update")
        return

    cdo = unreal.get_default_object(bp_cls)

    try:
        spring_arm = cdo.get_editor_property("SpringArmComp")
    except Exception:
        spring_arm = None

    try:
        camera = cdo.get_editor_property("CameraComp")
    except Exception:
        camera = None

    if spring_arm:
        try:
            spring_arm.set_editor_property("target_arm_length", 900.0)
            spring_arm.set_editor_property("relative_rotation", unreal.Rotator(-28.0, 20.0, 0.0))
            spring_arm.set_editor_property("do_collision_test", True)
        except Exception as e:
            unreal.log_warning(f"FIX_WARNING: SpringArm view update failed: {e}")

    if camera:
        try:
            camera.set_editor_property("field_of_view", 95.0)
            camera.set_editor_property("use_pawn_control_rotation", False)
        except Exception as e:
            unreal.log_warning(f"FIX_WARNING: Camera view update failed: {e}")

    unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/BP_WWCharacter")
    unreal.log("FIX_PROGRESS: Applied requested gameplay view change on BP_WWCharacter")

def create_wild_west_map():
    new_map_path = "/Game/Maps/WildWestMap"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("FIX_START: Ensuring clean 'WildWestMap' with dynamic lighting...")

    # 1. Switch away from current level to allow deletion
    level_sub.new_level("")

    # 2. Check and delete existing asset if it exists
    if unreal.EditorAssetLibrary.does_asset_exist(new_map_path):
        unreal.log(f"FIX_PROGRESS: Deleting existing {new_map_path}...")
        unreal.EditorAssetLibrary.delete_asset(new_map_path)

    # 3. Create fresh WildWestMap
    if not level_sub.new_level(new_map_path):
        unreal.log_error("FIX_ERROR: Failed to create new level at WildWestMap.")
        return

    # 4. Add desert floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -50))
    if floor:
        floor.set_actor_label("DesertFloor")
        floor.set_actor_scale3d(unreal.Vector(160, 160, 0.8))
        floor_mesh = _load_first_asset([
            "/Engine/BasicShapes/Plane.Plane",
            "/Engine/BasicShapes/Cube.Cube",
        ])
        _set_static_mesh(floor, floor_mesh)
        mesh_comp = floor.get_editor_property("static_mesh_component")
        sand_mat = _load_first_asset([
            "/Engine/EngineMaterials/DefaultDiffuse.DefaultDiffuse",
            "/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial",
        ])
        if mesh_comp and sand_mat:
            mesh_comp.set_material(0, sand_mat)
        unreal.log("FIX_PROGRESS: Added large desert floor")

    # 5. Add Player Start
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-300, -400, 160))
    if ps:
        ps.set_actor_label("PlayerStart")
        ps.set_actor_rotation(unreal.Rotator(0, 20, 0), False)
        unreal.log("FIX_PROGRESS: Added PlayerStart")

    # 6. Add blazing dynamic sun
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2200))
    if light:
        light.set_actor_label("BlazingSun")
        light.set_actor_rotation(unreal.Rotator(-38, -28, 0), True)
        light_comp = light.get_editor_property("light_component")
        light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        light_comp.set_editor_property("intensity", 20.0)
        light_comp.set_editor_property("temperature", 6500.0)
        unreal.log("FIX_PROGRESS: Added blazing sun")

    # 6b. Add atmosphere/exponential fog for heat haze depth
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    if fog:
        fog_comp = fog.get_editor_property("component")
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.015)
            fog_comp.set_editor_property("fog_height_falloff", 0.2)

    # 7. Add Sky Light for ambient brightness
    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 0))
    if sky_light:
        sky_light.set_actor_label("SkyLight")
        sky_light_comp = sky_light.get_editor_property("light_component")
        sky_light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        sky_light_comp.set_editor_property("real_time_capture", True)
        sky_light_comp.set_editor_property("intensity", 1.2)
        unreal.log("FIX_PROGRESS: Added Dynamic Sky Light")

    # 6c. Post process for brighter blue-sky/desert readability
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    if pp:
        pp.set_actor_label("WildWestPostProcess")
        pp.set_editor_property("bUnbound", True)
        settings = pp.get_editor_property("settings")
        settings.set_editor_property("override_auto_exposure_method", True)
        settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
        settings.set_editor_property("override_auto_exposure_bias", True)
        settings.set_editor_property("auto_exposure_bias", 0.8)
        settings.set_editor_property("override_bloom_intensity", True)
        settings.set_editor_property("bloom_intensity", 0.25)
        settings.set_editor_property("override_scene_fringe_intensity", True)
        settings.set_editor_property("scene_fringe_intensity", 0.0)
        pp.set_editor_property("settings", settings)

    # 7b. Desert prop placement (prefer real assets by keyword, fallback to primitives)
    cactus_mesh = _find_static_mesh_by_keywords(["cactus", "prickly", "yucca"]) or _load_first_asset(["/Engine/BasicShapes/Cylinder.Cylinder"])
    desert_plant_mesh = _find_static_mesh_by_keywords(["desert", "shrub", "bush", "plant"]) or _load_first_asset(["/Engine/BasicShapes/Cone.Cone"])
    dead_cattle_mesh = _find_static_mesh_by_keywords(["cattle", "cow", "carcass", "bones", "skull"]) or _load_first_asset(["/Engine/BasicShapes/Capsule.Capsule"])
    lizard_mesh = _find_static_mesh_by_keywords(["lizard", "iguana", "gecko"]) or _load_first_asset(["/Engine/BasicShapes/Sphere.Sphere"])
    barrel_mesh = _find_static_mesh_by_keywords(["barrel"]) or _load_first_asset(["/Engine/BasicShapes/Cylinder.Cylinder"])
    crate_mesh = _find_static_mesh_by_keywords(["crate", "box", "wood"]) or _load_first_asset(["/Engine/BasicShapes/Cube.Cube"])
    wagon_mesh = _find_static_mesh_by_keywords(["wagon", "cart", "wheel"]) or _load_first_asset(["/Engine/BasicShapes/Torus.Torus", "/Engine/BasicShapes/Cylinder.Cylinder"])
    rock_mesh = _find_static_mesh_by_keywords(["rock", "stone", "boulder"]) or _load_first_asset(["/Engine/BasicShapes/Sphere.Sphere"])

    for index in range(95):
        location = unreal.Vector(random.uniform(-9500, 9500), random.uniform(-9500, 9500), -45)
        _spawn_static(
            cactus_mesh,
            f"Cactus_{index:03}",
            location,
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(random.uniform(0.6, 1.6), random.uniform(0.6, 1.6), random.uniform(1.2, 2.8)),
        )

    for index in range(70):
        location = unreal.Vector(random.uniform(-9500, 9500), random.uniform(-9500, 9500), -48)
        _spawn_static(
            desert_plant_mesh,
            f"DesertPlant_{index:03}",
            location,
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(random.uniform(0.35, 1.2), random.uniform(0.35, 1.2), random.uniform(0.35, 1.1)),
        )

    for index in range(9):
        location = unreal.Vector(random.uniform(-6000, 6000), random.uniform(-6000, 6000), -22)
        _spawn_static(
            dead_cattle_mesh,
            f"DeadCattle_{index:02}",
            location,
            unreal.Rotator(random.uniform(-5, 5), random.uniform(0, 360), random.uniform(-35, 35)),
            unreal.Vector(random.uniform(1.0, 1.7), random.uniform(0.7, 1.2), random.uniform(0.22, 0.5)),
        )

    for index in range(45):
        location = unreal.Vector(random.uniform(-8500, 8500), random.uniform(-8500, 8500), -50)
        _spawn_static(
            rock_mesh,
            f"DesertRock_{index:02}",
            location,
            unreal.Rotator(random.uniform(-8, 8), random.uniform(0, 360), random.uniform(-8, 8)),
            unreal.Vector(random.uniform(0.7, 2.6), random.uniform(0.7, 2.6), random.uniform(0.35, 1.5)),
        )

    for index in range(28):
        location = unreal.Vector(random.uniform(-4200, 4200), random.uniform(-4200, 4200), -42)
        _spawn_static(
            barrel_mesh,
            f"Barrel_{index:02}",
            location,
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(random.uniform(0.7, 1.2), random.uniform(0.7, 1.2), random.uniform(0.8, 1.3)),
        )

    for index in range(24):
        location = unreal.Vector(random.uniform(-4200, 4200), random.uniform(-4200, 4200), -42)
        _spawn_static(
            crate_mesh,
            f"Crate_{index:02}",
            location,
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(random.uniform(0.8, 1.4), random.uniform(0.8, 1.4), random.uniform(0.6, 1.2)),
        )

    for index in range(10):
        location = unreal.Vector(random.uniform(-5000, 5000), random.uniform(-5000, 5000), -40)
        _spawn_static(
            wagon_mesh,
            f"WagonProp_{index:02}",
            location,
            unreal.Rotator(0, random.uniform(0, 360), 0),
            unreal.Vector(random.uniform(0.7, 1.6), random.uniform(0.7, 1.6), random.uniform(0.5, 1.2)),
        )

    # "Alive" lizards: use moving enemy blueprint if available, else static lizard markers
    lizard_bp = unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
    if lizard_bp:
        for index in range(12):
            location = unreal.Vector(random.uniform(-4500, 4500), random.uniform(-4500, 4500), 80)
            lizard_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(lizard_bp, location)
            if lizard_actor:
                lizard_actor.set_actor_label(f"LizardAlive_{index:02}")
                lizard_actor.set_actor_scale3d(unreal.Vector(0.24, 0.24, 0.24))
    else:
        for index in range(12):
            location = unreal.Vector(random.uniform(-4500, 4500), random.uniform(-4500, 4500), -35)
            _spawn_static(
                lizard_mesh,
                f"LizardAlive_{index:02}",
                location,
                unreal.Rotator(0, random.uniform(0, 360), 0),
                unreal.Vector(0.12, 0.2, 0.08),
            )

    unreal.log("FIX_PROGRESS: Desert biome populated with cacti, rocks, barrels, crates, wagon props, and critters")

    # 8. Set GameMode Override
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        settings = world.get_world_settings()
        gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
        if gm_bp:
            settings.set_editor_property("default_game_mode", gm_bp.generated_class())
            unreal.log("FIX_PROGRESS: Assigned BP_WWGameMode")

    # 8b. Apply requested player view change
    _configure_player_view()

    # 9. Save
    level_sub.save_current_level()
    
    # 10. Update Project Settings safely
    try:
        maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
        path_struct = unreal.SoftObjectPath(f"{new_map_path}.WildWestMap")
        maps_settings.set_editor_property("game_default_map", path_struct)
        maps_settings.set_editor_property("editor_startup_map", path_struct)
        unreal.log("FIX_PROGRESS: Updated Project Map Settings")
    except Exception as e:
        unreal.log_warning(f"FIX_WARNING: Could not update project settings: {e}")
    
    unreal.log("FIX_COMPLETE: WildWestMap updated to realistic Wild West desert style. Press Play. 🤠")

if __name__ == "__main__":
    create_wild_west_map()
