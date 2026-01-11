🛡️ ZenKensa - AI 表面欠陥検査システム [AI Surface Inspection System]

ZenKensaは、製造業の品質保証向けに設計されたプロフェッショナルなAI表面検査システムです。 [ZenKensa is a professional AI surface inspection system designed for manufacturing quality assurance.]

🚀 主な機能 [Key Features]

**OpenCVによる高性能な検知解析** [High-performance OpenCV detection]: 高速な画像処理と最適化されたライブラリにより、高解像度の画像でも遅延なく瞬時に解析を行います。 [Utilizes optimized OpenCV libraries and auto-resizing for instantaneous analysis of high-resolution images without delay.]

**リアルタイム解析機能** [Real-time Processing]: 独自のアルゴリズムを用いて、欠陥の数と健全性スコアをリアルタイムに算出します。 [Calculates the number of defects and health score in real-time using a proprietary algorithm.]

**高度なエッジ検出** [Advanced Edge Detection]: Sobel法を用いて、表面の影などのノイズを排除し、実際のひび割れのみを特定します。 [Uses Sobel method to eliminate noise like shadows and identify only actual cracks.]

**モバイル最適化** [Mobile Optimized]: スマートフォンのカメラに直接アクセス可能で、現場での即時検査に対応しています。 [Direct access to smartphone cameras for immediate on-site inspection.]

**プロフェッショナルレポート** [Professional Reports]: 日本語フォント（IPAexゴシック）を搭載し、詳細なPDFレポートを自動生成します。 [Equipped with IPAex Gothic fonts to automatically generate detailed PDF reports.]

📊 判定ロジック [Detection Logic]

**合格基準** [Pass Criteria]: 健全性スコア (Health Score) ≥ 90% かつ 総欠陥数 (Total Defects) ≤ 5

**不合格基準** [Fail Criteria]: 健全性スコア < 90% または 総欠陥数 > 5

**適応型コントラスト調整** [Adaptive Contrast]: CLAHE技術により、照明条件に関わらず安定した検知精度を維持します。 [Maintains stable detection accuracy regardless of lighting conditions using CLAHE technology.]

⚙️ セットアップ [Setup]

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

📂 プロジェクト構造 [Project Structure]

```
zenkensa/
├── app/
│   ├── main.py              # バックエンドロジック [Backend Logic]
│   ├── templates/
│   │   └── index.html       # ウェブインターフェース [Web Interface]
│   └── static/
│       ├── fonts/
│       │   └── ipaexg.ttf   # 日本語フォント [Japanese Font]
│       └── reports/         # 生成されたPDF [Generated PDFs]
├── requirements.txt         # 依存ライブラリ [Dependencies]
├── .gitignore               # Git除外設定 [Git Ignore Rules]
└── README.md                # 本ファイル [This File]
```

Developed for Industrial Quality Excellence.
