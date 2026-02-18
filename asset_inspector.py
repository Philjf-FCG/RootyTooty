import unreal

def inspect_imc_mappings():
    print("\n" + "="*50)
    print("--- INPUT MAPPING INSPECTION START ---")
    print("="*50)
    
    # 1. Load IMC
    imc_path = "/Game/Input/IMC_Default"
    imc = unreal.load_asset(imc_path)
    
    if not imc:
        print(f"ERROR: Could not load {imc_path}")
        return

    print(f"Inspecting IMC: {imc.get_name()}")
    
    # 2. Get Mappings
    # Under the hood, mappings is an array of EnhancedActionKeyMapping
    try:
        mappings = imc.get_editor_property("mappings")
        print(f"Total Mappings: {len(mappings)}")
        
        found_wasd = []
        for m in mappings:
            # m.key is the FKey
            key_name = m.key.get_editor_property("key_name")
            action = m.action
            action_name = action.get_name() if action else "NONE"
            print(f"  - Key: {key_name} | Action: {action_name}")
            
            if action_name == "IA_Move" and str(key_name) in ["W", "A", "S", "D"]:
                found_wasd.append(str(key_name))
        
        print("\nSUMMARY:")
        if len(found_wasd) < 4:
            print(f"  WARNING: Only found these WASD keys for IA_Move: {found_wasd}")
            print("  YOU MUST ADD W, A, S, D TO IMC_DEFAULT!")
        else:
            print("  SUCCESS: W, A, S, D are all mapped to IA_Move.")
            
    except Exception as e:
        print(f"Error reading mappings: {e}")

    print("\n" + "="*50)
    print("--- INPUT MAPPING INSPECTION END ---")
    print("="*50)

if __name__ == "__main__":
    inspect_imc_mappings()
