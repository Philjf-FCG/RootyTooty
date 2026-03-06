import unreal
import random

MAP_PATH = "/Game/Maps/VictoryMap"


def _load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _spawn_static(mesh, label, location, rotation=None, scale=None):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location)
    if not actor:
        return None

    actor.set_actor_label(label)
    if rotation:
        actor.set_actor_rotation(rotation, False)
    if scale:
        actor.set_actor_scale3d(scale)

    mesh_comp = actor.get_editor_property("static_mesh_component")
    if mesh and mesh_comp:
        mesh_comp.set_editor_property("static_mesh", mesh)

    return actor


def _remove_old_environment(world):
    remove_class_names = {
        "DirectionalLight",
        "SkyLight",
        "SkyAtmosphere",
        "ExponentialHeightFog",
        "VolumetricCloud",
        "PostProcessVolume",
    }

    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        label = actor.get_actor_label().lower()

        actor_class = actor.get_class() if hasattr(actor, "get_class") else None
        actor_class_name = actor_class.get_name() if actor_class else ""

        if actor_class_name in remove_class_names:
            actor.destroy_actor()
            continue

        if isinstance(actor, unreal.StaticMeshActor):
            mesh_comp = actor.get_editor_property("static_mesh_component")
            mesh = mesh_comp.get_editor_property("static_mesh") if mesh_comp else None
            mesh_path = mesh.get_path_name() if mesh else ""
            loc = actor.get_actor_location()

            label_match = any(k in label for k in ["floor", "tile", "grid", "ground", "block"])
            basic_shape_match = "/Engine/BasicShapes/" in mesh_path
            near_ground = abs(loc.z) < 140.0

            if basic_shape_match and near_ground and label_match:
                actor.destroy_actor()


def _spawn_desert_floor():
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -50.0)
    )
    floor.set_actor_label("DesertFloor")

    mesh_comp = floor.get_editor_property("static_mesh_component")
    plane_mesh = _load_first([
        "/Engine/BasicShapes/Plane.Plane",
        "/Engine/BasicShapes/Cube.Cube",
    ])
    if plane_mesh and mesh_comp:
        mesh_comp.set_editor_property("static_mesh", plane_mesh)

    floor.set_actor_scale3d(unreal.Vector(280.0, 280.0, 1.0))

    # Pick the most earth-like material available in-project, then fallback to engine default.
    floor_material = _load_first([
        "/Game/Characters/Mannequins/Materials/M_Mannequin.M_Mannequin",
        "/Game/Mannequins/Materials/M_Mannequin.M_Mannequin",
        "/Engine/EngineMaterials/DefaultDiffuse.DefaultDiffuse",
        "/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial",
    ])
    if floor_material and mesh_comp:
        mesh_comp.set_material(0, floor_material)


def _spawn_dune_variation():
    dune_mesh = _load_first([
        "/Engine/BasicShapes/Sphere.Sphere",
        "/Engine/BasicShapes/Cube.Cube",
    ])

    for index in range(42):
        x = random.uniform(-18000.0, 18000.0)
        y = random.uniform(-18000.0, 18000.0)
        z = random.uniform(-90.0, -35.0)
        scale = unreal.Vector(
            random.uniform(10.0, 42.0),
            random.uniform(10.0, 42.0),
            random.uniform(0.18, 0.65),
        )
        _spawn_static(
            dune_mesh,
            f"DuneMound_{index:02}",
            unreal.Vector(x, y, z),
            unreal.Rotator(random.uniform(-4.0, 4.0), random.uniform(0.0, 360.0), random.uniform(-4.0, 4.0)),
            scale,
        )


