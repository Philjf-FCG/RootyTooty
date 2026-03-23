#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "WWUpgradePanelWidget.generated.h"

class UTextBlock;

UCLASS()
class ROOTYTOOTY_API UWWUpgradePanelWidget : public UUserWidget {
  GENERATED_BODY()

public:
  virtual TSharedRef<SWidget> RebuildWidget() override;
  virtual void NativeConstruct() override;

  UFUNCTION(BlueprintCallable, Category = "HUD")
  void UpdateStatsPanel(int32 Score,
                        float CurrentHealth,
                        float MaxHealth,
                        int32 Level,
                        float XP,
                        float XPToNext,
                        int32 SkillPoints);

  UFUNCTION(BlueprintImplementableEvent, Category = "HUD")
  void BP_OnStatsUpdated(int32 Score,
                         float CurrentHealth,
                         float MaxHealth,
                         int32 Level,
                         float XP,
                         float XPToNext,
                         int32 SkillPoints);

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  int32 CachedScore = 0;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  float CachedCurrentHealth = 0.0f;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  float CachedMaxHealth = 0.0f;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  int32 CachedLevel = 1;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  float CachedXP = 0.0f;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  float CachedXPToNext = 0.0f;

  UPROPERTY(BlueprintReadOnly, Category = "HUD")
  int32 CachedSkillPoints = 0;

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
