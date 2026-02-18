import unreal
import time

def break_immobility_v3():
    print("\n" + "="*50)
    print("--- IMMOBILITY BREAKER V3 START ---")
    print("="*50)
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    if not world:
        print("ERROR: Please PRESS PLAY first.")
        return

    # 1. Safe Player Access
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        print("ERROR: No Player Controller found.")
        return

    # 2. Force Movement Mode
    # Lifting all characters to clear collision issues
    char_classes = [
        unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C"),
        unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
    ]
    
    for cls in char_classes:
        if not cls: continue
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, cls)
        for a in actors:
            cmc = a.get_component_by_class(unreal.CharacterMovementComponent)
            if cmc:
                cmc.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
                a.add_actor_world_offset(unreal.Vector(0, 0, 100), True, True)
                print(f"LIFTED: {a.get_name()} set to WALKING and lifted 1m.")

    # 3. Hardware Pulse Check (No more complex lookups)
    print("\n" + "-"*30)
    print("COUNTDOWN: Click Viewport and HOLD 'W' in...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("!!! CHECKING 'W' NOW !!!")
    detected = False
    for i in range(30):
        # We try the most basic key check possible
        if pc.is_input_key_down(unreal.Key(key_name="W")):
            detected = True
            break
        time.sleep(0.1)
    
    if detected:
        print("\nRESULT: SUCCESS! Your 'W' key IS being received by the game.")
    else:
        print("\nRESULT: FAILED! The game is deaf to your 'W' key.")
        print("TIP: Try holding 'W' BEFORE you start the script.")

    print("\n" + "="*50)
    print("--- IMMOBILITY BREAKER END ---")
    print("="*50)

if __name__ == "__main__":
    break_immobility_v3()
