.PHONY: up down build train test lint

# Start full stack (Postgres + Streamlit app)
up:
	docker-compose up --build

# Stop everything
down:
	docker-compose down

# Build image only
build:
	docker-compose build

# Train the model (run this after labeling data)
train:
	python -m src.model.train

# Run tests
test:
	pytest tests/ -v

# Lint
lint:
	ruff check src/ app/ tests/

# Run app locally without Docker (needs local Postgres)
run:
	streamlit run app/main.py

# Open psql shell into running container
db-shell:
	docker-compose exec db psql -U postgres -d fake_detector
