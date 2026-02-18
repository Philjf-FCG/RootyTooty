import unreal

def runtime_input_check():
    print("\n" + "="*50)
    print("--- FINAL RUNTIME INPUT CHECK START ---")
    print("="*50)
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    if not world:
        print("ERROR: Please PRESS PLAY first.")
        return

    # 1. Player & Controller
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    print(f"Controller: {pc.get_name() if pc else 'NONE'}")
    print(f"Pawn: {pawn.get_name() if pawn else 'NOT POSSESSED'}")

    if not pawn:
        return

    # 2. IA_Move Asset Integrity
    ia_move = unreal.load_asset("/Game/Input/Actions/IA_Move")
    if ia_move:
        # Check Value Type (0=bool, 1=axis1d, 2=axis2d)
        vt = ia_move.get_editor_property("value_type")
        print(f"IA_Move Value Type: {vt}")
        if str(vt) != "AXIS2D":
            print("  WARNING: IA_Move should be AXIS2D for WASD!")
    else:
        print("ERROR: IA_Move asset NOT FOUND at /Game/Input/Actions/IA_Move")

    # 3. Subsystem Check
    lp = pc.get_local_player()
    if lp:
        ei_sub = unreal.get_local_player_subsystem(unreal.EnhancedInputLocalPlayerSubsystem, lp)
        if ei_sub:
            imc = unreal.load_asset("/Game/Input/IMC_Default")
            is_mapped = ei_sub.has_mapping_context(imc)
            print(f"IMC_Default in Subsystem? {is_mapped}")
        else:
            print("ERROR: Enhanced Input Subsystem not found.")

    # 4. Input Component
    ic = pawn.get_component_by_class(unreal.InputComponent)
    print(f"Input Component: {ic.get_name() if ic else 'NONE'}")
    if ic:
        is_enhanced = isinstance(ic, unreal.EnhancedInputComponent)
        print(f"  Is EnhancedInputComponent? {is_enhanced}")

    print("\n" + "="*50)
    print("--- CHECK OUTPUT LOG FOR [DEBUG] LINES ---")
    print("="*50)

if __name__ == "__main__":
    runtime_input_check()
