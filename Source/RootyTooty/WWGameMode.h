#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "WWGameMode.generated.h"

UCLASS()
class ROOTYTOOTY_API AWWGameMode : public AGameModeBase {
  GENERATED_BODY()

public:
  AWWGameMode();

  virtual void Tick(float DeltaTime) override;

protected:
  virtual void BeginPlay() override;

  UPROPERTY(EditAnywhere, Category = "Spawning")
  TSubclassOf<class AWWEnemy> EnemyClass;

  UPROPERTY(EditAnywhere, Category = "Spawning")
  float SpawnInterval;

  UPROPERTY(EditAnywhere, Category = "Spawning")
  float SpawnRadius;

private:
  float SpawnTimer;

  void SpawnEnemy();
};
