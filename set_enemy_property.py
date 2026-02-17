import unreal

def set_enemy_class_in_gamemode():
    gamemode_path = "/Game/Blueprints/BP_WWGameMode"
    bandit_path = "/Game/Blueprints/BP_Bandit.BP_Bandit_C"
    
    # Load GameMode Blueprint
    gm_blueprint = unreal.load_asset(gamemode_path)
    if not gm_blueprint:
        print(f"ERROR: Could not load GameMode Blueprint at {gamemode_path}")
        return

    # Load Bandit Class
    bandit_class = unreal.load_class(None, bandit_path)
    if not bandit_class:
        print(f"ERROR: Could not load Bandit Class at {bandit_path}")
        return

    # Get the Class Default Object (CDO) of the GameMode
    gm_class_path = f"{gamemode_path}.BP_WWGameMode_C"
    gm_class = unreal.load_class(None, gm_class_path)
    if gm_class:
        default_object = unreal.get_default_object(gm_class)
        
        # Set the property. In C++ it's 'EnemyClass'. 
        # Unreal Python API typically exposes this as 'enemy_class'.
        try:
            default_object.set_editor_property("enemy_class", bandit_class)
            unreal.EditorAssetLibrary.save_asset(gamemode_path)
            print(f"SUCCESS: Set EnemyClass to {bandit_path} in {gamemode_path}")
        except Exception as e:
            print(f"ERROR: Failed to set property: {e}")
    else:
        print(f"ERROR: Could not load GameMode Class at {gm_class_path}")

if __name__ == "__main__":
    set_enemy_class_in_gamemode()
