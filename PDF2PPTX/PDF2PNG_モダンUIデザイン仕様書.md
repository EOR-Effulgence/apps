# PDF2PPTX v3.0 モダンUIデザイン仕様書

## 1. デザイン理念

### 1.1 Material Design 3準拠
- **Material You**: 動的カラーとパーソナライゼーション
- **アダプティブデザイン**: デバイス・環境に適応
- **アクセシビリティ**: ユニバーサルデザインの実現
- **表現力**: 美しく機能的なインターフェース

### 1.2 デザイン原則
1. **明確性**: 情報の優先順位を明確に表現
2. **一貫性**: 統一されたデザイン言語
3. **効率性**: 直感的で効率的な操作
4. **美しさ**: 視覚的に魅力的なインターフェース

## 2. カラーシステム

### 2.1 ライトテーマ
```css
/* Primary Colors */
--md-primary: #6750A4
--md-on-primary: #FFFFFF
--md-primary-container: #EADDFF
--md-on-primary-container: #21005D

/* Secondary Colors */
--md-secondary: #625B71
--md-on-secondary: #FFFFFF
--md-secondary-container: #E8DEF8
--md-on-secondary-container: #1D192B

/* Tertiary Colors */
--md-tertiary: #7D5260
--md-on-tertiary: #FFFFFF
--md-tertiary-container: #FFD8E4
--md-on-tertiary-container: #31111D

/* Error Colors */
--md-error: #BA1A1A
--md-on-error: #FFFFFF
--md-error-container: #FFDAD6
--md-on-error-container: #410002

/* Surface Colors */
--md-surface: #FFFBFE
--md-on-surface: #1C1B1F
--md-surface-variant: #E7E0EC
--md-on-surface-variant: #49454F
--md-outline: #79747E
--md-outline-variant: #CAC4D0
```

### 2.2 ダークテーマ
```css
/* Primary Colors */
--md-primary: #D0BCFF
--md-on-primary: #381E72
--md-primary-container: #4F378B
--md-on-primary-container: #EADDFF

/* Secondary Colors */
--md-secondary: #CCC2DC
--md-on-secondary: #332D41
--md-secondary-container: #4A4458
--md-on-secondary-container: #E8DEF8

/* Tertiary Colors */
--md-tertiary: #EFB8C8
--md-on-tertiary: #492532
--md-tertiary-container: #633B48
--md-on-tertiary-container: #FFD8E4

/* Error Colors */
--md-error: #FFB4AB
--md-on-error: #690005
--md-error-container: #93000A
--md-on-error-container: #FFDAD6

/* Surface Colors */
--md-surface: #10070F
--md-on-surface: #E6E1E5
--md-surface-variant: #49454F
--md-on-surface-variant: #CAC4D0
--md-outline: #938F99
--md-outline-variant: #49454F
```

### 2.3 セマンティックカラー
```css
/* Success */
--success: #4CAF50
--success-container: #E8F5E8
--on-success-container: #1B5E20

/* Warning */
--warning: #FF9800
--warning-container: #FFF3E0
--on-warning-container: #E65100

/* Info */
--info: #2196F3
--info-container: #E3F2FD
--on-info-container: #0D47A1
```

## 3. タイポグラフィ

### 3.1 フォントファミリー
```css
/* Primary Font Stack */
--font-family-primary: 'Noto Sans JP', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif

/* Display Font */
--font-family-display: 'M PLUS Rounded 1c', --font-family-primary

/* Monospace Font */
--font-family-mono: 'JetBrains Mono', 'Consolas', 'Monaco', monospace
```

### 3.2 タイプスケール
```css
/* Display */
--text-display-large: 57px/64px 400
--text-display-medium: 45px/52px 400
--text-display-small: 36px/44px 400

/* Headline */
--text-headline-large: 32px/40px 400
--text-headline-medium: 28px/36px 400
--text-headline-small: 24px/32px 400

/* Title */
--text-title-large: 22px/28px 500
--text-title-medium: 16px/24px 500
--text-title-small: 14px/20px 500

/* Body */
--text-body-large: 16px/24px 400
--text-body-medium: 14px/20px 400
--text-body-small: 12px/16px 400

/* Label */
--text-label-large: 14px/20px 500
--text-label-medium: 12px/16px 500
--text-label-small: 11px/16px 500
```

## 4. レイアウトシステム

