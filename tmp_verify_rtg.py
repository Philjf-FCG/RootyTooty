import unreal

names = [
    "/Game/RTG_Western_MM_Idle",
    "/Game/RTG_Western_MF_Unarmed_Jog_Fwd",
    "/Game/RTG_Bobrito_MM_Idle",
    "/Game/RTG_Bobrito_MF_Unarmed_Jog_Fwd",
]

for path in names:
    asset = unreal.load_asset(path)
    if asset is None:
        print(f"FAIL load: {path}")
        continue
    asset_type = type(asset).__name__
    if isinstance(asset, unreal.AnimSequence):
        frames = asset.get_editor_property("number_of_sampled_frames") if hasattr(asset, "get_editor_property") else "?"
        length = asset.get_editor_property("sequence_length") if hasattr(asset, "sequence_length") else "?"
        try:
            frames = asset.get_number_of_sampled_keys()
        except:
            try:
                frames = asset.get_number_of_frames()
            except:
                frames = "?"
        try:
            length = asset.get_play_length()
        except:
            length = "?"
        print(f"OK [{asset_type}] {path}  frames={frames}  length={length}")
    else:
        print(f"OK [{asset_type}] {path}")
