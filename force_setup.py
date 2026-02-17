import unreal

def force_setup():
    report = []
    
    # 1. Paths
    bp_folder = "/Game/Blueprints"
    char_path = f"{bp_folder}/BP_WWCharacter"
    enemy_path = f"{bp_folder}/BP_Bandit"
    gm_path = f"{bp_folder}/BP_WWGameMode"
    
    # 2. Cleanup old BPs to ensure fresh state
    for old_bp in ["BP_Gunslinger", "BP_WWCharacter", "BP_WWGameMode", "BP_Bandit"]:
        path = f"{bp_folder}/{old_bp}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            unreal.EditorAssetLibrary.delete_asset(path)
            report.append(f"Deleted old BP: {old_bp}")

    # 3. Create Fresh Blueprints
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    
    def create_bp(name, parent_class):
        factory.set_editor_property("parent_class", unreal.load_class(None, f"/Script/RootyTooty.{parent_class}"))
        new_bp = asset_tools.create_asset(name, bp_folder, unreal.Blueprint, factory)
        if new_bp:
            unreal.EditorAssetLibrary.save_asset(new_bp.get_path_name())
            report.append(f"SUCCESS: Created {name}")
            return new_bp
        return None

    char_bp = create_bp("BP_WWCharacter", "WWCharacter")
    enemy_bp = create_bp("BP_Bandit", "WWEnemy")
    gm_bp = create_bp("BP_WWGameMode", "WWGameMode")

    # 4. Configure GameMode
    if gm_bp:
        gm_class = gm_bp.generated_class()
        gm_cdo = unreal.get_default_object(gm_class)
        
        # Set Pawn and Enemy
        char_class = unreal.load_class(None, f"{char_path}.BP_WWCharacter_C")
        bandit_class = unreal.load_class(None, f"{enemy_path}.BP_Bandit_C")
        
        if char_class:
            gm_cdo.set_editor_property("default_pawn_class", char_class)
        if bandit_class:
            gm_cdo.set_editor_property("enemy_class", bandit_class)
            
        unreal.EditorAssetLibrary.save_asset(gm_path)
        report.append("SUCCESS: Configured GameMode Pawn/Enemy")

    # 5. Fix MainMap Override
    map_path = "/Game/Maps/MainMap"
    unreal.EditorLevelLibrary.load_level(map_path)
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        settings = world.get_world_settings()
        if gm_bp:
            # The property for GameMode override is 'default_game_mode'
            settings.set_editor_property("default_game_mode", gm_bp.generated_class())
            unreal.EditorLevelLibrary.save_current_level()
            report.append(f"SUCCESS: Set GameMode in MainMap settings")
    else: report.append("ERROR: MainMap not found")

    # Write report
    with open("D:/Unreal Projects/RootyTooty/force_setup_report.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    force_setup()
