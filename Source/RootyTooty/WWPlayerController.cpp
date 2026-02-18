#include "WWPlayerController.h"

AWWPlayerController::AWWPlayerController(
    const FObjectInitializer &ObjectInitializer)
    : Super(ObjectInitializer) {
  UE_LOG(LogTemp, Warning,
         TEXT("[DEBUG] WWPlayerController Constructor Called"));
}