### 4.1 グリッドシステム
```css
/* Layout Constraints */
--layout-margin: 16px
--layout-gutter: 24px
--layout-column-count: 12

/* Breakpoints */
--breakpoint-compact: 600px
--breakpoint-medium: 840px
--breakpoint-expanded: 1200px
--breakpoint-large: 1600px

/* Container Widths */
--container-compact: 100%
--container-medium: 840px
--container-expanded: 1200px
--container-large: 1600px
```

### 4.2 スペーシング
```css
/* Spacing Scale (8px base) */
--space-1: 4px   /* 0.5x */
--space-2: 8px   /* 1x */
--space-3: 12px  /* 1.5x */
--space-4: 16px  /* 2x */
--space-5: 20px  /* 2.5x */
--space-6: 24px  /* 3x */
--space-8: 32px  /* 4x */
--space-10: 40px /* 5x */
--space-12: 48px /* 6x */
--space-16: 64px /* 8x */
--space-20: 80px /* 10x */
--space-24: 96px /* 12x */
```

## 5. コンポーネントデザイン

### 5.1 ボタン

#### 5.1.1 Filled Button (Primary)
```css
.button-filled {
  background: var(--md-primary);
  color: var(--md-on-primary);
  padding: 10px 24px;
  border-radius: 20px;
  font: var(--text-label-large);
  border: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.button-filled:hover {
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15);
  background: color-mix(in srgb, var(--md-primary) 92%, var(--md-on-primary));
}

.button-filled:active {
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
}
```

#### 5.1.2 Outlined Button (Secondary)
```css
.button-outlined {
  background: transparent;
  color: var(--md-primary);
  padding: 10px 24px;
  border-radius: 20px;
  border: 1px solid var(--md-outline);
  font: var(--text-label-large);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.button-outlined:hover {
  background: color-mix(in srgb, var(--md-primary) 8%, transparent);
}
```

#### 5.1.3 Text Button (Tertiary)
```css
.button-text {
  background: transparent;
  color: var(--md-primary);
  padding: 10px 12px;
  border-radius: 20px;
  border: none;
  font: var(--text-label-large);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.button-text:hover {
  background: color-mix(in srgb, var(--md-primary) 8%, transparent);
}
```

### 5.2 カード

#### 5.2.1 Elevated Card
```css
.card-elevated {
  background: var(--md-surface);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
  padding: var(--space-4);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.card-elevated:hover {
  box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15);
}
```

#### 5.2.2 Filled Card
```css
.card-filled {
  background: var(--md-surface-variant);
  border-radius: 12px;
  padding: var(--space-4);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}
```

#### 5.2.3 Outlined Card
```css
.card-outlined {
  background: var(--md-surface);
  border: 1px solid var(--md-outline-variant);
  border-radius: 12px;
  padding: var(--space-4);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}
```

### 5.3 入力フィールド

#### 5.3.1 Filled Text Field
```css
.textfield-filled {
  background: var(--md-surface-variant);
  border-radius: 4px 4px 0 0;
  border-bottom: 1px solid var(--md-on-surface-variant);
  padding: 16px 16px 8px 16px;
  font: var(--text-body-large);
  color: var(--md-on-surface);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.textfield-filled:focus {
  outline: none;
  border-bottom: 2px solid var(--md-primary);
}

.textfield-filled-label {
  position: absolute;
  top: 16px;
  left: 16px;
  font: var(--text-body-large);
  color: var(--md-on-surface-variant);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
  pointer-events: none;
}

.textfield-filled:focus + .textfield-filled-label,
.textfield-filled:not(:placeholder-shown) + .textfield-filled-label {
  top: 8px;
  font: var(--text-body-small);
  color: var(--md-primary);
}
```

#### 5.3.2 Outlined Text Field
```css
.textfield-outlined {
  background: transparent;
  border: 1px solid var(--md-outline);
  border-radius: 4px;
  padding: 16px;
  font: var(--text-body-large);
  color: var(--md-on-surface);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.textfield-outlined:focus {
  outline: none;
  border: 2px solid var(--md-primary);
  padding: 15px; /* Adjust for thicker border */
}
```

### 5.4 プログレスインジケーター

#### 5.4.1 Linear Progress
```css
.progress-linear {
  width: 100%;
  height: 4px;
  background: var(--md-surface-variant);
  border-radius: 2px;
  overflow: hidden;
}

.progress-linear-indicator {
  height: 100%;
  background: var(--md-primary);
  border-radius: 2px;
  transition: transform 200ms cubic-bezier(0.2, 0, 0, 1);
}

.progress-linear-indeterminate {
  animation: linear-progress 2s infinite linear;
}

@keyframes linear-progress {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0%); }
  100% { transform: translateX(100%); }
}
```

