import unreal

def safe_inspect():
    pc_class = unreal.load_class(None, "/Script/Engine.PlayerController")
    if not pc_class:
        print("ERROR: Could not load PlayerController class")
        return

    print(f"--- Properties for {pc_class.get_full_name()} ---")
    
    # We'll use get_default_object and look at the properties it exposes
    cdo = unreal.get_default_object(pc_class)
    
    # Try to find property names by iterating through possible candidates
    candidates = [
        "PlayerInputClass", 
        "PlayerInput", 
        "InputComponentClass", 
        "InputComponent",
        "DefaultInputComponentClass",
        "OverridePlayerInputClass"
    ]
    
    for name in candidates:
        try:
            # Check if property exists
            prop = pc_class.find_property_by_name(name)
            if prop:
                val = cdo.get_editor_property(name)
                print(f"Prop '{name}': FOUND, Value: {val}")
            else:
                print(f"Prop '{name}': NOT FOUND")
        except Exception as e:
            print(f"Prop '{name}': Error checking - {str(e)}")

    print("--- End Inspection ---")

if __name__ == "__main__":
    safe_inspect()
