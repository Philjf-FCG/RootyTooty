import unreal
import time

def final_pulse_check():
    print("\n" + "="*50)
    print("--- HARDWARE PULSE CHECK START ---")
    print("="*50)
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    if not world:
        print("ERROR: Please PRESS PLAY first.")
        return

    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    
    # Attempt to create a Key object safely
    w_key = None
    try:
        # Some versions use Key('W')
        w_key = unreal.Key('W')
    except:
        try:
            # Some versions use Key(name='W')
            w_key = unreal.Key(name='W')
        except:
            try:
                # Some versions require empty constructor then property set
                w_key = unreal.Key()
                w_key.set_editor_property('key_name', 'W')
            except:
                pass

    if not w_key:
        print("CRITICAL: Python cannot create an 'unreal.Key' object in this UE version.")
        print("Please rely on the Output Log for [DEBUG] lines instead.")
        return

    print("\nCOUNTDOWN: Click inside the game window and HOLD 'W' in...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("!!! CHECKING 'W' NOW !!!")
    detected = False
    for i in range(30):
        if pc.is_input_key_down(w_key):
            detected = True
            break
        time.sleep(0.1)
    
    if detected:
        print("\nRESULT: SUCCESS! Unreal is receiving your 'W' key.")
    else:
        print("\nRESULT: FAILED! Unreal is not hearing 'W'. Check window focus.")

    print("\n" + "="*50)

if __name__ == "__main__":
    final_pulse_check()
