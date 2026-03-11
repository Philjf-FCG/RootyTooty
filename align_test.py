import unreal

def attach_and_align():
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if "Bandit" in actor.get_name() or "Character" in actor.get_name():
            # Get the skeletal mesh
            skel_mesh = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            hats = [c for c in actor.get_components_by_class(unreal.StaticMeshComponent) if "Hat" in c.get_name()]
            for hat in hats:
                hat.attach_to_component(skel_mesh, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_RELATIVE, "head")
                hat.set_relative_scale3d(unreal.Vector(0.28, 0.28, 0.28))
                # For standard Manny head bone, X is forward, Z is up (or along neck), Y is right
                # The hat usually needs to be rotated maybe -90 on pitch?
                hat.set_relative_rotation(unreal.Rotator(0, 90, -90))
                hat.set_relative_location(unreal.Vector(5.0, 15.0, 0.0))
                print(f"Set hat on {actor.get_name()} to {hat.relative_location}, {hat.relative_rotation}")

attach_and_align()
