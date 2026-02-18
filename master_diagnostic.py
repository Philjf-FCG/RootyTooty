import unreal

def diagnose_world():
    print("\n--- MASTER DIAGNOSTIC START ---")
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    print(f"Current World: {world.get_name()}")

    # 1. Inspect Actors
    print("\n[Actors In World]")
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    for actor in all_actors:
        label = actor.get_actor_label()
        loc = actor.get_actor_location()
        print(f"  Actor: {label} ({actor.get_class().get_name()}) at {loc}")

    # 2. Inspect Post Process Volumes
    print("\n[Post Process Volumes]")
    pp_volumes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PostProcessVolume)
    for pp in pp_volumes:
        settings = pp.get_editor_property("settings")
        unbound = pp.get_editor_property("bUnbound")
        priority = pp.get_editor_property("priority")
        bias = settings.get_editor_property("auto_exposure_bias")
        print(f"  Volume: {pp.get_actor_label()} | Unbound: {unbound} | Priority: {priority}")
        print(f"    Exposure Bias: {bias}")
        # Check for distortion
        chromatic = settings.get_editor_property("scene_fringe_intensity")
        vignette = settings.get_editor_property("vignette_intensity")
        print(f"    Chromatic Aberration: {chromatic} | Vignette: {vignette}")

    # 3. Inspect Blueprints
    print("\n[Blueprint Settings]")
    char_bp = unreal.load_asset("/Game/Blueprints/BP_Gunslinger")
    if char_bp:
        gen_class = char_bp.generated_class()
        cdo = unreal.get_default_object(gen_class)
        # Check Mesh
        mesh_comp = cdo.get_editor_property("mesh")
        if mesh_comp:
            mesh_asset = mesh_comp.get_editor_property("skeletal_mesh_asset")
            print(f"  BP_Gunslinger Mesh: {mesh_asset.get_name() if mesh_asset else 'NONE'}")
        
        # Check Camera in BP
        # Python visibility of BP components can be limited, but let's try
        try:
            # We can't easily iterate BP components via Python CDC, 
            # but we can check properties if they are exposed.
            pass
        except:
            pass
    else:
        print("  ERROR: BP_Gunslinger not found")

    # 4. Inspect GameMode
    print("\n[GameMode Settings]")
    gm_bp = unreal.load_asset("/Game/Blueprints/BP_WWGameMode")
    if gm_bp:
        cdo = unreal.get_default_object(gm_bp.generated_class())
        pawn_class = cdo.get_editor_property("default_pawn_class")
        print(f"  Default Pawn Class: {pawn_class.get_name() if pawn_class else 'NONE'}")
        # Check if it matches BP_Gunslinger
        if pawn_class and "BP_Gunslinger" not in pawn_class.get_name():
            print("  WARNING: Default Pawn Class is NOT BP_Gunslinger!")
    else:
        print("  ERROR: BP_WWGameMode not found")

    # 5. Check Project Settings
    print("\n[Project Settings]")
    maps_settings = unreal.get_default_object(unreal.GameMapsSettings)
    print(f"  Game Default Map: {maps_settings.get_editor_property('game_default_map').get_editor_property('asset_path_name')}")
    
    render_settings = unreal.get_default_object(unreal.RendererSettings)
    # Some settings might be hard to read via CDO, but let's try
    try:
        aa_method = render_settings.get_editor_property("default_anti_aliasing_method")
        print(f"  Anti-Aliasing Method: {aa_method}")
    except:
        pass

    print("\n--- MASTER DIAGNOSTIC END ---")

if __name__ == "__main__":
    diagnose_world()
