import unreal

# Load the Blueprint
bp_char = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_WWCharacter")

if bp_char:
    # Get the default object
    cdo = unreal.get_default_object(bp_char)
    
    # Try to get the mesh component
    mesh_comp = unreal.get_editor_property(cdo, 'mesh')
    if mesh_comp:
        print("=== BP_WWCharacter Mesh Component ===")
        
        # Check if mesh is set
        skeletal_mesh = unreal.get_editor_property(mesh_comp, 'skeletal_mesh')
        print(f"Skeletal Mesh: {skeletal_mesh}")
        
        # Check material count and what's assigned
        material_count = unreal.get_editor_property(mesh_comp, 'num_materials')
        print(f"Material Count: {material_count}")
        
        # Try to get materials
        for i in range(0, 4):
            mat = unreal.get_editor_property(mesh_comp, 'materials')
            if mat:
                print(f"Material Slot {i}: {mat}")
        
        # Check visibility
        visibility = unreal.get_editor_property(mesh_comp, 'visibility')
        print(f"Visibility: {visibility}")
        
        # Check hidden in game
        hidden_in_game = unreal.get_editor_property(mesh_comp, 'hidden_in_game')
        print(f"Hidden in Game: {hidden_in_game}")
        
        # Check cast shadow
        cast_shadow = unreal.get_editor_property(mesh_comp, 'cast_shadow')
        print(f"Cast Shadow: {cast_shadow}")
    else:
        print("Could not find mesh component")
else:
    print("Could not load BP_WWCharacter")
