# System Design Document

## Medical Annotation Tool - Architecture & Design

**Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Frontend Architecture](#frontend-architecture)
7. [AI Integration](#ai-integration)
8. [Security Considerations](#security-considerations)
9. [Performance & Scalability](#performance--scalability)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Purpose

The Medical Annotation Tool is designed to facilitate the annotation of medical text documents with structured medical entities (diseases, medications, symptoms, etc.) and the relationships between them. It supports both manual annotation workflows and AI-assisted extraction.

### Key Features

- **Document Management**: CRUD operations for medical text documents
- **Multi-Entity Annotation**: Support for 8 entity types with character-level positioning
- **Relationship Mapping**: Define and track relationships between entities
- **Multi-Annotator Support**: Track work by different annotators with audit trails
- **AI-Powered Extraction**: Automated entity and relation extraction using LLMs
- **Real-Time Collaboration**: Track annotation status and timestamps
- **Data Export**: Full database dump capability for backups and analysis

### Users & Roles

- **Annotators**: Users who create and manage annotations
- **Administrators**: Manage documents and review annotations (future)
- **Data Scientists**: Export annotated data for ML training (via API/export)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            React SPA (Port 5173 / 80)                  │    │
│  │  - TypeScript, Vite, Tailwind CSS, shadcn/ui          │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         FastAPI Backend (Port 8000)                    │    │
│  │  - Python 3.13, FastAPI, SQLModel, PydanticAI        │    │
│  │  - REST API, OpenAPI/Swagger Documentation            │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
         ┌──────────────────┐  ┌──────────────────┐
         │  Database Layer  │  │   AI Services    │
         │                  │  │                  │
         │ SQLite/PostgreSQL│  │  OpenAI GPT-4o   │
         │   (SQLModel)     │  │   (PydanticAI)   │
         └──────────────────┘  └──────────────────┘
```

### Service Breakdown

#### 1. Frontend Service (React/Vite)

**Responsibilities**:
- User interface rendering and interaction
- Client-side routing and navigation
- Form validation and user input handling
- API request orchestration
- Local state management (annotator context)

**Technology**:
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- Context API for global state

**Key Components**:
- `Landing.tsx` - Annotator identification
- `Documents.tsx` - Document list and management
- `Annotation.tsx` - Main annotation interface
- `AddDocument.tsx` - Document creation form

#### 2. Backend Service (FastAPI)

**Responsibilities**:
- RESTful API endpoints
- Business logic implementation
- Database operations (CRUD)
- AI model integration
- Request validation
- Error handling and logging

**Technology**:
- FastAPI framework
- SQLModel for ORM
- Pydantic for validation
- PydanticAI for LLM integration
- Uvicorn as ASGI server

**Architecture Pattern**: Layered Architecture
```
┌─────────────────────────┐
│   API Routes Layer      │ ← Request/Response handling
├─────────────────────────┤
│   Business Logic        │ ← Core application logic
├─────────────────────────┤
│   Data Access Layer     │ ← SQLModel models & queries
├─────────────────────────┤
│   Database              │ ← SQLite/PostgreSQL
└─────────────────────────┘
```

#### 3. Database Service

**Responsibilities**:
- Persistent data storage
- Transactional integrity
- Relationship management
- Query optimization

**Technology**:
- SQLite (default database)
- SQLModel as ORM/query builder

#### 4. AI Service (PydanticAI + OpenAI)

**Responsibilities**:
- Medical entity extraction from text
- Relationship identification between entities
- Confidence scoring
- Response validation and parsing

**Technology**:
- PydanticAI agent framework
- OpenAI GPT-4o-mini model
- Custom system prompts for medical domain

---

## Technology Stack

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104+ | Web framework |
| **Language** | Python | 3.13+ | Core language |
| **ORM** | SQLModel | 0.0.14+ | Database abstraction |
| **Validation** | Pydantic | 2.5+ | Data validation |
| **AI Framework** | PydanticAI | 1.11+ | LLM integration |
| **Database** | SQLite | - | Data persistence |
| **ASGI Server** | Uvicorn | 0.24+ | HTTP server |
| **Package Manager** | uv | latest | Dependency management |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Library** | React | 18.x | UI framework |
| **Language** | TypeScript | 5.x | Type safety |
| **Build Tool** | Vite | 5.x | Development & bundling |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **UI Components** | shadcn/ui | latest | Component library |
| **Routing** | React Router | 6.x | Client-side routing |
| **HTTP Client** | Fetch API | native | API communication |

### DevOps Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose | Multi-container deployment |
| **Web Server** | Nginx | Reverse proxy & static files |
| **Testing** | Pytest | Backend testing |
| **Linting** | Ruff | Code quality |
| **Type Checking** | Pyright | Static type analysis |

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────────────┐
│     Document        │
│─────────────────────│
│ id: INTEGER (PK)    │
│ title: TEXT         │
│ text: TEXT          │
│ created_at: DATETIME│
│ updated_at: DATETIME│
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐
│    Annotation       │
│─────────────────────│
│ id: INTEGER (PK)    │
│ document_id: INT(FK)│
│ annotator_id: TEXT  │
│ status: TEXT (ENUM) │
│ created_at: DATETIME│
│ updated_at: DATETIME│
└──────────┬──────────┘
           │
           ├─────────────────┐
           │ 1:N             │ 1:N
           │                 │
           ▼                 ▼
┌─────────────────────┐  ┌─────────────────────┐
│      Entity         │  │     Relation        │
│─────────────────────│  │─────────────────────│
│ id: INTEGER (PK)    │  │ id: INTEGER (PK)    │
│ annotation_id: INT  │  │ annotation_id: INT  │
│ text: TEXT          │  │ source_entity_id:INT│
│ entity_type: TEXT   │  │ target_entity_id:INT│
│ start_char: INTEGER │  │ relation_type: TEXT │
│ end_char: INTEGER   │  │ confidence: FLOAT   │
│ confidence: FLOAT   │  │ created_at: DATETIME│
│ created_at: DATETIME│  │ updated_at: DATETIME│
│ updated_at: DATETIME│  └─────────────────────┘
└─────────────────────┘
```

### Table Schemas

#### 1. Documents Table

Stores the raw medical text documents to be annotated.

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `id`: Unique identifier
- `title`: Document title/name
- `text`: Full medical text content
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Indexes**: Primary key on `id`

#### 2. Annotations Table

Represents an annotation session for a document by a specific annotator.

```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    annotator_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

**Fields**:
- `id`: Unique identifier
- `document_id`: Reference to document
- `annotator_id`: Identifier of the annotator (username/email)
- `status`: Annotation status (not_started, in_progress, completed)
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Indexes**: 
- Primary key on `id`
- Index on `document_id`
- Composite index on `(document_id, annotator_id)`

**Status Values**:
- `not_started`: Annotation created but no entities added
- `in_progress`: Actively being worked on
- `completed`: Annotation finished and reviewed

#### 3. Entities Table

Stores individual medical entities identified in the text.

```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annotation_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (annotation_id) REFERENCES annotations(id) ON DELETE CASCADE
);
```

**Fields**:
- `id`: Unique identifier
- `annotation_id`: Reference to annotation
- `text`: Entity text as it appears in document
- `entity_type`: Type of entity (see Entity Types below)
- `start_char`: Starting character position in document
- `end_char`: Ending character position in document
- `confidence`: Confidence score (0.0-1.0, default 1.0 for manual)
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Indexes**:
- Primary key on `id`
- Index on `annotation_id`
- Composite index on `(annotation_id, start_char)`

**Entity Types** (Enum):
- `disease`: Medical conditions, diagnoses, pathologies
- `medication`: Drug names, treatments, medications
- `symptom`: Clinical symptoms, signs, complaints
- `procedure`: Medical procedures, tests, interventions
- `anatomy`: Anatomical structures, body parts, organs
- `lab_value`: Laboratory test results, measurements
- `dosage`: Drug dosages, medication measurements
- `other`: Other medically relevant entities

#### 4. Relations Table

Stores relationships between pairs of entities.

```sql
CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annotation_id INTEGER NOT NULL,
    source_entity_id INTEGER NOT NULL,
    target_entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.8,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (annotation_id) REFERENCES annotations(id) ON DELETE CASCADE,
    FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE
);
```

**Fields**:
- `id`: Unique identifier
- `annotation_id`: Reference to annotation
- `source_entity_id`: Source entity in the relationship
- `target_entity_id`: Target entity in the relationship
- `relation_type`: Type of relationship (see Relation Types below)
- `confidence`: Confidence score (0.0-1.0)
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Indexes**:
- Primary key on `id`
- Index on `annotation_id`
- Index on `source_entity_id`
- Index on `target_entity_id`

**Relation Types** (Enum):
- `treats`: Medication/procedure treats disease/symptom
- `causes`: Entity causes another entity
- `has_symptom`: Disease has associated symptom
- `indicates`: Symptom/lab value indicates disease
- `contraindicates`: Medication contraindicated for condition
- `dosage_for`: Dosage amount for specific medication
- `located_in`: Anatomical location relationship
- `temporal`: Temporal relationship (before, after, during)
- `other`: Other medically relevant relationships

**Note**: Default confidence for relations is `1.0` (manually created) or varies for AI-extracted relations.

### Database Constraints

1. **Referential Integrity**: All foreign keys use `ON DELETE CASCADE`
2. **Character Positions**: `end_char` must be >= `start_char` (validated in application)
3. **Confidence Scores**: Must be between 0.0 and 1.0 (validated by Pydantic)
4. **Status Values**: Must be one of the defined enum values
5. **Entity/Relation Types**: Must be one of the defined enum values

### Indexing Strategy

**Current Indexes**:
- Primary keys on all tables
- Foreign key indexes (automatic)
- `(document_id, annotator_id)` on annotations
- `(annotation_id, start_char)` on entities

**Future Optimization Opportunities**:
- Full-text search index on `documents.text`
- Index on `annotations.status` for filtering
- Index on `entities.entity_type` for type-based queries

---

## API Design

### API Architecture

**Style**: RESTful  
**Format**: JSON  
**Authentication**: None (future: JWT)  
**Versioning**: URL path (`/api/v1/`)  
**Documentation**: Interactive Swagger UI at `/docs`

### Endpoint Overview

```
/api/v1/
├── /documents/          # Document CRUD + AI entity extraction
├── /annotations/        # Annotation CRUD + AI relation extraction
├── /entities/           # Entity CRUD (filterable by annotation)
└── /relations/          # Relation CRUD (filterable by annotation)

Utility Endpoints:
├── GET  /health         # Health check
├── GET  /dump_db        # Export entire database as JSON
└── POST /wipe_db        # Clear all data (caution!)
```

### Key Endpoints

#### Core Resources

All resources follow standard REST patterns:
- `GET /` - List all (with pagination: `?skip=0&limit=100`)
- `POST /` - Create new
- `GET /{id}` - Get by ID
- `PUT /{id}` - Update (partial updates supported)
- `DELETE /{id}` - Delete

#### Special Endpoints

**AI-Powered Extraction**:
- `POST /documents/{id}/extract-entities` - Extract medical entities from document text
- `POST /annotations/{id}/extract-relations` - Identify relationships between entities

**Filtering**:
- `GET /annotations/?document_id={id}&annotator_id={name}` - Filter annotations
- `GET /entities/?annotation_id={id}` - Get entities for specific annotation
- `GET /relations/?annotation_id={id}` - Get relations for specific annotation

### Response Format

**Success Response**:
```json
{
  "id": 1,
  "field": "value",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

**Error Response**:
```json
{
  "detail": "Error message"
}
```

**Status Codes**: `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `422 Validation Error`, `500 Server Error`

### Interactive Documentation

For complete API specifications, request/response schemas, and interactive testing:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Frontend Architecture

### Component Hierarchy

```
App (Router + Annotator Context)
│
├─ Landing Page
│  └─ AnnotatorForm
│
├─ Documents Page
│  ├─ DocumentTile (repeated)
│  └─ AddDocumentTile
│
├─ AddDocument Page
│  └─ DocumentForm
│
└─ Annotation Page
   ├─ Header (status, timestamps)
   ├─ EntityPanel (left half)
   │  ├─ EntityLegend
   │  ├─ EntityList
   │  ├─ CreateEntityModal
   │  └─ EditEntityModal
   ├─ RelationPanel (right half)
   │  ├─ RelationList
   │  ├─ CreateRelationModal
   │  └─ EditRelationModal
   └─ DocumentTextWithEntities
```

### State Management

#### Global State (Context API)

**AnnotatorContext**: Stores current annotator ID
- Persisted to localStorage
- Accessible across all components
- Used for creating annotations

#### Local Component State

Each page manages its own state:
- **Documents**: List of documents, loading state
- **Annotation**: Entities, relations, document, annotation details
- **Modals**: Form inputs, selected entities

### Data Flow

```
User Action
    ↓
Component Handler
    ↓
API Call (fetch)
    ↓
Backend Processing
    ↓
API Response
    ↓
State Update
    ↓
Re-render
```

### Key Design Patterns

1. **Protected Routes**: Check for annotator ID before rendering
2. **Optimistic Updates**: Update UI immediately, rollback on error
3. **Error Boundaries**: Graceful error handling
4. **Loading States**: Visual feedback during API calls
5. **Modal Pattern**: Reusable modal components for forms

### Styling Strategy

- **Tailwind CSS**: Utility-first approach
- **shadcn/ui**: Pre-built accessible components
- **Color Coding**: Entity types have consistent colors
- **Responsive Design**: Mobile-friendly layouts

---

## AI Integration

### Architecture

```
Backend API
    ↓
PydanticAI Agent
    ↓
OpenAI API (GPT-4o-mini)
    ↓
Structured Response
    ↓
Pydantic Validation
    ↓
Database Storage
```

### Entity Extraction Agent

**Purpose**: Extract medical entities from raw text

**System Prompt**: Instructs model to identify 8 entity types

**Input**: Document text (string)

**Output**: Structured `ExtractedEntitiesResponse`
```python
{
  "text": "...",
  "entities": [
    {
      "text": "entity text",
      "entity_type": "disease",
      "start_char": 10,
      "end_char": 21,
      "confidence": 0.95
    }
  ]
}
```

**Post-Processing**:
- Character position correction (LLMs are unreliable with counting)
- Case-insensitive text matching
- Deduplication of overlapping entities

### Relation Extraction Agent

**Purpose**: Identify relationships between entities

**System Prompt**: Instructs model on 9 relation types

**Input**: 
- Document text
- List of existing entities

**Output**: Structured `ExtractedRelationsResponse`
```python
{
  "relations": [
    {
      "source_entity_id": 1,
      "target_entity_id": 2,
      "relation_type": "treats",
      "confidence": 0.89
    }
  ]
}
```

**Processing**:
- Validates entity IDs exist
- Filters redundant relations
- Ensures directional consistency

### AI Configuration

**Model**: `openai:gpt-4o-mini`  
**Retries**: 2 attempts  
**Timeout**: 60 seconds (configurable in Nginx)  
**Temperature**: Default (not explicitly set)

### Error Handling

- API key validation on startup
- Timeout handling with graceful degradation
- Error messages returned to frontend
- Logging for debugging

---

## Security Considerations

### Current Implementation

1. **CORS**: Configured for development (`allow_origins=["*"]`)
2. **Input Validation**: All inputs validated via Pydantic
3. **SQL Injection**: Protected by SQLModel/SQLAlchemy
4. **XSS**: React automatically escapes content
5. **Environment Variables**: Sensitive data in `.env`

### Production Recommendations

1. **Authentication**: Implement JWT-based auth
2. **Authorization**: Role-based access control
3. **CORS**: Restrict to specific origins
4. **HTTPS**: Enforce TLS encryption
5. **Rate Limiting**: Prevent API abuse
6. **Input Sanitization**: Additional validation layers
7. **Secrets Management**: Use vault services
8. **API Keys**: Rotate regularly
9. **Audit Logging**: Track all data modifications
10. **Database**: Use connection pooling and prepared statements

### Data Privacy

- **PHI Considerations**: Medical data may be PHI/PII
- **Anonymization**: Consider de-identification before annotation
- **Access Control**: Implement proper user permissions
- **Encryption**: Encrypt data at rest and in transit
- **Compliance**: HIPAA, GDPR considerations

---

## Performance & Scalability

### Current Performance Characteristics

**Backend**:
- **Response Time**: <100ms for CRUD operations
- **AI Extraction**: 2-10 seconds depending on text length
- **Database**: SQLite suitable for <1000 concurrent users
- **Memory**: ~100MB base + ~50MB per worker

**Frontend**:
- **Initial Load**: <1 second (optimized build)
- **Time to Interactive**: <2 seconds
- **Bundle Size**: ~500KB (gzipped)

### Scalability Considerations

#### Database Scaling

**Current**: SQLite (single-file)
- **Pros**: Simple, no setup, portable, sufficient for most use cases
- **Cons**: Limited write concurrency
- **Recommendation**: For high-concurrency production environments (>100 concurrent writers), consider a client-server database system

#### Backend Scaling

**Vertical Scaling**:
- Increase CPU/RAM for more uvicorn workers
- Use gunicorn with multiple uvicorn workers

**Horizontal Scaling**:
- Deploy multiple backend instances
- Use load balancer (Nginx, HAProxy)
- Requires client-server database for write concurrency

**Caching Strategy**:
- Redis for session storage
- CDN for static assets
- Query result caching

#### AI Service Scaling

**Current Bottleneck**: OpenAI API rate limits

**Solutions**:
- Implement request queuing
- Batch processing for multiple documents
- Cache common extractions
- Use async processing with task queue (Celery)

### Optimization Opportunities

1. **Database Indexes**: Add based on query patterns
2. **Query Optimization**: Use joins instead of N+1 queries
3. **Pagination**: Implement cursor-based pagination
4. **Lazy Loading**: Load entities/relations on demand
5. **Connection Pooling**: For client-server database deployments
6. **Compression**: Enable gzip compression in Nginx
7. **Asset Optimization**: Code splitting, tree shaking

---

## Deployment Architecture

### Development Environment

```
Developer Machine
├── Backend: uvicorn (reload mode)
├── Frontend: vite dev server
└── Database: SQLite (local file)
```

### Docker Compose Deployment

```
Docker Host
├── Frontend Container (Nginx)
│   ├── Static React build
│   └── Reverse proxy to backend
├── Backend Container (Uvicorn)
│   ├── FastAPI application
│   └── PydanticAI agents
└── Volume: Database storage
```

**Network**: Internal Docker network  
**Ports**: 80 (HTTP), 8000 (API - internal)  
**Volumes**: `./data` for database persistence

### Production Deployment (Recommended)

```
Internet
    ↓
Load Balancer / CDN
    ↓
Reverse Proxy (Nginx/Traefik)
    ↓
    ├─→ Frontend (Static Files)
    └─→ Backend API Servers (N instances)
            ↓
        Database Server
            ↓
        Persistent Storage
```

**Additional Services**:
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or similar
- **Secrets**: Vault or AWS Secrets Manager
- **Backups**: Automated daily snapshots
- **CI/CD**: GitHub Actions, GitLab CI

### Health Checks

**Backend**: `GET /health`
```json
{"status": "healthy"}
```

**Docker Compose**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Backup Strategy

**Database Backups**:
```bash
# SQLite
cp data/medical.db backups/medical_$(date +%Y%m%d).db
```

**API-Based Export**:
```bash
curl http://localhost:8000/dump_db > backup.json
```

---

## Future Enhancements

### Planned Features

1. **Authentication & Authorization**
   - User registration and login
   - Role-based access (annotator, reviewer, admin)
   - OAuth2 integration

2. **Collaboration Features**
   - Real-time collaborative annotation
   - Comment system for discussions
   - Annotation conflict resolution

3. **Advanced Search**
   - Full-text search across documents
   - Filter by entity types
   - Search within annotations

4. **Annotation Quality**
   - Inter-annotator agreement metrics
   - Quality scoring
   - Review and approval workflow

5. **Export Formats**
   - CSV export for entities/relations
   - BRAT format export
   - JSON-LD for linked data

6. **Analytics Dashboard**
   - Annotation statistics
   - Annotator productivity metrics
   - Entity distribution visualizations

7. **Batch Operations**
   - Bulk document upload
   - Batch entity/relation creation
   - Mass status updates

8. **Model Training Integration**
   - Export to training data format
   - Active learning suggestions
   - Model performance tracking

### Technical Debt

- [ ] Add comprehensive error logging
- [ ] Implement request rate limiting
- [ ] Add database migration system (Alembic)
- [ ] Improve test coverage for AI agents
- [ ] Add end-to-end tests
- [ ] Implement WebSocket for real-time updates
- [ ] Add API versioning strategy
- [ ] Create admin dashboard

---

## Appendix

### Key Design Decisions

1. **SQLite as Default**: SQLite chosen for simplicity and zero-configuration; suitable for most deployments
2. **REST vs GraphQL**: REST chosen for simplicity and broad tooling support
3. **Monorepo vs Multi-repo**: Monorepo for easier development and deployment
4. **State Management**: Context API sufficient for current needs, Redux overkill
5. **AI Provider**: OpenAI chosen for quality and ease of integration
6. **Docker Compose**: Chosen over Kubernetes for deployment simplicity

### Glossary

- **Entity**: A labeled span of text (e.g., "diabetes" as a disease)
- **Relation**: A directed relationship between two entities
- **Annotation**: A collection of entities and relations for a document by an annotator
- **Confidence**: A score (0.0-1.0) indicating certainty of an annotation
- **LLM**: Large Language Model (e.g., GPT-4)
- **ORM**: Object-Relational Mapping (SQLModel)
- **PHI**: Protected Health Information

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [React Documentation](https://react.dev/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Maintained By**: Jan Sobus

