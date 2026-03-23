import unreal

SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]
TARGET_WESTERN_MESH = "/Game/ImportedCharacters/Western/SK_WesternPlayer.SK_WesternPlayer"
RETARGETER_PATH = "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Western.RTG_Manny_To_Western"
ANIM_CANDIDATES = [
    "/Game/Characters/Mannequins/Anims/Pistol/Jog/MF_Pistol_Jog_Fwd.MF_Pistol_Jog_Fwd",
    "/Game/Mannequins/Anims/Pistol/Jog/MF_Pistol_Jog_Fwd.MF_Pistol_Jog_Fwd",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a
    return None


anim_data = []
seen = set()
for path in ANIM_CANDIDATES:
    ad = unreal.EditorAssetLibrary.find_asset_data(path)
    if ad and ad.is_valid():
        pkg = str(ad.package_name)
        if pkg not in seen:
            seen.add(pkg)
            anim_data.append(ad)

src = load_first(SOURCE_MESH_CANDIDATES)
trg = unreal.load_asset(TARGET_WESTERN_MESH)
rtg = unreal.load_asset(RETARGETER_PATH)

if not src or not trg or not rtg or not anim_data:
    raise RuntimeError("Missing source/target/retargeter/anim asset")

created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    anim_data,
    src,
    trg,
    rtg,
    "",
    "",
    "RTG_Western_",
    "",
    False,
    True,
)

unreal.log("RETARGET_WESTERN_PISTOL_JOG=" + str([str(a.package_name) for a in created]))
