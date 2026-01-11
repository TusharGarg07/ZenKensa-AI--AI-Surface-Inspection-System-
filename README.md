# ZenKensa - AI Surface Inspection System

A professional-grade AI-powered surface inspection system with Japanese localization, real-time defect detection, and enterprise features.

## Features

- **Advanced Edge Detection**: Sobel-based adaptive logic for accurate crack detection
- **Mobile-Friendly**: Responsive design with native camera access
- **Enterprise Features**: SQLite database, email alerts, inspection history
- **Japanese Localization**: Full bilingual support (Japanese/English)
- **PDF Reports**: Professional inspection reports with Japanese fonts
- **Real-Time Processing**: High-performance OpenCV detection

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd zenkensa

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Requirements

- Python 3.8+
- FastAPI
- OpenCV (headless for deployment)
- SQLite
- Modern web browser

## Usage

1. **Web Interface**: Open `http://localhost:8000` in your browser
2. **Mobile**: Tap the upload button to use camera or select image
3. **Desktop**: Click upload button to select image file
4. **Results**: View health score, defect count, and download PDF report
5. **History**: Track inspection results in the history table

## API Endpoints

- `GET /`: Main web interface
- `POST /predict`: AI surface inspection analysis
- `GET /history`: Retrieve inspection history
- `GET /generate-report`: Generate PDF report

## Detection Logic

**Industrial Standards**:
- **Pass Criteria**: Health Score ≥ 90% AND Defects ≤ 5
- **Fail Criteria**: Any condition below pass threshold
- **Health Score**: 100 - (edge_percentage * 2) with safety buffer (10-99%)

**Edge Detection**:
- **Sobel Operators**: X/Y gradients for real physical crack detection
- **CLAHE**: Adaptive contrast enhancement for shadow handling
- **OTSU Threshold**: Automatic lighting level detection
- **Professional Filtering**: Only significant defects marked in reports

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

- Uses `opencv-python-headless` for server environments
- Font paths work on Linux servers
- Database auto-initialization on startup
- Static files properly served

## Project Structure

```
zenkensa/
├── app/
│   ├── main.py              # FastAPI application
│   ├── templates/
│   │   └── index.html       # Web interface
│   └── static/
│       ├── fonts/
│       │   └── ipaexg.ttf   # Japanese font
│       └── reports/           # Generated PDFs
├── requirements.txt            # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Configuration

### Database
- **Type**: SQLite
- **Location**: `inspections.db` (auto-created)
- **Schema**: id, timestamp, inspector, batch, status, score, defects

### Font
- **Japanese**: IPAex Gothic font bundled locally
- **Path**: `app/static/fonts/ipaexg.ttf`
- **Fallback**: System fonts if local font missing

## Mobile Features

- **Camera Access**: Native mobile camera integration
- **Touch-Friendly**: Large buttons and tap targets
- **Responsive Layout**: Stacked interface on mobile
- **Full-Screen Processing**: Clear feedback during AI analysis

## Enterprise Features

- **Inspection History**: Last 10 inspections with filtering
- **Email Alerts**: Automatic notifications for failed inspections
- **PDF Reports**: Professional bilingual inspection reports
- **Database Persistence**: SQLite for reliable data storage

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## Support

For issues and support, please use the GitHub issue tracker.
