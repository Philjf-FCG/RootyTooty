import unreal

def final_input_purge():
    print("\n" + "="*50)
    print("--- DEEP INPUT PURGE & REBUILD START ---")
    print("="*50)
    
    # 1. Assets
    imc_path = "/Game/Input/IMC_Default"
    ia_path = "/Game/Input/Actions/IA_Move"
    
    imc = unreal.load_asset(imc_path)
    ia = unreal.load_asset(ia_path)
    
    if not imc or not ia:
        print("ERROR: Assets not found.")
        return

    # 2. Fix IA_Move (Action)
    print(f"Cleaning {ia.get_name()}...")
    try:
        # Force value type to AXIS2D (Value Type 2)
        ia.set_editor_property("value_type", unreal.InputActionValueType.AXIS2D)
        # Deep purge triggers/modifiers
        ia.set_editor_property("triggers", [])
        ia.set_editor_property("modifiers", [])
        print("  [OK] IA_Move reset to AXIS2D and cleared.")
    except Exception as e:
        print(f"  [FAIL] IA_Move cleanup: {e}")

    # 3. Fix IMC_Default (Mapping Context)
    print(f"Cleaning {imc.get_name()}...")
    try:
        # Purge all mappings
        imc.set_editor_property("mappings", [])
        print("  [OK] IMC Mappings purged.")
        
        configs = [
            ("W", ["Swizzle"]),
            ("S", ["Swizzle", "Negate"]),
            ("A", ["Negate"]),
            ("D", [])
        ]

        for key_name, mods in configs:
            print(f"Mapping {key_name}...")
            # Discover working Key creation
            key = None
            try: key = unreal.KismetInputLibrary.make_key(key_name)
            except: 
                try: 
                    key = unreal.Key()
                    key.set_editor_property("key_name", key_name)
                except: pass
            
            if not key:
                print(f"  [FAIL] Could not create key {key_name}")
                continue
                
            mapping = imc.map_key(ia, key)
            if mapping:
                # Add default triggers to prevent "Null Trigger" error
                # Usually we want 'Pressed' or 'Down' but AXIS2D often needs none (Continuous)
                mapping.set_editor_property("triggers", []) 
                
                # Add Modifiers
                for m_type in mods:
                    if m_type == "Swizzle":
                        mapping.modifiers.append(unreal.InputModifierSwizzleAxis())
                    elif m_type == "Negate":
                        mapping.modifiers.append(unreal.InputModifierNegate())
                print(f"  [OK] {key_name} mapped.")
            else:
                print(f"  [FAIL] imc.map_key failed for {key_name}")

        # 4. Save
        unreal.EditorAssetLibrary.save_asset(imc_path)
        unreal.EditorAssetLibrary.save_asset(ia_path)
        print("\nSUCCESS: Input assets purged and rebuilt.")
        
    except Exception as e:
        print(f"  [FATAL] IMC Purge failed: {e}")

    print("\n" + "="*50)
    print("NEXT STEP: Press Play and check if WASD works!")
    print("="*50)

if __name__ == "__main__":
    final_input_purge()
