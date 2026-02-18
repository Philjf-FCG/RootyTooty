#include "WWEnemy.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "WWCharacter.h"

AWWEnemy::AWWEnemy() {
  PrimaryActorTick.bCanEverTick = true;

  MoveSpeed = 300.0f;
  Health = 50.0f;
  Damage = 10.0f;
  XPReward = 20.0f;

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;
  AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
}

void AWWEnemy::BeginPlay() {
  Super::BeginPlay();
  if (GetCharacterMovement()) {
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Bandit %s initialized to MOVE_Walking"), *GetName());
  }
}

void AWWEnemy::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  APawn *PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
  if (PlayerPawn) {
    FVector Direction = PlayerPawn->GetActorLocation() - GetActorLocation();
    Direction.Z = 0.0f;
    float Distance = Direction.Size(); // Calculate distance before normalizing
    Direction.Normalize();
    AddMovementInput(Direction, 1.0f);

    // Contact Damage
    if (Distance < 100.0f) {
      UGameplayStatics::ApplyDamage(PlayerPawn, Damage * DeltaTime,
                                    GetController(), this, nullptr);
    }

    static float LogTimer = 0.0f;
    LogTimer += DeltaTime;
    if (LogTimer >= 2.0f) {
      UE_LOG(LogTemp, Warning,
             TEXT("[DEBUG] Bandit %s moving towards player. Dist: %f"),
             *GetName(), Distance); // Log actual distance
      LogTimer = 0.0f;
    }
  }
}

float AWWEnemy::TakeDamage(float DamageAmount, FDamageEvent const &DamageEvent,
                           AController *EventInstigator, AActor *DamageCauser) {
  Health -= DamageAmount;
  if (Health <= 0.0f) {
    Die();
  }
  return DamageAmount;
}

void AWWEnemy::Die() {
  AWWCharacter *Player =
      Cast<AWWCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
  if (Player) {
    Player->AddXP(XPReward);
  }
  Destroy();
}
