#include "WWProjectile.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Particles/ParticleSystemComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "DrawDebugHelpers.h"
#include "WWEnemy.h"

AWWProjectile::AWWProjectile() {
  PrimaryActorTick.bCanEverTick = true;

  CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
  CollisionComp->InitSphereRadius(15.0f);
  CollisionComp->BodyInstance.SetCollisionProfileName("Projectile");
  CollisionComp->OnComponentHit.AddDynamic(this, &AWWProjectile::OnHit);
  CollisionComp->SetWalkableSlopeOverride(
      FWalkableSlopeOverride(WalkableSlope_Unwalkable, 0.f));
  CollisionComp->CanCharacterStepUpOn = ECB_No;

  RootComponent = CollisionComp;

  MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
  MeshComp->SetupAttachment(RootComponent);
  MeshComp->SetRelativeScale3D(FVector(0.2f, 0.2f, 0.2f));
  MeshComp->SetCastShadow(false);
  MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);

  // Load sphere mesh
  static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(
      TEXT("/Engine/BasicShapes/Sphere.Sphere"));
  if (SphereMesh.Succeeded()) {
    MeshComp->SetStaticMesh(SphereMesh.Object);
  }

  // Add a bright point light for visibility
  BulletLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("BulletLight"));
  BulletLight->SetupAttachment(RootComponent);
  BulletLight->SetIntensity(5000.0f);
  BulletLight->SetLightColor(FLinearColor(1.0f, 0.5f, 0.0f)); // Orange
  BulletLight->SetAttenuationRadius(500.0f);
  BulletLight->SetCastShadows(false);

  // Add particle trail
  TrailEffect = CreateDefaultSubobject<UParticleSystemComponent>(TEXT("TrailEffect"));
  TrailEffect->SetupAttachment(RootComponent);
  TrailEffect->bAutoActivate = true;

  ProjectileMovement = CreateDefaultSubobject<UProjectileMovementComponent>(
      TEXT("ProjectileComp"));
  ProjectileMovement->UpdatedComponent = CollisionComp;
  ProjectileMovement->InitialSpeed = 3000.f;
  ProjectileMovement->MaxSpeed = 3000.f;
  ProjectileMovement->bRotationFollowsVelocity = true;
  ProjectileMovement->bShouldBounce = false;
  ProjectileMovement->ProjectileGravityScale = 0.0f;

  InitialLifeSpan = 3.0f;
  Damage = 20.0f;
}

void AWWProjectile::BeginPlay() {
  Super::BeginPlay();

  if (CollisionComp) {
    CollisionComp->SetSphereRadius(5.0f, true);
  }

  SetActorScale3D(FVector(1.0f, 1.0f, 1.0f));

  if (MeshComp) {
    MeshComp->SetRelativeScale3D(FVector(0.2f, 0.2f, 0.2f));
    MeshComp->SetWorldScale3D(FVector(0.2f, 0.2f, 0.2f));
    MeshComp->SetVisibility(true);
    MeshComp->SetHiddenInGame(false);
    MeshComp->SetMaterial(0, nullptr);
  } else {
    UE_LOG(LogTemp, Error, TEXT("NO MESH COMPONENT!"));
  }

  if (BulletLight) {
    BulletLight->SetVisibility(false);
    BulletLight->SetIntensity(0.0f);
    BulletLight->SetAttenuationRadius(0.0f);
  }
}

void AWWProjectile::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);
}

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
