import unreal

def inspect_input_settings():
    print("--- INPUT SETTINGS INSPECTION ---")
    settings_class = unreal.InputSettings
    cdo = unreal.get_default_object(settings_class)
    
    # List all members that might hold classes or relate to defaults
    members = dir(cdo)
    found = []
    for m in members:
        low = m.lower()
        if "class" in low or "default" in low:
            found.append(m)
            
    found.sort()
    for f in found:
        try:
            val = cdo.get_editor_property(f)
            print(f"Property: {f} | Value: {val.get_name() if hasattr(val, 'get_name') else val}")
        except:
            print(f"Property: {f} | (Found but not readable)")

    print("--- END ---")

if __name__ == "__main__":
    inspect_input_settings()
