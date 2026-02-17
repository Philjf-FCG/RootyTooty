using UnrealBuildTool;
using System.Collections.Generic;

public class RootyTootyEditorTarget : TargetRules
{
	public RootyTootyEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V6;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RootyTooty");
	}
}
