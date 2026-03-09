#include "WWUpgradePanelWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Styling/SlateBrush.h"
#include "Styling/SlateTypes.h"

void UWWUpgradePanelWidget::NativeConstruct() {
  Super::NativeConstruct();

  if (!WidgetTree) {
    return;
  }

  UCanvasPanel* RootCanvas =
      WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("RootCanvas"));
  WidgetTree->RootWidget = RootCanvas;

  UBorder* VellumBorder =
      WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("VellumBorder"));
  VellumBorder->SetPadding(FMargin(14.0f, 10.0f));
  // High-contrast debug-safe parchment tint so visibility issues are obvious.
  VellumBorder->SetBrushColor(FLinearColor(0.24f, 0.19f, 0.11f, 0.96f));

  UCanvasPanelSlot* BorderSlot = RootCanvas->AddChildToCanvas(VellumBorder);
  if (BorderSlot) {
    BorderSlot->SetAutoSize(false);
    BorderSlot->SetSize(FVector2D(470.0f, 250.0f));
    BorderSlot->SetPosition(FVector2D(24.0f, 24.0f));
    BorderSlot->SetAnchors(FAnchors(0.0f, 0.0f, 0.0f, 0.0f));
    BorderSlot->SetAlignment(FVector2D(0.0f, 0.0f));
  }

  UVerticalBox* ContentBox =
      WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("ContentBox"));
  VellumBorder->SetContent(ContentBox);

  HeaderText =
      WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("HeaderText"));
  HeaderText->SetText(FText::FromString(TEXT("XP: 0 / 5 | Level: 1 | Skill Points: 0")));
  HeaderText->SetColorAndOpacity(FSlateColor(FLinearColor(0.98f, 0.92f, 0.75f, 1.0f)));
  HeaderText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 16));
  HeaderText->SetShadowOffset(FVector2D(1.0f, 1.0f));
  HeaderText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.9f));
  ContentBox->AddChildToVerticalBox(HeaderText);

  UpgradeTextRows.Reset();
  for (int32 RowIndex = 0; RowIndex < 5; ++RowIndex) {
    UTextBlock* RowText = WidgetTree->ConstructWidget<UTextBlock>(
        UTextBlock::StaticClass(),
        FName(*FString::Printf(TEXT("UpgradeRow_%d"), RowIndex)));
    RowText->SetText(FText::FromString(TEXT("")));
    RowText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 14));
    RowText->SetShadowOffset(FVector2D(1.0f, 1.0f));
    RowText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.85f));
    ContentBox->AddChildToVerticalBox(RowText);
    UpgradeTextRows.Add(RowText);
  }

  ChoiceTitleText = WidgetTree->ConstructWidget<UTextBlock>(
      UTextBlock::StaticClass(), TEXT("ChoiceTitleText"));
  ChoiceTitleText->SetText(FText::FromString(TEXT("Choose Upgrade: 1 / 2 / 3")));
  ChoiceTitleText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 14));
  ChoiceTitleText->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f, 0.93f, 0.45f, 1.0f)));
  ChoiceTitleText->SetShadowOffset(FVector2D(1.0f, 1.0f));
  ChoiceTitleText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.9f));
  ChoiceTitleText->SetVisibility(ESlateVisibility::Collapsed);
  ContentBox->AddChildToVerticalBox(ChoiceTitleText);

  ChoiceTextRows.Reset();
  for (int32 ChoiceIndex = 0; ChoiceIndex < 3; ++ChoiceIndex) {
    UTextBlock* ChoiceText = WidgetTree->ConstructWidget<UTextBlock>(
        UTextBlock::StaticClass(),
        FName(*FString::Printf(TEXT("ChoiceRow_%d"), ChoiceIndex)));
    ChoiceText->SetText(FText::FromString(TEXT("")));
    ChoiceText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 14));
    ChoiceText->SetShadowOffset(FVector2D(1.0f, 1.0f));
    ChoiceText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.85f));
    ChoiceText->SetVisibility(ESlateVisibility::Collapsed);
    ContentBox->AddChildToVerticalBox(ChoiceText);
    ChoiceTextRows.Add(ChoiceText);
  }

  // Temporary beacon to confirm UMG is rendering at all in PIE.
  UTextBlock* BeaconText =
      WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("PanelBeaconText"));
  BeaconText->SetText(FText::FromString(TEXT("PANEL ACTIVE")));
  BeaconText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 24));
  BeaconText->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f, 0.15f, 0.15f, 1.0f)));
  BeaconText->SetShadowOffset(FVector2D(1.0f, 1.0f));
  BeaconText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 1.0f));

  UCanvasPanelSlot* BeaconSlot = RootCanvas->AddChildToCanvas(BeaconText);
  if (BeaconSlot) {
    BeaconSlot->SetAutoSize(true);
    BeaconSlot->SetAnchors(FAnchors(0.5f, 0.5f, 0.5f, 0.5f));
    BeaconSlot->SetAlignment(FVector2D(0.5f, 0.5f));
    BeaconSlot->SetPosition(FVector2D(0.0f, -180.0f));
  }
}

void UWWUpgradePanelWidget::UpdatePanel(const FString& HeaderLine,
                                        const TArray<FString>& UpgradeLines,
                                        const TArray<FLinearColor>& UpgradeColors,
                                        bool bShowChoices,
                                        const TArray<FString>& ChoiceLines,
                                        const TArray<FLinearColor>& ChoiceColors) {
  if (HeaderText) {
    HeaderText->SetText(FText::FromString(HeaderLine));
  }

  for (int32 RowIndex = 0; RowIndex < UpgradeTextRows.Num(); ++RowIndex) {
    UTextBlock* RowText = UpgradeTextRows[RowIndex];
    if (!RowText) {
      continue;
    }

    RowText->SetText(FText::FromString(
        UpgradeLines.IsValidIndex(RowIndex) ? UpgradeLines[RowIndex] : TEXT("")));

    const FLinearColor RowColor = UpgradeColors.IsValidIndex(RowIndex)
                                      ? UpgradeColors[RowIndex]
                                      : FLinearColor(0.95f, 0.9f, 0.78f, 1.0f);
    RowText->SetColorAndOpacity(FSlateColor(RowColor));
  }

  if (ChoiceTitleText) {
    ChoiceTitleText->SetVisibility(
        bShowChoices ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
  }

  for (int32 ChoiceIndex = 0; ChoiceIndex < ChoiceTextRows.Num(); ++ChoiceIndex) {
    UTextBlock* ChoiceText = ChoiceTextRows[ChoiceIndex];
    if (!ChoiceText) {
      continue;
    }

    const bool bHasChoice = bShowChoices && ChoiceLines.IsValidIndex(ChoiceIndex);
    ChoiceText->SetVisibility(
        bHasChoice ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);

    if (bHasChoice) {
      ChoiceText->SetText(FText::FromString(ChoiceLines[ChoiceIndex]));
      const FLinearColor ChoiceColor = ChoiceColors.IsValidIndex(ChoiceIndex)
                                           ? ChoiceColors[ChoiceIndex]
                                           : FLinearColor::White;
      ChoiceText->SetColorAndOpacity(FSlateColor(ChoiceColor));
    }
  }
}
