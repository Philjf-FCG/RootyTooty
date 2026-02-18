import unreal

def fix_character_blueprint():
    print("\n--- CHARACTER BLUEPRINT FIX START ---")
    bp_path = "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C"
    char_class = unreal.load_class(None, bp_path)
    
    if not char_class:
        print(f"ERROR: Could not load {bp_path}")
        return

    cdo = unreal.get_default_object(char_class)
    
    # 1. Check/Set Projectile Class
    # Based on ProjectileClass in C++, Python name is usually projectile_class
    proj_class = unreal.load_class(None, "/Script/RootyTooty.WWProjectile")
    if proj_class:
        try:
            cdo.set_editor_property("projectile_class", proj_class)
            print("ProjectileClass: SET to WWProjectile")
        except Exception as e:
            print(f"ProjectileClass: Failed to set - {e}")
    else:
        print("ERROR: Could not find C++ class WWProjectile")

    # 2. Check/Set Rotation Settings
    # use_controller_rotation_yaw is the correct property name in this build
    try:
        cdo.set_editor_property("use_controller_rotation_yaw", False)
        print("use_controller_rotation_yaw: SET to False")
    except Exception as e:
        print(f"use_controller_rotation_yaw: Failed to set - {e}")

    # orient_rotation_to_movement is the correct property name in this build
    char_movement = cdo.get_editor_property("character_movement")
    if char_movement:
        try:
            char_movement.set_editor_property("orient_rotation_to_movement", True)
            print("orient_rotation_to_movement: SET to True")
        except Exception as e:
            print(f"orient_rotation_to_movement: Failed to set - {e}")
    else:
        print("ERROR: Could not find CharacterMovementComponent on CDO")

    print("\n--- FIX COMPLETE ---")
    print("Please RESTART the game and check for rotation and bullets. 🤠")

if __name__ == "__main__":
    fix_character_blueprint()
