import unreal


def save_tiny_skeleton():
    skeleton = unreal.load_asset("/Game/Assets/SKM_Tiny_Cowboy_Skeleton.SKM_Tiny_Cowboy_Skeleton")
    if not skeleton:
        unreal.log_error("SKELETON_SAVE: Could not load /Game/Assets/SKM_Tiny_Cowboy_Skeleton")
        return

    # Loading the bandit mesh first can force any pending skeleton-bone merge state.
    bandit = unreal.load_asset("/Game/Assets/SKM_Tiny_Bandit.SKM_Tiny_Bandit")
    if bandit:
        unreal.log("SKELETON_SAVE: Loaded SKM_Tiny_Bandit before save")

    unreal.EditorAssetLibrary.save_loaded_asset(skeleton)
    unreal.log("SKELETON_SAVE: Saved SKM_Tiny_Cowboy_Skeleton")


if __name__ == "__main__":
    save_tiny_skeleton()
