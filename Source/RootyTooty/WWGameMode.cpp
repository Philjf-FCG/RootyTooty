#include "WWGameMode.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "WWEnemy.h"


AWWGameMode::AWWGameMode() {
  PrimaryActorTick.bCanEverTick = true;
  SpawnInterval = 2.0f;
  SpawnRadius = 1500.0f;
  SpawnTimer = 0.0f;
}

void AWWGameMode::BeginPlay() { Super::BeginPlay(); }

void AWWGameMode::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  SpawnTimer += DeltaTime;
  if (SpawnTimer >= SpawnInterval) {
    SpawnEnemy();
    SpawnTimer = 0.0f;
  }
}

void AWWGameMode::SpawnEnemy() {
  APawn *PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
  if (!PlayerPawn || !EnemyClass)
    return;

  FVector PlayerLocation = PlayerPawn->GetActorLocation();
  float Angle = FMath::FRandRange(0.0f, 2.0f * PI);
  FVector SpawnOffset =
      FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0.0f) * SpawnRadius;
  FVector SpawnLocation = PlayerLocation + SpawnOffset;

  GetWorld()->SpawnActor<AWWEnemy>(EnemyClass, SpawnLocation,
                                   FRotator::ZeroRotator);
}
