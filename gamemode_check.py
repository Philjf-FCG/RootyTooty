import unreal

def check_gamemode_and_controller():
    print("\n--- GAMEMOD AND CONTROLLER CHECK ---")
    
    gm_path = "/Game/Blueprints/BP_WWGameMode.BP_WWGameMode_C"
    gm_class = unreal.load_class(None, gm_path)
    
    if gm_class:
        cdo = unreal.get_default_object(gm_class)
        pc_class = cdo.get_editor_property("player_controller_class")
        pawn_class = cdo.get_editor_property("default_pawn_class")
        
        print(f"GameMode: {gm_path}")
        print(f"Default Pawn: {pawn_class.get_name() if pawn_class else 'NONE'}")
        print(f"Player Controller Class: {pc_class.get_name() if pc_class else 'NONE'}")
        
        if pc_class:
            pc_cdo = unreal.get_default_object(pc_class)
            try:
                # Check what type of input component this controller wants
                # This property name might vary
                for prop in pc_cdo.list_external_property_names():
                    if "input" in prop.lower():
                        val = pc_cdo.get_editor_property(prop)
                        print(f"  Controller Property '{prop}': {val}")
            except: pass
    else:
        print(f"ERROR: Could not load GameMode at {gm_path}")

    print("\n--- END CHECK ---")

if __name__ == "__main__":
    check_gamemode_and_controller()
