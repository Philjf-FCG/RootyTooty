import unreal

def create_via_new():
    report = []
    map_path = "/Game/Maps/MainMap"
    
    # new_level makes the new level current
    unreal.EditorLevelLibrary.new_level(map_path)
    report.append(f"SUCCESS: Created new level at {map_path}")
    
    # Add minimal actors
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,-50))
    if floor:
        floor.set_actor_label("Floor")
        floor.set_actor_scale3d(unreal.Vector(100, 100, 1))
        mesh_comp = floor.get_editor_property("static_mesh_component")
        mesh_asset = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        if mesh_asset:
            mesh_comp.set_editor_property("static_mesh", mesh_asset)
        report.append("SUCCESS: Added Floor")

    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,100))
    if ps: ps.set_actor_label("PlayerStart")
    
    # Save
    unreal.EditorLevelLibrary.save_current_level()
    report.append("SUCCESS: Saved level")

    with open("D:/Unreal Projects/RootyTooty/creation_report.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    create_via_new()
