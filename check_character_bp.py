import unreal

def check_character_bp_robust():
    print("\n--- ROBUST CHARACTER BP DIAGNOSTIC ---")
    bp_path = "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C"
    char_class = unreal.load_class(None, bp_path)
    
    if not char_class:
        print(f"ERROR: Could not load {bp_path}")
        return

    cdo = unreal.get_default_object(char_class)
    print(f"Blueprint Class: {bp_path}")
    
    # List all properties that might be relevant
    properties = unreal.ControlRigBlueprint.get_all_properties(char_class) if hasattr(unreal, 'ControlRigBlueprint') else []
    # If standard listing fails, we use dir() on the CDO and filter
    members = dir(cdo)
    
    print("\n[RELEVANT PROPERTIES FOUND]")
    targets = ["rotation", "projectile", "orient", "yaw"]
    for m in members:
        if any(t in m.lower() for t in targets):
            try:
                val = cdo.get_editor_property(m)
                print(f"Prop: {m} | Value: {val}")
            except:
                # Some things might be functions, ignore
                pass

    print("\n--- END DIAGNOSTIC ---")

if __name__ == "__main__":
    check_character_bp_robust()
