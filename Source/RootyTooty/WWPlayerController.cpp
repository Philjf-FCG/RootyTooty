#include "WWPlayerController.h"
#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "TimerManager.h"

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
  MusicStartAttempts = 0;
  UE_LOG(LogTemp, Warning, TEXT("[DEBUG] WWPlayerController Initialized (AUDIO_PATCH_V2)"));
}

void AWWPlayerController::BeginPlay() {
  Super::BeginPlay();

  TryStartBackgroundMusic();
}

void AWWPlayerController::OnPossess(APawn* InPawn) {
  Super::OnPossess(InPawn);

  TryStartBackgroundMusic();
}

void AWWPlayerController::PostInitializeComponents() {
  Super::PostInitializeComponents();

  TryStartBackgroundMusic();
}

void AWWPlayerController::TryStartBackgroundMusic() {
  ++MusicStartAttempts;

  const UWorld* World = GetWorld();
  UE_LOG(LogTemp, Warning, TEXT("[AUDIO] Attempt %d | Local=%s | World=%s"),
         MusicStartAttempts,
         IsLocalController() ? TEXT("true") : TEXT("false"),
         World ? *World->GetName() : TEXT("<null>"));

  // Only local controller should start menu/gameplay music.
  if (!IsLocalController()) {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] Skip BGM attempt %d: not local controller."), MusicStartAttempts);
    return;
  }

  if (!bEnableBackgroundMusic) {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] Background music was disabled in defaults; forcing enable at runtime."));
    bEnableBackgroundMusic = true;
  }

  if (BackgroundMusicComponent && BackgroundMusicComponent->IsPlaying()) {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] BGM already playing on attempt %d."), MusicStartAttempts);
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

  BackgroundMusicComponent = UGameplayStatics::CreateSound2D(this, Bgm, 1.0f);
  if (BackgroundMusicComponent) {
    BackgroundMusicComponent->bAutoDestroy = false;
    BackgroundMusicComponent->bIsUISound = false;
    BackgroundMusicComponent->bAllowSpatialization = false;
    BackgroundMusicComponent->SetVolumeMultiplier(1.0f);
    BackgroundMusicComponent->SetPitchMultiplier(1.0f);
    BackgroundMusicComponent->Play();
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] BGM started via CreateSound2D: %s (attempt %d)"), *Bgm->GetName(), MusicStartAttempts);
  } else {
    UE_LOG(LogTemp, Warning, TEXT("[AUDIO] CreateSound2D returned null, trying SpawnSound2D fallback."));
    BackgroundMusicComponent = UGameplayStatics::SpawnSound2D(this, Bgm, 1.0f, 1.0f, 0.0f, nullptr, true, false);
    if (BackgroundMusicComponent) {
      BackgroundMusicComponent->bAutoDestroy = false;
      UE_LOG(LogTemp, Warning, TEXT("[AUDIO] BGM started via SpawnSound2D fallback: %s (attempt %d)"), *Bgm->GetName(), MusicStartAttempts);
    }
  }

  if ((!BackgroundMusicComponent || !BackgroundMusicComponent->IsPlaying()) && MusicStartAttempts < 6) {
    if (UWorld* RetryWorld = GetWorld()) {
      RetryWorld->GetTimerManager().ClearTimer(BackgroundMusicRetryHandle);
      RetryWorld->GetTimerManager().SetTimer(
          BackgroundMusicRetryHandle,
          this,
          &AWWPlayerController::TryStartBackgroundMusic,
          0.5f,
          false);
      UE_LOG(LogTemp, Warning, TEXT("[AUDIO] BGM not playing yet. Scheduling retry %d."), MusicStartAttempts + 1);
    }
  } else if (!BackgroundMusicComponent || !BackgroundMusicComponent->IsPlaying()) {
    UE_LOG(LogTemp, Error, TEXT("[AUDIO] BGM failed to start after %d attempts."), MusicStartAttempts);
  }
}
