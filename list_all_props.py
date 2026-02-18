import unreal

def list_valid_props():
    print("\n--- VALID PROPERTY NAME LISTER ---")
    bp_path = "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C"
    char_class = unreal.load_class(None, bp_path)
    
    if not char_class:
        print(f"ERROR: Could not load {bp_path}")
        return

    # List properties for the Character
    print(f"\n[PROPERTIES FOR {bp_path}]")
    for prop in unreal.EditorAssetLibrary.get_metadata_tag_values(unreal.load_asset("/Game/Blueprints/BP_WWCharacter")):
        print(f"Metadata: {prop}") # Just to see what's there

    # Get the class and list properties via unreal.reflect or similar
    # In newer Unreal, we can just use cdo.__dir__() or dir(cdo)
    cdo = unreal.get_default_object(char_class)
    
    important_keywords = ["rotation", "projectile", "orient", "yaw", "class", "movement"]
    
    all_members = dir(cdo)
    matching = [m for m in all_members if any(k in m.lower() for k in important_keywords)]
    matching.sort()
    
    for m in matching:
        print(f"Member: {m}")

    # Check the Movement Component specifically
    move_comp = cdo.get_editor_property("character_movement")
    if move_comp:
        print(f"\n[PROPERTIES FOR {move_comp.get_name()}]")
        move_members = dir(move_comp)
        move_matching = [m for m in move_members if any(k in m.lower() for k in important_keywords)]
        move_matching.sort()
        for m in move_matching:
            print(f"Member: {m}")

    print("\n--- END LISTING ---")

if __name__ == "__main__":
    list_valid_props()
