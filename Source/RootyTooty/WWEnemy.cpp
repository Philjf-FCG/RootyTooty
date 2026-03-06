#include "WWEnemy.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimationAsset.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "WWCharacter.h"

AWWEnemy::AWWEnemy() {
  PrimaryActorTick.bCanEverTick = true;

  MoveSpeed = 300.0f;
  Health = 50.0f;
  Damage = 10.0f;
  XPReward = 20.0f;
  bIsMoving = false;
  bUsingMoveAnimation = false;
  IdleAnimationAsset = nullptr;
  MoveAnimationAsset = nullptr;

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;
  bUseControllerRotationYaw = false;
  GetCharacterMovement()->bOrientRotationToMovement = true;
  GetCharacterMovement()->bUseControllerDesiredRotation = false;
  GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);

  if (GetMesh()) {
    GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
  }

  HatBrimComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HatBrimComp"));
  HatBrimComp->SetupAttachment(GetMesh());
  HatBrimComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  HatBrimComp->SetCastShadow(true);

  HatCrownComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HatCrownComp"));
  HatCrownComp->SetupAttachment(GetMesh());
  HatCrownComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  HatCrownComp->SetCastShadow(true);

  AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

  // NOTE: Animations must be assigned in Blueprint editor
  // Look for montages in /Content/Mannequins/Anims/Pistol/
  IdleMontage = nullptr;
  RunMontage = nullptr;
  AttackMontage = nullptr;
}

