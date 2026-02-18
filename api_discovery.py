import unreal

def api_discovery():
    print("\n--- API DISCOVERY START ---")
    
    # 1. Key Creation Test
    methods = [
        ("unreal.Key()", lambda: unreal.Key()),
        ("unreal.Key('W')", lambda: unreal.Key("W")),
        ("unreal.Key(name='W')", lambda: unreal.Key(name="W")),
        ("unreal.Key(key_name='W')", lambda: unreal.Key(key_name="W")),
    ]
    
    for label, fn in methods:
        try:
            k = fn()
            print(f"SUCCESS: {label} works. (Name: {k.get_name() if hasattr(k, 'get_name') else 'N/A'})")
        except Exception as e:
            print(f"FAILED: {label} -> {e}")

    # 2. Check for InputLibrary
    try:
        if hasattr(unreal, "InputLibrary"):
             print("SUCCESS: unreal.InputLibrary exists.")
    except: pass

    # 3. Check for EnhancedInputLibrary
    try:
        if hasattr(unreal, "EnhancedInputLibrary"):
             print("SUCCESS: unreal.EnhancedInputLibrary exists.")
    except: pass

    print("\n--- API DISCOVERY END ---")

if __name__ == "__main__":
    api_discovery()
