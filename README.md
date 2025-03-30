# Portfolio Project Documentation
## Project Overview
* **Purpose:** AI-powered chatbot that answers questions about your professional experience  

* **Architecture:**

  * React frontend ↔ FastAPI backend ↔ OpenAI API ↔ Milvus vector DB
  * Redis for rate limiting
  * PostgreSQL for chat/message storage

* **Key Features:**

  * Context-aware responses about your career/education
  * Session-based chats (resets on page refresh)
  * Rate limiting (50 messages/5min, 2 chats/5min)
  * Off-topic detection with 3-strike policy
---
## Project structure

```
portfolio_backend
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```
---

## API Reference

### Endpoints
#### Chat  
* `POST /api/v1/chat` - Create new chat (rate limited: 2/5min)
* `GET /api/v1/chat/{chat_id}` - Get chat details  

#### Message  
* `POST /api/v1/message` - Send message (rate limited: 50/5min)
* `GET /api/v1/message/{message_id}` - Get single message
* `GET /api/v1/message/chat/{chat_id}` - Get all messages in chat
---
## Setup & Configuration
### Requirements
* Python 3.10+
* Redis
* PostgreSQL
* Milvus

This project uses uv. It's a modern dependency management tool.
### Installation
```
uv pip install -e .
```
### Environment Variables (`.env`)
This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "PORTFOLIO_BACKEND_" prefix.

For example if you see in your "portfolio_backend/settings.py" a variable named like
`random_parameter`, you should provide the "PORTFOLIO_BACKEND_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `portfolio_backend.settings.Settings.Config`.

An example of .env file:
```dotenv
PORTFOLIO_BACKEND_HOST=""
PORTFOLIO_BACKEND_PORT=""
PORTFOLIO_BACKEND_DB_HOST=""
PORTFOLIO_BACKEND_DB_PORT=""
PORTFOLIO_BACKEND_DB_USER=""
PORTFOLIO_BACKEND_DB_PASS=""
PORTFOLIO_BACKEND_DB_BASE=""
PORTFOLIO_BACKEND_OPENAI_API_KEY=""
```
### Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default, it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possible bugs);

You can read more about pre-commit [here](https://pre-commit.com/).

### Migrations

If you want to migrate your database, you should run following commands:
```
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

#### Reverting migrations

If you want to revert migrations, you should run:
```
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

#### Migration generation

To generate migrations you should run:
```
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```

### Running
```
uv run alembic upgrade head 
uv run portfolio_backend
```
---
## Core Components
### Chat Flow
1. User sends message → Frontend calls /api/v1/message
2. Backend:
   * Embeds message using OpenAI
   * Searches Milvus for similar content
   * Formats prompt with context
   * Gets response from OpenAI
   * Stores message in PostgreSQL
   * Returns AI response

### Rate Limiting
* Redis tracks:
  * 50 messages per 5 minutes
  * 2 new chats per 5 minutes

### Vector Database
* Milvus stores embedded text data
* Pre-embedded content in static/data/embedded_text.csv
* On startup:
  * Checks for collection
  * Creates if missing
  * Loads from CSV if exists
---
## Database Schema
###  Tables
#### `chats`
```
chat_id UUID PRIMARY KEY
off_topic_response_count INTEGER DEFAULT 0
created_at TIMESTAMP DEFAULT NOW()
```
#### `messages`
```
message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4()
chat_id UUID REFERENCES chats(chat_id) ON DELETE CASCADE
message_text TEXT
message_by VARCHAR(10)  -- 'human', 'ai', or 'system'
created_at TIMESTAMP DEFAULT NOW()
```
---
## Configuration
### Key Settings (settings.py)
* OpenAI models: text-embedding-3-small and gpt-4o-mini
* Vector DB: 1536-dimension embeddings
* Search: Top 5 results, L2 distance metric
* Prometheus metrics enabled
---
## API Documentation (Swagger/OpenAPI)
FastAPI backend automatically generates interactive API documentation using Swagger UI and ReDoc. This provides a convenient way to explore and test the API endpoints.

### Accessing the Documentation

1. **Swagger UI** (Interactive Documentation):
   * Available at: http://<host>:<port>/api/v1/docs
   * Features:
     * Interactive endpoint testing
     * Schema visualization
     * Try-it-out functionality
     * Example requests/responses

2. **ReDoc** (Alternative Documentation):
   * Available at: http://<your-host>:<your-port>/api/v1/redoc
   * Features:
     * Clean, responsive documentation
     * Better for reading/navigating
     * No interactive testing

### Customization
The documentation is self-hosted (files are in `portfolio_backend/static/docs/`) with these configurations:  
* **OpenAPI Schema Path:** `/api/openapi.json`
* **Disabled Default Docs:** Set in `application.py`:
```
app = FastAPI(
    docs_url=None,  # Disables default Swagger
    redoc_url=None,  # Disables default ReDoc
    openapi_url="/api/openapi.json"
)
```

* **Custom Mounting:** The static docs are mounted at `/static`:
```
Copy
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
```

### How It Works
1. The docs router (`web/api/docs/views.py`) serves the customized Swagger UI
2. FastAPI generates the OpenAPI schema automatically from your:
   * Route definitions
   * Pydantic models (request/response schemas)
   * Docstrings (appear as endpoint descriptions)

### Example Endpoint Documentation
Chat endpoints are automatically documented with:
* All available parameters
* Request/response schemas
* Example values
* Authentication requirements (rate limits in this case)

### Testing API Endpoints
Using Swagger UI, you can:
   1. Click on an endpoint (e.g., `POST /api/v1/chat`)
   2. Click "Try it out"
   3. Enter required parameters
   4. Execute the request
   5. View the live response
