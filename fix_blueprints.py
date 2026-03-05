import unreal

print("=== Fixing Blueprint Animation References ===")

# Load the blueprints
player_bp_path = "/Game/Blueprints/BP_WWCharacter"
bandit_bp_path = "/Game/Blueprints/BP_Bandit"

player_bp = unreal.EditorAssetLibrary.load_blueprint_class(player_bp_path)
bandit_bp = unreal.EditorAssetLibrary.load_blueprint_class(bandit_bp_path)

if player_bp:
    player_cdo = unreal.get_default_object(player_bp)
    mesh_comp = player_cdo.get_editor_property('mesh')
    
    if mesh_comp:
        # Clear animation blueprint reference using correct property name
        try:
            mesh_comp.set_editor_property('animation_blueprint_generated_class', None)
            print("Cleared animation blueprint from BP_WWCharacter")
        except Exception:
            try:
                mesh_comp.set_editor_property('anim_class', None)
                print("Cleared anim_class from BP_WWCharacter")
            except Exception:
                print("Could not clear animation class (property not found, this may be OK)")
    
    unreal.EditorAssetLibrary.save_asset(player_bp_path)
    print("Saved BP_WWCharacter")

if bandit_bp:
    bandit_cdo = unreal.get_default_object(bandit_bp)
    mesh_comp = bandit_cdo.get_editor_property('mesh')
    
    if mesh_comp:
        # Clear animation blueprint reference using correct property name
        try:
            mesh_comp.set_editor_property('animation_blueprint_generated_class', None)
            print("Cleared animation blueprint from BP_Bandit")
        except Exception:
            try:
                mesh_comp.set_editor_property('anim_class', None)
                print("Cleared anim_class from BP_Bandit")
            except Exception:
                print("Could not clear animation class (property not found, this may be OK)")
    
    unreal.EditorAssetLibrary.save_asset(bandit_bp_path)
    print("Saved BP_Bandit")

print("=== Blueprint fixes complete! ===")

