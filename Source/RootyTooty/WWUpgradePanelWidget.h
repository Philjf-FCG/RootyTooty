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

  void UpdatePanel(const FString& HeaderLine,
                   const TArray<FString>& UpgradeLines,
                   const TArray<FLinearColor>& UpgradeColors,
                   bool bShowChoices,
                   const TArray<FString>& ChoiceLines,
                   const TArray<FLinearColor>& ChoiceColors);

private:
  UPROPERTY()
  UTextBlock* HeaderText;

  UPROPERTY()
  TArray<UTextBlock*> UpgradeTextRows;

  UPROPERTY()
  UTextBlock* ChoiceTitleText;

  UPROPERTY()
  TArray<UTextBlock*> ChoiceTextRows;
};
