import unreal

def create_character_blueprint(blueprint_name, parent_class_name):
    package_path = f"/Game/Blueprints/{blueprint_name}"
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        print(f"Blueprint already exists: {package_path}. Skipping creation.")
        return unreal.load_asset(package_path)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    
    # Load the parent class
    parent_class = unreal.load_class(None, f"/Script/RootyTooty.{parent_class_name}")
    if not parent_class:
        print(f"ERROR: Parent class {parent_class_name} not found!")
        return None
        
    factory.set_editor_property("parent_class", parent_class)
    
    new_asset = asset_tools.create_asset(blueprint_name, "/Game/Blueprints", unreal.Blueprint, factory)
    if new_asset:
        unreal.EditorAssetLibrary.save_asset(new_asset.get_path_name())
        print(f"SUCCESS: Created Blueprint: {blueprint_name}")
    return new_asset

def set_character_mesh(blueprint_name, skeletal_mesh_path):
    blueprint_path = f"/Game/Blueprints/{blueprint_name}"
    blueprint = unreal.load_asset(blueprint_path)
    if not blueprint:
        print(f"ERROR: Failed to load blueprint: {blueprint_path}")
        return

    skeletal_mesh = unreal.load_asset(skeletal_mesh_path)
    if not skeletal_mesh:
        print(f"ERROR: Failed to load skeletal mesh: {skeletal_mesh_path}")
        return

    # Load the generated class
    class_path = f"{blueprint_path}.{blueprint_name}_C"
    blueprint_class = unreal.load_class(None, class_path)
    
    if blueprint_class:
        default_object = unreal.get_default_object(blueprint_class)
        mesh_component = default_object.get_editor_property("mesh")
        if mesh_component:
            mesh_component.set_editor_property("skeletal_mesh_asset", skeletal_mesh)
            unreal.EditorAssetLibrary.save_asset(blueprint_path)
            print(f"SUCCESS: Assigned mesh {skeletal_mesh_path} to {blueprint_name}")
        else:
            print(f"ERROR: Could not find Mesh component on {blueprint_name}")
    else:
        print(f"ERROR: Failed to load class: {class_path}")

def create_gamemode_blueprint(blueprint_name, parent_class_name):
    package_path = f"/Game/Blueprints/{blueprint_name}"
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        print(f"Blueprint already exists: {package_path}. Skipping creation.")
        return unreal.load_asset(package_path)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.load_class(None, f"/Script/RootyTooty.{parent_class_name}"))
    
    new_asset = asset_tools.create_asset(blueprint_name, "/Game/Blueprints", unreal.Blueprint, factory)
    if new_asset:
        unreal.EditorAssetLibrary.save_asset(new_asset.get_path_name())
        print(f"SUCCESS: Created Blueprint: {blueprint_name}")
    return new_asset

def configure_gamemode(gamemode_blueprint_name):
    blueprint_path = f"/Game/Blueprints/{gamemode_blueprint_name}"
    class_path = f"{blueprint_path}.{gamemode_blueprint_name}_C"
    gm_class = unreal.load_class(None, class_path)
    
    if gm_class:
        default_object = unreal.get_default_object(gm_class)
        
        # Set Default Pawn Class
        pawn_class = unreal.load_class(None, "/Game/Blueprints/BP_Gunslinger.BP_Gunslinger_C")
        if pawn_class:
            default_object.set_editor_property("default_pawn_class", pawn_class)
            
        # Set Enemy Class for our spawner
        enemy_class = unreal.load_class(None, "/Game/Blueprints/BP_Bandit.BP_Bandit_C")
        if enemy_class:
            default_object.set_editor_property("enemy_class", enemy_class)
            
        unreal.EditorAssetLibrary.save_asset(blueprint_path)
        print(f"SUCCESS: Configured GameMode: {gamemode_blueprint_name}")

# --- Execution ---
print("Starting Blueprint Setup...")

# 1. Create Blueprints
create_character_blueprint("BP_Gunslinger", "WWCharacter")
create_character_blueprint("BP_Bandit", "WWEnemy")

# 2. Assign Meshes
mesh_path = "/Engine/EditorMeshes/SkeletalMesh/DefaultSkeletalMesh.DefaultSkeletalMesh"
set_character_mesh("BP_Gunslinger", mesh_path)
set_character_mesh("BP_Bandit", mesh_path)

# 3. GameMode
create_gamemode_blueprint("BP_WWGameMode", "WWGameMode")
configure_gamemode("BP_WWGameMode")

print("Blueprint Setup Complete.")
