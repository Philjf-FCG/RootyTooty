#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WWOrbitingPickaxe.generated.h"

class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class ROOTYTOOTY_API AWWOrbitingPickaxe : public AActor {
  GENERATED_BODY()

public:
  AWWOrbitingPickaxe();
  virtual void Tick(float DeltaTime) override;

  void Configure(AActor* InOrbitCenter,
                 int32 InOrbitIndex,
                 int32 InOrbitTotal,
                 float InOrbitRadius,
                 float InOrbitSpeedDegrees,
                 float InDamage,
                 float InHitCooldown);

protected:
  virtual void BeginPlay() override;

private:
  UPROPERTY(VisibleAnywhere, Category = "Pickaxe")
  USphereComponent* DamageSphere;

  UPROPERTY(VisibleAnywhere, Category = "Pickaxe")
  UStaticMeshComponent* MeshComp;

  UPROPERTY(Transient)
  AActor* OrbitCenter;

  float OrbitAngleDegrees;
  float OrbitRadius;
  float OrbitSpeedDegrees;
  float Damage;
  float HitCooldown;

  TMap<TWeakObjectPtr<AActor>, float> LastHitTimeByEnemy;

  void UpdateOrbitPosition(float DeltaTime);
  void ApplyOverlapDamage();
};
