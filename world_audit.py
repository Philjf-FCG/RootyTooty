import unreal

def audit_game_world():
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        unreal.log_error("AUDIT_ERROR: No editor world found!")
        return

    unreal.log("--- WORLD AUDIT START ---")
    unreal.log(f"Active World: {world.get_name()}")
    
    # 1. Audit GameMode
    settings = world.get_world_settings()
    gm_class = settings.get_editor_property("default_game_mode")
    unreal.log(f"Current GameMode: {gm_class.get_name() if gm_class else 'NONE'}")
    
    # 2. Audit All Actors
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    unreal.log(f"Total Actors in Level: {len(actors)}")
    
    for actor in actors:
        label = actor.get_actor_label()
        loc = actor.get_actor_location()
        unreal.log(f"Actor: {label} | Class: {actor.get_class().get_name()} | Loc: {loc}")
        
        # Check for mesh components
        if isinstance(actor, unreal.StaticMeshActor):
            comp = actor.get_editor_property("static_mesh_component")
            mesh = comp.get_editor_property("static_mesh")
            unreal.log(f"  - Static Mesh: {mesh.get_name() if mesh else 'NONE'}")
        
        if isinstance(actor, unreal.Character):
            mesh_comp = actor.get_editor_property("mesh")
            mesh = mesh_comp.get_editor_property("skeletal_mesh_asset") # UE5.1+ usage
            if not mesh:
                mesh = mesh_comp.get_editor_property("skeletal_mesh") # Older UE5 usage
            unreal.log(f"  - Skeletal Mesh: {mesh.get_name() if mesh else 'NONE'}")
            
    # 3. Check for Game Default Map setting
    gen_settings = unreal.get_default_object(unreal.GameMapsSettings)
    def_map = gen_settings.get_editor_property("game_default_map")
    unreal.log(f"Project Default Map Setting: {def_map}")
    
    unreal.log("--- WORLD AUDIT COMPLETE ---")

if __name__ == "__main__":
    audit_game_world()
