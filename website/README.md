# 🛍️ IndoCloth Market - AI-Powered Fashion Platform

Production-ready AI-powered ecommerce system for fashion recommendations, similar in UX style to Zara but powered by AI inference models.

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** with async routes and structured logging
- **PostgreSQL** with SQLAlchemy async ORM
- **Kafka** integration for real-time event streaming
- **Slack** notifications for business alerts
- **Model Management** - Dynamic loading from `MLOps/models`
- **Business Intelligence** - Automated daily/weekly reports
- **Drift Detection** - Model monitoring and alerting

### Frontend (React + TypeScript)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Zara-style minimalist UI** with dark/light theme
- **Real-time updates** via polling
- **Admin Dashboard** with KPIs and monitoring

### Infrastructure
- **Docker** multi-stage builds
- **Docker Compose** for local development
- **CI/CD** with GitHub Actions
- **Airflow DAGs** for scheduled tasks

## 📁 Project Structure

```
Fashion_Recommendation_Engineer/
│
├── MLOps/
│   ├── models/              # ML model files (.keras, .pkl)
│   └── airflow/
│       └── dags/
│           ├── indocloth_daily_ingestion.py
│           ├── indocloth_drift_check.py
│           └── indocloth_weekly_report.py
│
└── website/
    └── app/
        ├── backend/
        │   ├── main.py              # FastAPI app entry point
        │   ├── config/              # Configuration
        │   ├── api/v1/              # API endpoints
        │   ├── services/            # Business services
        │   ├── kafka/               # Kafka producer/consumer
        │   ├── database/            # DB models & connection
        │   ├── slack/               # Slack notifications
        │   ├── business_logic/      # Metrics & insights
        │   └── core/                 # Logging, exceptions, middleware
        │
        └── frontend/
            ├── src/
            │   ├── components/      # React components
            │   ├── pages/           # Page components
            │   ├── api/             # API client
            │   ├── store/           # State management
            │   └── hooks/           # Custom hooks
            └── Dockerfile
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local frontend development)

### Using Docker Compose

1. **Clone and navigate:**
```bash
cd website
```

2. **Set environment variables:**
Create a `.env` file in `website/`:
```env
SLACK_BOT_TOKEN=your_slack_token
SLACK_WEBHOOK_URL=your_webhook_url
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/indocloth
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd website/app/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd website/app/frontend
npm install
npm run dev
```

## 📡 API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /` - API info

### Models
- `GET /api/v1/models/` - Get model metadata
- `POST /api/v1/models/reload` - Force reload models

### Recommendations
- `POST /api/v1/recommendations/recommend` - Get recommendations
- `POST /api/v1/recommendations/click` - Log click
- `POST /api/v1/recommendations/purchase` - Log purchase

### Metrics
- `GET /api/v1/metrics/kpi` - Get KPI summary
- `POST /api/v1/metrics/daily` - Calculate daily metrics
- `POST /api/v1/metrics/weekly` - Calculate weekly insights

### Kafka
- `GET /api/v1/kafka/health` - Kafka consumer health

### Slack
- `POST /api/v1/slack/notify` - Send Slack notification

## 🔧 Configuration

Backend configuration is managed via environment variables (see `config/settings.py`):

- `DATABASE_URL` - PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses
- `SLACK_BOT_TOKEN` / `SLACK_WEBHOOK_URL` - Slack credentials
- `MODEL_BASE_PATH` - Path to model files
- `INFERENCE_SERVICE_URL` - FastAPI inference service URL
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

## 📊 Business Features

### Daily Reports
- AI-driven revenue contribution percentage
- Average cart uplift
- Most clicked recommended items
- Conversion rate delta

### Weekly Reports
- Emerging behavior patterns
- Cross-brand associations
- Trend shifts

### Slack Notifications
- 🛒 Cart abandonment alerts
- 🚀 Model deployment notifications
- 📉 Drift detection alerts
- 📸 Influencer tag detection
- 📊 Daily AI revenue reports
- 📘 Weekly "New Learnings" reports

## 🧪 Testing

### Backend Tests
```bash
cd website/app/backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd website/app/frontend
npm test
```

## 🚢 CI/CD

GitHub Actions pipeline includes:
- Linting (flake8, ESLint)
- Testing
- Docker image builds
- Smoke tests
- Deployment placeholder

## 📝 Environment Setup

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Kafka Topics
Topics are auto-created, but you can manually create:
- `realtime-recommendations`
- `fashion-events`

## 🔐 Security

- CORS configured for frontend origins
- Environment-based secrets
- Health checks for all services
- Structured logging (no sensitive data)

## 📈 Monitoring

- Health endpoints on all services
- Structured JSON logging
- Kafka consumer lag monitoring
- Drift detection with thresholds

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Submit pull request

## 📄 License

[Your License Here]

## 🆘 Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify `DATABASE_URL` is correct
- Check Kafka connectivity

### Frontend can't connect to API
- Verify backend is running on port 8000
- Check CORS settings
- Verify proxy configuration in `vite.config.ts`

### Models not loading
- Check `MODEL_BASE_PATH` points to correct directory
- Verify model files exist in `MLOps/models/`
- Check file permissions
