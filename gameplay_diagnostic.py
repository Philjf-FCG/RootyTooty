import unreal

def gameplay_diagnostic():
    print("\n--- GAMEPLAY DIAGNOSTIC START ---")
    
    # 1. Check Editor/Simulation World
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    print(f"Active World: {world.get_name()}")
    
    # 2. Check Player Pawn
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    if pawn:
        print(f"Player Pawn: {pawn.get_name()} ({pawn.get_class().get_name()})")
        print(f"  Location: {pawn.get_actor_location()}")
        
        # Check Mesh
        mesh_comp = pawn.get_component_by_class(unreal.SkeletalMeshComponent)
        if mesh_comp:
            mesh = mesh_comp.get_editor_property("skeletal_mesh")
            print(f"  Skeletal Mesh: {mesh.get_name() if mesh else 'NONE (Invisible!)'}")
        else:
            print("  No SkeletalMeshComponent found!")
            
        mesh_std = pawn.get_component_by_class(unreal.StaticMeshComponent)
        if mesh_std:
            mesh = mesh_std.get_editor_property("static_mesh")
            print(f"  Static Mesh: {mesh.get_name() if mesh else 'NONE'}")
    else:
        print("Player Pawn: NOT FOUND (Possession failed or wrong GameMode)")

    # 3. Check GameMode Defaults
    gm_path = "/Game/Blueprints/BP_WWGameMode"
    gm_asset = unreal.load_asset(gm_path)
    if gm_asset:
        cdo = unreal.get_default_object(gm_asset.generated_class())
        try:
            pawn_class = cdo.get_editor_property("default_pawn_class")
            print(f"GameMode Default Pawn: {pawn_class.get_name() if pawn_class else 'NONE'}")
            
            enemy_class = cdo.get_editor_property("EnemyClass")
            print(f"GameMode Enemy Class: {enemy_class.get_name() if enemy_class else 'NONE (Enemies won't spawn!)'}")
        except:
            print("Failed to read GameMode properties.")
    else:
        print(f"Could not load GameMode at {gm_path}")

    # 4. Count Enmies in World
    enemies = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C"))
    print(f"Enemies in World: {len(enemies)}")

    print("\n--- GAMEPLAY DIAGNOSTIC END ---")

if __name__ == "__main__":
    gameplay_diagnostic()
