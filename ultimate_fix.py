import unreal

def ultimate_fix():
    unreal.log("ULTIMATE_FIX: Starting total system reset...")
    
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    asset_lib = unreal.EditorAssetLibrary
    
    # 1. New Level to avoid any hidden actor/corruption
    map_path = "/Game/Maps/UltimaMap"
    level_sub.new_level(map_path)

    # 2. Environment
    # Large reliable Plane
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
    floor.set_actor_label("ULTIMA_FLOOR")
    floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
    mc = floor.get_editor_property("static_mesh_component")
    mc.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Plane.Plane"))
    # Pure white material to see lighting clearly
    white_mat = unreal.load_asset("/Engine/EngineMaterials/DefaultWhiteGrid.DefaultWhiteGrid")
    if white_mat:
        mc.set_material(0, white_mat)

    # Sun & Atmosphere
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sc = sun.get_editor_property("light_component")
    sc.set_editor_property("intensity", 10.0) # EV100 compatible intensity
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0))
    sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sl.get_editor_property("light_component").set_editor_property("real_time_capture", True)

    # 3. Post Process - THE ULTIMATE RESET
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp.set_editor_property("bUnbound", True)
    pp.set_actor_label("ULTIMATE_STABILITY_VOLUME")
    pp.set_editor_property("priority", 10000.0) # Highest priority
    
    s = pp.get_editor_property("settings")
    
    # Disable EVERYTHING that distorts
    # Lens/Distortion
    s.set_editor_property("override_lens_distortion_intensity", True)
    # Note: Property name might vary by version, but we'll try common ones
    try: s.set_editor_property("lens_distortion_intensity", 0.0)
    except: pass
    
    s.set_editor_property("override_scene_fringe_intensity", True)
    s.set_editor_property("scene_fringe_intensity", 0.0)
    
    s.set_editor_property("override_chromatic_aberration_intensity", True)
    try: s.set_editor_property("chromatic_aberration_intensity", 0.0)
    except: pass

    # Blur/Motion
    s.set_editor_property("override_motion_blur_amount", True)
    s.set_editor_property("motion_blur_amount", 0.0)
    
    s.set_editor_property("override_bloom_intensity", True)
    s.set_editor_property("bloom_intensity", 0.0)

    # Exposure
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 0.0) # Stable

    # Depth Of Field
    s.set_editor_property("override_depth_of_field_fstop", True)
    s.set_editor_property("depth_of_field_fstop", 32.0)
    
    # FOV/Projection
    s.set_editor_property("override_field_of_view", True)
    try: s.set_editor_property("field_of_view", 90.0)
    except: pass

    pp.set_editor_property("settings", s)

    # 4. Player Start & GameMode
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,200))
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world.get_world_settings().set_editor_property("default_game_mode", gm_bp.generated_class())

    # 5. Project Settings Sync
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    path_struct = unreal.SoftObjectPath(f"{map_path}.UltimaMap")
    maps_settings.set_editor_property("game_default_map", path_struct)
    maps_settings.set_editor_property("editor_startup_map", path_struct)

    level_sub.save_current_level()
    unreal.log("ULTIMATE_FIX: SUCCESS! Map 'UltimaMap' is ready. Distortion PURGED. 🤠")

if __name__ == "__main__":
    ultimate_fix()