void AWWEnemy::BeginPlay() {
  Super::BeginPlay();

  const FLinearColor BanditBlack = FLinearColor(0.03f, 0.03f, 0.03f, 1.0f);
  const FLinearColor BanditGray = FLinearColor(0.10f, 0.10f, 0.10f, 1.0f);

  if (USkeletalMeshComponent* EnemyMesh = GetMesh()) {
    USkeletalMesh* QuinnMesh = Cast<USkeletalMesh>(StaticLoadObject(
        USkeletalMesh::StaticClass(), nullptr,
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")));
    if (!QuinnMesh) {
      QuinnMesh = Cast<USkeletalMesh>(StaticLoadObject(
          USkeletalMesh::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")));
    }

    if (QuinnMesh) {
      EnemyMesh->SetSkeletalMesh(QuinnMesh);
      EnemyMesh->SetVisibility(true);
      EnemyMesh->SetHiddenInGame(false);

      UMaterialInterface *QuinnMat01 = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Materials/Quinn/MI_Quinn_01.MI_Quinn_01")));
      if (!QuinnMat01) {
        QuinnMat01 = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/Mannequins/Materials/Quinn/MI_Quinn_01.MI_Quinn_01")));
      }

      UMaterialInterface *QuinnMat02 = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Materials/Quinn/MI_Quinn_02.MI_Quinn_02")));
      if (!QuinnMat02) {
        QuinnMat02 = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/Mannequins/Materials/Quinn/MI_Quinn_02.MI_Quinn_02")));
      }

      if (QuinnMat01) {
        EnemyMesh->SetMaterial(0, QuinnMat01);
      }
      if (QuinnMat02) {
        EnemyMesh->SetMaterial(1, QuinnMat02);
      }

      const int32 MaterialCount = EnemyMesh->GetNumMaterials();
      for (int32 MaterialIndex = 0; MaterialIndex < MaterialCount; ++MaterialIndex) {
        if (UMaterialInstanceDynamic *BodyMat = EnemyMesh->CreateDynamicMaterialInstance(MaterialIndex)) {
          const FLinearColor SlotColor = (MaterialIndex % 2 == 0) ? BanditBlack : BanditGray;
          BodyMat->SetVectorParameterValue(FName("BaseColor"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("Color"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("Tint"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("BodyColor"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("ClothColor"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("PrimaryColor"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("SecondaryColor"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("AlbedoTint"), SlotColor);
          BodyMat->SetVectorParameterValue(FName("DiffuseColor"), SlotColor);
        }
      }
    } else {
      UE_LOG(LogTemp, Error, TEXT("Failed to load Quinn skeletal mesh for enemy"));
    }

    // Preserve the animation configuration authored in Blueprint.
    // Hardcoded mannequin locomotion assets currently emit skeleton errors in automation.
    IdleAnimationAsset = nullptr;
    MoveAnimationAsset = nullptr;
    bUsingMoveAnimation = false;

    UStaticMesh *EnemyHatMesh = Cast<UStaticMesh>(StaticLoadObject(
        UStaticMesh::StaticClass(), nullptr,
        TEXT("/Game/Assets/tophat.tophat")));
    if (!EnemyHatMesh) {
      EnemyHatMesh = Cast<UStaticMesh>(StaticLoadObject(
          UStaticMesh::StaticClass(), nullptr,
          TEXT("/Game/Assets/cowboy.cowboy")));
    }
    if (!EnemyHatMesh) {
      EnemyHatMesh = Cast<UStaticMesh>(StaticLoadObject(
          UStaticMesh::StaticClass(), nullptr,
          TEXT("/Engine/BasicShapes/Cone.Cone")));
    }

    if (EnemyHatMesh && HatCrownComp) {
      HatCrownComp->SetStaticMesh(EnemyHatMesh);
      HatCrownComp->AttachToComponent(EnemyMesh, FAttachmentTransformRules::SnapToTargetIncludingScale, FName(TEXT("head")));
      HatCrownComp->SetRelativeLocation(FVector(0.0f, 0.0f, 6.0f));
      HatCrownComp->SetRelativeRotation(FRotator(0.0f, 90.0f, 0.0f));
      HatCrownComp->SetRelativeScale3D(FVector(0.28f, 0.28f, 0.28f));
      if (UMaterialInstanceDynamic *HatTopMat = HatCrownComp->CreateDynamicMaterialInstance(0)) {
        HatTopMat->SetVectorParameterValue(FName("Color"), BanditBlack);
        HatTopMat->SetVectorParameterValue(FName("BaseColor"), BanditBlack);
        HatTopMat->SetVectorParameterValue(FName("Tint"), BanditBlack);
      }
    }

    if (HatBrimComp) {
      HatBrimComp->AttachToComponent(EnemyMesh, FAttachmentTransformRules::SnapToTargetIncludingScale, FName(TEXT("head")));
      HatBrimComp->SetStaticMesh(nullptr);
      HatBrimComp->SetVisibility(false);
    }
  }

  if (GetCharacterMovement()) {
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Bandit %s initialized to MOVE_Walking"), *GetName());
  }

  // Animation Blueprint handles locomotion automatically
  IdleMontage = nullptr;
  RunMontage = nullptr;
  
  // Load attack montage for firing animation
  if (!AttackMontage) {
    AttackMontage = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr,
        TEXT("/Game/Mannequins/Anims/Pistol/MM_Pistol_Fire_Montage.MM_Pistol_Fire_Montage")));
    UE_LOG(LogTemp, Warning, TEXT("Enemy Attack Montage: %s"),
           AttackMontage ? TEXT("Success") : TEXT("Failed"));
  }
}

void AWWEnemy::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  APawn *PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
  if (PlayerPawn) {
    FVector Direction = PlayerPawn->GetActorLocation() - GetActorLocation();
    Direction.Z = 0.0f;
    float Distance = Direction.Size(); // Calculate distance before normalizing
    Direction.Normalize();
    AddMovementInput(Direction, 1.0f);
    bIsMoving = Distance > 50.0f;

    if (USkeletalMeshComponent *EnemyMesh = GetMesh()) {
      if (bIsMoving && MoveAnimationAsset && !bUsingMoveAnimation) {
        EnemyMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
        EnemyMesh->PlayAnimation(MoveAnimationAsset, true);
        bUsingMoveAnimation = true;
      } else if (!bIsMoving && IdleAnimationAsset && bUsingMoveAnimation) {
        EnemyMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
        EnemyMesh->PlayAnimation(IdleAnimationAsset, true);
        bUsingMoveAnimation = false;
      }
    }

    // Play attack montage when close to player
    if (Distance < 150.0f && AttackMontage && GetMesh() && GetMesh()->GetAnimInstance()) {
      UAnimInstance *AnimInstance = GetMesh()->GetAnimInstance();
      if (!AnimInstance->Montage_IsPlaying(AttackMontage)) {
        AnimInstance->Montage_Play(AttackMontage, 1.0f);
      }
    }
    // Idle and running animations handled by Animation Blueprint automatically

    // Contact Damage
    if (Distance < 100.0f) {
      UGameplayStatics::ApplyDamage(PlayerPawn, Damage * DeltaTime,
                                    GetController(), this, nullptr);
    }

    static float LogTimer = 0.0f;
    LogTimer += DeltaTime;
    if (LogTimer >= 2.0f) {
      UE_LOG(LogTemp, Warning,
             TEXT("[DEBUG] Bandit %s moving towards player. Dist: %f"),
             *GetName(), Distance); // Log actual distance
      LogTimer = 0.0f;
    }
  }
}

float AWWEnemy::TakeDamage(float DamageAmount, FDamageEvent const &DamageEvent,
                           AController *EventInstigator, AActor *DamageCauser) {
  Health -= DamageAmount;
  if (Health <= 0.0f) {
    Die();
  }
  return DamageAmount;
}

void AWWEnemy::Die() {
  AWWCharacter *Player =
      Cast<AWWCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
  if (Player) {
    Player->AddXP(XPReward);
  }
  Destroy();
}
