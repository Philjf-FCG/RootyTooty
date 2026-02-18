import unreal

def revert_visuals():
    print("\n--- REVERT VISUALS START ---")
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    # Standard UE default grid material
    default_mat_path = "/Engine/EngineMaterials/DefaultMaterial"
    default_mat = unreal.load_asset(default_mat_path)
    
    if not default_mat:
        # Fallback to a common world grid if DefaultMaterial isn't what they want
        default_mat_path = "/Engine/EditorResources/S_LevelGrid_Default"
        default_mat = unreal.load_asset(default_mat_path)

    if not default_mat:
        print("ERROR: Could not find a suitable default material to revert to.")
        return

    count = 0
    for actor in all_actors:
        # We only want to revert things that we likely touched (Ground/Floor)
        name = actor.get_actor_label().lower()
        if any(keyword in name for keyword in ["floor", "plane", "ground", "grass"]):
            mesh_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if mesh_comp:
                mesh_comp.set_material(0, default_mat)
                print(f"Reverted material on: {actor.get_actor_label()}")
                count += 1
    
    print(f"\n--- REVERT COMPLETE ({count} actors restored) ---")

if __name__ == "__main__":
    revert_visuals()
