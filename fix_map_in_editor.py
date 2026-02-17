import unreal

def fix_map_final():
    map_path = "/Game/Maps/MainMap"
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    unreal.log("FIX_START: Creating fresh MainMap...")

    # 1. Switch away from current to be safe
    level_sub.new_level("")
    
    # 2. No deletion needed here as we moved files on disk, 
    # but we'll try a soft delete just in case anything is in memory
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        unreal.EditorAssetLibrary.delete_asset(map_path)

    # 3. Create fresh MainMap
    if not level_sub.new_level(map_path):
        unreal.log_error("FIX_ERROR: Failed to create new level at MainMap. Check Output Log for details.")
        return

    # 4. Spawn Floor
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-50))
    if floor:
        floor.set_actor_label("Floor")
        floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
        mesh_comp = floor.get_editor_property("static_mesh_component")
        mesh_asset = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        if mesh_asset:
            mesh_comp.set_editor_property("static_mesh", mesh_asset)
        unreal.log("FIX_PROGRESS: Added Floor")

    # 5. Spawn Player Start
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,100))
    if ps: 
        ps.set_actor_label("PlayerStart")
        unreal.log("FIX_PROGRESS: Added PlayerStart")

    # 6. Spawn Lighting
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,500))
    if light:
        light.set_actor_label("MainLight")
        light.set_actor_rotation(unreal.Rotator(-60, -45, 0), True)
        unreal.log("FIX_PROGRESS: Added Lighting")

    # 7. Set GameMode Override
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        settings = world.get_world_settings()
        gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
        if gm_bp:
            settings.set_editor_property("default_game_mode", gm_bp.generated_class())
            unreal.log("FIX_PROGRESS: Assigned BP_WWGameMode")

    # 8. Save
    level_sub.save_current_level()
    unreal.log("FIX_COMPLETE: MainMap is ready! Press Play now. 🤠")

if __name__ == "__main__":
    fix_map_final()
