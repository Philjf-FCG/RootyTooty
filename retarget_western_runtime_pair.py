import unreal

RETARGETER_PATH = "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Western.RTG_Manny_To_Western"
SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]
TARGET_MESH_PATH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
ANIMS = [
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


def gather_anim_data(paths):
    out = []
    seen = set()
    for p in paths:
        ad = unreal.EditorAssetLibrary.find_asset_data(p)
        if ad and ad.is_valid():
            pkg = str(ad.package_name)
            if pkg not in seen:
                seen.add(pkg)
                out.append(ad)
    return out


rtg = unreal.load_asset(RETARGETER_PATH)
src = load_first(SOURCE_MESH_CANDIDATES)
tgt = unreal.load_asset(TARGET_MESH_PATH)
anim_data = gather_anim_data(ANIMS)

if not rtg or not src or not tgt or len(anim_data) < 2:
    raise RuntimeError("Missing retarget prerequisites")

ctrl = unreal.IKRetargeterController.get_controller(rtg)
if not ctrl:
    raise RuntimeError("No IKRetargeterController")

# Known-good op stack: FK + Root + Curve
ctrl.remove_all_ops()
ctrl.add_default_ops()
for idx in [3, 2, 0]:
    ctrl.remove_retarget_op(idx)
unreal.EditorAssetLibrary.save_asset(RETARGETER_PATH)

created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    anim_data,
    src,
    tgt,
    rtg,
    "",
    "",
    "RTG_Western_",
    "",
    False,
    True,
)

unreal.log("RETARGET_WESTERN_RUNTIME_PAIR=" + str([str(a.package_name) for a in (created or [])]))
