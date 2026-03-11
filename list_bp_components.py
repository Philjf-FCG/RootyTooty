import unreal

def dump_components(bp_path):
    print(f"\n--- Checking components for {bp_path} ---")
    cls = unreal.load_class(None, bp_path)
    if not cls: return
    cdo = unreal.get_default_object(cls)
    components = cdo.get_default_subobjects()
    for comp in components:
        print(f"Component: {comp.get_name()} | Type: {comp.get_class().get_name()}")
        if isinstance(comp, unreal.StaticMeshComponent):
            try:
                mesh = comp.get_editor_property("static_mesh")
                print(f"  Mesh: {mesh.get_path_name() if mesh else 'None'}")
                rot = comp.get_editor_property("relative_rotation")
                loc = comp.get_editor_property("relative_location")
                print(f"  Transform: {loc} / {rot}")
                parent = comp.get_editor_property("attach_parent")
                socket = comp.get_editor_property("attach_socket_name")
                print(f"  Attached to: {parent.get_name() if parent else 'None'} Socket: {socket}")
            except Exception as e:
                print(f"  Exception reading properties: {e}")

dump_components("/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
dump_components("/Game/Blueprints/BP_Bandit.BP_Bandit_C")
