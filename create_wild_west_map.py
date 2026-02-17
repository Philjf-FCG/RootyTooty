import unreal

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

    # 4. Add Floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-50))
    if floor:
        floor.set_actor_label("Floor")
        floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
        mesh_comp = floor.get_editor_property("static_mesh_component")
        mesh_asset = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        if mesh_asset:
            mesh_comp.set_editor_property("static_mesh", mesh_asset)
        unreal.log("FIX_PROGRESS: Added Floor")

    # 5. Add Player Start
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,100))
    if ps: 
        ps.set_actor_label("PlayerStart")
        unreal.log("FIX_PROGRESS: Added PlayerStart")

    # 6. Add Dynamic Lighting (Movable) - This avoids the "rebuild lighting" error
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,500))
    if light:
        light.set_actor_label("MainLight")
        light.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
        # Set light to Movable
        light_comp = light.get_editor_property("light_component")
        light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        light_comp.set_editor_property("intensity", 10.0)
        unreal.log("FIX_PROGRESS: Added Dynamic Directional Light")

    # 7. Add Sky Light for ambient brightness
    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    if sky_light:
        sky_light.set_actor_label("SkyLight")
        sky_light_comp = sky_light.get_editor_property("light_component")
        sky_light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        sky_light_comp.set_editor_property("real_time_capture", True)
        unreal.log("FIX_PROGRESS: Added Dynamic Sky Light")

    # 8. Set GameMode Override
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        settings = world.get_world_settings()
        gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
        if gm_bp:
            settings.set_editor_property("default_game_mode", gm_bp.generated_class())
            unreal.log("FIX_PROGRESS: Assigned BP_WWGameMode")

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
    
    unreal.log("FIX_COMPLETE: WildWestMap is ready with DYNAMIC lighting! Press Play. 🤠")

if __name__ == "__main__":
    create_wild_west_map()
