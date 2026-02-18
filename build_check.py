import unreal
import os
import datetime

def build_status_check():
    print("\n" + "="*50)
    print("--- ADVANCED BUILD VERIFICATION START ---")
    print("="*50)
    
    # 1. Check DLL Timestamp
    dll_path = r"c:\Unreal Projects\rooty\RootyTooty\Binaries\Win64\UnrealEditor-RootyTooty.dll"
    if os.path.exists(dll_path):
        mtime = os.path.getmtime(dll_path)
        dt_mtime = datetime.datetime.fromtimestamp(mtime)
        print(f"DLL on disk: {dll_path}")
        print(f"DLL Last Modified: {dt_mtime}")
    else:
        print(f"CRITICAL: DLL NOT FOUND at {dll_path}!")

    # 2. Check Class Connection
    char_class = unreal.load_class(None, "/Game/Blueprints/BP_WWCharacter.BP_WWCharacter_C")
    if char_class:
        cdo = unreal.get_default_object(char_class)
        # Check standard properties and our new custom ones
        # Unreal Python often maps PascalCase to snake_case
        test_pairs = [
            ("DefaultMappingContext", "default_mapping_context"),
            ("MoveAction", "move_action"),
            ("MoveSpeed", "move_speed")
        ]
        
        print("\nChecking Blueprint CDO for C++ Properties:")
        for pascal, snake in test_pairs:
            found = False
            # Method 1: getattr (Pascal)
            try:
                val = getattr(cdo, pascal)
                print(f"  [FOUND] {pascal} (via getattr)")
                found = True
            except: pass
            
            # Method 2: getattr (Snake)
            if not found:
                try:
                    val = getattr(cdo, snake)
                    print(f"  [FOUND] {snake} (via getattr snake_case)")
                    found = True
                except: pass
                
            # Method 3: get_editor_property
            if not found:
                try:
                    val = cdo.get_editor_property(pascal)
                    print(f"  [FOUND] {pascal} (via get_editor_property)")
                    found = True
                except: pass
                
            if not found:
                print(f"  [MISSING] {pascal} (Checked all methods)")

    print("\nNOTE: If everything says MISSING but the DLL time is new,")
    print("you MUST RESTART THE UNREAL EDITOR.")
    print("Unreal cannot always Hot Reload header changes (.h files).")
    print("="*50)
    print("--- BUILD VERIFICATION END ---")

if __name__ == "__main__":
    build_status_check()
