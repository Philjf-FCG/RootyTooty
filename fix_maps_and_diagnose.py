import unreal
import os

def diagnose_and_fix():
    report = []
    report.append("--- DIAGNOSIS REPORT ---")
    
    # 1. Check/Set GameMode Override in MainMap
    map_path = "/Game/Maps/MainMap"
    gm_path = "/Game/Blueprints/BP_WWGameMode"
    
    unreal.EditorLevelLibrary.load_level(map_path)
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    if world:
        settings = world.get_world_settings()
        gm_bp = unreal.load_asset(gm_path)
        if gm_bp:
            settings.set_editor_property("game_mode_override", gm_bp.generated_class())
            unreal.EditorLevelLibrary.save_current_level()
            report.append(f"SUCCESS: Set GameMode override to {gm_path} in {map_path}")
        else:
            report.append(f"ERROR: Could not load GameMode at {gm_path}")
    else:
        report.append(f"ERROR: Could not load level at {map_path}")

    # 2. Verify Character Blueprint Components
    char_bp_path = "/Game/Blueprints/BP_Gunslinger"
    char_bp = unreal.load_asset(char_bp_path)
    if char_bp:
        report.append(f"Found character BP: {char_bp_path}")
        cdo = unreal.get_default_object(char_bp.generated_class())
        # Check for components in CDO
        components = unreal.EditorFilterLibrary.by_class(cdo.get_editor_property("root_component").get_children_components(True), unreal.CameraComponent)
        report.append(f"Camera Components found: {len(components)}")
    else:
        report.append(f"ERROR: BP_Gunslinger missing!")

    report.append("--- DIAGNOSIS END ---")
    
    # Write report to file
    with open("D:/Unreal Projects/RootyTooty/diagnosis_report.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    diagnose_and_fix()
