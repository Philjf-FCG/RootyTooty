import unreal

def verify_render():
    print("--- RENDER VERIFICATION START ---")
    
    # Check for PostProcessVolume
    pp_volumes = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PostProcessVolume)
    if not pp_volumes:
        print("WARNING: No PostProcessVolume found in the level.")
    else:
        for pp in pp_volumes:
            settings = pp.get_editor_property("settings")
            bias = settings.get_editor_property("auto_exposure_bias")
            method = settings.get_editor_property("auto_exposure_method")
            unbound = pp.get_editor_property("bUnbound")
            print(f"PostProcessVolume: {pp.get_actor_label()}")
            print(f"  Unbound: {unbound}")
            print(f"  Auto Exposure Bias: {bias}")
            print(f"  Auto Exposure Method: {method}")

    # Check Directional Light
    lights = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.DirectionalLight)
    if not lights:
        print("WARNING: No DirectionalLight found in the level.")
    else:
        for light in lights:
            lc = light.get_editor_property("light_component")
            intensity = lc.get_editor_property("intensity")
            mobility = lc.get_editor_property("mobility")
            print(f"DirectionalLight: {light.get_actor_label()}")
            print(f"  Intensity: {intensity}")
            print(f"  Mobility: {mobility}")

    # Check for Player Start
    player_starts = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.PlayerStart)
    if not player_starts:
        print("WARNING: No PlayerStart found in the level.")
    else:
        for ps in player_starts:
            print(f"PlayerStart: {ps.get_actor_label()} at {ps.get_actor_location()}")

    print("--- RENDER VERIFICATION END ---")

if __name__ == "__main__":
    verify_render()