#### 5.4.2 Circular Progress
```css
.progress-circular {
  width: 48px;
  height: 48px;
  position: relative;
}

.progress-circular-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-circular-track {
  fill: none;
  stroke: var(--md-surface-variant);
  stroke-width: 4;
}

.progress-circular-indicator {
  fill: none;
  stroke: var(--md-primary);
  stroke-width: 4;
  stroke-linecap: round;
  transition: stroke-dashoffset 200ms cubic-bezier(0.2, 0, 0, 1);
}
```

### 5.5 ナビゲーション

#### 5.5.1 Tab Bar
```css
.tab-bar {
  display: flex;
  background: var(--md-surface);
  border-bottom: 1px solid var(--md-outline-variant);
}

.tab {
  flex: 1;
  padding: 16px 12px;
  text-align: center;
  font: var(--text-title-small);
  color: var(--md-on-surface-variant);
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.tab:hover {
  background: color-mix(in srgb, var(--md-primary) 8%, transparent);
}

.tab.active {
  color: var(--md-primary);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--md-primary);
  border-radius: 3px 3px 0 0;
}
```

### 5.6 ドロップゾーン

#### 5.6.1 File Drop Zone
```css
.drop-zone {
  border: 2px dashed var(--md-outline);
  border-radius: 12px;
  padding: var(--space-12);
  text-align: center;
  background: var(--md-surface);
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: var(--md-primary);
  background: color-mix(in srgb, var(--md-primary) 4%, var(--md-surface));
}

.drop-zone-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-4);
  color: var(--md-on-surface-variant);
}

.drop-zone-text {
  font: var(--text-body-large);
  color: var(--md-on-surface);
  margin-bottom: var(--space-2);
}

.drop-zone-subtext {
  font: var(--text-body-small);
  color: var(--md-on-surface-variant);
}
```

## 6. アイコンシステム

### 6.1 Material Symbols
```css
/* Icon Base Styles */
.material-symbols {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  font-feature-settings: 'liga';
}

/* Size Variants */
.icon-small { font-size: 18px; }
.icon-medium { font-size: 24px; }
.icon-large { font-size: 32px; }
.icon-xl { font-size: 48px; }

/* Fill Variants */
.icon-filled { font-variation-settings: 'FILL' 1; }
.icon-outlined { font-variation-settings: 'FILL' 0; }
```

### 6.2 アプリケーション専用アイコン
```css
/* PDF Icons */
.icon-pdf::before { content: '\e415'; }
.icon-image::before { content: '\e3f4'; }
.icon-presentation::before { content: '\e5c1'; }

/* Action Icons */
.icon-download::before { content: '\e2c0'; }
.icon-upload::before { content: '\e2c6'; }
.icon-convert::before { content: '\e86b'; }
.icon-settings::before { content: '\e8b8'; }
.icon-help::before { content: '\e887'; }

/* Navigation Icons */
.icon-folder::before { content: '\e2c7'; }
.icon-history::before { content: '\e8a5'; }
.icon-favorite::before { content: '\e87d'; }
.icon-clear::before { content: '\e5c9'; }
```

## 7. アニメーションとトランジション

### 7.1 動きの原則
- **自然な動き**: イージング関数を使用
- **目的性**: 意味のあるアニメーション
- **スピード**: 適切なデュレーション
- **一貫性**: 統一されたタイミング

### 7.2 イージング関数
```css
/* Standard Easing */
--easing-standard: cubic-bezier(0.2, 0, 0, 1);
--easing-emphasized: cubic-bezier(0.05, 0.7, 0.1, 1);
--easing-decelerated: cubic-bezier(0, 0, 0.2, 1);
--easing-accelerated: cubic-bezier(0.3, 0, 1, 1);

/* Duration Tokens */
--duration-short1: 50ms;
--duration-short2: 100ms;
--duration-short3: 150ms;
--duration-short4: 200ms;
--duration-medium1: 250ms;
--duration-medium2: 300ms;
--duration-medium3: 350ms;
--duration-medium4: 400ms;
--duration-long1: 450ms;
--duration-long2: 500ms;
--duration-long3: 550ms;
--duration-long4: 600ms;
--duration-extra-long1: 700ms;
--duration-extra-long2: 800ms;
--duration-extra-long3: 900ms;
--duration-extra-long4: 1000ms;
```

