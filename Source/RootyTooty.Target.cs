using UnrealBuildTool;
using System.Collections.Generic;

public class RootyTootyTarget : TargetRules
{
	public RootyTootyTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V6;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RootyTooty");
	}
}
