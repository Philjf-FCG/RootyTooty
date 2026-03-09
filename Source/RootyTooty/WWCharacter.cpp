#include "WWCharacter.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimationAsset.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "Kismet/GameplayStatics.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "UObject/ConstructorHelpers.h"
#include "WWEnemy.h"
#include "WWProjectile.h"

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

FName ResolveHeadAttachPoint(USkeletalMeshComponent* MeshComp) {
  if (!MeshComp) {
    return FName(TEXT("head"));
  }

  const FName Candidates[] = {
      FName(TEXT("head")),
      FName(TEXT("Head")),
      FName(TEXT("headSocket")),
      FName(TEXT("HeadSocket")),
      FName(TEXT("neck_01"))};

  for (const FName Candidate : Candidates) {
    if (MeshComp->DoesSocketExist(Candidate)) {
      return Candidate;
    }
    if (MeshComp->GetBoneIndex(Candidate) != INDEX_NONE) {
      return Candidate;
    }
  }

  return FName(TEXT("head"));
}

void PlaceHatOnHead(UStaticMeshComponent* HatComp, float UniformScale,
                    const FRotator& LocalRotation, float BaseLift) {
  if (!HatComp || !HatComp->GetStaticMesh()) {
    return;
  }

  // Keep transforms deterministic relative to head socket.
  HatComp->SetRelativeScale3D(FVector(UniformScale, UniformScale, UniformScale));
  HatComp->SetRelativeRotation(LocalRotation);
  HatComp->SetRelativeLocation(FVector(0.0f, 0.0f, BaseLift));
}

} // namespace

AWWCharacter::AWWCharacter() {
  PrimaryActorTick.bCanEverTick = true;

  MoveSpeed = 600.0f;
  MaxHealth = 100.0f;
  CurrentHealth = MaxHealth;
  XP = 0.0f;
  Level = 1;
  SkillPoints = 0;
  XPToNextLevel = 5.0f;
  FireRate = 1.0f;
  AttackRange = 1000.0f;
  ProjectileClass = AWWProjectile::StaticClass();
  FireTimer = 0.0f;
  bIsMoving = false;
  bIsAttacking = false;
  bUsingMoveAnimation = false;
  bShowAnimationDebug = false;
  bAwaitingSkillChoice = false;
  PendingSkillChoices = 0;
  MaxHealthUpgradeLevel = 0;
  MoveSpeedUpgradeLevel = 0;
  FireRateUpgradeLevel = 0;
  AttackRangeUpgradeLevel = 0;
  SkillPointBonusUpgradeLevel = 0;
  IdleAnimationAsset = nullptr;
  MoveAnimationAsset = nullptr;

  CurrentHealth = MaxHealth;

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;

  // NOTE: Animations must be assigned in Blueprint editor
  // Look for montages in /Content/Mannequins/Anims/Rifle/
  IdelMontage = nullptr;
  RunMontage = nullptr;
  AttackMontage = nullptr;

  // Camera Setup
  SpringArmComp =
      CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArmComp"));
  SpringArmComp->SetupAttachment(RootComponent);
  SpringArmComp->TargetArmLength = 820.0f;
  SpringArmComp->SetRelativeRotation(FRotator(-32.0f, 18.0f, 0.0f));
  SpringArmComp->bDoCollisionTest = true;

  // Disable rotation inheritance to prevent screen shake when character turns
  SpringArmComp->bInheritPitch = false;
  SpringArmComp->bInheritYaw = false;
  SpringArmComp->bInheritRoll = false;

  CameraComp = CreateDefaultSubobject<UCameraComponent>(TEXT("CameraComp"));
  CameraComp->SetupAttachment(SpringArmComp);
  CameraComp->bUsePawnControlRotation = false;

  HatBrimComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HatBrimComp"));
  HatBrimComp->SetupAttachment(GetMesh());
  HatBrimComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  HatBrimComp->SetCastShadow(true);

  HatCrownComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HatCrownComp"));
  HatCrownComp->SetupAttachment(GetMesh());
  HatCrownComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  HatCrownComp->SetCastShadow(true);

  // Rotation to movement
  bUseControllerRotationYaw = false;
  GetCharacterMovement()->bOrientRotationToMovement = true;
  GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);

  // Fix character facing (Characters in UE usually need -90 Yaw to face +X)
  if (GetMesh()) {
    GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
    GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
  }
}

