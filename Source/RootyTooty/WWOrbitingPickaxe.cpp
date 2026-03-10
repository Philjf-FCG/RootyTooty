#include "WWOrbitingPickaxe.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "WWEnemy.h"

namespace {
UStaticMesh* LoadFirstMesh(std::initializer_list<const TCHAR*> Paths) {
  for (const TCHAR* Path : Paths) {
    if (UStaticMesh* Mesh = Cast<UStaticMesh>(
            StaticLoadObject(UStaticMesh::StaticClass(), nullptr, Path))) {
      return Mesh;
    }
  }
  return nullptr;
}

UMaterialInterface* LoadFirstMaterial(std::initializer_list<const TCHAR*> Paths) {
  for (const TCHAR* Path : Paths) {
    if (UMaterialInterface* Mat = Cast<UMaterialInterface>(
            StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, Path))) {
      return Mat;
    }
  }
  return nullptr;
}
}  // namespace

AWWOrbitingPickaxe::AWWOrbitingPickaxe() {
  PrimaryActorTick.bCanEverTick = true;

  DamageSphere = CreateDefaultSubobject<USphereComponent>(TEXT("DamageSphere"));
  RootComponent = DamageSphere;
  DamageSphere->InitSphereRadius(35.0f);
  DamageSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
  DamageSphere->SetCollisionObjectType(ECC_WorldDynamic);
  DamageSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
  DamageSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
  DamageSphere->SetGenerateOverlapEvents(true);

  MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
  MeshComp->SetupAttachment(RootComponent);
  MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  MeshComp->SetCastShadow(false);

  if (UStaticMesh* PickaxeMesh = LoadFirstMesh({
          TEXT("/Game/Weapons/Pickaxe/stylized_pickaxe_SM.stylized_pickaxe_SM"),
          TEXT("/Game/Weapons/Pickaxe/pickaxe.pickaxe"),
          TEXT("/Engine/BasicShapes/Cone.Cone")})) {
    MeshComp->SetStaticMesh(PickaxeMesh);
  }

  if (UMaterialInterface* PickaxeMat = LoadFirstMaterial({
          TEXT("/Game/Weapons/Pickaxe/M_StylizedPickaxe.M_StylizedPickaxe"),
          TEXT("/Game/Weapons/Pickaxe/pickaxe.pickaxe")})) {
    MeshComp->SetMaterial(0, PickaxeMat);
  }

  MeshComp->SetRelativeScale3D(FVector(0.22f, 0.22f, 0.22f));
  MeshComp->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));

  OrbitCenter = nullptr;
  OrbitAngleDegrees = 0.0f;
  OrbitRadius = 145.0f;
  OrbitSpeedDegrees = 220.0f;
  Damage = 25.0f;
  HitCooldown = 0.25f;
}

void AWWOrbitingPickaxe::BeginPlay() { Super::BeginPlay(); }

void AWWOrbitingPickaxe::Configure(AActor* InOrbitCenter,
                                   int32 InOrbitIndex,
                                   int32 InOrbitTotal,
                                   float InOrbitRadius,
                                   float InOrbitSpeedDegrees,
                                   float InDamage,
                                   float InHitCooldown) {
  OrbitCenter = InOrbitCenter;
  OrbitRadius = InOrbitRadius;
  OrbitSpeedDegrees = InOrbitSpeedDegrees;
  Damage = InDamage;
  HitCooldown = FMath::Max(0.05f, InHitCooldown);

  const int32 SafeTotal = FMath::Max(1, InOrbitTotal);
  const int32 SafeIndex = FMath::Clamp(InOrbitIndex, 0, SafeTotal - 1);
  OrbitAngleDegrees = (360.0f / SafeTotal) * SafeIndex;

  UpdateOrbitPosition(0.0f);
}

void AWWOrbitingPickaxe::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  if (!OrbitCenter || !IsValid(OrbitCenter)) {
    Destroy();
    return;
  }

  UpdateOrbitPosition(DeltaTime);
  ApplyOverlapDamage();
}

void AWWOrbitingPickaxe::UpdateOrbitPosition(float DeltaTime) {
  OrbitAngleDegrees += OrbitSpeedDegrees * DeltaTime;
  if (OrbitAngleDegrees >= 360.0f) {
    OrbitAngleDegrees = FMath::Fmod(OrbitAngleDegrees, 360.0f);
  }

  const FVector Center = OrbitCenter->GetActorLocation() + FVector(0.0f, 0.0f, 65.0f);
  const FVector RadialDir = FRotator(0.0f, OrbitAngleDegrees, 0.0f).Vector();
  const FVector NewLocation = Center + (RadialDir * OrbitRadius);

  SetActorLocation(NewLocation);
  SetActorRotation(FRotator(0.0f, OrbitAngleDegrees + 90.0f, 0.0f));
}

void AWWOrbitingPickaxe::ApplyOverlapDamage() {
  TArray<AActor*> OverlappingActors;
  DamageSphere->GetOverlappingActors(OverlappingActors, AWWEnemy::StaticClass());
  const float Now = GetWorld()->GetTimeSeconds();

  for (AActor* Target : OverlappingActors) {
    if (!Target || Target == this || Target == OrbitCenter) {
      continue;
    }

    float* LastHitTime = LastHitTimeByEnemy.Find(Target);
    if (LastHitTime && (Now - *LastHitTime) < HitCooldown) {
      continue;
    }

    UGameplayStatics::ApplyDamage(Target, Damage, nullptr, OrbitCenter, nullptr);
    LastHitTimeByEnemy.Add(Target, Now);
  }
}
