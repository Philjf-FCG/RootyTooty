#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "WWUpgradePanelWidget.generated.h"

class UTextBlock;

UCLASS()
class ROOTYTOOTY_API UWWUpgradePanelWidget : public UUserWidget {
  GENERATED_BODY()

public:
  virtual void NativeConstruct() override;

  void UpdateStatsPanel(int32 Score,
                        float CurrentHealth,
                        float MaxHealth,
                        int32 Level,
                        float XP,
                        float XPToNext,
                        int32 SkillPoints);

private:
  UPROPERTY()
  UTextBlock* ScoreText;

  UPROPERTY()
  UTextBlock* HealthText;

  UPROPERTY()
  UTextBlock* LevelText;

  UPROPERTY()
  UTextBlock* XPText;

  UPROPERTY()
  UTextBlock* SPText;
};
