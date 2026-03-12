#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WWCrystalPickup.generated.h"

class USphereComponent;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class ECrystalRewardType : uint8 {
  XP UMETA(DisplayName = "XP"),
  SkillPoint UMETA(DisplayName = "Skill Point")
};

UCLASS()
class ROOTYTOOTY_API AWWCrystalPickup : public AActor {
  GENERATED_BODY()

public:
  AWWCrystalPickup();

  UPROPERTY(EditAnywhere, Category = "Pickup")
  float XPValue;

  UPROPERTY(EditAnywhere, Category = "Pickup")
  int32 SkillPointsValue;

  UPROPERTY(EditAnywhere, Category = "Pickup")
  ECrystalRewardType RewardType;

protected:
  virtual void BeginPlay() override;

private:
  UPROPERTY(VisibleAnywhere, Category = "Pickup")
  USphereComponent *CollisionComp;

  UPROPERTY(VisibleAnywhere, Category = "Pickup")
  UStaticMeshComponent *MeshComp;

  UPROPERTY(VisibleAnywhere, Category = "Pickup")
  UStaticMeshComponent *SecondaryMeshComp;

  virtual void Tick(float DeltaTime) override;

  UFUNCTION()
  void OnOverlap(UPrimitiveComponent *OverlappedComp, AActor *OtherActor,
                 UPrimitiveComponent *OtherComp, int32 OtherBodyIndex,
                 bool bFromSweep, const FHitResult &SweepResult);

  void TryPickup(class AWWCharacter *Player);

  bool bPickedUp = false;
  float SpawnTime = 0.0f; // grace period: don't auto-collect immediately on spawn
  float SpinDegreesPerSecond = 180.0f;
  bool bUsingFazCoinVisual = false;
};
