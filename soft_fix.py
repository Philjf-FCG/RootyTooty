import unreal

def soft_fix():
    report = []
    bp_folder = "/Game/Blueprints"
    
    def get_or_create_bp(name, parent_class_name):
        path = f"{bp_folder}/{name}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            report.append(f"Asset exists: {name}")
            return unreal.load_asset(path)
        
        report.append(f"Creating new asset: {name}")
        factory = unreal.BlueprintFactory()
        parent_class = unreal.load_class(None, f"/Script/RootyTooty.{parent_class_name}")
        if not parent_class:
            report.append(f"ERROR: Parent class {parent_class_name} not found!")
            return None
        factory.set_editor_property("parent_class", parent_class)
        return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, bp_folder, unreal.Blueprint, factory)

    # 1. Ensure BPs exist
    char_bp = get_or_create_bp("BP_WWCharacter", "WWCharacter")
    enemy_bp = get_or_create_bp("BP_Bandit", "WWEnemy")
    gm_bp = get_or_create_bp("BP_WWGameMode", "WWGameMode")

    # 2. Configure GameMode
    if gm_bp:
        gm_class = gm_bp.generated_class()
        gm_cdo = unreal.get_default_object(gm_class)
        
        char_class = unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
        bandit_class = unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
        
        if char_class:
            gm_cdo.set_editor_property("default_pawn_class", char_class)
            report.append("Set DefaultPawnClass to BP_WWCharacter")
        if bandit_class:
            gm_cdo.set_editor_property("enemy_class", bandit_class)
            report.append("Set EnemyClass to BP_Bandit")
            
        unreal.EditorAssetLibrary.save_asset(gm_bp.get_path_name())

    # 3. Fix Map
    map_path = "/Game/Maps/MainMap"
    unreal.EditorLevelLibrary.load_level(map_path)
    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        settings = world.get_world_settings()
        if gm_bp:
            settings.set_editor_property("default_game_mode", gm_bp.generated_class())
            unreal.EditorLevelLibrary.save_current_level()
            report.append("Set MainMap GameMode override")
    
    # Write report
    with open("D:/Unreal Projects/RootyTooty/soft_fix_report.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    soft_fix()
