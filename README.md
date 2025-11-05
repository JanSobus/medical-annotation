# Medical Annotation Tool

A full-stack web application for annotating medical text with entities (diseases, medications, symptoms, etc.) and relationships between them. Built with FastAPI, React, and powered by AI for automated entity and relation extraction.

## 🌟 Features

- **Document Management**: Create, edit, and manage medical text documents
- **Entity Annotation**: Manually annotate medical entities with 8 different types
- **Relation Annotation**: Define relationships between entities (treats, causes, indicates, etc.)
- **AI-Powered Extraction**: Automatic entity and relation extraction using OpenAI GPT models
- **Multi-Annotator Support**: Track annotations by different annotators
- **Real-time Updates**: Live timestamp tracking for all changes
- **Export/Import**: Database dump functionality for backups and data migration

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Compose Setup](#docker-compose-setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **SQLite** - Lightweight database (easily swappable with PostgreSQL)
- **PydanticAI** - AI agent framework for entity/relation extraction
- **OpenAI GPT-4o-mini** - LLM for medical text analysis

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Re-usable component library

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **uv** - Fast Python package manager

## 📦 Prerequisites

### For Local Development

- **Python 3.13+** (specified in `pyproject.toml`)
- **Node.js 18+** and **npm**
- **uv** (Python package manager)
  ```bash
  # Install uv (macOS/Linux)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Install uv (Windows)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### For Docker Deployment

- **Docker Engine 20.10+**
- **Docker Compose 2.0+**

## 🚀 Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd oracle-challenge
```

### 2. Backend Setup

#### Install Dependencies

```bash
# Install Python dependencies using uv
uv sync
```

#### Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./data/medical_annotations.db
TEST_DB_URL=sqlite:///./test.db

# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your-openai-api-key-here
```

#### Run Database Migrations

```bash
# The database tables are created automatically on first run
# No manual migration needed
```

#### Start the Backend Server

```bash
# Development mode with auto-reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
uv run python run.py
```

The backend will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Start the Development Server

```bash
npm run dev
```

The frontend will be available at:
- **App**: http://localhost:5173

### 4. Verify Setup

1. Open http://localhost:5173 in your browser
2. Enter your name as an annotator
3. Create a test document
4. Start annotating!

## 🐳 Docker Compose Setup

Docker Compose provides a production-ready setup with both frontend and backend containerized.

### 1. Prerequisites

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./data/medical_annotations.db

# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 4. Access the Application

Once the services are running:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Manage Services

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (deletes database!)
docker-compose down -v

# Restart a specific service
docker-compose restart backend
```

### 6. Database Persistence

The database is stored in a Docker volume and persists between container restarts. The data is mapped to `./data/` directory on your host machine.

To backup the database:

```bash
# The database file is at ./data/medical_annotations.db
cp data/medical_annotations.db data/backup_$(date +%Y%m%d).db
```

## 📁 Project Structure

```
oracle-challenge/
├── src/                          # Backend source code
│   ├── api/
│   │   ├── routes/              # API route handlers
│   │   │   ├── annotations.py   # Annotation endpoints
│   │   │   ├── documents.py     # Document endpoints
│   │   │   ├── entities.py      # Entity endpoints
│   │   │   └── relations.py     # Relation endpoints
│   │   └── dependencies.py      # Dependency injection
│   ├── models/                  # SQLModel database models
│   │   ├── annotation.py
│   │   ├── document.py
│   │   ├── entity.py
│   │   └── relation.py
│   ├── agents.py                # PydanticAI agents for extraction
│   ├── config.py                # Application configuration
│   ├── database.py              # Database setup and session
│   └── main.py                  # FastAPI application
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── constants/           # Constants and configurations
│   │   ├── pages/               # Page components
│   │   ├── types/               # TypeScript type definitions
│   │   ├── utils/               # Utility functions
│   │   ├── App.tsx              # Main app component
│   │   └── main.tsx             # Entry point
│   ├── public/                  # Static assets
│   └── index.html               # HTML template
├── tests/                       # Backend tests
│   ├── test_agents.py
│   ├── test_annotations.py
│   ├── test_documents.py
│   ├── test_entities.py
│   ├── test_health.py
│   └── test_relations.py
├── data/                        # Database storage (gitignored)
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile.backend           # Backend Docker image
├── Dockerfile.frontend          # Frontend Docker image
├── nginx.conf                   # Nginx configuration
├── pyproject.toml               # Python project configuration
├── .env                         # Environment variables (gitignored)
└── README.md                    # This file
```

## 📚 API Documentation

### Core Endpoints

#### Documents
- `POST /api/v1/documents/` - Create a new document
- `GET /api/v1/documents/?skip=0&limit=100` - List all documents (with pagination)
- `GET /api/v1/documents/{id}` - Get a specific document
- `PUT /api/v1/documents/{id}` - Update a document (partial updates supported)
- `DELETE /api/v1/documents/{id}` - Delete a document
- `POST /api/v1/documents/{id}/extract-entities` - AI entity extraction

#### Annotations
- `POST /api/v1/annotations/` - Create a new annotation
- `GET /api/v1/annotations/?document_id={id}&annotator_id={name}` - List annotations (with optional filters)
- `GET /api/v1/annotations/{id}` - Get a specific annotation
- `PUT /api/v1/annotations/{id}` - Update annotation (partial updates supported)
- `DELETE /api/v1/annotations/{id}` - Delete an annotation
- `POST /api/v1/annotations/{id}/extract-relations` - AI relation extraction

#### Entities
- `POST /api/v1/entities/` - Create a new entity
- `GET /api/v1/entities/?annotation_id={id}` - List entities (with optional annotation filter)
- `GET /api/v1/entities/{id}` - Get a specific entity
- `PUT /api/v1/entities/{id}` - Update an entity (partial updates supported)
- `DELETE /api/v1/entities/{id}` - Delete an entity

#### Relations
- `POST /api/v1/relations/` - Create a new relation
- `GET /api/v1/relations/?annotation_id={id}` - List relations (with optional annotation filter)
- `GET /api/v1/relations/{id}` - Get a specific relation
- `PUT /api/v1/relations/{id}` - Update a relation (partial updates supported)
- `DELETE /api/v1/relations/{id}` - Delete a relation

#### Utility
- `GET /health` - Health check
- `GET /dump_db` - Export entire database as JSON
- `POST /wipe_db` - Clear all data (use with caution!)

### Interactive API Documentation

Visit http://localhost:8000/docs for the full interactive Swagger UI documentation.

## 🧪 Testing

### Run All Tests

```bash
# Run all tests with coverage
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_documents.py

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html
```

### Test Coverage

The project maintains **>80% test coverage**. View the coverage report:

```bash
# Generate and open HTML coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in your browser
```

### Linting and Type Checking

```bash
# Run ruff linter
uv run ruff check .

# Run ruff formatter
uv run ruff format .

# Run type checker
uv run pyright
```

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/medical.db` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_DB_URL` | Test database URL | `sqlite:///./data/test.db` |

### Security Notes

- **Never commit `.env` files** to version control
- Use different API keys for development and production
- Rotate API keys regularly
- Use environment-specific configurations

## 🚢 Production Deployment

### Using Docker Compose (Recommended)

1. **Set up production environment variables**:
   ```bash
   # Use strong, unique values in production
   DATABASE_URL=sqlite:///./data/medical.db
   OPENAI_API_KEY=your-production-api-key
   ```

2. **Build and deploy**:
   ```bash
   docker-compose up -d --build
   ```

3. **Set up SSL/TLS** (recommended):
   - Use a reverse proxy like Nginx or Traefik
   - Obtain SSL certificates (Let's Encrypt)
   - Configure HTTPS

4. **Configure backups**:
   ```bash
   # Set up automated backups
   0 2 * * * cp /path/to/data/medical_annotations.db /path/to/backups/backup_$(date +\%Y\%m\%d).db
   ```

### Production Checklist

- [ ] Set up proper CORS origins (not `*`)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure automated backups
- [ ] Use secrets management (not `.env` files)
- [ ] Set resource limits in Docker Compose
- [ ] Enable rate limiting
- [ ] Set up health checks and alerting
- [ ] Review and harden security settings
- [ ] Consider database scaling strategy for high concurrency

### Database Considerations

The application uses SQLite by default, which is suitable for most use cases. For high-concurrency production environments, consider using a client-server database system.

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Make sure you're in the project root and using uv
uv run uvicorn src.main:app --reload
```

**Issue**: `Database is locked`
```bash
# Solution: SQLite doesn't handle high concurrency well
# Use PostgreSQL for production or ensure only one process accesses the DB
```

**Issue**: `OPENAI_API_KEY not found`
```bash
# Solution: Create .env file with your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Frontend Issues

**Issue**: `Cannot connect to backend`
```bash
# Solution: Ensure backend is running on port 8000
# Check frontend/vite.config.ts proxy configuration
```

**Issue**: `CORS errors`
```bash
# Solution: Backend CORS is configured for development
# For production, update allowed origins in src/main.py
```

### Docker Issues

**Issue**: `Backend container exits immediately`
```bash
# Solution: Check logs
docker-compose logs backend

# Ensure .env file exists with required variables
```

**Issue**: `Port already in use`
```bash
# Solution: Stop conflicting services or change ports in docker-compose.yml
# Check what's using the port:
netstat -ano | findstr :80    # Windows
lsof -i :80                   # macOS/Linux
```

**Issue**: `Database not persisting`
```bash
# Solution: Ensure volume is properly configured
docker-compose down
docker volume ls
# Volume should be listed as oracle-challenge_db-data
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Run linter (`uv run ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- AI powered by [OpenAI](https://openai.com/)
- Icons from [Lucide](https://lucide.dev/)

## Author
[Jan Sobus](https://jansobus.com)

---

**Need help?** Open an issue or check the [API documentation](http://localhost:8000/docs) for more details.

