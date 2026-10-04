# Лабораторная 7. Monitoring

Автор: Скляров Константин Александрович, группа РИМ-150975к.
Проект: https://github.com/dyda5505-cloud/textlab-course. Полный комплект файлов находится в этом каталоге.

Backend публикует /metrics: прикладной counter textlab_jobs_submitted_total
показывает число принятых заданий, gauge textlab_jobs{status} — распределение
заданий по статусам queued/running/done/failed.
Prometheus собирает метрики каждые 5 секунд; выбран вместо рекомендованного Mimir
для компактного локального стенда. Alloy собирает логи помеченных контейнеров
через Docker API и отправляет в Loki. Grafana получает обе datasource и dashboard
TextLab через provisioning. Панели показывают счётчик, скорость поступления
заданий, статусы очереди и журналы API/worker.

В комплекте для Practice107 включён compose.override.yaml, поэтому запуск:
`docker compose up --build`. Приложение: http://localhost:8080;
Grafana: http://localhost:3000, гостевой просмотр для локального учебного стенда.

Фактическая проверка на Ubuntu runner: https://github.com/dyda5505-cloud/textlab-course/actions/runs/37193914473, job monitoring.
Стенд поднялся; проверены выполнение задания, метрика в Prometheus,
логи в Loki, доступность Grafana и provisioned dashboard через API.
Проверка tools/monitoring_smoke.py завершилась успешно.
Вывод: метрики показывают состояние очереди, централизованные логи позволяют
проследить принятие и завершение задания по id.