void AWWCharacter::BeginPlay() {
  Super::BeginPlay();

  if (!ProjectileClass) {
    // Keep combat working even if a Blueprint default was cleared.
    ProjectileClass = AWWProjectile::StaticClass();
    UE_LOG(LogTemp, Warning, TEXT("ProjectileClass was null at BeginPlay; defaulted to AWWProjectile."));
  }

  CurrentHealth = MaxHealth;
  const FLinearColor SheriffCoat = FLinearColor(0.16f, 0.23f, 0.31f, 1.0f);
  const FLinearColor SheriffLeather = FLinearColor(0.43f, 0.28f, 0.13f, 1.0f);
  const FLinearColor SheriffHat = FLinearColor(0.73f, 0.59f, 0.83f, 1.0f);
  const FLinearColor SheriffBadge = FLinearColor(0.81f, 0.68f, 0.22f, 1.0f);

  if (USkeletalMeshComponent* CharacterMesh = GetMesh()) {
    USkeletalMesh* MannyMesh = Cast<USkeletalMesh>(StaticLoadObject(
        USkeletalMesh::StaticClass(), nullptr,
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple")));
    if (!MannyMesh) {
      MannyMesh = Cast<USkeletalMesh>(StaticLoadObject(
          USkeletalMesh::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple")));
    }

    if (MannyMesh) {
      CharacterMesh->SetSkeletalMesh(MannyMesh);
      CharacterMesh->SetVisibility(true);
      CharacterMesh->SetHiddenInGame(false);
      CharacterMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
      CharacterMesh->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));

        UMaterialInterface *MannyMat01 = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Materials/Manny/MI_Manny_01_New.MI_Manny_01_New")));
      if (!MannyMat01) {
        MannyMat01 = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/Mannequins/Materials/Manny/MI_Manny_01_New.MI_Manny_01_New")));
      }

      UMaterialInterface *MannyMat02 = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/Characters/Mannequins/Materials/Manny/MI_Manny_02_New.MI_Manny_02_New")));
      if (!MannyMat02) {
        MannyMat02 = Cast<UMaterialInterface>(StaticLoadObject(
            UMaterialInterface::StaticClass(), nullptr,
            TEXT("/Game/Mannequins/Materials/Manny/MI_Manny_02_New.MI_Manny_02_New")));
      }

      UMaterialInterface *JeansMat = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/CharacterLooks/Materials/M_jeans_fabric.M_jeans_fabric")));
      UMaterialInterface *PlaidMat = Cast<UMaterialInterface>(StaticLoadObject(
          UMaterialInterface::StaticClass(), nullptr,
          TEXT("/Game/CharacterLooks/Materials/M_red_plaid.M_red_plaid")));

      UMaterialInterface *PrimaryPlayerMat = JeansMat ? JeansMat : MannyMat01;
      UMaterialInterface *SecondaryPlayerMat = PlaidMat ? PlaidMat : MannyMat02;

      if (PrimaryPlayerMat) {
        CharacterMesh->SetMaterial(0, PrimaryPlayerMat);
      }
      if (SecondaryPlayerMat) {
        CharacterMesh->SetMaterial(1, SecondaryPlayerMat);
      }

      const int32 MaterialCount = CharacterMesh->GetNumMaterials();
      for (int32 MaterialIndex = 0; MaterialIndex < MaterialCount; ++MaterialIndex) {
        if (UMaterialInstanceDynamic *BodyMat = CharacterMesh->CreateDynamicMaterialInstance(MaterialIndex)) {
          const FLinearColor SlotColor = (MaterialIndex % 2 == 0) ? SheriffCoat : SheriffLeather;
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
      UE_LOG(LogTemp, Error, TEXT("Failed to load Manny skeletal mesh for player"));
    }

    IdleAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
        UAnimationAsset::StaticClass(), nullptr,
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle")));
    if (!IdleAnimationAsset) {
      IdleAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle")));
    }

    MoveAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
        UAnimationAsset::StaticClass(), nullptr,
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd")));
    if (!MoveAnimationAsset) {
      MoveAnimationAsset = Cast<UAnimationAsset>(StaticLoadObject(
          UAnimationAsset::StaticClass(), nullptr,
          TEXT("/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.MF_Unarmed_Jog_Fwd")));
    }

    if (IdleAnimationAsset) {
      CharacterMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
      CharacterMesh->PlayAnimation(IdleAnimationAsset, true);
      bUsingMoveAnimation = false;
    } else {
      UE_LOG(LogTemp, Warning, TEXT("Failed to load idle locomotion animation for player"));
    }

    if (!MoveAnimationAsset) {
      UE_LOG(LogTemp, Warning, TEXT("Failed to load move locomotion animation for player"));
    }

    UStaticMesh* SheriffHatWhole = LoadFirstStaticMesh({
      TEXT("/Game/Assets/cowboy.cowboy"),
      TEXT("/Game/Assets/FreeWestern/cowboy.cowboy")});
    if (!SheriffHatWhole) {
      UE_LOG(LogTemp, Warning, TEXT("Player hat mesh not found at /Game/Assets/cowboy or /Game/Assets/FreeWestern/cowboy"));
    }

    const FName HatAttachPoint = ResolveHeadAttachPoint(CharacterMesh);

    if (HatCrownComp) {
      HatCrownComp->SetStaticMesh(SheriffHatWhole);
      HatCrownComp->AttachToComponent(
          CharacterMesh,
          FAttachmentTransformRules::SnapToTargetNotIncludingScale,
          HatAttachPoint);
      HatCrownComp->SetVisibility(SheriffHatWhole != nullptr);
      if (SheriffHatWhole) {
        // Pitch keeps brim horizontal; roll flips from upside-down to upright.
        PlaceHatOnHead(HatCrownComp, 0.28f, FRotator(90.0f, 0.0f, 180.0f), 8.0f);
      } else {
        HatCrownComp->SetRelativeLocation(FVector::ZeroVector);
        HatCrownComp->SetRelativeRotation(FRotator::ZeroRotator);
        HatCrownComp->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
      }
      if (SheriffHatWhole) {
        UMaterialInterface* VelvetHatMat = LoadFirstMaterial({
          TEXT("/Game/HatLooks/Materials/M_PlayerHat_Fabric162_Lilac.M_PlayerHat_Fabric162_Lilac"),
          TEXT("/Game/HatLooks/Materials/M_fabric_162_basecolor_1k.M_fabric_162_basecolor_1k"),
          TEXT("/Game/HatLooks/Materials/M_fabric_162.M_fabric_162")});

        const int32 HatMaterialCount = FMath::Max(HatCrownComp->GetNumMaterials(), 1);
        for (int32 MaterialIndex = 0; MaterialIndex < HatMaterialCount; ++MaterialIndex) {
          if (VelvetHatMat) {
            HatCrownComp->SetMaterial(MaterialIndex, VelvetHatMat);
          }

          // Always tint every hat slot so player hats stay red.
          if (UMaterialInstanceDynamic *HatTopMat = HatCrownComp->CreateDynamicMaterialInstance(MaterialIndex)) {
            HatTopMat->SetVectorParameterValue(FName("Color"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("BaseColor"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("Tint"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("BodyColor"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("ClothColor"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("PrimaryColor"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("DiffuseColor"), SheriffHat);
            HatTopMat->SetVectorParameterValue(FName("SecondaryColor"), SheriffBadge);
          }
        }
      }
    }

    if (HatBrimComp) {
      HatBrimComp->AttachToComponent(
          CharacterMesh,
          FAttachmentTransformRules::SnapToTargetNotIncludingScale,
          HatAttachPoint);
      HatBrimComp->SetStaticMesh(nullptr);
      HatBrimComp->SetVisibility(false);
    }
  }

  if (bShowAnimationDebug && GEngine && GetMesh()) {
    FString CurrentAnimationName = TEXT("None");
    if (UAnimSingleNodeInstance *SingleNodeInstance = GetMesh()->GetSingleNodeInstance()) {
      if (UAnimationAsset *CurrentAnimation = SingleNodeInstance->GetCurrentAsset()) {
        CurrentAnimationName = CurrentAnimation->GetName();
      }
    }

    const float Speed2D = GetVelocity().Size2D();
    const FString DebugText = FString::Printf(
        TEXT("AnimDebug | Speed: %.1f | Moving: %s | Asset: %s"),
        Speed2D,
        bIsMoving ? TEXT("Yes") : TEXT("No"),
        *CurrentAnimationName);

    GEngine->AddOnScreenDebugMessage(
        (uint64)((PTRINT)this),
        0.0f,
        FColor::Cyan,
        DebugText);
  }

  // Setup input mapping context
  if (APlayerController *PC = Cast<APlayerController>(Controller)) {
    if (UEnhancedInputLocalPlayerSubsystem *Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(
                PC->GetLocalPlayer())) {
      if (DefaultMappingContext) {
        Subsystem->AddMappingContext(DefaultMappingContext, 0);
        UE_LOG(LogTemp, Warning, TEXT("[DEBUG] IMC Added in BeginPlay"));
      } else {
        UE_LOG(LogTemp, Error,
               TEXT("[DEBUG] DefaultMappingContext is NULL in BeginPlay"));
      }
    }
  }
}

void AWWCharacter::PossessedBy(AController *NewController) {
  Super::PossessedBy(NewController);

  if (APlayerController *PC = Cast<APlayerController>(NewController)) {
    if (UEnhancedInputLocalPlayerSubsystem *Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(
                PC->GetLocalPlayer())) {
      if (DefaultMappingContext) {
        Subsystem->AddMappingContext(DefaultMappingContext, 0);
        UE_LOG(LogTemp, Warning, TEXT("[DEBUG] IMC Added in PossessedBy"));
      }
    }
  }
}

void AWWCharacter::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);

  if (GEngine && IsPlayerControlled()) {
    const float AttacksPerSecond = (FireRate > KINDA_SMALL_NUMBER) ? (1.0f / FireRate) : 0.0f;
    const FString HeaderLine = FString::Printf(
        TEXT("XP: %.1f / %.1f | Level: %d | Skill Points: %d"), XP,
        XPToNextLevel, Level, SkillPoints);

    GEngine->AddOnScreenDebugMessage(
        (uint64)((PTRINT)this + 500), 0.0f, FColor::Green, HeaderLine);

    const FString PanelLine = FString::Printf(
        TEXT("HP Lv%d | SPD Lv%d | ROF Lv%d | RNG Lv%d | SP Lv%d | APS %.2f"),
        MaxHealthUpgradeLevel, MoveSpeedUpgradeLevel, FireRateUpgradeLevel,
        AttackRangeUpgradeLevel, SkillPointBonusUpgradeLevel, AttacksPerSecond);
    GEngine->AddOnScreenDebugMessage(
        (uint64)((PTRINT)this + 501), 0.0f, FColor::Cyan, PanelLine);

    if (bAwaitingSkillChoice && CurrentSkillChoices.Num() >= 3) {
      const FString Choice1 = FString::Printf(
          TEXT("[1] %s [%s]"),
          *GetSkillUpgradeLabel(CurrentSkillChoices[0]),
          *GetSkillUpgradeRarityLabel(CurrentSkillChoices[0]));
      const FString Choice2 = FString::Printf(
          TEXT("[2] %s [%s]"),
          *GetSkillUpgradeLabel(CurrentSkillChoices[1]),
          *GetSkillUpgradeRarityLabel(CurrentSkillChoices[1]));
      const FString Choice3 = FString::Printf(
          TEXT("[3] %s [%s]"),
          *GetSkillUpgradeLabel(CurrentSkillChoices[2]),
          *GetSkillUpgradeRarityLabel(CurrentSkillChoices[2]));

      GEngine->AddOnScreenDebugMessage(
          (uint64)((PTRINT)this + 502), 0.0f,
          GetSkillUpgradeRarityColor(CurrentSkillChoices[0]), Choice1);
      GEngine->AddOnScreenDebugMessage(
          (uint64)((PTRINT)this + 503), 0.0f,
          GetSkillUpgradeRarityColor(CurrentSkillChoices[1]), Choice2);
      GEngine->AddOnScreenDebugMessage(
          (uint64)((PTRINT)this + 504), 0.0f,
          GetSkillUpgradeRarityColor(CurrentSkillChoices[2]), Choice3);
    }
  }

  // Animation Blueprint handles locomotion automatically based on velocity
  // Just track movement state for other systems if needed
  FVector Velocity = GetCharacterMovement()->Velocity;
  bIsMoving = !Velocity.IsNearlyZero(0.1f);

  if (USkeletalMeshComponent* CharacterMesh = GetMesh()) {
    if (bIsMoving && MoveAnimationAsset && !bUsingMoveAnimation) {
      CharacterMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
      CharacterMesh->PlayAnimation(MoveAnimationAsset, true);
      bUsingMoveAnimation = true;
    } else if (!bIsMoving && IdleAnimationAsset && bUsingMoveAnimation) {
      CharacterMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
      CharacterMesh->PlayAnimation(IdleAnimationAsset, true);
      bUsingMoveAnimation = false;
    }
  }

  FireTimer += DeltaTime;
  if (FireTimer >= FireRate) {
    AutoAttack();
    FireTimer = 0.0f;
  }
}

void AWWCharacter::SetupPlayerInputComponent(
    UInputComponent *PlayerInputComponent) {
  Super::SetupPlayerInputComponent(PlayerInputComponent);

  UE_LOG(LogTemp, Warning,
         TEXT("[DEBUG] SetupPlayerInputComponent Called | Component: %s"),
         PlayerInputComponent ? *PlayerInputComponent->GetClass()->GetName()
                              : TEXT("NULL"));

  if (UEnhancedInputComponent *EnhancedInput =
          Cast<UEnhancedInputComponent>(PlayerInputComponent)) {
    UE_LOG(LogTemp, Warning, TEXT("[DEBUG] EnhancedInputComponent Detected"));
    if (MoveAction) {
      EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this,
                                &AWWCharacter::Move);
      UE_LOG(LogTemp, Warning, TEXT("[DEBUG] MoveAction Bound: %s"),
             *MoveAction->GetName());
    } else {
      UE_LOG(LogTemp, Error,
             TEXT("[DEBUG] MoveAction is NULL in SetupPlayerInputComponent"));
    }
  } else {
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Falling back to Legacy InputComponent"));
  }

  // Legacy Fallback (Works with standard InputComponent)
  PlayerInputComponent->BindAxis("MoveForward", this,
                                 &AWWCharacter::MoveForward);
  PlayerInputComponent->BindAxis("MoveRight", this, &AWWCharacter::MoveRight);

  // Skill choices remain available while paused during level-up selection.
  FInputActionBinding &SkillChoice1Binding =
      PlayerInputComponent->BindAction("SkillChoice1", IE_Pressed, this,
                                       &AWWCharacter::ChooseSkillOption1);
  SkillChoice1Binding.bExecuteWhenPaused = true;

  FInputActionBinding &SkillChoice2Binding =
      PlayerInputComponent->BindAction("SkillChoice2", IE_Pressed, this,
                                       &AWWCharacter::ChooseSkillOption2);
  SkillChoice2Binding.bExecuteWhenPaused = true;

  FInputActionBinding &SkillChoice3Binding =
      PlayerInputComponent->BindAction("SkillChoice3", IE_Pressed, this,
                                       &AWWCharacter::ChooseSkillOption3);
  SkillChoice3Binding.bExecuteWhenPaused = true;
}

void AWWCharacter::Move(const FInputActionValue &Value) {
  FVector2D MovementVector = Value.Get<FVector2D>();

  if (Controller != nullptr) {
    // Fixed world directions to prevent jitter when the actor rotates
    AddMovementInput(FVector::XAxisVector, MovementVector.Y);
    AddMovementInput(FVector::YAxisVector, MovementVector.X);
    bIsMoving = !MovementVector.IsNearlyZero();
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Enhanced Move Called | X: %f, Y: %f (World Space)"),
           MovementVector.X, MovementVector.Y);
  }
}

void AWWCharacter::MoveForward(float Value) {
  if (Controller != nullptr && Value != 0.0f) {
    // Fixed world direction
    AddMovementInput(FVector::XAxisVector, Value);
    bIsMoving = true;
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Legacy MoveForward: %f (World Space)"), Value);
  }
}

void AWWCharacter::MoveRight(float Value) {
  if (Controller != nullptr && Value != 0.0f) {
    // Fixed world direction
    AddMovementInput(FVector::YAxisVector, Value);
    bIsMoving = true;
    UE_LOG(LogTemp, Warning, TEXT("[DEBUG] Legacy MoveRight: %f (World Space)"),
           Value);
  }
}

void AWWCharacter::PlayAttackAnimation() {
  // Animation Blueprint handles attack animations automatically
  // This method can be expanded later if needed for special attack effects
  bIsAttacking = true;
  
  // Reset attack flag after a short time
  FTimerHandle TimerHandle;
  GetWorld()->GetTimerManager().SetTimer(
      TimerHandle, 
      [this]() { bIsAttacking = false; }, 
      0.3f, 
      false
  );
}

void AWWCharacter::AutoAttack() {
  AWWEnemy *Target = FindNearestEnemy();
  if (Target) {
    // Play attack animation
    PlayAttackAnimation();

    if (ProjectileClass) {
      FVector ToTarget = Target->GetActorLocation() - GetActorLocation();
      ToTarget.Z = 0.0f;
      ToTarget.Normalize();
      FVector SpawnLocation = GetActorLocation() + ToTarget * 90.0f + FVector(0, 0, 60.0f);
      FRotator SpawnRotation = (Target->GetActorLocation() - GetActorLocation()).Rotation();

      UE_LOG(LogTemp, Warning, TEXT("Spawn Location: %s"), *SpawnLocation.ToString());
      UE_LOG(LogTemp, Warning, TEXT("Target Location: %s"), *Target->GetActorLocation().ToString());

      FActorSpawnParameters SpawnParams;
      SpawnParams.Owner = this;
      SpawnParams.Instigator = GetInstigator();
      SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

      GetWorld()->SpawnActor<AWWProjectile>(
          ProjectileClass, SpawnLocation, SpawnRotation, SpawnParams);
    } else {
      // FALLBACK: Instant damage
      UGameplayStatics::ApplyDamage(Target, 20.0f, GetController(), this, nullptr);
    }
  }
}

AWWEnemy *AWWCharacter::FindNearestEnemy() {
  TArray<AActor *> FoundEnemies;
  UGameplayStatics::GetAllActorsOfClass(GetWorld(), AWWEnemy::StaticClass(),
                                        FoundEnemies);

  AWWEnemy *NearestEnemy = nullptr;
  float MinDistance = AttackRange;

  for (AActor *Actor : FoundEnemies) {
    float Distance = GetDistanceTo(Actor);
    if (Distance < MinDistance) {
      MinDistance = Distance;
      NearestEnemy = Cast<AWWEnemy>(Actor);
    }
  }

  return NearestEnemy;
}

void AWWCharacter::AddXP(float Amount) {
  if (Amount <= 0.0f) {
    return;
  }

  XP += Amount;

  while (XP >= XPToNextLevel) {
    XP -= XPToNextLevel;
    Level++;
    XPToNextLevel *= 2.0f;
    PendingSkillChoices++;
    UE_LOG(LogTemp, Warning, TEXT("Level Up! Current Level: %d"), Level);
  }

  if (!bAwaitingSkillChoice && PendingSkillChoices > 0) {
    OfferNextSkillChoices();
  }
}

void AWWCharacter::AddSkillPoints(int32 Amount) {
  if (Amount <= 0) {
    return;
  }

  SkillPoints += Amount;
  UE_LOG(LogTemp, Warning, TEXT("Skill points increased to: %d"), SkillPoints);
}

void AWWCharacter::OfferNextSkillChoices() {
  if (bAwaitingSkillChoice || PendingSkillChoices <= 0) {
    return;
  }

  const ESkillUpgrade AllUpgrades[] = {
      ESkillUpgrade::MaxHealth,
      ESkillUpgrade::MoveSpeed,
      ESkillUpgrade::FireRate,
      ESkillUpgrade::AttackRange,
      ESkillUpgrade::SkillPointBonus};

  TArray<ESkillUpgrade> UpgradePool;
  for (ESkillUpgrade Upgrade : AllUpgrades) {
    UpgradePool.Add(Upgrade);
  }

  CurrentSkillChoices.Reset();
  while (CurrentSkillChoices.Num() < 3 && UpgradePool.Num() > 0) {
    int32 TotalWeight = 0;
    for (ESkillUpgrade Upgrade : UpgradePool) {
      TotalWeight += GetSkillUpgradeWeight(Upgrade);
    }

    if (TotalWeight <= 0) {
      const int32 FallbackPickIndex = FMath::RandRange(0, UpgradePool.Num() - 1);
      CurrentSkillChoices.Add(UpgradePool[FallbackPickIndex]);
      UpgradePool.RemoveAtSwap(FallbackPickIndex);
      continue;
    }

    int32 Roll = FMath::RandRange(1, TotalWeight);
    int32 PickIndex = 0;
    for (int32 PoolIndex = 0; PoolIndex < UpgradePool.Num(); ++PoolIndex) {
      Roll -= GetSkillUpgradeWeight(UpgradePool[PoolIndex]);
      if (Roll <= 0) {
        PickIndex = PoolIndex;
        break;
      }
    }

    CurrentSkillChoices.Add(UpgradePool[PickIndex]);
    UpgradePool.RemoveAtSwap(PickIndex);
  }

  bAwaitingSkillChoice = CurrentSkillChoices.Num() == 3;
}

void AWWCharacter::ChooseSkillOption1() { ChooseSkillOptionByIndex(0); }

void AWWCharacter::ChooseSkillOption2() { ChooseSkillOptionByIndex(1); }

void AWWCharacter::ChooseSkillOption3() { ChooseSkillOptionByIndex(2); }

void AWWCharacter::ChooseSkillOptionByIndex(int32 OptionIndex) {
  if (!bAwaitingSkillChoice || !CurrentSkillChoices.IsValidIndex(OptionIndex)) {
    return;
  }

  ApplySkillUpgrade(CurrentSkillChoices[OptionIndex]);

  bAwaitingSkillChoice = false;
  CurrentSkillChoices.Reset();
  PendingSkillChoices = FMath::Max(0, PendingSkillChoices - 1);

  if (PendingSkillChoices > 0) {
    OfferNextSkillChoices();
  }
}

void AWWCharacter::ApplySkillUpgrade(ESkillUpgrade Upgrade) {
  const float PrevMaxHealth = MaxHealth;
  const float PrevMoveSpeed = MoveSpeed;
  const float PrevFireRate = FireRate;
  const float PrevAttackRange = AttackRange;
  const int32 PrevSkillPoints = SkillPoints;

  switch (Upgrade) {
    case ESkillUpgrade::MaxHealth:
      MaxHealthUpgradeLevel++;
      MaxHealth += 20.0f;
      CurrentHealth = FMath::Min(CurrentHealth + 20.0f, MaxHealth);
      break;
    case ESkillUpgrade::MoveSpeed:
      MoveSpeedUpgradeLevel++;
      MoveSpeed += 50.0f;
      GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;
      break;
    case ESkillUpgrade::FireRate:
      FireRateUpgradeLevel++;
      // Lower interval means faster attacks (10% faster each level).
      FireRate = FMath::Max(0.15f, FireRate * 0.9f);
      FireTimer = FMath::Min(FireTimer, FireRate);
      break;
    case ESkillUpgrade::AttackRange:
      AttackRangeUpgradeLevel++;
      AttackRange += 200.0f;
      break;
    case ESkillUpgrade::SkillPointBonus:
      SkillPointBonusUpgradeLevel++;
      SkillPoints += 1;
      break;
    default:
      break;
  }

  UE_LOG(LogTemp, Warning, TEXT("Selected upgrade: %s"),
         *GetSkillUpgradeLabel(Upgrade));
    UE_LOG(LogTemp, Warning,
      TEXT("Upgrade effect | MaxHP: %.1f->%.1f Move: %.1f->%.1f FireInterval: %.3f->%.3f Range: %.1f->%.1f SkillPoints: %d->%d"),
      PrevMaxHealth, MaxHealth, PrevMoveSpeed, MoveSpeed, PrevFireRate,
      FireRate, PrevAttackRange, AttackRange, PrevSkillPoints, SkillPoints);
}

FString AWWCharacter::GetSkillUpgradeLabel(ESkillUpgrade Upgrade) const {
  switch (Upgrade) {
    case ESkillUpgrade::MaxHealth:
      return TEXT("Max Health +20");
    case ESkillUpgrade::MoveSpeed:
      return TEXT("Move Speed +50");
    case ESkillUpgrade::FireRate:
      return TEXT("Fire Rate +10%");
    case ESkillUpgrade::AttackRange:
      return TEXT("Attack Range +200");
    case ESkillUpgrade::SkillPointBonus:
      return TEXT("Skill Point +1");
    default:
      return TEXT("Unknown Upgrade");
  }
}

int32 AWWCharacter::GetSkillUpgradeWeight(ESkillUpgrade Upgrade) const {
  switch (Upgrade) {
    case ESkillUpgrade::MaxHealth:
      return 35; // Common
    case ESkillUpgrade::MoveSpeed:
      return 30; // Common
    case ESkillUpgrade::AttackRange:
      return 20; // Uncommon
    case ESkillUpgrade::FireRate:
      return 10; // Rare
    case ESkillUpgrade::SkillPointBonus:
      return 5; // Epic
    default:
      return 1;
  }
}

FString AWWCharacter::GetSkillUpgradeRarityLabel(ESkillUpgrade Upgrade) const {
  const int32 Weight = GetSkillUpgradeWeight(Upgrade);
  if (Weight >= 30) {
    return TEXT("Common");
  }
  if (Weight >= 20) {
    return TEXT("Uncommon");
  }
  if (Weight >= 10) {
    return TEXT("Rare");
  }
  return TEXT("Epic");
}

FColor AWWCharacter::GetSkillUpgradeRarityColor(ESkillUpgrade Upgrade) const {
  const int32 Weight = GetSkillUpgradeWeight(Upgrade);
  if (Weight >= 30) {
    return FColor(180, 180, 180); // Common: gray
  }
  if (Weight >= 20) {
    return FColor(80, 200, 120); // Uncommon: green
  }
  if (Weight >= 10) {
    return FColor(70, 140, 255); // Rare: blue
  }
  return FColor(200, 90, 255); // Epic: magenta
}

float AWWCharacter::TakeDamage(float DamageAmount,
                               FDamageEvent const &DamageEvent,
                               AController *EventInstigator,
                               AActor *DamageCauser) {
  float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent,
                                         EventInstigator, DamageCauser);

  CurrentHealth -= ActualDamage;
  UE_LOG(LogTemp, Warning, TEXT("[DEBUG] Player Health: %f / %f"),
         CurrentHealth, MaxHealth);

  if (CurrentHealth <= 0.0f) {
    Die();
  }

  return ActualDamage;
}

void AWWCharacter::Die() {
  UE_LOG(LogTemp, Warning, TEXT("[DEBUG] PLAYER DIED!"));
  // Restart the level on death
  UGameplayStatics::OpenLevel(this, FName(*GetWorld()->GetName()), false);
}

void AWWCharacter::ToggleAnimationDebug() {
  bShowAnimationDebug = !bShowAnimationDebug;
  UE_LOG(LogTemp, Warning, TEXT("Animation debug %s"),
         bShowAnimationDebug ? TEXT("ENABLED") : TEXT("DISABLED"));

  if (!bShowAnimationDebug && GEngine) {
    GEngine->AddOnScreenDebugMessage((uint64)((PTRINT)this), 0.01f, FColor::Cyan,
                                     TEXT("AnimDebug OFF"));
  }
}
