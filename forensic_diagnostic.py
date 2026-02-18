import unreal

def forensic_diagnostic():
    print("\n--- FORENSIC DIAGNOSTIC START ---")
    
    # 1. Check Blueprint Parent
    bp_path = "/Game/Blueprints/BP_WWCharacter"
    bp_asset = unreal.load_asset(bp_path)
    if bp_asset:
        print(f"Blueprint Asset Loaded: {bp_path}")
        gen_class = bp_asset.generated_class()
        
        if gen_class:
            # Most robust way to see inheritance in Python
            cdo = unreal.get_default_object(gen_class)
            actual_class = cdo.get_class()
            print(f"  CDO Class: {actual_class.get_name()}")
            
            # Check for properties on the CDO
            print("\n[CDO Properties Check]")
            test_props = ["DefaultMappingContext", "MoveAction", "MoveSpeed", "CameraComp", "SpringArmComp", "MaxHealth"]
            for p in test_props:
                try:
                    # Generic way to check if an attribute exists
                    if hasattr(cdo, p):
                        val = getattr(cdo, p)
                        print(f"  {p}: FOUND | Value: {val}")
                    else:
                        # Try the editor property system as fallback
                        val = cdo.get_editor_property(p)
                        print(f"  {p}: FOUND (via EditorProperty) | Value: {val}")
                except Exception as e:
                    print(f"  {p}: MISSING (Error: {str(e).splitlines()[0]})")
        else:
            print("  ERROR: Generated Class could not be retrieved from Blueprint!")
    else:
        print(f"ERROR: Could not load asset at {bp_path}")

    # 2. World & Environmental Analysis
    world = unreal.EditorLevelLibrary.get_editor_world()
    print(f"\nActive World: {world.get_name()}")
    
    # 3. Actor Placement & Visibility
    # Check if a PlayerStart actually exists
    player_starts = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PlayerStart)
    print(f"Player Starts Found: {len(player_starts)}")
    for ps in player_starts:
        print(f"  - {ps.get_actor_label()} at {ps.get_actor_location()}")

    # Check for Ground/Floor
    static_meshes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
    print(f"Static Mesh Actors Found: {len(static_meshes)}")
    for sm in static_meshes:
        print(f"  - {sm.get_actor_label()} at {sm.get_actor_location()}")

    # 4. Light & Exposure Analysis
    lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Light)
    print(f"\nLights Found: {len(lights)}")
    for l in lights:
        try:
            lc = l.light_component
            intensity = lc.intensity
            print(f"  - {l.get_actor_label()} ({l.get_class().get_name()}) | {intensity}")
        except:
            print(f"  - {l.get_actor_label()} | Property access failed")

    print("\n--- FORENSIC DIAGNOSTIC END ---")

if __name__ == "__main__":
    forensic_diagnostic()
