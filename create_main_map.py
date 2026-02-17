import unreal

def create_main_map():
    map_name = "MainMap"
    map_package_path = f"/Game/Maps/{map_name}"
    
    # Ensure the Maps directory exists
    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Maps"):
        unreal.EditorAssetLibrary.make_directory("/Game/Maps")

    # Create a new world
    world = unreal.EditorLevelLibrary.new_level(map_package_path)
    if not world:
        print(f"ERROR: Failed to create level at {map_package_path}")
        return

    # Set as active world for editing
    unreal.EditorLevelLibrary.load_level(map_package_path)

    # 1. Add a Floor (Cube scaled up)
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    floor.set_actor_label("Floor")
    mesh_comp = floor.static_mesh_component
    cube_mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    mesh_comp.set_static_mesh(cube_mesh)
    floor.set_actor_scale3d(unreal.Vector(100, 100, 1)) # Large floor
    
    # 2. Add a Directional Light
    light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 500))
    light.set_actor_label("MainLight")
    light.set_actor_rotation(unreal.Rotator(-45, 0, 0), True)

    # 3. Add a Sky Atmosphere
    sky_atm = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0))
    
    # 4. Add a Sky Light
    sky_light = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 0))

    # 5. Add a Player Start
    player_start = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 100))

    # Save the level
    unreal.EditorLevelLibrary.save_current_level()
    print(f"SUCCESS: Created and populated {map_package_path}")

if __name__ == "__main__":
    create_main_map()
