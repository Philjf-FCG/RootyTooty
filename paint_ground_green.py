import unreal

def paint_ground_green():
    print("\n--- PAINT GROUND GREEN START ---")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    found_ground = False
    
    # Try to find a green material in engine content
    green_mat_path = "/Engine/EngineDebugMaterials/VertexColorViewMode_GreenOnly"
    green_mat = unreal.load_asset(green_mat_path)
    
    if not green_mat:
        print(f"ERROR: Could not find green material at {green_mat_path}")
        return

    for actor in all_actors:
        name = actor.get_actor_label().lower()
        if any(keyword in name for keyword in ["floor", "plane", "ground", "grass"]):
            print(f"Found ground candidate: {actor.get_actor_label()}")
            mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if mesh_comp:
                mesh_comp.set_material(0, green_mat)
                print("Applied green material.")
                found_ground = True
    
    if not found_ground:
        print("Searching by bounds (large horizontal objects)...")
        for actor in all_actors:
            if isinstance(actor, unreal.StaticMeshActor):
                origin, extent = actor.get_actor_bounds(False)
                # If it's wide and thin
                if extent.x > 500 and extent.y > 500 and extent.z < 100:
                     mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
                     if mesh_comp:
                        mesh_comp.set_material(0, green_mat)
                        print(f"Applied green material to {actor.get_actor_label()} by bounds.")
                        found_ground = True

    print("\n--- PAINT GROUND GREEN COMPLETE ---")

if __name__ == "__main__":
    paint_ground_green()
