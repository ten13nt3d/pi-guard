.PHONY: compose-init compose-up compose-down logs ps restart

compose-init:
	@cp -n docker-compose.yml.template docker-compose.yml
	@echo "Created docker-compose.yml (if it did not exist)."

compose-up: compose-init
	@docker compose up -d

compose-down:
	@docker compose down

logs:
	@docker compose logs -f --tail=200

ps:
	@docker compose ps

restart:
	@docker compose restart
