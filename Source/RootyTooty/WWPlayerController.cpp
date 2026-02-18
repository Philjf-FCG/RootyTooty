#include "WWPlayerController.h"

AWWPlayerController::AWWPlayerController(
    const FObjectInitializer &ObjectInitializer)
    : Super(ObjectInitializer) {
  // We are keeping this minimal for now to ensure the build passes.
  // We will force the settings via either .ini or a more robust C++ method
  // later.
  UE_LOG(LogTemp, Warning, TEXT("[DEBUG] WWPlayerController Initialized"));
}
