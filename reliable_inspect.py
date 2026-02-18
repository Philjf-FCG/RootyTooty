import unreal

def reliable_inspect():
    print("--- RELIABLE INSPECTION START ---")
    pc_class = unreal.load_class(None, "/Script/Engine.PlayerController")
    if not pc_class:
        print("ERROR: Could not load APlayerController")
        return

    # Use the most basic dir() on a CDO to see what's exposed to Python
    cdo = unreal.get_default_object(pc_class)
    
    # Filter for things that look like input or class properties
    found = []
    for member in dir(cdo):
        low = member.lower()
        if "input" in low or "class" in low:
            found.append(member)
    
    found.sort()
    for f in found:
        print(f"Member: {f}")
        
    print("--- END ---")

if __name__ == "__main__":
    reliable_inspect()
