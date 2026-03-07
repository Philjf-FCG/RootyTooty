#include "WWGameMode.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "WWEnemy.h"
#include "WWPlayerController.h"

AWWGameMode::AWWGameMode() {
  PrimaryActorTick.bCanEverTick = true;
  PrimaryActorTick.TickInterval = 0.1f;
  SpawnInterval = 3.0f;
  SpawnRadius = 1500.0f;
  MaxAliveEnemies = 10;
  SpawnTimer = 0.0f;

  PlayerControllerClass = AWWPlayerController::StaticClass();
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
  if (!PlayerPawn) {
    // UE_LOG(LogTemp, Warning, TEXT("[DEBUG] SpawnEnemy: No PlayerPawn
    // found"));
    return;
  }

  if (!EnemyClass) {
    UE_LOG(LogTemp, Error, TEXT("SpawnEnemy: EnemyClass is NULL"));
    return;
  }

  TArray<AActor*> ExistingEnemies;
  UGameplayStatics::GetAllActorsOfClass(GetWorld(), AWWEnemy::StaticClass(), ExistingEnemies);
  if (ExistingEnemies.Num() >= MaxAliveEnemies) {
    return;
  }

  FVector PlayerLocation = PlayerPawn->GetActorLocation();
  float Angle = FMath::FRandRange(0.0f, 2.0f * PI);
  FVector SpawnOffset =
      FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0.0f) * SpawnRadius;
  FVector SpawnLocation = PlayerLocation + SpawnOffset;

  FActorSpawnParameters SpawnParams;
  SpawnParams.SpawnCollisionHandlingOverride =
      ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

  AWWEnemy *NewEnemy = GetWorld()->SpawnActor<AWWEnemy>(
      EnemyClass, SpawnLocation, FRotator::ZeroRotator, SpawnParams);

  if (NewEnemy) {
    // UE_LOG(LogTemp, Warning, TEXT("[DEBUG] SpawnEnemy: Success Spawned %s at
    // %s"), *NewEnemy->GetName(), *SpawnLocation.ToString());
  } else {
    UE_LOG(LogTemp, Error, TEXT("SpawnEnemy: FAILED to SpawnActor"));
  }
}