### 7.3 共通アニメーション

#### 7.3.1 フェードイン・アウト
```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-8px);
  }
}

.animate-fade-in {
  animation: fade-in var(--duration-medium2) var(--easing-standard);
}

.animate-fade-out {
  animation: fade-out var(--duration-medium1) var(--easing-standard);
}
```

#### 7.3.2 スケールアニメーション
```css
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes scale-out {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.8);
  }
}

.animate-scale-in {
  animation: scale-in var(--duration-medium3) var(--easing-emphasized);
}

.animate-scale-out {
  animation: scale-out var(--duration-medium1) var(--easing-accelerated);
}
```

#### 7.3.3 スライドアニメーション
```css
@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(32px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slide-out-left {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-32px);
  }
}

.animate-slide-in-right {
  animation: slide-in-right var(--duration-medium4) var(--easing-emphasized);
}

.animate-slide-out-left {
  animation: slide-out-left var(--duration-medium2) var(--easing-accelerated);
}
```

## 8. レスポンシブデザイン

### 8.1 ブレークポイント戦略
```css
/* Compact Layout (0-599px) */
@media (max-width: 599px) {
  .layout-compact {
    padding: var(--space-4);
    gap: var(--space-3);
  }

  .button {
    width: 100%;
    margin-bottom: var(--space-2);
  }
}

/* Medium Layout (600-839px) */
@media (min-width: 600px) and (max-width: 839px) {
  .layout-medium {
    padding: var(--space-6);
    gap: var(--space-4);
    max-width: var(--container-medium);
    margin: 0 auto;
  }
}

/* Expanded Layout (840-1199px) */
@media (min-width: 840px) and (max-width: 1199px) {
  .layout-expanded {
    padding: var(--space-8);
    gap: var(--space-6);
    max-width: var(--container-expanded);
    margin: 0 auto;
  }
}

/* Large Layout (1200px+) */
@media (min-width: 1200px) {
  .layout-large {
    padding: var(--space-10);
    gap: var(--space-8);
    max-width: var(--container-large);
    margin: 0 auto;
  }
}
```

### 8.2 コンテナクエリ
```css
/* Container Query Support */
.component-container {
  container-type: inline-size;
}

/* Small Container (< 400px) */
@container (max-width: 399px) {
  .responsive-component {
    flex-direction: column;
    gap: var(--space-2);
  }
}

/* Medium Container (400-799px) */
@container (min-width: 400px) and (max-width: 799px) {
  .responsive-component {
    flex-direction: row;
    gap: var(--space-4);
  }
}

/* Large Container (800px+) */
@container (min-width: 800px) {
  .responsive-component {
    flex-direction: row;
    gap: var(--space-6);
  }
}
```

## 9. アクセシビリティ

### 9.1 カラーコントラスト
```css
/* Ensure WCAG AA compliance (4.5:1 ratio) */
.high-contrast {
  --text-primary: #000000;
  --text-secondary: #424242;
  --background-primary: #FFFFFF;
  --background-secondary: #F5F5F5;
}

/* Focus indicators */
.focusable:focus-visible {
  outline: 2px solid var(--md-primary);
  outline-offset: 2px;
  border-radius: 4px;
}
```

### 9.2 スクリーンリーダー対応
```css
/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Skip links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--md-primary);
  color: var(--md-on-primary);
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

## 10. パフォーマンス最適化

### 10.1 CSS最適化
```css
/* GPU acceleration for animations */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform, opacity;
}

/* Efficient transitions */
.efficient-transition {
  transition: transform var(--duration-short4) var(--easing-standard),
              opacity var(--duration-short4) var(--easing-standard);
}

/* Contain layout shifts */
.layout-contained {
  contain: layout style paint;
}
```

### 10.2 フォント最適化
```css
/* Font loading optimization */
@font-face {
  font-family: 'Noto Sans JP';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('noto-sans-jp-400.woff2') format('woff2');
}

/* Preload critical fonts */
/* <link rel="preload" href="noto-sans-jp-400.woff2" as="font" type="font/woff2" crossorigin> */
```

---

**文書バージョン**: 3.0-Design
**作成日**: 2025年9月20日
**対象バージョン**: PDF2PPTX v3.0（モダンUIデザイン版）
**準拠**: Material Design 3 Guidelines