import unreal

def check_pc_api():
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    if not world:
        world = editor_sub.get_editor_world()
        
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    print(f"Inspecting PlayerController: {pc.get_name()}")
    
    # Check for methods to get LocalPlayer or Subsystem
    for member in dir(pc):
        if "player" in member.lower() or "local" in member.lower():
            print(f"  - {member}")
            
    # Check EnhancedInputSubsystem access points
    print("\nChecking EnhancedInputSubsystem access points:")
    for member in dir(unreal.EnhancedInputLocalPlayerSubsystem):
        if not member.startswith("_"):
            print(f"  - {member}")

if __name__ == "__main__":
    check_pc_api()
