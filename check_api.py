import unreal
editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
print("UnrealEditorSubsystem members:")
for member in dir(editor_sub):
    if "world" in member.lower():
        print(f"  - {member}")
