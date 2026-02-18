import unreal

def check_engine_input_settings():
    print("\n--- ENGINE INPUT SETTINGS CHECK ---")
    
    settings = unreal.get_default_object(unreal.InputSettings)
    if settings:
        dicc = settings.get_editor_property("default_input_component_class")
        dpic = settings.get_editor_property("default_player_input_class")
        
        print(f"DefaultInputComponentClass: {dicc.get_name() if dicc else 'NONE'}")
        print(f"DefaultPlayerInputClass: {dpic.get_name() if dpic else 'NONE'}")
        
    else:
        print("ERROR: Could not access InputSettings CDO.")

    print("\n--- PLUGIN CHECK ---")
    plugin_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    # Check if EnhancedInput is loaded in the engine
    try:
        if unreal.load_class(None, "/Script/EnhancedInput.EnhancedInputComponent"):
            print("EnhancedInput Classes: LOADED")
        else:
            print("EnhancedInput Classes: NOT LOADED")
    except:
        print("EnhancedInput Classes: LOAD ERROR")

    print("\n--- END CHECK ---")

if __name__ == "__main__":
    check_engine_input_settings()
