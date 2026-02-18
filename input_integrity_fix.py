import unreal

def fix_input_integrity():
    print("\n" + "="*50)
    print("--- INPUT INTEGRITY PURGE START ---")
    print("="*50)
    
    imc_path = "/Game/Input/IMC_Default"
    ia_path = "/Game/Input/Actions/IA_Move"
    
    imc = unreal.load_asset(imc_path)
    ia = unreal.load_asset(ia_path)
    
    if not imc or not ia:
        print("ERROR: Assets not found. Check paths.")
        return

    # 1. Purge Triggers on IA_Move
    print(f"Cleaning Triggers on {ia.get_name()}...")
    try:
        ia.set_editor_property("triggers", [])
        print("  - IA_Move triggers cleared.")
    except: pass

    # 2. Purge and Re-create Mappings in IMC
    # 'Null input trigger' often lives inside the 'mappings' of the IMC.
    print(f"Purging Mappings in {imc.get_name()}...")
    try:
        # We clear the mappings completely to remove hidden null triggers
        imc.set_editor_property("mappings", [])
        print("  - IMC Mappings cleared.")
        
        # Now we re-add the 4 basic keys WITHOUT any modifiers/triggers for a "Plain Test"
        raw_keys = ["W", "S", "A", "D"]
        for k in raw_keys:
            mapping = imc.map_key(ia, unreal.Key(key_name=k))
            if mapping:
                print(f"  - Re-mapped {k} (Raw)")
            else:
                print(f"  - FAILED to map {k}")

        unreal.EditorAssetLibrary.save_asset(imc_path)
        unreal.EditorAssetLibrary.save_asset(ia_path)
        print("\nSUCCESS: Integrity Purge Complete. NO MODIFIERS (Plain WASD).")
        print("If this works, we will add Swizzles back later.")
        
    except Exception as e:
        print(f"Purge FAILED: {e}")

    print("\n" + "="*50)
    print("--- INPUT INTEGRITY PURGE END ---")
    print("="*50)

if __name__ == "__main__":
    fix_input_integrity()
