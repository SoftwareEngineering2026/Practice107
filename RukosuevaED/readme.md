# Задание 107. Мониторинг

## Описание

Микросервис `Notes API` (FastAPI) для хранения заметок в памяти, обвязанный стеком
централизованного сбора логов и метрик:

- **Grafana Alloy** — собирает логи Docker-контейнеров и метрики приложения;
- **Loki** — хранилище логов;
- **Grafana Mimir** — хранилище метрик (Prometheus remote_write);
- **Grafana** — визуализация логов и метрик в едином дашборде.

## Приложение

`app/main.py` — REST API для заметок:

- `GET /notes`, `POST /notes`, `GET /notes/{id}`, `DELETE /notes/{id}`
- `GET /health` — проверка живости
- `GET /metrics` — метрики в формате Prometheus

Кастомные метрики:

- `app_requests_total{method, path, status_code}` — счётчик HTTP-запросов;
- `app_request_duration_seconds{method, path}` — гистограмма длительности запросов.

Каждый запрос также логируется в stdout в формате JSON (метод, путь, код ответа,
длительность, request id) — эти логи забирает Alloy и отправляет в Loki.

## Как это работает

1. `app` отдаёт метрики на `/metrics` и пишет логи в stdout.
2. `alloy`:
   - скрейпит `/metrics` приложения и пушит метрики в Mimir (`remote_write`);
   - через Docker discovery читает логи всех контейнеров и пушит их в Loki.
3. `mimir` и `loki` хранят метрики и логи на диске (filesystem storage, том Docker).
4. `grafana` подключается к Mimir и Loki как к datasource'ам (автоматически, через
   provisioning) и показывает дашборд `Notes App` с графиками RPS, latency (p95),
   счётчиком запросов и панелью логов приложения.

## Запуск

```bash
docker compose up --build
```

После запуска доступны:

- приложение — http://localhost:8000 (Swagger UI — http://localhost:8000/docs)
- метрики приложения — http://localhost:8000/metrics
- Grafana — http://localhost:3000 (анонимный доступ с правами admin, дашборд
  "Notes App" открывается сразу после входа)
- Loki API — http://localhost:3100
- Mimir API — http://localhost:9009

Чтобы в дашборде появились данные, нужно сделать несколько запросов к API, например:

```bash
curl -X POST http://localhost:8000/notes -H "Content-Type: application/json" \
  -d '{"title": "test", "content": "hello"}'
curl http://localhost:8000/notes
```

## Структура проекта

```
RukosuevaED/
├── app/                # исходники и Dockerfile приложения
├── alloy/              # конфигурация Grafana Alloy (сбор логов и метрик)
├── loki/               # конфигурация Loki
├── mimir/              # конфигурация Grafana Mimir
├── grafana/             # provisioning datasource'ов и готовый дашборд
├── docker-compose.yml
└── readme.md
```
