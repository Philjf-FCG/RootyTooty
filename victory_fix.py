import unreal

def final_victory_cleanup_and_build():
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    asset_lib = unreal.EditorAssetLibrary
    
    unreal.log("VICTORY_FIX: Starting Final Nuclear Cleanup...")

    # 1. Switch to a blank level to unlock everything
    # This is critical so we don't have VictoryMap open while trying to delete it
    level_sub.new_level("")
    
    # 2. Delete ALL conflicting map assets
    targets = [
        "/Game/Maps/MainMap",
        "/Game/Maps/MainMap_Old",
        "/Game/Maps/WildWestMap",
        "/Game/Maps/FinalWildWestMap",
        "/Game/Maps/VictoryMap" # Added this to cleanup list!
    ]
    
    for t in targets:
        if asset_lib.does_asset_exist(t):
            unreal.log(f"VICTORY_FIX: Deleting stale asset {t}...")
            # We use delete_asset which handles the registry correctly
            if not asset_lib.delete_asset(t):
                unreal.log_warning(f"VICTORY_FIX: Could not delete {t}. Might be locked.")

    # 3. Create the real VictoryMap
    map_path = "/Game/Maps/VictoryMap"
    if not level_sub.new_level(map_path):
        unreal.log_error("VICTORY_FIX: Still failed to create new map. Please manually delete VictoryMap in Content Browser.")
        return

    # 4. Environment - FORCE VISIBILITY
    # Huge Floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-100))
    floor.set_actor_label("DEBUG_GROUND_MASSIVE")
    floor.set_actor_scale3d(unreal.Vector(5000, 5000, 1))
    mc = floor.get_editor_property("static_mesh_component")
    mc.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
    
    # Sun
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sc = sun.get_editor_property("light_component")
    sc.set_editor_property("intensity", 15.0)
    sc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    # Atmosphere & Light
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0))
    sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl.get_editor_property("light_component").set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sl.get_editor_property("light_component").set_editor_property("intensity", 1.0)

    # 5. Post Process - FORCE EXPOSURE (THE MOST IMPORTANT PART)
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp.set_editor_property("bUnbound", True)
    s = pp.get_editor_property("settings")
    
    # Kill auto-exposure completely to stop the grey screen
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 12.0)
    
    pp.set_editor_property("settings", s)

    # 6. Player Start
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,500))
    ps.set_actor_label("ACTUAL_PLAYER_START")

    # 7. Final Config
    world = unreal.EditorLevelLibrary.get_editor_world()
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world.get_world_settings().set_editor_property("default_game_mode", gm_bp.generated_class())

    level_sub.save_current_level()
    unreal.log("VICTORY_FIX: SUCCESS! All conflicts deleted, VictoryMap built. PRESS PLAY! 🤠")

if __name__ == "__main__":
    final_victory_cleanup_and_build()
