import unreal

def diagnose():
    print("--- DIAGNOSIS START ---")
    
    # Check GameMode
    gm_path = "/Game/Blueprints/BP_WWGameMode"
    gm_bp = unreal.load_asset(gm_path)
    if gm_bp:
        gm_class = gm_bp.generated_class()
        gm_cdo = unreal.get_default_object(gm_class)
        try:
            pawn_class = gm_cdo.get_editor_property("default_pawn_class")
            enemy_class = gm_cdo.get_editor_property("enemy_class")
            print(f"GameMode DefaultPawnClass: {pawn_class.get_name() if pawn_class else 'NONE'}")
            print(f"GameMode EnemyClass: {enemy_class.get_name() if enemy_class else 'NONE'}")
        except Exception as e:
            print(f"ERROR: Could not read GameMode properties: {e}")
    else:
        print("ERROR: GameMode BP not found")

    # Check for character blueprints
    bps = ["BP_Gunslinger", "BP_WWCharacter", "BP_Bandit"]
    for bp_name in bps:
        bp_path = f"/Game/Blueprints/{bp_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
            print(f"Blueprint EXISTS: {bp_name}")
        else:
            print(f"Blueprint MISSING: {bp_name}")

    # Check Project Settings for Default Map
    gen_settings = unreal.get_default_object(unreal.GameMapsSettings)
    print(f"Project Default Map: {gen_settings.get_editor_property('game_default_map')}")
    print(f"Project Global Default GameMode: {gen_settings.get_editor_property('global_default_game_mode')}")

    print("--- DIAGNOSIS END ---")

if __name__ == "__main__":
    diagnose()
