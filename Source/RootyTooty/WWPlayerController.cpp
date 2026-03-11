#include "WWPlayerController.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

namespace {
USoundBase* LoadFirstSound(std::initializer_list<const TCHAR*> Paths) {
  for (const TCHAR* Path : Paths) {
    if (USoundBase* Sound = Cast<USoundBase>(
            StaticLoadObject(USoundBase::StaticClass(), nullptr, Path))) {
      return Sound;
    }
  }
  return nullptr;
}
} // namespace

AWWPlayerController::AWWPlayerController(
    const FObjectInitializer &ObjectInitializer)
    : Super(ObjectInitializer) {
  bEnableBackgroundMusic = true;
  BackgroundMusicComponent = nullptr;
  UE_LOG(LogTemp, Warning, TEXT("[DEBUG] WWPlayerController Initialized"));
}

void AWWPlayerController::BeginPlay() {
  Super::BeginPlay();

  // Only local controller should start menu/gameplay music.
  if (!IsLocalController()) {
    return;
  }

  if (!bEnableBackgroundMusic) {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] Background music disabled for stability."));
    return;
  }

  if (BackgroundMusicComponent && BackgroundMusicComponent->IsPlaying()) {
    return;
  }

  USoundBase* Bgm = LoadFirstSound({
      TEXT("/Game/Audio/BGM_Ragtime.BGM_Ragtime"),
      TEXT("/Game/Audio/back_drop-ragtime-piano-honky-tonk-swipesy-354895.back_drop-ragtime-piano-honky-tonk-swipesy-354895"),
      TEXT("/Game/Audio/WesternMusic.WesternMusic")});

  if (!Bgm) {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] BGM asset not found. Skipping music playback."));
    return;
  }

  BackgroundMusicComponent = UGameplayStatics::SpawnSound2D(this, Bgm, 0.35f);
  if (BackgroundMusicComponent) {
    BackgroundMusicComponent->bAutoDestroy = false;
    BackgroundMusicComponent->Play();
  }
}
