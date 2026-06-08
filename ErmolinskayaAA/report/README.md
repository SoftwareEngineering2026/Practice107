# Practice107 — Логирование и мониторинг микросервисного приложения

## Описание проекта

Для выполнения работы используется микросервисное приложение **AI Text Helper**.

AI Text Helper — это веб-приложение для обработки и улучшения текста. Пользователь вводит текст, выбирает режим обработки, после чего backend создаёт задачу и помещает её в очередь. Длительная обработка выполняется отдельным worker-сервисом.

Приложение развёртывается с помощью Docker Compose и состоит из нескольких сервисов:

- `frontend` — пользовательский интерфейс;
- `backend` — WSGI API на Flask;
- `worker` — сервис для выполнения длительных задач обработки текста;
- `redis` — очередь задач и временное хранилище результатов;
- `nginx` — единая внешняя точка входа;
- `grafana` — визуализация логов и метрик;
- `alloy` — сбор логов и метрик;
- `loki` — хранение логов;
- `mimir` — хранение метрик.

## Цель работы

Цель работы — изучить подходы к централизованному сбору логов и мониторингу параметров микросервисного приложения.

В рамках работы были выполнены следующие задачи:

- развёрнуто микросервисное приложение;
- реализована прикладная метрика;
- добавлен endpoint `/metrics`;
- настроен сбор логов контейнеров;
- настроен сбор метрик backend-сервиса;
- организована визуализация логов и метрик в Grafana.

## Архитектура приложения

```text
Пользователь
    |
    v
Nginx
    |
    |----> Frontend
    |
    |----> Backend API
                |
                v
              Redis
                |
                v
              Worker
```

## Архитектура мониторинга

```text
Docker containers
      |
      v
Grafana Alloy
      |
      |----> Loki  ----> Grafana Logs
      |
      |----> Mimir ----> Grafana Metrics
```

Grafana Alloy собирает:

- логи Docker-контейнеров и отправляет их в Loki;
- метрики backend-сервиса с endpoint `/metrics` и отправляет их в Mimir.

Grafana используется для просмотра логов и метрик.

## Используемые инструменты

- Docker
- Docker Compose
- Flask
- Redis
- RQ
- Nginx
- Grafana
- Grafana Alloy
- Loki
- Grafana Mimir
- Prometheus Client

## Прикладная метрика

В backend-сервис добавлен endpoint:

```text
/metrics
```

Через корневой Nginx метрики доступны по адресу:

```text
http://localhost/api/metrics
```

В проекте реализованы следующие метрики:

| Метрика | Описание |
|---|---|
| `ai_text_helper_requests_total` | Общее количество HTTP-запросов к backend |
| `ai_text_helper_tasks_created_total` | Количество созданных задач обработки текста |
| `ai_text_helper_request_duration_seconds` | Время обработки HTTP-запросов |

Основная прикладная метрика:

```text
ai_text_helper_tasks_created_total
```

Она показывает количество созданных задач обработки текста с разбивкой по режимам обработки.

Пример значения:

```text
ai_text_helper_tasks_created_total{mode="improve"} 1.0
```

Это означает, что была создана одна задача обработки текста в режиме `improve`.

## Структура проекта

```text
.
├── README.md
├── docker-compose.yml
├── backend
│   ├── Dockerfile
│   ├── app.py
│   ├── tasks.py
│   └── requirements.txt
├── frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src
│       ├── index.html
│       ├── style.css
│       └── app.js
├── worker
│   ├── Dockerfile
│   ├── worker.py
│   ├── tasks.py
│   └── requirements.txt
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
└── monitoring
    ├── alloy
    │   └── config.alloy
    ├── loki
    │   └── loki-config.yml
    ├── mimir
    │   └── mimir.yml
    └── grafana
        └── provisioning
            └── datasources
                └── datasources.yml
```

## Описание сервисов

### Frontend

Frontend отвечает за пользовательский интерфейс. Через него пользователь вводит текст, отправляет задачу на обработку и получает результат.

### Backend

Backend реализован на Flask. Он принимает HTTP-запросы, создаёт задачи обработки текста, помещает их в Redis и отдаёт статусы выполнения.

Также backend публикует прикладные метрики на endpoint `/metrics`.

