#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "WWCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UAnimMontage;
class UAnimationAsset;
class UStaticMeshComponent;

UCLASS()
class ROOTYTOOTY_API AWWCharacter : public ACharacter {
  GENERATED_BODY()

public:
  AWWCharacter();

  virtual void Tick(float DeltaTime) override;
  virtual void SetupPlayerInputComponent(
      class UInputComponent *PlayerInputComponent) override;

  void AddXP(float Amount);
  virtual float TakeDamage(float DamageAmount,
                           struct FDamageEvent const &DamageEvent,
                           class AController *EventInstigator,
                           AActor *DamageCauser) override;
  void Die();

  FORCEINLINE float GetCurrentHealth() const { return CurrentHealth; }
  FORCEINLINE float GetMaxHealth() const { return MaxHealth; }

  UFUNCTION(Exec)
  void ToggleAnimationDebug();

protected:
  virtual void BeginPlay() override;
  virtual void PossessedBy(AController *NewController) override;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input")
  class UInputMappingContext *DefaultMappingContext;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input")
  class UInputAction *MoveAction;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float MoveSpeed;

  UPROPERTY(EditAnywhere, Category = "Stats")
  float MaxHealth;

  UPROPERTY(BlueprintReadOnly, Category = "Stats")
  float CurrentHealth;

  UPROPERTY(BlueprintReadOnly, Category = "Stats")
  float XP;

  UPROPERTY(BlueprintReadOnly, Category = "Stats")
  int32 Level;

  UPROPERTY(EditAnywhere, Category = "Weapon")
  float FireRate;

  UPROPERTY(EditAnywhere, Category = "Weapon")
  float AttackRange;

  UPROPERTY(EditAnywhere, Category = "Weapon")
  TSubclassOf<class AWWProjectile> ProjectileClass;

  UPROPERTY(EditAnywhere, Category = "Animation")
  UAnimMontage *IdelMontage;

  UPROPERTY(EditAnywhere, Category = "Animation")
  UAnimMontage *RunMontage;

  UPROPERTY(EditAnywhere, Category = "Animation")
  UAnimMontage *AttackMontage;

protected:
  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
  USpringArmComponent *SpringArmComp;

  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
  UCameraComponent *CameraComp;

  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Visual")
  UStaticMeshComponent *HatBrimComp;

  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Visual")
  UStaticMeshComponent *HatCrownComp;

private:
  float FireTimer;
  float EnemySearchCooldownTimer;
  bool bIsMoving;
  bool bIsAttacking;
  bool bUsingMoveAnimation;
  bool bShowAnimationDebug;
  UAnimationAsset *IdleAnimationAsset;
  UAnimationAsset *MoveAnimationAsset;
  TWeakObjectPtr<class AWWEnemy> CachedEnemyTarget;

  void Move(const FInputActionValue &Value);
  void MoveForward(float Value);
  void MoveRight(float Value);
  void AutoAttack();
  void PlayAttackAnimation();
  class AWWEnemy *FindNearestEnemy();
};
