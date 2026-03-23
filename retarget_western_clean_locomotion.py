import unreal

RETARGETER_PATH = "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Western.RTG_Manny_To_Western"
SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]
TARGET_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
SOURCE_ANIMS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Pistol/Jog/MF_Pistol_Jog_Fwd.MF_Pistol_Jog_Fwd",
    "/Game/Mannequins/Anims/Pistol/Jog/MF_Pistol_Jog_Fwd.MF_Pistol_Jog_Fwd",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a
    return None


def gather_assets():
    out = []
    seen = set()
    for p in SOURCE_ANIMS:
        ad = unreal.EditorAssetLibrary.find_asset_data(p)
        if ad and ad.is_valid():
            pkg = str(ad.package_name)
            if pkg not in seen:
                seen.add(pkg)
                out.append(ad)
    return out


def make_name(src_name: str) -> str:
    if src_name == "MM_Idle":
        return "/Game/RTG_Western_MM_Idle.RTG_Western_MM_Idle"
    if src_name == "MF_Pistol_Jog_Fwd":
        return "/Game/RTG_Western_MF_Pistol_Jog_Fwd_Clean.RTG_Western_MF_Pistol_Jog_Fwd_Clean"
    return f"/Game/RTG_Western_{src_name}.RTG_Western_{src_name}"


rtg = unreal.load_asset(RETARGETER_PATH)
src_mesh = load_first(SOURCE_MESH_CANDIDATES)
tgt_mesh = unreal.load_asset(TARGET_MESH_PATH)
assets = gather_assets()

if not rtg or not src_mesh or not tgt_mesh or not assets:
    raise RuntimeError("Missing retargeter/source/target/assets")

ctrl = unreal.IKRetargeterController.get_controller(rtg)
if not ctrl:
    raise RuntimeError("No retarget controller")

ctrl.remove_all_ops()
ctrl.add_default_ops()
for idx in [3, 2, 0]:
    ctrl.remove_retarget_op(idx)

unreal.EditorAssetLibrary.save_asset(RETARGETER_PATH)

created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    assets,
    src_mesh,
    tgt_mesh,
    rtg,
    "",
    "",
    "RTG_Western_",
    "",
    False,
    True,
)

for ad in created or []:
    pkg = str(ad.package_name)
    src_name = pkg.rsplit("/", 1)[-1]
    src_obj = f"{pkg}.{src_name}"
    dst_obj = make_name(src_name)
    if src_obj != dst_obj:
        if unreal.EditorAssetLibrary.does_asset_exist(dst_obj):
            unreal.EditorAssetLibrary.delete_asset(dst_obj)
        unreal.EditorAssetLibrary.rename_asset(src_obj, dst_obj)

unreal.EditorAssetLibrary.save_directory("/Game", False, True)
unreal.log("RETARGET_WESTERN_CLEAN_DONE")
