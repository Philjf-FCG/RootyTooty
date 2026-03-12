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
class UAudioComponent;
class AWWOrbitingPickaxe;

UENUM()
enum class ESkillUpgrade : uint8 {
  MaxHealth,
  MoveSpeed,
  FireRate,
  AttackRange,
  SkillPointBonus,
  CriticalChance,
  BulletDamage,
  PickaxeUnlock,
  PickaxeDamage,
  PickaxeSpeed
};

UCLASS()
class ROOTYTOOTY_API AWWCharacter : public ACharacter {
  GENERATED_BODY()

public:
  AWWCharacter();

  virtual void Tick(float DeltaTime) override;
  virtual void SetupPlayerInputComponent(
      class UInputComponent *PlayerInputComponent) override;

  void AddXP(float Amount);
  void AddSkillPoints(int32 Amount);
  void GetUpgradePanelData(FString& HeaderLine,
                           TArray<FString>& UpgradeLines,
                           TArray<FLinearColor>& UpgradeColors,
                           bool& bShowChoices,
                           TArray<FString>& ChoiceLines,
                           TArray<FLinearColor>& ChoiceColors) const;
  virtual float TakeDamage(float DamageAmount,
                           struct FDamageEvent const &DamageEvent,
                           class AController *EventInstigator,
                           AActor *DamageCauser) override;
  void Die();

  FORCEINLINE float GetCurrentHealth() const { return CurrentHealth; }
  FORCEINLINE float GetMaxHealth() const { return MaxHealth; }

  UFUNCTION(Exec)
  void ToggleAnimationDebug();

  UFUNCTION(Exec)
  void ChooseSkillOption1();

  UFUNCTION(Exec)
  void ChooseSkillOption2();

  UFUNCTION(Exec)
  void ChooseSkillOption3();

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

  UPROPERTY(BlueprintReadOnly, Category = "Stats")
  int32 SkillPoints;

  UPROPERTY(BlueprintReadOnly, Category = "Stats")
  float XPToNextLevel;

  UPROPERTY(EditAnywhere, Category = "Weapon")
  float FireRate;

  UPROPERTY(EditAnywhere, Category = "Weapon")
  float AttackRange;

  UPROPERTY(BlueprintReadOnly, Category = "Weapon")
  float CriticalHitChance;

  UPROPERTY(BlueprintReadOnly, Category = "Weapon")
  float BaseShotDamage;

  UPROPERTY(EditAnywhere, Category = "Weapon|Pickaxe")
  TSubclassOf<AWWOrbitingPickaxe> OrbitingPickaxeClass;

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

  UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Visual")
  UStaticMeshComponent *TinyBodyComp;

private:
  float FireTimer;
  float LastFootstepTime;
  bool bIsMoving;
  bool bIsAttacking;
  bool bUsingMoveAnimation;
  bool bUseAnimationBlueprintLocomotion;
  bool bSkipIdleSingleNodeAnimation;
  bool bShowAnimationDebug;
  UAnimationAsset *IdleAnimationAsset;
  UAnimationAsset *MoveAnimationAsset;

  void Move(const FInputActionValue &Value);
  void TryStartBackgroundMusic();
  void MoveForward(float Value);
  void MoveRight(float Value);
  void AutoAttack();
  void PlayAttackAnimation();
  void EndAttackAnimation();
  class AWWEnemy *FindNearestEnemy();
  void OfferNextSkillChoices();
  void ChooseSkillOptionByIndex(int32 OptionIndex);
  void ApplySkillUpgrade(ESkillUpgrade Upgrade);
  FString GetSkillUpgradeLabel(ESkillUpgrade Upgrade) const;
  int32 GetSkillUpgradeWeight(ESkillUpgrade Upgrade) const;
  FString GetSkillUpgradeRarityLabel(ESkillUpgrade Upgrade) const;
  FColor GetSkillUpgradeRarityColor(ESkillUpgrade Upgrade) const;

  bool bAwaitingSkillChoice;
  int32 PendingSkillChoices;
  TArray<ESkillUpgrade> CurrentSkillChoices;

  int32 MaxHealthUpgradeLevel;
  int32 MoveSpeedUpgradeLevel;
  int32 FireRateUpgradeLevel;
  int32 AttackRangeUpgradeLevel;
  int32 SkillPointBonusUpgradeLevel;
  int32 CriticalChanceUpgradeLevel;
  int32 BulletDamageUpgradeLevel;
  int32 PickaxeUnlockUpgradeLevel;
  int32 PickaxeDamageUpgradeLevel;
  int32 PickaxeSpeedUpgradeLevel;

  int32 ActivePickaxeCount;
  float PickaxeDamage;
  float PickaxeOrbitRadius;
  float PickaxeOrbitSpeedDegrees;
  
  UPROPERTY(Transient)
  TArray<AWWOrbitingPickaxe*> ActivePickaxes;

  UPROPERTY(Transient)
  UAudioComponent* RuntimeBgmComponent;

  void RefreshPickaxeWeapons();
};

