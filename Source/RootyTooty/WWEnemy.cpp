#include "WWEnemy.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimationAsset.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "WWCharacter.h"
#include "WWCrystalPickup.h"

namespace {
UStaticMesh* LoadFirstStaticMesh(std::initializer_list<const TCHAR*> Paths) {
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

USoundBase* LoadFirstSound(std::initializer_list<const TCHAR*> Paths) {
  for (const TCHAR* Path : Paths) {
    if (USoundBase* Sound = Cast<USoundBase>(
            StaticLoadObject(USoundBase::StaticClass(), nullptr, Path))) {
      return Sound;
    }
  }
  return nullptr;
}

} // namespace

AWWEnemy::AWWEnemy() {
  PrimaryActorTick.bCanEverTick = true;

  MoveSpeed = 300.0f;
  Health = 50.0f;
  Damage = 10.0f;
  XPReward = 20.0f;
  SkillCrystalDropChance = 0.25f;
  SkillPointsPerCrystal = 1;
  bIsDead = false;
  bIsMoving = false;
  LastFootstepTime = 0.0f;
  bUsingMoveAnimation = false;
  IdleAnimationAsset = nullptr;
  MoveAnimationAsset = nullptr;

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;
  bUseControllerRotationYaw = false;
  GetCharacterMovement()->bOrientRotationToMovement = true;
  GetCharacterMovement()->bUseControllerDesiredRotation = false;
  GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);

  if (GetMesh()) {
    GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
    GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
  }

  AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

  // NOTE: Animations must be assigned in Blueprint editor
  // Look for montages in /Content/Mannequins/Anims/Pistol/
  IdleMontage = nullptr;
  RunMontage = nullptr;
  AttackMontage = nullptr;
}

