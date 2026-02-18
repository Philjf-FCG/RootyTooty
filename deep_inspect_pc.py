import unreal

def deep_inspect():
    print("--- DEEP INSPECTION START ---")
    pc_class = unreal.load_class(None, "/Script/Engine.PlayerController")
    if not pc_class:
        print("ERROR: Could not load APlayerController")
        return

    print(f"Inspecting Class: {pc_class.get_full_name()}")
    
    # Get all properties via the class object itself
    # Unreal Python API has Class.get_editor_property but we want to LIST them
    # We can use the unreal.ControlRigBlueprint hack or just iterate on a CDO
    cdo = unreal.get_default_object(pc_class)
    
    # Get all member names
    members = dir(cdo)
    
    # Find anything that stores a class
    print("\n[POTENTIAL CLASS PROPERTIES]")
    for m in members:
        if m.startswith("_"): continue
        try:
            val = cdo.get_editor_property(m)
            if isinstance(val, unreal.Class) or (val and "class" in str(type(val)).lower()):
                print(f"Property: {m} | Value: {val.get_name() if hasattr(val, 'get_name') else val}")
        except:
            pass

    # Find anything related to input
    print("\n[INPUT-RELATED MEMBERS]")
    for m in members:
        if "input" in m.lower():
            print(f"Member: {m}")

    print("\n--- END ---")

if __name__ == "__main__":
    deep_inspect()
