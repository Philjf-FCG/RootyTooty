import unreal

def list_everything():
    print("\n--- COMPLETE MEMBER LISTER ---")
    bp_path = "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C"
    char_class = unreal.load_class(None, bp_path)
    
    if not char_class:
        print(f"ERROR: Could not load {bp_path}")
        return

    cdo = unreal.get_default_object(char_class)
    print(f"Class: {char_class.get_name()}")
    
    # List absolutely everything
    all_members = dir(cdo)
    all_members.sort()
    
    for m in all_members:
        # Just print everything starting with p or r to narrow it down if it's too long
        # but for now let's try to find our specific one
        lower = m.lower()
        if "projectile" in lower or "rotation" in lower or "orient" in lower:
             print(f"MATCH: {m}")
             
    print("\n--- END COMPLETE LIST ---")

if __name__ == "__main__":
    list_everything()
