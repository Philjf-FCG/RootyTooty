import unreal

def gameplay_safe_diagnostic():
    print("\n--- GAMEPLAY SAFE DIAGNOSTIC START ---")
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    
    if not world:
        print("ERROR: No active Game World found. Press Play first!")
        return

    # 1. Player Controller Check (Public methods only)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if pc:
        print(f"Player Controller 0: {pc.get_name()}")
        # get_controlled_pawn() is a public C++ function exposed to Python
        pawn = pc.get_controlled_pawn()
        print(f"  Controlled Pawn: {pawn.get_name() if pawn else 'NONE'}")
    else:
        print("ERROR: No Player Controller found!")

    # 2. Search for BP_WWCharacter instances
    char_class = unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
    if char_class:
        chars = unreal.GameplayStatics.get_all_actors_of_class(world, char_class)
        print(f"\nBP_WWCharacter count: {len(chars)}")
        for i, character in enumerate(chars):
            # get_controller() is public
            ctrl = character.get_controller()
            print(f"  [{i}] {character.get_name()} | Controller: {ctrl.get_name() if ctrl else 'NONE'}")
            
            # Check for standard InputComponent without protected access
            ic = character.get_component_by_class(unreal.InputComponent)
            print(f"      InputComponent: {'FOUND' if ic else 'MISSING'}")
            
    # 3. Bandit Check
    bandit_class = unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
    if bandit_class:
        bandits = unreal.GameplayStatics.get_all_actors_of_class(world, bandit_class)
        print(f"\nBandits in world: {len(bandits)}")
        if len(bandits) > 0:
            print(f"  Example Bandit: {bandits[0].get_name()} at {bandits[0].get_actor_location()}")
    else:
        print("\nERROR: Could not load BP_Bandit class.")

    print("\n--- GAMEPLAY SAFE DIAGNOSTIC END ---")

if __name__ == "__main__":
    gameplay_safe_diagnostic()
