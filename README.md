# 🛡️ ZenKensa – AI 表面欠陥検査システム

**AI Surface Defect Inspection System**

---

## 🏭 Japanese Industrial Inspection System

**日本の工業用検査システム**

ZenKensaは、日本の中小製造業（SME）向けに設計された**AI支援型金属表面検査システム**です。
本システムにおけるAIは**参考指標（AI参考指標）**として機能し、**最終的な合否判定は必ず検査担当者の責任において行われます**。

ZenKensa is an AI-assisted metal surface inspection system designed for Japanese SMEs.
AI functions strictly as a reference indicator, and all final pass/fail decisions remain the responsibility of the human inspector.

---

## ⚠️ AI Responsibility Disclaimer

**AI責任の明確化（重要）**

**重要：**
本システムにおけるAI解析結果は参考指標です。
最終的な合否判定は、必ず検査担当者の責任において行ってください。

**IMPORTANT:**
AI analysis results are reference indicators only.
Final inspection judgment must always be made by the responsible inspector.

---

## 📋 System Architecture

**システムアーキテクチャ**

### 🔁 Two-Stage Inspection Pipeline

**二段階検査パイプライン**

#### ① Metal Surface Validation（ゲートキーパー）

* 入力画像が工業用検査に適した**金属表面かどうかを判定**
* 非金属（ゴム・木材・布・背景画像など）は自動拒否
* 不適切な入力による誤検知を防止

#### ② Defect Tendency Inspection（欠陥傾向解析）

* 金属表面と判定された画像のみ解析
* 表面欠陥の傾向を評価
* **健全性スコア（0–100%）を算出**

---

## 🤖 AI Reference Positioning

**AI参考指標の位置付け**

✅ AIは検査支援ツール
✅ 人間が最終判断者
✅ 責任境界が明確
✅ AIは決定権を持たない

---

## 📂 Metal Surface Validation Dataset

**金属表面検証データセット（学習済みモデル使用）**

本システムのゲートキーパーAIは、**金属 / 非金属の二値分類**を目的として構築された専用データセットで学習されています。

**Binary Classes**

* `metal`：検査対象となる工業用金属表面
* `non_metal`：ゴム、プラスチック、木材、布、背景画像など

**Design Principles**

* クラス完全均衡（50 / 50）
* データリークなし（train / val / test 厳密分離）
* 非金属クラスは「拒否動作学習」を目的に設計

※ 本番環境には学習データは含まれません。

---

## 🚀 主な機能

**Key Features**

* **軽量AIモデル（TensorFlow Lite）**
  CPU環境で動作可能な工業向け軽量構成

* **健全性スコア算出**
  欠陥傾向を数値化し、判断を支援

* **日本語PDF検査レポート自動生成**
  検査ID、日時、スコア、判定結果を記録
  監査・トレーサビリティ対応

* **工場現場向けUI**
  余白・視線誘導・安心感を重視した日本的工業UI

---

## 📱 Mobile & On-Site Workflow

**モバイル・現場対応**

* モバイル端末・タブレット対応
* レスポンシブUI
* 現場撮影 → 即検査 → レポート生成

---

## 📊 判定ロジック

**Inspection Criteria**

* **合格（Pass）**
  健全性スコア ≥ 90% かつ 欠陥数 ≤ 5

* **不合格（Fail）**
  上記条件を満たさない場合

※ 判定基準は現場要件に応じて調整可能

---

## ⚙️ Setup

**セットアップ**

```bash
git clone <repository-url>
cd zenkensa
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📂 Project Structure

**プロジェクト構成**

```
zenkensa/
├── app/
│   ├── main.py              # FastAPI Backend & AI Pipeline
│   └── templates/
│       └── index.html       # Japanese Industrial UI
├── metal_surface_validator.tflite
├── zenkensa_model.tflite
├── reports/                 # Inspection JSON / PDF outputs
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🏭 Design Philosophy

**設計思想**

* AIは補助、判断は人間
* 説明可能性・監査対応重視
* 日本の製造現場で「毎日使われる」ことを前提

---

**ZenKensa – 工場で安心して使えるAI検査支援システム**
Developed for Industrial Quality Excellence.