void AWWEnemy::BeginPlay() {
  Super::BeginPlay();

  const FLinearColor BanditCoat = FLinearColor(0.11f, 0.08f, 0.07f, 1.0f);
  const FLinearColor BanditDust = FLinearColor(0.28f, 0.22f, 0.16f, 1.0f);

  if (USkeletalMeshComponent* EnemyMesh = GetMesh()) {
    USkeletalMesh* EnemyCharMesh = Cast<USkeletalMesh>(StaticLoadObject(
        USkeletalMesh::StaticClass(), nullptr,
        TEXT("/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy.SK_BobritoEnemy")));
    const bool bUsingBobrito = EnemyCharMesh != nullptr;
    if (!EnemyCharMesh) {
      EnemyCharMesh = Cast<USkeletalMesh>(StaticLoadObject(
          USkeletalMesh::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")));
    }
    if (!EnemyCharMesh) {
      EnemyCharMesh = Cast<USkeletalMesh>(StaticLoadObject(
          USkeletalMesh::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")));
    }

    if (EnemyCharMesh) {
      EnemyMesh->SetSkeletalMesh(EnemyCharMesh);
      EnemyMesh->SetVisibility(true);
      EnemyMesh->SetHiddenInGame(false);
      EnemyMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
      EnemyMesh->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));

      if (bUsingBobrito) {
        UMaterialInterface* BobritoMat = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/ImportedCharacters/Bobrito/M_BobritoImported.M_BobritoImported")));
        if (BobritoMat) {
          const int32 MatCount = EnemyMesh->GetNumMaterials();
          for (int32 i = 0; i < MatCount; ++i) {
            EnemyMesh->SetMaterial(i, BobritoMat);
          }
        }
      } else {
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

        UMaterialInterface *LeatherMat = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/CharacterLooks/Materials/M_brown_leather.M_brown_leather")));
        UMaterialInterface *PlaidMat = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/CharacterLooks/Materials/M_red_plaid.M_red_plaid")));

        UMaterialInterface *PrimaryEnemyMat = LeatherMat ? LeatherMat : QuinnMat01;
        UMaterialInterface *SecondaryEnemyMat = PlaidMat ? PlaidMat : QuinnMat02;

        if (PrimaryEnemyMat) {
          EnemyMesh->SetMaterial(0, PrimaryEnemyMat);
        }
        if (SecondaryEnemyMat) {
          EnemyMesh->SetMaterial(1, SecondaryEnemyMat);
        }

        const int32 MaterialCount = EnemyMesh->GetNumMaterials();
        for (int32 MaterialIndex = 0; MaterialIndex < MaterialCount; ++MaterialIndex) {
          if (UMaterialInstanceDynamic *BodyMat = EnemyMesh->CreateDynamicMaterialInstance(MaterialIndex)) {
            const FLinearColor SlotColor = (MaterialIndex % 2 == 0) ? BanditCoat : BanditDust;
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
      }
    } else {
      UE_LOG(LogTemp, Error, TEXT("Failed to load enemy skeletal mesh"));
    }

    IdleAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
        UAnimationAsset::StaticClass(), nullptr,
        TEXT("/Game/RTG_Bobrito_MM_Idle.RTG_Bobrito_MM_Idle")));
    if (!IdleAnimationAsset) {
      IdleAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle")));
    }
    if (!IdleAnimationAsset) {
      IdleAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle")));
    }

    MoveAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
        UAnimationAsset::StaticClass(), nullptr,
        TEXT("/Game/RTG_Bobrito_MF_Unarmed_Jog_Fwd.RTG_Bobrito_MF_Unarmed_Jog_Fwd")));
    if (!MoveAnimationAsset) {
      MoveAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd")));
    }
    if (!MoveAnimationAsset) {
      MoveAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd")));
    }

    if (IdleAnimationAsset) {
      EnemyMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
      EnemyMesh->PlayAnimation(IdleAnimationAsset, true);
      bUsingMoveAnimation = false;
    } else {
      UE_LOG(LogTemp, Warning, TEXT("Failed to load idle locomotion animation for enemy"));
    }

    if (!MoveAnimationAsset) {
      UE_LOG(LogTemp, Warning, TEXT("Failed to load move locomotion animation for enemy"));
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

    if (bIsMoving) {
      // Use world-time cadence to avoid mutating per-instance timers during live patch sessions.
      const float TimeNow = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
      const float Phase = FMath::Fmod(TimeNow + (GetUniqueID() * 0.017f), 0.4f);
      if (Phase < DeltaTime) {
        static USoundBase* FootstepSound = LoadFirstSound({
          TEXT("/Game/Audio/Footsteps.Footsteps"),
          TEXT("/Game/Audio/Footsteps_Cue.Footsteps_Cue")});
        if (FootstepSound) {
          const float Pitch = FMath::RandRange(0.7f, 1.0f);
          UGameplayStatics::PlaySoundAtLocation(this, FootstepSound, GetActorLocation() - FVector(0, 0, 90), 0.35f, Pitch);
        }
      }
    }

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
  if (bIsDead || DamageAmount <= 0.0f) {
    return 0.0f;
  }

  UE_LOG(LogTemp, Display, TEXT("Enemy %s took damage: %.2f (health before: %.2f)"),
         *GetName(), DamageAmount, Health);
  Health -= DamageAmount;
  UE_LOG(LogTemp, Display, TEXT("Enemy %s health after damage: %.2f"),
         *GetName(), Health);

  if (Health <= 0.0f && !bIsDead) {
    bIsDead = true;
    Die();
  }

  return DamageAmount;
}

void AWWEnemy::Die() {
  UE_LOG(LogTemp, Display, TEXT("Enemy %s died"), *GetName());

  SetActorEnableCollision(false);
  if (GetCapsuleComponent()) {
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  }
  if (GetMesh()) {
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  }

  if (UWorld *World = GetWorld()) {
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

    const FVector DropLocation = GetActorLocation() + FVector(0.0f, 0.0f, 24.0f);
    AWWCrystalPickup *Drop = World->SpawnActor<AWWCrystalPickup>(
        AWWCrystalPickup::StaticClass(), DropLocation, FRotator::ZeroRotator,
        SpawnParams);
    if (Drop) {
      const float ClampedChance = FMath::Clamp(SkillCrystalDropChance, 0.0f, 1.0f);
      const bool bDropSkillCrystal = FMath::FRand() < ClampedChance;

      Drop->RewardType = bDropSkillCrystal ? ECrystalRewardType::SkillPoint
                                           : ECrystalRewardType::XP;
      Drop->XPValue = XPReward;
      Drop->SkillPointsValue = SkillPointsPerCrystal;
    }
  }
  Destroy();
}






