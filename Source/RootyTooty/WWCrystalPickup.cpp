#include "WWCrystalPickup.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"
#include "WWCharacter.h"

AWWCrystalPickup::AWWCrystalPickup() {
  PrimaryActorTick.bCanEverTick = false;

  XPValue = 20.0f;
  SkillPointsValue = 1;
  RewardType = ECrystalRewardType::XP;

  CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
  CollisionComp->InitSphereRadius(40.0f);
  CollisionComp->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
  CollisionComp->SetCollisionObjectType(ECC_WorldDynamic);
  CollisionComp->SetCollisionResponseToAllChannels(ECR_Ignore);
  CollisionComp->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
  CollisionComp->SetGenerateOverlapEvents(true);
  CollisionComp->OnComponentBeginOverlap.AddDynamic(this, &AWWCrystalPickup::OnOverlap);
  RootComponent = CollisionComp;

  MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshComp"));
  MeshComp->SetupAttachment(RootComponent);
  MeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  MeshComp->SetRelativeLocation(FVector(0.0f, 0.0f, 12.0f));
  MeshComp->SetRelativeScale3D(FVector(0.25f, 0.25f, 0.6f));
  MeshComp->SetRelativeRotation(FRotator(0.0f, 45.0f, 0.0f));

  SecondaryMeshComp =
      CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SecondaryMeshComp"));
  SecondaryMeshComp->SetupAttachment(RootComponent);
  SecondaryMeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  SecondaryMeshComp->SetRelativeLocation(FVector(0.0f, 0.0f, -12.0f));
  SecondaryMeshComp->SetRelativeScale3D(FVector(0.20f, 0.20f, 0.45f));
  SecondaryMeshComp->SetRelativeRotation(FRotator(180.0f, 45.0f, 0.0f));

  static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeMesh(
      TEXT("/Engine/BasicShapes/Cone.Cone"));
  if (ConeMesh.Succeeded()) {
    MeshComp->SetStaticMesh(ConeMesh.Object);
    SecondaryMeshComp->SetStaticMesh(ConeMesh.Object);
  }

  InitialLifeSpan = 30.0f;
}

void AWWCrystalPickup::BeginPlay() {
  Super::BeginPlay();

  const FLinearColor CrystalColor =
      (RewardType == ECrystalRewardType::SkillPoint)
          ? FLinearColor(1.0f, 0.85f, 0.20f, 1.0f)
          : FLinearColor(0.10f, 0.95f, 1.0f, 1.0f);

  if (UMaterialInstanceDynamic *MID = MeshComp->CreateAndSetMaterialInstanceDynamic(0)) {
    MID->SetVectorParameterValue(FName("BaseColor"), CrystalColor);
    MID->SetVectorParameterValue(FName("Color"), CrystalColor);
    MID->SetVectorParameterValue(FName("Tint"), CrystalColor);
    MID->SetVectorParameterValue(FName("EmissiveColor"), CrystalColor * 7.0f);
  }

  if (SecondaryMeshComp && SecondaryMeshComp->GetStaticMesh()) {
    if (UMaterialInstanceDynamic *SecondaryMID =
            SecondaryMeshComp->CreateAndSetMaterialInstanceDynamic(0)) {
      const FLinearColor SecondaryColor = CrystalColor * 0.85f;
      SecondaryMID->SetVectorParameterValue(FName("BaseColor"), SecondaryColor);
      SecondaryMID->SetVectorParameterValue(FName("Color"), SecondaryColor);
      SecondaryMID->SetVectorParameterValue(FName("Tint"), SecondaryColor);
      SecondaryMID->SetVectorParameterValue(FName("EmissiveColor"),
                                            SecondaryColor * 6.0f);
    }
  }
}

void AWWCrystalPickup::OnOverlap(UPrimitiveComponent *OverlappedComp, AActor *OtherActor,
                                 UPrimitiveComponent *OtherComp, int32 OtherBodyIndex,
                                 bool bFromSweep, const FHitResult &SweepResult) {
  AWWCharacter *Player = Cast<AWWCharacter>(OtherActor);
  if (!Player) {
    return;
  }

  if (RewardType == ECrystalRewardType::SkillPoint) {
    Player->AddSkillPoints(SkillPointsValue);
  } else {
    Player->AddXP(XPValue);
  }
  Destroy();
}
