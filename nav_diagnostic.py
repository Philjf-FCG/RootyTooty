import unreal

def nav_diagnostic():
    print("\n--- NAVIGATION & TICK DIAGNOSTIC START ---")
    
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_sub.get_game_world()
    if not world:
        world = editor_sub.get_editor_world()
        print(f"Using Editor World: {world.get_name()}")
    else:
        print(f"Using Active PIE World: {world.get_name()}")

    # 1. Global Settings
    time_dilation = unreal.GameplayStatics.get_global_time_dilation(world)
    print(f"Global Time Dilation: {time_dilation}")

    # 2. Check for NavMesh (Bandits might need it if they use AI MoveTo, though current code uses Tick)
    nav_volumes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.NavMeshBoundsVolume)
    print(f"NavMeshBoundsVolumes found: {len(nav_volumes)}")

    # 3. Check Actors
    char_classes = [
        ("/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C", "Player"),
        ("/Game/Blueprints/BP_Bandit.BP_Bandit_C", "Bandit")
    ]
    
    for path, label in char_classes:
        cls = unreal.load_class(None, path)
        if cls:
            actors = unreal.GameplayStatics.get_all_actors_of_class(world, cls)
            print(f"\n--- Checking {label} (Count: {len(actors)}) ---")
            for a in actors:
                # Check Tick Status via actor methods
                is_tick_enabled = a.is_actor_tick_enabled()
                print(f"  - {a.get_name()} | TickEnabled: {is_tick_enabled}")
                
                # Check Movement Component
                cmc = a.get_component_by_class(unreal.CharacterMovementComponent)
                if cmc:
                    speed = cmc.get_editor_property("max_walk_speed")
                    is_active = cmc.is_active()
                    velocity = cmc.velocity
                    gravity = cmc.get_editor_property("gravity_scale")
                    movement_mode = cmc.get_editor_property("movement_mode")
                    print(f"    Movement: Active={is_active} | Mode={movement_mode} | MaxSpeed={speed} | Velocity={velocity}")
                else:
                    print("    WARNING: No CharacterMovementComponent found!")
    
    print("\n--- NAVIGATION & TICK DIAGNOSTIC END ---")

if __name__ == "__main__":
    nav_diagnostic()
