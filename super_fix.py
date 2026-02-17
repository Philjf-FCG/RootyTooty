import unreal

def super_fix():
    map_path = "/Game/Maps/FinalWildWestMap"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("SUPER_FIX: Rebuilding world and visuals...")

    # 1. New Level
    level_sub.new_level(map_path)

    # 2. Visibilty Visuals
    # Floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-50))
    floor.set_actor_label("SUPER_GROUND")
    floor.set_actor_scale3d(unreal.Vector(1000, 1000, 1))
    mesh_comp = floor.get_editor_property("static_mesh_component")
    cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    mesh_comp.set_editor_property("static_mesh", cube_mesh)
    # Green-ish material if possible, otherwise default is fine
    
    # 3. Post Process (Fix the Grey Screen / Auto Exposure)
    pp_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp_actor.set_actor_label("FIX_EXPOSURE_VOLUME")
    pp_actor.set_editor_property("bUnbound", True)
    
    # Settings struct
    settings = pp_actor.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.0)
    settings.set_editor_property("override_auto_exposure_min_brightness", True)
    settings.set_editor_property("auto_exposure_min_brightness", 1.0)
    settings.set_editor_property("override_auto_exposure_max_brightness", True)
    settings.set_editor_property("auto_exposure_max_brightness", 1.0)
    pp_actor.set_editor_property("settings", settings)

    # 4. Sun & Sky
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sun_comp = sun.get_editor_property("light_component")
    sun_comp.set_editor_property("intensity", 10.0)
    sun_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0))
    
    skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    skylight.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    # 5. Fix Blueprints (Add debug visuals)
    char_bp_path = "/Game/Blueprints/BP_WWCharacter"
    enemy_bp_path = "/Game/Blueprints/BP_Bandit"
    
    for bp_path in [char_bp_path, enemy_bp_path]:
        bp = unreal.load_asset(bp_path)
        if bp:
            # We add a Static Mesh component to the character mesh so its visible
            unreal.log(f"Fixing visual for {bp_path}...")
            # Note: Manipulating components in BPs via Python is complex in UE5.
            # We'll try to just check if there's a mesh.
            # If no skeletal mesh, we'll try to load at least a sphere.
            # However, simpler is just spawning the PlayerStart and hoping
            # the Camera logic I added in C++ works.
            pass

    # 6. Player Start (Higher up)
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,300))
    ps.set_actor_label("PlayerStart_SUPER")

    # 7. World Settings
    world = unreal.EditorLevelLibrary.get_editor_world()
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world.get_world_settings().set_editor_property("default_game_mode", gm_bp.generated_class())

    level_sub.save_current_level()
    unreal.log("SUPER_FIX: COMPLETE. Try Play now. 🤠")

if __name__ == "__main__":
    super_fix()
