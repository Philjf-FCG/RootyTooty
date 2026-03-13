#include "WWUpgradePanelWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Engine/Texture2D.h"
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

  UBorder* HudBorder =
      WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("HudBorder"));
  HudBorder->SetPadding(FMargin(22.0f, 24.0f));

  UTexture2D* HudTexture = Cast<UTexture2D>(
      StaticLoadObject(UTexture2D::StaticClass(), nullptr, TEXT("/Game/UI/HUD.HUD")));
  if (HudTexture) {
    FSlateBrush Brush;
    Brush.SetResourceObject(HudTexture);
    Brush.ImageSize = FVector2D(340.0f, 620.0f);
    Brush.DrawAs = ESlateBrushDrawType::Image;
    HudBorder->SetBrush(Brush);
    HudBorder->SetBrushColor(FLinearColor::White);
  } else {
    // Fallback tint so panel remains visible if texture is missing.
    HudBorder->SetBrushColor(FLinearColor(0.14f, 0.11f, 0.09f, 0.92f));
  }

  UCanvasPanelSlot* BorderSlot = RootCanvas->AddChildToCanvas(HudBorder);
  if (BorderSlot) {
    BorderSlot->SetAutoSize(false);
    BorderSlot->SetSize(FVector2D(340.0f, 620.0f));
    BorderSlot->SetPosition(FVector2D(16.0f, 16.0f));
    BorderSlot->SetAnchors(FAnchors(0.0f, 0.0f, 0.0f, 0.0f));
    BorderSlot->SetAlignment(FVector2D(0.0f, 0.0f));
  }

  UVerticalBox* ContentBox =
      WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("ContentBox"));
  HudBorder->SetContent(ContentBox);

  auto ConfigureStatText = [&](UTextBlock*& OutText, const TCHAR* Name, const TCHAR* Initial) {
    OutText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), FName(Name));
    OutText->SetText(FText::FromString(Initial));
    OutText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFont(), 24));
    OutText->SetColorAndOpacity(FSlateColor(FLinearColor(0.97f, 0.95f, 0.90f, 1.0f)));
    OutText->SetShadowOffset(FVector2D(1.0f, 1.0f));
    OutText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.9f));
    ContentBox->AddChildToVerticalBox(OutText);
  };

  ConfigureStatText(ScoreText, TEXT("ScoreText"), TEXT("Score: 0"));
  ConfigureStatText(HealthText, TEXT("HealthText"), TEXT("Health: 100 / 100"));
  ConfigureStatText(LevelText, TEXT("LevelText"), TEXT("Level: 1"));
  ConfigureStatText(XPText, TEXT("XPText"), TEXT("XP: 0 / 5"));
  ConfigureStatText(SPText, TEXT("SPText"), TEXT("SP: 0"));
}

void UWWUpgradePanelWidget::UpdateStatsPanel(int32 Score,
                                             float CurrentHealth,
                                             float MaxHealth,
                                             int32 Level,
                                             float XP,
                                             float XPToNext,
                                             int32 SkillPoints) {
  if (ScoreText) {
    ScoreText->SetText(FText::FromString(FString::Printf(TEXT("Score: %d"), Score)));
  }

  if (HealthText) {
    HealthText->SetText(FText::FromString(
        FString::Printf(TEXT("Health: %.0f / %.0f"), CurrentHealth, MaxHealth)));
  }

  if (LevelText) {
    LevelText->SetText(FText::FromString(FString::Printf(TEXT("Level: %d"), Level)));
  }

  if (XPText) {
    XPText->SetText(FText::FromString(
        FString::Printf(TEXT("XP: %.1f / %.1f"), XP, XPToNext)));
  }

  if (SPText) {
    SPText->SetText(FText::FromString(FString::Printf(TEXT("SP: %d"), SkillPoints)));
  }
}
