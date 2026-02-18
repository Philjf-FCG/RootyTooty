import unreal

def gameplay_input_diagnostic():
    print("\n--- GAMEPLAY INPUT DIAGNOSTIC START ---")
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    
    if not world:
        print("ERROR: No active Game World found. Press Play first!")
        return

    # 1. Player Controller
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        print("ERROR: No Player Controller 0!")
        return

    pawn = pc.get_controlled_pawn()
    print(f"Pawn: {pawn.get_name() if pawn else 'NONE'}")

    # 2. Enhanced Input Subsystem Check
    subsystem = None
    try:
        # Direct property access for 'player' (ULocalPlayer)
        lp = pc.get_editor_property("player")
        if lp:
            print(f"Found Player object: {lp.get_name()}")
            subsystem = unreal.get_local_player_subsystem(unreal.EnhancedInputLocalPlayerSubsystem, lp)
    except Exception as e:
        print(f"Subsystem access error: {str(e)}")

    if subsystem:
        print("Enhanced Input Subsystem: FOUND")
        # Check if IMC is active
        if pawn:
            imc = pawn.get_editor_property("DefaultMappingContext")
            if imc:
                print(f"  Checking IMC: {imc.get_name()}")
                is_active = subsystem.has_mapping_context(imc)
                print(f"  Is IMC Active? {is_active}")
            else:
                print("  WARNING: Pawn has no DefaultMappingContext assigned!")
        
        # Check all mappings as a fallback
        print("  Checking subsystem for any active mappings...")
    else:
        print("ERROR: Could not access Enhanced Input Subsystem.")

    # 3. Input Component
    if pawn:
        ic = pawn.get_editor_property("InputComponent")
        print(f"Pawn Input Component: {ic.get_name() if ic else 'NONE'}")

    print("\n--- GAMEPLAY INPUT DIAGNOSTIC END ---")

if __name__ == "__main__":
    gameplay_input_diagnostic()
