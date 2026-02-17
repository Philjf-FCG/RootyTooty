import unreal
import sys

def log(msg):
    print(f"DEBUG_FIX: {msg}")
    sys.stdout.flush()

def populate_debug():
    map_path = "/Game/Maps/MainMap"
    log(f"Attempting to load level: {map_path}")
    unreal.EditorLevelLibrary.load_level(map_path)
    log("Level loaded successfully")
    
    log("Spawning Floor actor...")
    floor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
    if floor:
        log("Floor actor spawned")
        floor.set_actor_label("Floor")
        log("Set floor label")
    else:
        log("FAILED to spawn floor")

    log("Saving level...")
    unreal.EditorLevelLibrary.save_current_level()
    log("Level saved successfully")

if __name__ == "__main__":
    try:
        populate_debug()
    except Exception as e:
        log(f"PYTHON ERROR: {str(e)}")
