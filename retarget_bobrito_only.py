import unreal

SOURCE_MESH_CANDIDATES = [
    "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
]
BOBRITO_TARGET_MESH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy"
RTG_PATH = "/Game/ImportedCharacters/Retarget/RTG_Manny_To_Bobrito.RTG_Manny_To_Bobrito"
ANIM_PATHS = [
    "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle",
    "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
    "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd",
]


def load_first(paths):
    for p in paths:
        a = unreal.load_asset(p)
        if a:
            return a
    return None

assets = []
seen = set()
for p in ANIM_PATHS:
    ad = unreal.EditorAssetLibrary.find_asset_data(p)
    if ad and ad.is_valid():
        pkg = str(ad.package_name)
        if pkg not in seen:
            seen.add(pkg)
            assets.append(ad)

src = load_first(SOURCE_MESH_CANDIDATES)
trg = unreal.load_asset(BOBRITO_TARGET_MESH)
rtg = unreal.load_asset(RTG_PATH)

if not src or not trg or not rtg or not assets:
    raise RuntimeError('Missing source/target/retargeter/assets')

created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    assets,
    src,
    trg,
    rtg,
    "",
    "",
    "RTG_Bobrito_",
    "",
    False,
    True,
)

unreal.log(f"RETARGET_BOBRITO_ONLY={ [str(a.package_name) for a in created] }")
