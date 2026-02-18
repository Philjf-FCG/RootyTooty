import unreal

def ultimate_victory_fix():
    print("--- ULTIMATE VICTORY FIX (UE 5.7) ---")
    
    # Correct subsystems for 5.7
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    asset_editor_sub = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    
    # 1. Create/Load Map
    map_asset = "/Game/Maps/VictoryMap"
    if not unreal.EditorAssetLibrary.does_asset_exist(f"{map_asset}.VictoryMap"):
        level_sub.new_level(f"{map_asset}")
    else:
        # Load the level asset
        level_asset = unreal.load_asset(map_asset)
        if level_asset:
            asset_editor_sub.open_editor_for_assets([level_asset])
        else:
            print(f"FAILED to load map asset: {map_asset}")
            return

    world = editor_sub.get_editor_world()
    if not world:
        print("FAILED: Could not retrieve Editor World.")
        return
    
    # 2. Cleanup existing to avoid clutter
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        if actor.get_actor_label() in ["ULTIMA_FLOOR", "STABILITY_VOLUME", "SUN", "SKY", "SKY_LIGHT", "VICTORY_START"]:
            actor.destroy_actor()
    
    # Also clear any old PlayerStarts that might not have the right label
    for ps in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PlayerStart):
        ps.destroy_actor()

    # 3. Environment Spawning
    # Floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
    floor.set_actor_label("ULTIMA_FLOOR")
    floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
    comp = floor.static_mesh_component
    mesh = unreal.load_asset("/Engine/BasicShapes/Plane")
    if mesh: comp.set_static_mesh(mesh)
    
    # SUN
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,5000))
    sun.set_actor_label("SUN")
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sc = sun.light_component
    sc.set_editor_property("intensity", 120000.0)
    # sc.set_editor_property("intensity_units", ...) # LUX is missing in 5.7 enums
    sc.set_editor_property("atmosphere_sun_light", True)
    
    # SKY & LIGHT
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0)).set_actor_label("SKY")
    sl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl.set_actor_label("SKY_LIGHT")
    sl.light_component.set_editor_property("real_time_capture", True)

    # 4. Post Process - VISIBILITY RESET
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
    pp.set_editor_property("bUnbound", True)
    pp.set_actor_label("STABILITY_VOLUME")
    pp.set_editor_property("priority", 10000.0)
    
    s = pp.get_editor_property("settings")
    s.set_editor_property("override_auto_exposure_method", True)
    s.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
    s.set_editor_property("override_auto_exposure_bias", True)
    s.set_editor_property("auto_exposure_bias", 0.0)
    pp.set_editor_property("settings", s)

    # 5. Spawn Player Start
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,500))
    ps.set_actor_label("VICTORY_START")

    # 6. Set Default Map/Mode
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    path_struct = unreal.SoftObjectPath(f"{map_asset}.VictoryMap")
    maps_settings.set_editor_property("game_default_map", path_struct)
    maps_settings.set_editor_property("editor_startup_map", path_struct)

    # Force GameMode on World Settings
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        world_settings = world.get_world_settings()
        world_settings.set_editor_property("default_game_mode", gm_bp.generated_class())
        print(f"ULTIMATE_FIX: Assigned {gm_bp.get_name()} to World Settings.")

    level_sub.save_current_level()
    print("ULTIMATE_FIX (5.7): SUCCESS! Map & GameMode refreshed. Check BP_WWCharacter and PRESS PLAY! 🤠")

if __name__ == "__main__":
    ultimate_victory_fix()

if __name__ == "__main__":
    ultimate_victory_fix()