### Worker

Worker выполняет длительные задачи обработки текста. Он получает задачи из Redis и возвращает результат после обработки.

### Redis

Redis используется как очередь задач и временное хранилище результатов.

### Nginx

Nginx является единой внешней точкой входа в приложение.

Он проксирует запросы:

```text
/             -> frontend:80
/api/         -> backend:5000/api/
/api/metrics  -> backend:5000/metrics
```

### Grafana Alloy

Grafana Alloy собирает логи контейнеров Docker и метрики backend-сервиса.

Логи отправляются в Loki, а метрики отправляются в Mimir.

### Loki

Loki используется для хранения логов микросервисного приложения.

### Mimir

Grafana Mimir используется для хранения метрик приложения.

### Grafana

Grafana используется для визуализации логов и метрик.

## Запуск проекта

Для запуска проекта необходимо установить Docker и Docker Compose.

В корне проекта выполнить команду:

```bash
docker compose up --build
```

После запуска приложение доступно по адресу:

```text
http://localhost
```

Grafana доступна по адресу:

```text
http://localhost:3000
```

Логин и пароль для Grafana:

```text
admin / admin
```

## Проверка приложения

Проверить backend можно командой:

```bash
curl http://localhost/api/health
```

Ожидаемый ответ:

```json
{
  "service": "backend",
  "status": "ok"
}
```

## Проверка метрик

Проверить endpoint с метриками можно командой:

```bash
curl http://localhost/api/metrics
```

В ответе должны присутствовать строки:

```text
ai_text_helper_requests_total
ai_text_helper_tasks_created_total
ai_text_helper_request_duration_seconds
```

Для увеличения значения прикладной метрики можно создать задачу:

```bash
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"text":"привет это тестовый текст","mode":"improve"}'
```

После этого можно проверить метрику:

```bash
curl http://localhost/api/metrics | grep ai_text_helper_tasks_created
```

Пример результата:

```text
ai_text_helper_tasks_created_total{mode="improve"} 1.0
```

## Просмотр метрик в Grafana

1. Открыть Grafana:

```text
http://localhost:3000
```

2. Перейти в раздел **Explore**.

3. Выбрать источник данных:

```text
Mimir
```

4. Выполнить запрос:

```promql
ai_text_helper_tasks_created_total
```

Или запрос с группировкой по режимам:

```promql
sum by (mode) (ai_text_helper_tasks_created_total)
```

Также можно посмотреть количество HTTP-запросов:

```promql
ai_text_helper_requests_total
```

## Просмотр логов в Grafana

1. Открыть Grafana:

```text
http://localhost:3000
```

2. Перейти в раздел **Explore**.

3. Выбрать источник данных:

```text
Loki
```

4. Выполнить запрос для просмотра логов всех контейнеров:

```logql
{container=~".+"}
```

Для просмотра логов только backend-сервиса:

```logql
{container="ai_text_helper_backend"}
```

## Дашборд Grafana

В Grafana был создан дашборд для визуализации:

- прикладной метрики `ai_text_helper_tasks_created_total`;
- логов микросервисного приложения.

Для метрик используется источник данных **Mimir**.

Для логов используется источник данных **Loki**.

## Скриншоты

Скриншоты выполнения работы находятся в папке:

```text
screenshots/
```

Рекомендуемые скриншоты:

- запущенное приложение;
- endpoint `/api/metrics`;
- Grafana с метрикой из Mimir;
- Grafana с логами из Loki.

Пример структуры:

```text
screenshots/
├── app.png
├── metrics-endpoint.png
├── grafana-metrics.png
└── grafana-logs.png
```

## Остановка проекта

Для остановки проекта выполнить:

```bash
docker compose down
```

Если нужно удалить также volume с данными Grafana, Loki и Mimir:

```bash
docker compose down --volumes
```

## Вывод

В результате работы был настроен централизованный сбор логов и метрик для микросервисного приложения.

Backend публикует прикладные метрики через endpoint `/metrics`. Grafana Alloy собирает эти метрики и отправляет их в Grafana Mimir. Также Alloy собирает логи Docker-контейнеров и отправляет их в Loki.

В Grafana была настроена визуализация как прикладной метрики, так и логов микросервисного приложения.
