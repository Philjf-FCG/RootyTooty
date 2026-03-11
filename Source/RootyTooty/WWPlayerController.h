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
  virtual void OnPossess(APawn* InPawn) override;
  virtual void PostInitializeComponents() override;

private:
  void TryStartBackgroundMusic();

  UPROPERTY(EditAnywhere, Category = "Audio")
  bool bEnableBackgroundMusic;

  UPROPERTY(Transient)
  class UAudioComponent* BackgroundMusicComponent;

  UPROPERTY(Transient)
  int32 MusicStartAttempts;

  FTimerHandle BackgroundMusicRetryHandle;
};
