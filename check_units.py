import unreal
try:
    print("LightUnits members:")
    for member in dir(unreal.LightUnits):
        if not member.startswith("_"):
            print(f"  - {member}")
except Exception as e:
    print(f"Error checking LightUnits: {e}")
