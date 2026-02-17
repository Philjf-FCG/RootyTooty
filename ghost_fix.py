import unreal

def ghost_fix():
    # Use a brand new unique name to avoid the 'Locked/Already Exists' error
    map_path = "/Game/Maps/GhostTown"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("GHOST_FIX: Building GHOST TOWN - The Ultimate Visibility Test")

    # 1. Create Level
    level_sub.new_level(map_path)

    # 2. FLOOR - BRIGHT RED (Impossible to miss)
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-100))
    floor.set_actor_label("RED_GROUND")
    floor.set_actor_scale3d(unreal.Vector(1000, 1000, 1))
    mc = floor.get_editor_property("static_mesh_component")
    mc.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
    
    # 3. DEBUG MARKERS (So we know where (0,0,0) is)
    for i in range(5):
        marker = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(i*200, 0, 0))
        marker.set_actor_label(f"Marker_{i}")
        m_mc = marker.get_editor_property("static_mesh_component")
        m_mc.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere"))

    # 4. LIGHTING - NUCLEAR BRIGHT
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sc = sun.get_editor_property("light_component")
    sc.set_editor_property("intensity", 50.0) # 5x brighter than normal
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    # Sky Light - for ambient
    sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sl.get_editor_property("light_component").set_editor_property("intensity", 5.0)

    # 5. POST PROCESS - THE GREY KILLER
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp.set_editor_property("bUnbound", True)
    s = pp.get_editor_property("settings")
    
    # MANUALLY force exposure so it can't go grey
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 10.0) # Standard sunny day level
    
    pp.set_editor_property("settings", s)

    # 6. PLAYER START
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,500))
    ps.set_actor_label("PLAYER_START_FINAL")

    # 7. GAMEMODE
    world = unreal.EditorLevelLibrary.get_editor_world()
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world.get_world_settings().set_editor_property("default_game_mode", gm_bp.generated_class())

    # 8. SAVE & SET AS DEFAULT
    level_sub.save_current_level()
    
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    path_struct = unreal.SoftObjectPath(f"{map_path}.GhostTown")
    maps_settings.set_editor_property("game_default_map", path_struct)
    maps_settings.set_editor_property("editor_startup_map", path_struct)
    
    unreal.log("GHOST_FIX: SUCCESS! Map 'GhostTown' is ready. If you see a RED floor, we've won. 🤠")

if __name__ == "__main__":
    ghost_fix()
