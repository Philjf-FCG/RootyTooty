import unreal

def inspect_pc():
    pc_class = unreal.load_class(None, "/Script/Engine.PlayerController")
    if not pc_class:
        print("Could not load PlayerController class")
        return
    
    print(f"Inspecting Class: {pc_class.get_name()}")
    
    # List all properties
    cdo = unreal.get_default_object(pc_class)
    props = unreal.ControlRigBlueprint.get_all_properties(pc_class) if hasattr(unreal, "ControlRigBlueprint") else []
    # Alternative: use list_external_property_names if available
    try:
        external_props = cdo.list_external_property_names()
        for p in external_props:
            if "class" in p.lower() or "input" in p.lower():
                print(f"Property: {p}")
    except:
        pass

    # Specific checks
    check_names = ["PlayerInputClass", "InputComponentClass", "DefaultInputComponentClass"]
    for name in check_names:
        try:
            val = cdo.get_editor_property(name)
            print(f"FOUND Property '{name}': {val}")
        except:
            print(f"MISSING Property '{name}'")

if __name__ == "__main__":
    inspect_pc()
