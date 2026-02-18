import unreal

def fix_input_mappings_v2():
    print("\n" + "="*50)
    print("--- AUTO-FIX INPUT MAPPINGS V2 START ---")
    print("="*50)
    
    # 1. Load Assets
    imc_path = "/Game/Input/IMC_Default"
    ia_path = "/Game/Input/Actions/IA_Move"
    
    imc = unreal.load_asset(imc_path)
    ia_move = unreal.load_asset(ia_path)
    
    if not imc or not ia_move:
        print(f"ERROR: Could not load assets. IMC: {imc}, IA: {ia_move}")
        return

    print(f"Target IMC: {imc.get_name()}")
    print(f"Target Action: {ia_move.get_name()}")

    # 2. Define Mappings (Key, Swizzle, Negate)
    wasd_data = [
        {"key": "W", "swizzle": True, "negate": False},
        {"key": "S", "swizzle": True, "negate": True},
        {"key": "D", "swizzle": False, "negate": False},
        {"key": "A", "swizzle": False, "negate": True},
    ]

    try:
        # In modern UE, the most robust way is often assigning the array directly
        # or using the InputMappingContext methods.
        
        # We'll use the simplest route: Tell the user exactly how to fix it manually
        # but try one more internal method for mapping.
        
        print("Attempting to Clear and Map...")
        
        # Note: In Python, we can't always easily manipulate the nested modifier structs.
        # If this fails, Manual Fix is the 100% path.
        
        for k in wasd_data:
            key_name = k["key"]
            mapping = imc.map_key(ia_move, unreal.Key(key_name))
            if mapping:
                print(f"  [SUCCESS] {key_name} added.")
                # Modifiers are tricky via Python, we'll try to add them if possible
                try:
                    if k["swizzle"]:
                        mapping.modifiers.append(unreal.InputModifierSwizzleAxis())
                    if k["negate"]:
                        mapping.modifiers.append(unreal.InputModifierNegate())
                except:
                    print(f"  [NOTE] Could not auto-add modifiers for {key_name}. Please add them manually.")
            else:
                print(f"  [FAILED] Could not map {key_name}. Asset might be locked.")

        unreal.EditorAssetLibrary.save_asset(imc_path)
        print("\nSUCCESS: Script finished. Check IMC_Default in the Editor!")
        
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n--- MANUAL FIX INSTRUCTIONS ---")
    print("If you still can't move, open IMC_Default and add these 4 keys to IA_Move:")
    print("1. W -> Add Modifier: Swizzle Input Axis")
    print("2. S -> Add Modifiers: Swizzle Input Axis, Negate")
    print("3. D -> No Modifiers")
    print("4. A -> Add Modifier: Negate")
    print("="*50)

if __name__ == "__main__":
    fix_input_mappings_v2()
