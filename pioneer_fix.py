import unreal

def pioneer_fix():
    map_path = "/Game/Maps/PioneerMap"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("PIONEER_FIX: Building PIONEER TOWN - The Final Frontier of Visibility")

    # 1. Create Level
    level_sub.new_level(map_path)

    # 2. FLOOR - Huge Plane (using a material that is definitely not grey if possible)
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-100))
    floor.set_actor_label("PIONEER_GROUND")
    floor.set_actor_scale3d(unreal.Vector(5000, 5000, 1))
    mc = floor.get_editor_property("static_mesh_component")
    mc.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
    # Let's try to find a material that isn't plain grey
    grid_mat = unreal.load_asset("/Engine/EngineMaterials/DefaultWhiteGrid.DefaultWhiteGrid")
    if grid_mat:
        mc.set_material(0, grid_mat)

    # 3. TEXT RENDER - To prove the world is real
    text_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(500, 0, 200))
    text_actor.set_actor_label("WELCOME_SIGN")
    text_actor.set_actor_rotation(unreal.Rotator(0, 180, 0), True)
    text_comp = text_actor.get_editor_property("text_render")
    text_comp.set_editor_property("text", "PIONEER TOWN - WELCOME")
    text_comp.set_editor_property("world_size", 100.0)

    # 4. LIGHTING - CORRECT ATMOSPHERE SETUP
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sc = sun.get_editor_property("light_component")
    sc.set_editor_property("intensity", 20.0)
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    # CRITICAL: This connects the light to the sky
    sc.set_editor_property("atmosphere_sun_light", True)
    
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0))
    
    sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl_comp = sl.get_editor_property("light_component")
    sl_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sl_comp.set_editor_property("real_time_capture", True)

    # 5. FOG - To fill the void
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0,0,0))
    fog.set_actor_label("PIONEER_FOG")

    # 6. POST PROCESS - STABLE EXPOSURE
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp.set_editor_property("bUnbound", True)
    s = pp.get_editor_property("settings")
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 10.0)
    pp.set_editor_property("settings", s)

    # 7. PLAYER START
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,500))
    ps.set_actor_label("PIONEER_PLAYER_START")

    # 8. GAMEMODE
    world = unreal.EditorLevelLibrary.get_editor_world()
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world.get_world_settings().set_editor_property("default_game_mode", gm_bp.generated_class())

    # 9. SAVE & SET AS DEFAULT
    level_sub.save_current_level()
    
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    path_struct = unreal.SoftObjectPath(f"{map_path}.PioneerMap")
    maps_settings.set_editor_property("game_default_map", path_struct)
    maps_settings.set_editor_property("editor_startup_map", path_struct)
    
    unreal.log("PIONEER_FIX: SUCCESS! PioneerMap is ready. Look for the sign that says 'PIONEER TOWN'. 🤠")

if __name__ == "__main__":
    pioneer_fix()
