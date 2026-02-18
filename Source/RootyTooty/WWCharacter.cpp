#include "WWCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "Kismet/GameplayStatics.h"
#include "WWEnemy.h"
#include "WWProjectile.h"

AWWCharacter::AWWCharacter() {
  PrimaryActorTick.bCanEverTick = true;

  MoveSpeed = 600.0f;
  MaxHealth = 100.0f;
  CurrentHealth = MaxHealth;
  XP = 0.0f;
  Level = 1;
  FireRate = 1.0f;
  AttackRange = 1000.0f;
  FireTimer = 0.0f;

  CurrentHealth = MaxHealth;

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;

  // Camera Setup
  SpringArmComp =
      CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArmComp"));
  SpringArmComp->SetupAttachment(RootComponent);
  SpringArmComp->TargetArmLength = 1200.0f;
  SpringArmComp->SetRelativeRotation(FRotator(-60.0f, 0.0f, 0.0f));
  SpringArmComp->bDoCollisionTest = false; // Usually off for Survivors style

  // Disable rotation inheritance to prevent screen shake when character turns
  SpringArmComp->bInheritPitch = false;
  SpringArmComp->bInheritYaw = false;
  SpringArmComp->bInheritRoll = false;

  CameraComp = CreateDefaultSubobject<UCameraComponent>(TEXT("CameraComp"));
  CameraComp->SetupAttachment(SpringArmComp);

  // Rotation to movement
  bUseControllerRotationYaw = false;
  GetCharacterMovement()->bOrientRotationToMovement = true;
  GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);

  // Fix character facing (Characters in UE usually need -90 Yaw to face +X)
  if (GetMesh()) {
    GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
  }
}

void AWWCharacter::BeginPlay() {
  Super::BeginPlay();

  CurrentHealth = MaxHealth;

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
}

void AWWCharacter::Move(const FInputActionValue &Value) {
  FVector2D MovementVector = Value.Get<FVector2D>();

  if (Controller != nullptr) {
    // Fixed world directions to prevent jitter when the actor rotates
    AddMovementInput(FVector::XAxisVector, MovementVector.Y);
    AddMovementInput(FVector::YAxisVector, MovementVector.X);
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Enhanced Move Called | X: %f, Y: %f (World Space)"),
           MovementVector.X, MovementVector.Y);
  }
}

void AWWCharacter::MoveForward(float Value) {
  if (Controller != nullptr && Value != 0.0f) {
    // Fixed world direction
    AddMovementInput(FVector::XAxisVector, Value);
    UE_LOG(LogTemp, Warning,
           TEXT("[DEBUG] Legacy MoveForward: %f (World Space)"), Value);
  }
}

void AWWCharacter::MoveRight(float Value) {
  if (Controller != nullptr && Value != 0.0f) {
    // Fixed world direction
    AddMovementInput(FVector::YAxisVector, Value);
    UE_LOG(LogTemp, Warning, TEXT("[DEBUG] Legacy MoveRight: %f (World Space)"),
           Value);
  }
}

void AWWCharacter::AutoAttack() {
  AWWEnemy *Target = FindNearestEnemy();
  if (Target) {
    if (ProjectileClass) {
      FVector SpawnLocation =
          GetActorLocation() +
          GetActorForwardVector() * 150.0f; // Slightly further
      FRotator SpawnRotation =
          (Target->GetActorLocation() - GetActorLocation()).Rotation();

      FActorSpawnParameters SpawnParams;
      SpawnParams.Owner = this;
      SpawnParams.Instigator = GetInstigator();
      SpawnParams.SpawnCollisionHandlingOverride =
          ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

      AWWProjectile *Proj = GetWorld()->SpawnActor<AWWProjectile>(
          ProjectileClass, SpawnLocation, SpawnRotation, SpawnParams);
      if (Proj) {
        Proj->SetActorScale3D(
            FVector(2.0f, 2.0f, 2.0f)); // Make it BIGGER to see it
        UE_LOG(LogTemp, Warning, TEXT("[DEBUG] Projectile Spawned: %s at %s"),
               *Proj->GetName(), *SpawnLocation.ToString());
      } else {
        UE_LOG(LogTemp, Error,
               TEXT("[DEBUG] Projectile FAILED to spawn from %s"),
               *ProjectileClass->GetName());
      }
    } else {
      // Fallback to instant damage if no projectile class is set
      UGameplayStatics::ApplyDamage(Target, 20.0f, GetController(), this,
                                    nullptr);
      UE_LOG(LogTemp, Warning,
             TEXT("[DEBUG] Instant Shot fired at %s (No ProjectileClass)"),
             *Target->GetName());
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
  XP += Amount;
  if (XP >= 100.0f) // Simple level up logic
  {
    XP -= 100.0f;
    Level++;
    UE_LOG(LogTemp, Warning, TEXT("Level Up! Current Level: %d"), Level);
  }
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
  UE_LOG(LogTemp, Error, TEXT("[DEBUG] PLAYER DIED!"));
  // Restart the level on death
  UGameplayStatics::OpenLevel(this, FName(*GetWorld()->GetName()), false);
}
