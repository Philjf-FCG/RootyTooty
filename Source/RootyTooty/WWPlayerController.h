#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "WWPlayerController.generated.h"

UCLASS()
class ROOTYTOOTY_API AWWPlayerController : public APlayerController {
  GENERATED_BODY()

public:
  AWWPlayerController(
      const FObjectInitializer &ObjectInitializer = FObjectInitializer::Get());

protected:
  virtual void BeginPlay() override;

private:
  UPROPERTY(EditAnywhere, Category = "Audio")
  bool bEnableBackgroundMusic;

  UPROPERTY(Transient)
  class UAudioComponent* BackgroundMusicComponent;
};
