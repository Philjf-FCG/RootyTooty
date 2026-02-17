import unreal

def inspect_level():
    report = []
    map_path = "/Game/Maps/MainMap"
    unreal.EditorLevelLibrary.load_level(map_path)
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    if world:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        report.append(f"Level: {map_path}")
        report.append(f"Total Actors: {len(actors)}")
        for actor in actors:
            report.append(f" - {actor.get_name()} ({actor.get_class().get_name()})")
            
        settings = world.get_world_settings()
        gm_override = settings.get_editor_property("default_game_mode")
        report.append(f"GameMode Override: {gm_override.get_name() if gm_override else 'NONE'}")
    else:
        report.append("ERROR: World not found")

    with open("D:/Unreal Projects/RootyTooty/level_inspection.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    inspect_level()
