import unreal

def simple_check():
    print("\n--- PLUGIN & CLASS STATUS ---")
    
    # 1. Check Plugin State
    try:
        plugin_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        # Using a more direct lookup for the class
        ei_class = unreal.load_class(None, "/Script/EnhancedInput.EnhancedInputComponent")
        if ei_class:
            print(f"SUCCESS: EnhancedInputComponent class is LOADED.")
        else:
            print(f"FAILED: EnhancedInputComponent class is NOT LOADED.")
    except Exception as e:
        print(f"ERROR checking class: {e}")

    # 2. Check Input Settings Property
    try:
        settings = unreal.get_default_object(unreal.InputSettings)
        # We'll use a safer way to access the property name
        prop_name = "default_input_component_class"
        val = settings.get_editor_property(prop_name)
        print(f"Engine Default Input Class: {val.get_name() if val else 'NONE'}")
    except Exception as e:
        print(f"ERROR checking settings: {e}")

    print("--- CHECK END ---")

if __name__ == "__main__":
    simple_check()
