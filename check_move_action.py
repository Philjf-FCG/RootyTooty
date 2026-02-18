import unreal

def check_move_action():
    print("\n--- MOVE ACTION ASSIGNMENT CHECK ---")
    
    char_class = unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
    if not char_class:
        print("ERROR: Could not load BP_WWCharacter")
        return
        
    cdo = unreal.get_default_object(char_class)
    
    # Check property names (Unreal maps Pascal to snake_case in Python)
    try:
        ma = cdo.get_editor_property("move_action")
        print(f"MoveAction Property (move_action): {ma.get_name() if ma else 'NULL'}")
    except:
        try:
            ma = cdo.get_editor_property("MoveAction")
            print(f"MoveAction Property (MoveAction): {ma.get_name() if ma else 'NULL'}")
        except Exception as e:
            print(f"ERROR: Could not find MoveAction property: {e}")

    imc = None
    try:
        imc = cdo.get_editor_property("default_mapping_context")
        print(f"MappingContext Property: {imc.get_name() if imc else 'NULL'}")
    except: pass

    # If NULL, we can try to fix it automatically here
    if not ma:
        print("ACTION: Attempting to assign IA_Move automatically...")
        ia_asset = unreal.load_asset("/Game/Input/Actions/IA_Move")
        if ia_asset:
            try:
                cdo.set_editor_property("move_action", ia_asset)
                print("  [SUCCESS] IA_Move assigned to CDO.")
                unreal.EditorAssetLibrary.save_loaded_asset(cdo)
            except: pass
    
    if not imc:
        print("ACTION: Attempting to assign IMC_Default automatically...")
        imc_asset = unreal.load_asset("/Game/Input/IMC_Default")
        if imc_asset:
            try:
                cdo.set_editor_property("default_mapping_context", imc_asset)
                print("  [SUCCESS] IMC_Default assigned to CDO.")
                unreal.EditorAssetLibrary.save_loaded_asset(cdo)
            except: pass

    print("--- CHECK END ---")

if __name__ == "__main__":
    check_move_action()
