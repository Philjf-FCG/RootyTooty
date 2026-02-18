#include "WWProjectile.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "WWEnemy.h"

AWWProjectile::AWWProjectile() {
  PrimaryActorTick.bCanEverTick = false;

  CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
  CollisionComp->InitSphereRadius(10.0f);
  CollisionComp->BodyInstance.SetCollisionProfileName("Projectile");
  CollisionComp->OnComponentHit.AddDynamic(this, &AWWProjectile::OnHit);

  // Players can't walk on it
  CollisionComp->SetWalkableSlopeOverride(
      FWalkableSlopeOverride(WalkableSlope_Unwalkable, 0.f));
  CollisionComp->CanCharacterStepUpOn = ECB_No;

  RootComponent = CollisionComp;

  MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
  MeshComp->SetupAttachment(RootComponent);
  MeshComp->SetRelativeScale3D(FVector(0.2f, 0.2f, 0.2f));

  ProjectileMovement = CreateDefaultSubobject<UProjectileMovementComponent>(
      TEXT("ProjectileComp"));
  ProjectileMovement->UpdatedComponent = CollisionComp;
  ProjectileMovement->InitialSpeed = 3000.f;
  ProjectileMovement->MaxSpeed = 3000.f;
  ProjectileMovement->bRotationFollowsVelocity = true;
  ProjectileMovement->bShouldBounce = false;
  ProjectileMovement->ProjectileGravityScale =
      0.0f; // survivors style bullets fly straight

  InitialLifeSpan = 3.0f;
  Damage = 20.0f;
}

void AWWProjectile::BeginPlay() { Super::BeginPlay(); }

void AWWProjectile::OnHit(UPrimitiveComponent *HitComp, AActor *OtherActor,
                          UPrimitiveComponent *OtherComp, FVector NormalImpulse,
                          const FHitResult &Hit) {
  if (OtherActor && (OtherActor != this) &&
      OtherActor->IsA(AWWEnemy::StaticClass())) {
    UGameplayStatics::ApplyDamage(OtherActor, Damage, GetInstigatorController(),
                                  this, nullptr);
    Destroy();
  }
}
