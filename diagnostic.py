import unreal
print("--- PYTHON DIAGNOSTIC START ---")
print(f"Project Name: {unreal.SystemLibrary.get_game_name()}")
try:
    char_class = unreal.load_class(None, "/Script/RootyTooty.WWCharacter")
    print(f"WWCharacter class: {char_class}")
except Exception as e:
    print(f"Error loading WWCharacter: {e}")
print("--- PYTHON DIAGNOSTIC END ---")
