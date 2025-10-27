.PHONY: dev-backend dev-frontend docker-up docker-down

dev-backend:
	@cd backend && uvicorn app.main:app --reload

dev-frontend:
	@cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
