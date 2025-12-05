# Postgres schema for InFocus

Файл `schema.sql` описывает минимальную схему хранения телеграм-новостей и артефактов обработки.

## Основные таблицы
- `telegram_channels` — список каналов с метаданными и флагом мониторинга.
- `raw_posts` — сырые посты (идемпотентность по `channel_id + source_message_id`).
- `media_assets` — вложения (фото/видео/документы) с параметрами файла.
- `post_links` — явные ссылки внутри поста (в т.ч. t.me).
- `enriched_posts` — результаты LLM-аннотации: заголовок, summary, теги, эмбеддинг.
- `duplicate_candidates` — кандидаты на дедупликацию по чек-сумме содержимого.
- `processing_queue` — лёгкая очередь задач для воркеров (аннотация/эмбеддинг/кластеризация).

## Особенности
- Включены расширения `uuid-ossp` и `vector` (для pgvector) — Postgres должен быть собран с pgvector.
- Индекс `ivfflat` на колонке `enriched_posts.embedding` ускоряет поиск схожих новостей.
- Триггеры автоматически обновляют `updated_at` при изменениях ключевых таблиц.

## Запуск локальной базы
1. Скопируйте пример переменных: `cp .env.example .env` и при необходимости обновите значения.
2. Запустите контейнер: `docker compose up -d postgres` (Docker Desktop/colima/wsl2 должны быть установлены).
3. Проверьте доступность: `psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB" -c "\dt"`.
4. При первом старте `schema.sql` применится автоматически через `docker-entrypoint-initdb.d`.

## Схема расширения
- Добавьте миграции в `db/migrations/` (например, с помощью sqitch/tern/flyway/alembic) — папка подключена в compose.
- Вносите изменения в `schema.sql` только для базовых таблиц; далее лучше использовать миграции.
