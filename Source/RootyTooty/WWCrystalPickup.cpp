#include "WWCrystalPickup.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"
#include "WWCharacter.h"
#include "Kismet/GameplayStatics.h"

namespace {
UStaticMesh *LoadFirstPickupMesh(std::initializer_list<const TCHAR *> Paths) {
  for (const TCHAR *Path : Paths) {
    if (UStaticMesh *Mesh = Cast<UStaticMesh>(
            StaticLoadObject(UStaticMesh::StaticClass(), nullptr, Path))) {
      return Mesh;
    }
  }
  return nullptr;
}
} // namespace

AWWCrystalPickup::AWWCrystalPickup() {
  PrimaryActorTick.bCanEverTick = true; // proximity pickup check
  bPickedUp = false;

  XPValue = 20.0f;
  SkillPointsValue = 1;
  RewardType = ECrystalRewardType::XP;

  CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
  // Radius boosted to 100 so the scaled-down Western player (SetActorScale3D 0.257)
  // whose capsule shrinks to ~11 units can still trigger the overlap.
  CollisionComp->InitSphereRadius(100.0f);
  CollisionComp->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
  CollisionComp->SetCollisionObjectType(ECC_WorldDynamic);
  CollisionComp->SetCollisionResponseToAllChannels(ECR_Ignore);
  CollisionComp->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
  CollisionComp->SetGenerateOverlapEvents(true);
  CollisionComp->OnComponentBeginOverlap.AddDynamic(this, &AWWCrystalPickup::OnOverlap);
  RootComponent = CollisionComp;

  // Flat coin: wide cylinder, thin in Z, lying flat on the ground.
  MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
  MeshComp->SetupAttachment(RootComponent);
  MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  MeshComp->SetRelativeLocation(FVector(0.0f, 0.0f, 5.0f));
  MeshComp->SetRelativeScale3D(FVector(0.5f, 0.5f, 0.04f)); // wide flat disc
  MeshComp->SetRelativeRotation(FRotator::ZeroRotator);

  SecondaryMeshComp =
      CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SecondaryMeshComp"));
  SecondaryMeshComp->SetupAttachment(RootComponent);
  SecondaryMeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  SecondaryMeshComp->SetHiddenInGame(true);

  static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(
      TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
  if (CylinderMesh.Succeeded()) {
    MeshComp->SetStaticMesh(CylinderMesh.Object);
  }

  InitialLifeSpan = 30.0f;
}

void AWWCrystalPickup::BeginPlay() {
  Super::BeginPlay();
  SpawnTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;

  // Use the project's red plaid material for a bright red crystal.
  // Fall back to creating a MID on the basic shape material if not found.
  UMaterialInterface* RedMat = Cast<UMaterialInterface>(StaticLoadObject(
      UMaterialInterface::StaticClass(), nullptr,
      TEXT("/Game/CharacterLooks/Materials/M_red_plaid.M_red_plaid")));
  if (RedMat) {
    MeshComp->SetMaterial(0, RedMat);
  } else if (UMaterialInstanceDynamic *MID = MeshComp->CreateAndSetMaterialInstanceDynamic(0)) {
    const FLinearColor CrystalRed = FLinearColor(1.0f, 0.0f, 0.0f, 1.0f);
    MID->SetVectorParameterValue(FName("Color"), CrystalRed);
    MID->SetVectorParameterValue(FName("BaseColor"), CrystalRed);
  }
}

void AWWCrystalPickup::TryPickup(AWWCharacter *Player) {
  bPickedUp = true;
  if (RewardType == ECrystalRewardType::SkillPoint) {
    Player->AddSkillPoints(SkillPointsValue);
  } else {
    Player->AddXP(XPValue);
  }
  Destroy();
}

void AWWCrystalPickup::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);
  if (bPickedUp) return;
  // 0.75s grace period so the crystal is visible before it can be auto-collected
  // (enemies often die <120 units from the player due to contact damage).
  if (GetWorld() && (GetWorld()->GetTimeSeconds() - SpawnTime) < 0.75f) return;
  // Proximity check — bypasses the overlap channel issue caused by SetActorScale3D
  // shrinking the Western player's capsule to ~8 units radius.
  APawn *P = UGameplayStatics::GetPlayerPawn(this, 0);
  if (!P) return;
  AWWCharacter *Player = Cast<AWWCharacter>(P);
  if (!Player) return;
  if (FVector::DistSquared(GetActorLocation(), Player->GetActorLocation()) < FMath::Square(120.0f)) {
    TryPickup(Player);
  }
}

void AWWCrystalPickup::OnOverlap(UPrimitiveComponent *OverlappedComp, AActor *OtherActor,
                                 UPrimitiveComponent *OtherComp, int32 OtherBodyIndex,
                                 bool bFromSweep, const FHitResult &SweepResult) {
  AWWCharacter *Player = Cast<AWWCharacter>(OtherActor);
  if (!Player || bPickedUp) return;
  TryPickup(Player);
}
