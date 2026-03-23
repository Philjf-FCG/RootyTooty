import unreal

ASSET_NAME = "WBP_HUDPanel"
PACKAGE_PATH = "/Game/UI"
ASSET_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}"

if unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH):
    unreal.log(f"WIDGET_BP already exists: {ASSET_PATH}")
else:
    parent_cls = unreal.load_class(None, "/Script/RootyTooty.WWUpgradePanelWidget")
    if not parent_cls:
        raise RuntimeError("Could not load parent class /Script/RootyTooty.WWUpgradePanelWidget")

    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("ParentClass", parent_cls)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    created = asset_tools.create_asset(ASSET_NAME, PACKAGE_PATH, unreal.WidgetBlueprint, factory)
    if not created:
        raise RuntimeError("Failed to create Widget Blueprint asset")

    unreal.EditorAssetLibrary.save_loaded_asset(created)
    unreal.log(f"WIDGET_BP created: {created.get_path_name()}")
