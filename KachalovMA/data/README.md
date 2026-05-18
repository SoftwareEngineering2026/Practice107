# UUID Spring Microservices Demo

1. **Frontend** — HTML-страница с одной кнопкой.
2. **Backend** — генератор UUID и endpoint `/metrics` с прикладной метрикой.
3. **Long Task Processor** — шедулер, который периодически проверяет доступность интернета.
4. **Observability** — Grafana + Loki + Alloy + Prometheus.

## Запуск

```bash
docker compose up --build
```

После запуска открыть приложение:

```text
http://localhost:8081
```

Grafana:

```text
http://localhost:3000
```

Логин/пароль:

```text
admin / admin
```

Дашборд уже создаётся автоматически:

```text
Practice105 / Practice105 Observability
```

## Что делает приложение

На странице есть кнопка **"Сгенерировать UUID"**.  
Frontend вызывает backend:

```http
GET http://localhost:8080/api/uuid
```

Backend возвращает JSON:

```json
{
  "uuid": "8e8f0ad1-4ac9-42d5-9017-29d42ebf2e20"
}
```

При каждом вызове `/api/uuid` backend увеличивает счётчик `uuid_requests_total` и пишет строку в лог.

Метрика доступна тут:

```http
GET http://localhost:8080/metrics
```

Пример ответа:

```text
# HELP uuid_requests_total Total UUID generation requests
# TYPE uuid_requests_total counter
uuid_requests_total 3
```

Prometheus забирает эту метрику с backend, Alloy читает Docker-логи контейнеров и отправляет их в Loki, Grafana показывает всё на одном дашборде.

## Проверка вручную

```bash
curl http://localhost:8080/api/uuid
curl http://localhost:8080/metrics
curl http://localhost:8080/actuator/health
```

Prometheus:

```text
http://localhost:9090
```

Loki:

```text
http://localhost:3100/ready
```

## Структура проекта

```text
uuid-spring-microservices-demo/
├── docker-compose.yml
├── README.md
├── frontend/
├── backend-wsgi/
├── long-task-processor/
└── observability/
    ├── alloy/
    │   └── config.alloy
    ├── prometheus/
    │   └── prometheus.yml
    └── grafana/
        ├── dashboards/
        │   └── practice105-observability.json
        └── provisioning/
            ├── dashboards/
            │   └── dashboards.yml
            └── datasources/
                └── datasources.yml
```
