import unreal

world = unreal.EditorLevelLibrary.get_editor_world()
if not world:
    unreal.EditorLevelLibrary.load_level("/Game/Maps/VictoryMap")

with open('c:/Unreal Projects/rooty/RootyTooty/hat_output3.txt', 'w') as f:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    if actors:
        for actor in actors:
            if "Bandit" in actor.get_name() or "Character" in actor.get_name():
                comps = actor.get_components_by_class(unreal.StaticMeshComponent)
                for comp in comps:
                    if "Hat" in comp.get_name():
                        f.write(f"Actor: {actor.get_name()} | Component: {comp.get_name()}\n")
                        f.write(f"  Parent: {comp.get_attach_parent().get_name() if comp.get_attach_parent() else 'None'}\n")
                        f.write(f"  Socket: {comp.get_attach_socket_name()}\n")
                        f.write(f"  Rel Loc: {comp.relative_location}\n")
                        f.write(f"  Rel Rot: {comp.relative_rotation}\n")
                        f.write(f"  Rel Scale: {comp.relative_scale3d}\n")
                        f.write(f"  World Loc: {comp.get_world_location()}\n")
    else:
        f.write("No actors found in level.\n")
