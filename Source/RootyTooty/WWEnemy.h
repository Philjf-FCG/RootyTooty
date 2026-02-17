#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "WWEnemy.generated.h"

UCLASS()
class ROOTYTOOTY_API AWWEnemy : public ACharacter {
  GENERATED_BODY()

public:
  AWWEnemy();

  virtual void Tick(float DeltaTime) override;

protected:
  virtual void BeginPlay() override;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float MoveSpeed;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float Health;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float Damage;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float XPReward;

  virtual float TakeDamage(float DamageAmount,
                           struct FDamageEvent const &DamageEvent,
                           class AController *EventInstigator,
                           AActor *DamageCauser) override;

private:
  void Die();
};
