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

  GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;

  // Camera Setup
  SpringArmComp =
      CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArmComp"));
  SpringArmComp->SetupAttachment(RootComponent);
  SpringArmComp->TargetArmLength = 1200.0f;
  SpringArmComp->SetRelativeRotation(FRotator(-60.0f, 0.0f, 0.0f));
  SpringArmComp->bDoCollisionTest = false; // Usually off for Survivors style

  CameraComp = CreateDefaultSubobject<UCameraComponent>(TEXT("CameraComp"));
  CameraComp->SetupAttachment(SpringArmComp);
}

void AWWCharacter::BeginPlay() {
  Super::BeginPlay();

  if (APlayerController *PC = Cast<APlayerController>(Controller)) {
    if (UEnhancedInputLocalPlayerSubsystem *Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(
                PC->GetLocalPlayer())) {
      if (DefaultMappingContext) {
        Subsystem->AddMappingContext(DefaultMappingContext, 0);
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

  if (UEnhancedInputComponent *EnhancedInput =
          Cast<UEnhancedInputComponent>(PlayerInputComponent)) {
    if (MoveAction) {
      EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this,
                                &AWWCharacter::Move);
    }
  }
}

void AWWCharacter::Move(const FInputActionValue &Value) {
  FVector2D MovementVector = Value.Get<FVector2D>();

  if (Controller != nullptr) {
    AddMovementInput(GetActorForwardVector(), MovementVector.Y);
    AddMovementInput(GetActorRightVector(), MovementVector.X);
    UE_LOG(LogTemp, Warning, TEXT("[DEBUG] Moving: %s"),
           *MovementVector.ToString());
  }
}

void AWWCharacter::AutoAttack() {
  AWWEnemy *Target = FindNearestEnemy();
  if (Target) {
    // In a full implementation, we would spawn a projectile or apply damage
    UGameplayStatics::ApplyDamage(Target, 20.0f, GetController(), this,
                                  nullptr);
    UE_LOG(LogTemp, Warning, TEXT("Shot fired at %s"), *Target->GetName());
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
