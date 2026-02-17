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
}

void AWWEnemy::BeginPlay() { Super::BeginPlay(); }

void AWWEnemy::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  APawn *PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
  if (PlayerPawn) {
    FVector Direction = PlayerPawn->GetActorLocation() - GetActorLocation();
    Direction.Z = 0.0f;
    Direction.Normalize();
    AddMovementInput(Direction, 1.0f);
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
