#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "WWCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;

UCLASS()
class ROOTYTOOTY_API AWWCharacter : public ACharacter {
  GENERATED_BODY()

public:
  AWWCharacter();

  virtual void Tick(float DeltaTime) override;
  virtual void SetupPlayerInputComponent(
      class UInputComponent *PlayerInputComponent) override;

  void AddXP(float Amount);

protected:
  virtual void BeginPlay() override;

  UPROPERTY(EditAnywhere, Category = "Input")
  class UInputMappingContext *DefaultMappingContext;

  UPROPERTY(EditAnywhere, Category = "Input")
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

protected:
  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
  USpringArmComponent *SpringArmComp;

  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
  UCameraComponent *CameraComp;

private:
  float FireTimer;

  void Move(const FInputActionValue &Value);
  void AutoAttack();
  class AWWEnemy *FindNearestEnemy();
};
