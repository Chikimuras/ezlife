.PHONY: dev preprod prod down logs ps setup

dev:
	docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build -d
	@echo ""
	@echo "  → https://local.ezlife.com"
	@echo "  → Traefik dashboard: http://localhost:8080"
	@echo ""

preprod:
	docker compose --env-file .env.preprod -f docker-compose.yml -f docker-compose.preprod.yml up --build -d
	@echo ""
	@echo "  → https://preprod.ezlife.com"
	@echo ""

prod:
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build -d
	@echo ""
	@echo "  → https://$${DOMAIN:-ezlife.com}"
	@echo ""

down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.preprod.yml down 2>/dev/null; true

logs:
	docker compose logs -f

ps:
	docker compose ps

setup:
	@echo "Adding local domains to /etc/hosts (requires sudo)..."
	@grep -q "local.ezlife.com" /etc/hosts || echo "127.0.0.1 local.ezlife.com preprod.ezlife.com" | sudo tee -a /etc/hosts
	@echo "Done. Domains: local.ezlife.com, preprod.ezlife.com"
