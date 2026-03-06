#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WWProjectile.generated.h"

class USphereComponent;
class UProjectileMovementComponent;
class UStaticMeshComponent;
class UPointLightComponent;
class UParticleSystemComponent;

UCLASS()
class ROOTYTOOTY_API AWWProjectile : public AActor {
  GENERATED_BODY()

public:
  AWWProjectile();
  virtual void Tick(float DeltaTime) override;

protected:
  virtual void BeginPlay() override;

  UPROPERTY(VisibleAnywhere, Category = "Projectile")
  USphereComponent *CollisionComp;

  UPROPERTY(VisibleAnywhere, Category = "Projectile")
  UProjectileMovementComponent *ProjectileMovement;

  UPROPERTY(VisibleAnywhere, Category = "Projectile")
  UStaticMeshComponent *MeshComp;

  UPROPERTY(VisibleAnywhere, Category = "Projectile")
  UPointLightComponent *BulletLight;

  UPROPERTY(VisibleAnywhere, Category = "Projectile")
  UParticleSystemComponent *TrailEffect;

  UFUNCTION()
  void OnHit(UPrimitiveComponent *HitComp, AActor *OtherActor,
             UPrimitiveComponent *OtherComp, FVector NormalImpulse,
             const FHitResult &Hit);

  UFUNCTION()
  void OnOverlap(UPrimitiveComponent *OverlappedComp, AActor *OtherActor,
                 UPrimitiveComponent *OtherComp, int32 OtherBodyIndex,
                 bool bFromSweep, const FHitResult &SweepResult);

public:
  UPROPERTY(EditAnywhere, Category = "Projectile")
  float Damage;
};