def _spawn_desert_props():
    cactus_mesh = _load_first([
        "/Engine/BasicShapes/Cylinder.Cylinder",
    ])
    rock_mesh = _load_first([
        "/Engine/BasicShapes/Sphere.Sphere",
    ])
    barrel_mesh = _load_first([
        "/Engine/BasicShapes/Cylinder.Cylinder",
    ])
    crate_mesh = _load_first([
        "/Engine/BasicShapes/Cube.Cube",
    ])

    for index in range(70):
        _spawn_static(
            cactus_mesh,
            f"Cactus_{index:03}",
            unreal.Vector(random.uniform(-17000.0, 17000.0), random.uniform(-17000.0, 17000.0), -52.0),
            unreal.Rotator(0.0, random.uniform(0.0, 360.0), 0.0),
            unreal.Vector(random.uniform(0.5, 1.2), random.uniform(0.5, 1.2), random.uniform(1.0, 2.8)),
        )

    for index in range(75):
        _spawn_static(
            rock_mesh,
            f"DesertRock_{index:03}",
            unreal.Vector(random.uniform(-17000.0, 17000.0), random.uniform(-17000.0, 17000.0), -56.0),
            unreal.Rotator(random.uniform(-10.0, 10.0), random.uniform(0.0, 360.0), random.uniform(-10.0, 10.0)),
            unreal.Vector(random.uniform(0.6, 2.2), random.uniform(0.6, 2.2), random.uniform(0.25, 1.1)),
        )

    for index in range(20):
        _spawn_static(
            barrel_mesh,
            f"Barrel_{index:02}",
            unreal.Vector(random.uniform(-6000.0, 6000.0), random.uniform(-6000.0, 6000.0), -46.0),
            unreal.Rotator(0.0, random.uniform(0.0, 360.0), 0.0),
            unreal.Vector(random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.8, 1.3)),
        )

    for index in range(16):
        _spawn_static(
            crate_mesh,
            f"Crate_{index:02}",
            unreal.Vector(random.uniform(-6000.0, 6000.0), random.uniform(-6000.0, 6000.0), -46.0),
            unreal.Rotator(0.0, random.uniform(0.0, 360.0), 0.0),
            unreal.Vector(random.uniform(0.7, 1.4), random.uniform(0.7, 1.4), random.uniform(0.6, 1.2)),
        )


def _spawn_sky_and_lighting():
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 3000.0)
    )
    sun.set_actor_label("DesertSun")
    sun.set_actor_rotation(unreal.Rotator(-40.0, -25.0, 0.0), True)
    sun_comp = sun.get_editor_property("light_component")
    sun_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sun_comp.set_editor_property("intensity", 85000.0)
    sun_comp.set_editor_property("atmosphere_sun_light", True)
    sun_comp.set_editor_property("temperature", 6200.0)

    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0)
    )
    sky.set_actor_label("DesertSky")

    clouds = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.VolumetricCloud, unreal.Vector(0.0, 0.0, 1500.0)
    )
    if clouds:
        clouds.set_actor_label("DesertClouds")

    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, 0.0)
    )
    if fog:
        fog.set_actor_label("DesertFog")
        fog_comp = fog.get_editor_property("component")
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.01)
            fog_comp.set_editor_property("fog_height_falloff", 0.12)

    skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0.0, 0.0, 0.0)
    )
    skylight.set_actor_label("DesertSkyLight")
    skylight_comp = skylight.get_editor_property("light_component")
    skylight_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    skylight_comp.set_editor_property("real_time_capture", True)
    skylight_comp.set_editor_property("intensity", 1.6)

    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PostProcessVolume, unreal.Vector(0.0, 0.0, 0.0)
    )
    pp.set_actor_label("DesertPostProcess")
    pp.set_editor_property("bUnbound", True)
    settings = pp.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.4)
    settings.set_editor_property("override_color_saturation", True)
    settings.set_editor_property("color_saturation", unreal.Vector4(1.06, 1.03, 0.95, 1.0))
    pp.set_editor_property("settings", settings)


def apply_desert_environment():
    unreal.log("ENV_FIX: Loading VictoryMap...")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)

    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        unreal.log_error("ENV_FIX: Failed to get editor world")
        return

    _remove_old_environment(world)
    _spawn_desert_floor()
    _spawn_sky_and_lighting()
    _spawn_dune_variation()
    _spawn_desert_props()

    unreal.EditorLevelLibrary.save_current_level()
    unreal.log("ENV_FIX: Desert environment update complete for VictoryMap")


if __name__ == "__main__":
    apply_desert_environment()
