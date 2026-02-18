import unreal

def resilient_input_fix():
    print("\n" + "="*50)
    print("--- RESILIENT INPUT FIX START ---")
    print("="*50)
    
    # 1. Paths
    imc_path = "/Game/Input/IMC_Default"
    ia_path = "/Game/Input/Actions/IA_Move"
    
    # 2. Load Assets
    imc = unreal.load_asset(imc_path)
    ia_move = unreal.load_asset(ia_path)
    
    if not imc or not ia_move:
        print(f"ERROR: Could not load assets. IMC: {imc}, IA: {ia_move}")
        return

    # 3. Discover Key Creation
    def make_key(name):
        # Try KismetInputLibrary first (Common for UE Python)
        try:
            return unreal.KismetInputLibrary.make_key(name)
        except: pass
        
        # Try Property Setting on empty Key
        try:
            k = unreal.Key()
            k.set_editor_property('key_name', name)
            return k
        except: pass
        
        # Try cast from string if that's a thing in this version
        try:
            return unreal.Key(name)
        except: pass
        
        return None

    print(f"Purging Mappings in: {imc.get_name()}")
    try:
        # Clear existing mappings
        imc.set_editor_property("mappings", [])
    except Exception as e:
        print(f"Warning: Could not clear mappings via property: {e}")

    # 4. Define Config
    configs = [
        ("W", ["Swizzle"]),
        ("S", ["Swizzle", "Negate"]),
        ("A", ["Negate"]),
        ("D", [])
    ]

    for key_name, mods in configs:
        print(f"Mapping {key_name}...")
        key = make_key(key_name)
        if not key:
            print(f"  FAILED: Could not create Key object for {key_name}")
            continue
            
        # Use the imc.map_key which worked in previous tries but failed on Key object
        try:
            mapping = imc.map_key(ia_move, key)
            if mapping:
                for m_type in mods:
                    if m_type == "Swizzle":
                        mapping.modifiers.append(unreal.InputModifierSwizzleAxis())
                    elif m_type == "Negate":
                        mapping.modifiers.append(unreal.InputModifierNegate())
                print(f"  [SUCCESS] {key_name} mapped with {mods}")
            else:
                print(f"  [FAILED] imc.map_key returned None for {key_name}")
        except Exception as e:
            print(f"  [ERROR] Mapping {key_name} failed: {e}")

    # 5. Save
    unreal.EditorAssetLibrary.save_asset(imc_path)
    print("\n" + "="*50)
    print("FINISHED. Check your IMC_Default!")
    print("="*50)

if __name__ == "__main__":
    resilient_input_fix()
