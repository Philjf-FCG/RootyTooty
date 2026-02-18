import unreal

def final_recovery_check():
    print("\n" + "="*50)
    print("--- ULTIMATE GAMEPLAY DIAGNOSTIC START ---")
    print("="*50)
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    
    # 1. World Detection
    world = editor_sub.get_game_world()
    if not world:
        world = editor_sub.get_editor_world()
        print(f"STATUS: Looking at Editor World ({world.get_name()})")
        print("ACTION: For best results, PRESS PLAY before running this script.")
    else:
        print(f"STATUS: Found ACTIVE Play World ({world.get_name()})")

    # 2. Player Controller & Pawn (Using standard C++ methods)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if pc:
        print(f"Player Controller: {pc.get_name()}")
        # get_controlled_pawn is public
        pawn = pc.get_controlled_pawn()
        if pawn:
            print(f"Controlled Pawn: {pawn.get_name()} ({pawn.get_class().get_name()})")
            
            # Check for Mapping Context setting
            try:
                # We can't easily check 'active' status in Python due to protected properties,
                # but we can check if the Blueprint has it set.
                imc = pawn.get_editor_property("DefaultMappingContext")
                ma = pawn.get_editor_property("MoveAction")
                print(f"  Pawn IMC Assigned: {'SET' if imc else 'MISSING'}")
                print(f"  Pawn MoveAction Assigned: {'SET' if ma else 'MISSING'}")
            except:
                print("  Note: Could not read Pawn properties directly (Blueprint/C++ mismatch or protected)")
        else:
            print("Controlled Pawn: NONE (Character exists but is not possessed by you!)")
    else:
        print("Player Controller: MISSING (This is bad, should always exist in game)")

    # 3. Actor Search
    char_class = unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
    if char_class:
        chars = unreal.GameplayStatics.get_all_actors_of_class(world, char_class)
        print(f"\nBP_WWCharacter instances in world: {len(chars)}")
        for c in chars:
            ctrl = c.get_controller()
            print(f"  - {c.get_name()} | Possessed by: {ctrl.get_name() if ctrl else 'NOBODY'}")

    bandit_class = unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
    if bandit_class:
        bandits = unreal.GameplayStatics.get_all_actors_of_class(world, bandit_class)
        print(f"BP_Bandit instances in world: {len(bandits)}")
    
    print("\n" + "="*50)
    print("--- ULTIMATE GAMEPLAY DIAGNOSTIC END ---")
    print("="*50)

if __name__ == "__main__":
    final_recovery_check()
