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
  virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
  virtual void OnPossess(APawn* InPawn) override;
  virtual void PostInitializeComponents() override;
  virtual void PlayerTick(float DeltaTime) override;

private:
  void BindHudToCurrentCharacter();
  void HandleObservedCharacterStatsChanged();
  void EnsureHudPanel();
  void RefreshHudPanel();
  void TryStartBackgroundMusic();

  UPROPERTY(EditDefaultsOnly, Category = "HUD")
  TSubclassOf<class UWWUpgradePanelWidget> HudPanelWidgetClass;

  UPROPERTY(EditAnywhere, Category = "Audio")
  bool bEnableBackgroundMusic;

  UPROPERTY(Transient)
  class UAudioComponent* BackgroundMusicComponent;

  UPROPERTY(Transient)
  int32 MusicStartAttempts;

  UPROPERTY(Transient)
  class UWWUpgradePanelWidget* HudPanelWidget;

  UPROPERTY(Transient)
  class AWWCharacter* ObservedHudCharacter;

  FTimerHandle BackgroundMusicRetryHandle;
};
