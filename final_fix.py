import unreal

def final_fix_visibility():
    new_map_path = "/Game/Maps/FinalWildWestMap"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("FIX_START: Creating FinalWildWestMap with full visibility package...")

    # 1. New Level
    level_sub.new_level(new_map_path)

    # 2. Huge Green Floor (so it's obvious)
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-50))
    if floor:
        floor.set_actor_label("GROUND_PLANAR")
        floor.set_actor_scale3d(unreal.Vector(500, 500, 1)) # Massive
        mesh_comp = floor.get_editor_property("static_mesh_component")
        mesh_asset = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        if mesh_asset:
            mesh_comp.set_editor_property("static_mesh", mesh_asset)
        unreal.log("FIX_PROGRESS: Added MASSIVE Floor")

    # 3. Player Start - Raised up
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,200))
    if ps: 
        ps.set_actor_label("PlayerStart_FIXED")
        unreal.log("FIX_PROGRESS: Added PlayerStart at Z=200")

    # 4. Sunlight Package
    # Sun
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1000))
    sun.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
    sun_comp = sun.get_editor_property("light_component")
    sun_comp.set_editor_property("intensity", 15.0)
    sun_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    # Sky Atmosphere (Makes it blue, not grey)
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0))
    
    # Sky Light
    skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    sl_comp = skylight.get_editor_property("light_component")
    sl_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    sl_comp.set_editor_property("real_time_capture", True)

    unreal.log("FIX_PROGRESS: Added Sky Atmosphere and Dynamic Lights")

    # 5. Blueprint Validation
    gm_bp_path = "/Game/Blueprints/BP_WWGameMode"
    char_bp_path = "/Game/Blueprints/BP_WWCharacter"
    
    gm_bp = unreal.load_asset(gm_bp_path)
    char_bp = unreal.load_asset(char_bp_path)
    
    if gm_bp and char_bp:
        gm_class = gm_bp.generated_class()
        gm_cdo = unreal.get_default_object(gm_class)
        
        # Hard-set the default pawn
        char_class = char_bp.generated_class()
        gm_cdo.set_editor_property("default_pawn_class", char_class)
        unreal.EditorAssetLibrary.save_asset(gm_bp_path)
        unreal.log(f"FIX_PROGRESS: Forced DefaultPawnClass to {char_class.get_name()} in {gm_bp.get_name()}")
    else:
        unreal.log_error("FIX_ERROR: Could not find BP_WWGameMode or BP_WWCharacter!")

    # 6. Finalize Map
    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings()
    settings.set_editor_property("default_game_mode", gm_bp.generated_class())
    
    # Update defaults
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    path_struct = unreal.SoftObjectPath(f"{new_map_path}.FinalWildWestMap")
    maps_settings.set_editor_property("game_default_map", path_struct)
    maps_settings.set_editor_property("editor_startup_map", path_struct)

    level_sub.save_current_level()
    unreal.log("FIX_COMPLETE: FinalWildWestMap is ready! Blue Sky, Green Ground. Press Play now. 🤠")

if __name__ == "__main__":
    final_fix_visibility()
