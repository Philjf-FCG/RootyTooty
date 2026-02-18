import unreal

def verify_gamemode_assets():
    print("\n--- GAMEMOD ASSET VERIFICATION ---")
    
    gm_path = "/Game/Blueprints/BP_WWGameMode.BP_WWGameMode_C"
    gm_class = unreal.load_class(None, gm_path)
    
    if gm_class:
        cdo = unreal.get_default_object(gm_class)
        enemy_class = cdo.get_editor_property("enemy_class")
        
        print(f"GameMode Class: {gm_path}")
        if enemy_class:
            print(f"Enemy Class: {enemy_class.get_full_name()} | [OK]")
        else:
            print(f"Enemy Class: [MISSING / NULL] | <--- PROBLEM HERE")
            
        # Also check spawn parameters
        spawn_interval = cdo.get_editor_property("spawn_interval")
        spawn_radius = cdo.get_editor_property("spawn_radius")
        print(f"Spawn Interval: {spawn_interval}")
        print(f"Spawn Radius: {spawn_radius}")
        
    else:
        print(f"ERROR: Could not load GameMode at {gm_path}")

    print("\n--- END VERIFICATION ---")

if __name__ == "__main__":
    verify_gamemode_assets()
