🛡️ ZenKensa - AI 表面欠陥検査システム [AI Surface Inspection System]

## 🏭 **Japanese Industrial Inspection System** [日本の工業用検査システム]

**ZenKensaは日本の中小企業向けに設計されたAI支援型金属表面検査システムです。AIは参考指標として機能し、最終判断は検査担当者の責任において行われます。**

**ZenKensa is an AI-assisted metal surface inspection system designed for Japanese SMEs. AI functions as a reference indicator, with final judgment made by the responsible inspector.**

---

## ⚠️ **AI Responsibility Disclaimer** [AI責任の明確化]

**重要：本システムにおけるAI解析結果は参考指標です。最終的な合否判定は、必ず検査担当者の責任において行ってください。**

**IMPORTANT: AI analysis results in this system are reference indicators only. Final pass/fail judgment must always be made by the responsible inspector.**

---

## 📋 **System Architecture** [システムアーキテクチャ]

### **Two-Stage Inspection Pipeline** [二段階検査パイプライン]

1. **Metal Surface Validation** [金属表面検証]
   - 画像が金属表面として適切か検証
   - 非金属画像は自動的に拒否

2. **Defect Inspection** [欠陥検査]
   - 金属表面検証通過後のみ実行
   - 欠陥リスクを算出

### **AI Reference Positioning** [AI参考指標の位置付け]

- ✅ **AIは支援ツール** [AI as support tool]
- ✅ **人間が最終判断者** [Human as final decision maker]
- ✅ **責任境界明確** [Clear responsibility boundaries]

---

## 📂 **Metal Surface Validation Dataset** [金属表面検証データセット]

The system includes a specialized binary classification dataset for metal surface validation:

**Binary Classes:**
- **metal**: Close-up industrial metallic surfaces suitable for inspection
- **non_metal**: Visually distinct, non-inspectable surfaces such as rubber, plastic, wood, fabric, and background-heavy images

**Dataset Structure:**
```
dataset_metal_validator/
├── train/ (70% - 1,006 images)
│   ├── metal/ (503 images)
│   └── non_metal/ (503 images)
├── val/ (15% - 216 images)
│   ├── metal/ (108 images)
│   └── non_metal/ (108 images)
└── test/ (15% - 218 images)
    ├── metal/ (109 images)
    └── non_metal/ (109 images)
```

**Key Features:**
- **Perfect 50/50 Class Balance**: Ensures unbiased model training
- **Zero Data Leakage**: Strict separation between train/val/test splits
- **Industrial Realism**: Non_metal class contains visually distinct surfaces designed to teach rejection behavior for unsupported inspection inputs
- **Quality Validation**: All images validated for proper classification and split integrity

**Purpose**: The non_metal class is intentionally designed to teach rejection behavior for unsupported inspection inputs, ensuring the system only processes appropriate metallic surfaces.

---

🚀 **主な機能 **[Key Features]

**OpenCVによる高性能な検知解析** [High-performance OpenCV detection]: 高速な画像処理と最適化されたライブラリにより、高解像度の画像でも遅延なく瞬時に解析を行います。[Utilizes optimized OpenCV libraries and auto-resizing for instantaneous analysis of high-resolution images without delay.]

**リアルタイム解析機能** [Real-time Processing]: 独自のアルゴリズムを用いて、欠陥の数と健全性スコアをリアルタイムに算出します。[Calculates the number of defects and health score in real-time using a proprietary algorithm.]

**高度なエッジ検出** [Advanced Edge Detection]: Sobel法を用いて、表面の影などのノイズを排除し、実際のひび割れのみを特定します。[Uses Sobel method to eliminate noise like shadows and identify only actual cracks.]

---📱 **モバイルおよびカメラ機能** [Mobile & Camera Features]

**ネイティブカメラ連携** [Native Camera Integration]: モバイル端末のブラウザから直接カメラを起動し、現場で即座に撮影・検査が可能です。[Directly triggers the mobile device's native camera for instant on-site capture and inspection.]

**レスポンシブ設計** [Responsive Design]: スマートフォン、タブレット、デスクトップのあらゆる画面サイズに最適化されています。[The UI is fully optimized for smartphones, tablets, and desktop screens.]

**処理中のオーバーレイ** [Processing Overlay]: 解析中、ユーザーにスキャン中であることを知らせる視覚的なフィードバックを提供します。[Provides a 'Scanning...' visual overlay to inform users during the AI analysis.]

---🏢 **エンタープライズ機能** [Enterprise Features]

**検査履歴の管理** [Inspection History]: SQLiteデータベースを使用して、過去の検査データを自動的に保存・追跡します。[Automatically saves and tracks historical inspection data using a SQLite database.]

**自動メールアラート** [Automated Email Alerts]: 検査結果が「不合格」の場合、即座に管理者へ通知を送ります。[Sends immediate notifications to managers when an inspection results in a 'Fail' status.]

**プロフェッショナルレポート** [Professional PDF Reports]: 日本語フォント（IPAexゴシック）を搭載し、詳細なPDFレポートを自動生成します。[Equipped with IPAex Gothic fonts to automatically generate detailed, professional PDF reports.]

---📊 **判定ロジック** [Detection Logic]

**合格基準** [Pass Criteria]: 健全性スコア (Health Score) ≥ 90% かつ 総欠陥数 (Total Defects) ≤ 5

**不合格基準** [Fail Criteria]: 健全性スコア < 90% または 総欠陥数 > 5

**適応型コントラスト調整** [Adaptive Contrast]: CLAHE技術により、照明条件に関わらず安定した検知精度を維持します。[Maintains stable detection accuracy regardless of lighting conditions using CLAHE technology.]

---⚙️ **セットアップ **[Setup]

**リポジトリをクローン** [Clone repository]:
```bash
git clone <repository-url>
cd zenkensa
```

**依存関係のインストール** [Install dependencies]:
```bash
pip install -r requirements.txt
```

**アプリケーションの起動** [Run application]:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---📂 **プロジェクト構造** [Project Structure]

```
zenkensa/
├── app/
│   ├── main.py              # バックエンドおよびAIロジック [Backend & AI Logic]
│   ├── templates/
│   │   └── index.html       # モバイル最適化UI [Mobile Optimized UI]
│   └── static/
│       ├── fonts/
│       │   └── ipaexg.ttf   # 日本語フォント [Japanese Font]
│       └── reports/         # 生成されたPDFレポート [Generated PDF Reports]
├── requirements.txt         # 依存ライブラリ [Dependencies]
├── .gitignore               # Git除外設定 [Git Ignore Rules]
└── README.md                # 本ファイル [This File]
```

Developed for Industrial Quality Excellence.
