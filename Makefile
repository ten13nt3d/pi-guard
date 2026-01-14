.PHONY: compose-init compose-up compose-down compose-purge logs ps restart dns-check

compose-init:
	@cp -n docker-compose.yml.template docker-compose.yml
	@echo "Created docker-compose.yml (if it did not exist)."

compose-up: compose-init
	@docker compose up -d

compose-down:
	@docker compose down

compose-purge:
	@docker compose down --remove-orphans
	@docker rm -f wireguard duckdns adguardhome unbound 2>/dev/null || true

logs:
	@docker compose logs -f --tail=200

ps:
	@docker compose ps

restart:
	@docker compose restart

dns-check:
	@sudo ss -lunpt | grep ':53 ' || true
	@sudo ss -ltnp | grep ':53 ' || true
