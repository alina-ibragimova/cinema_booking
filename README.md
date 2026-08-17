# Cinema Booking API

Асинхронный REST API для системы бронирования билетов в кинотеатр.

## Возможности

- Регистрация и авторизация пользователей (JWT)
- Просмотр карты мест в реальном времени
- Управление структурой кинотеатра (залы, ряды, места) и расписанием сеансов
- Создание фильмов, сеансов и залов
- Простой веб-интерфейс
- Автоматическое снятие брони по истечении тайм-аута при бездействии пользователя

## Технологии

- **FastAPI** — фреймворк
- **Redis** — хранилище для временной блокировки мест
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **Pydantic** — валидация данных
- **JWT** — авторизация
- **Docker + docker-compose** — запуск
- **pytest** — тестирование

<p align="center">
  <img src="screenshots/image1.png" width="1000">
  <br><em>Начальный экран</em>
</p>
<p align="center">
  <img src="screenshots/image2.png" width="1000">
  <br><em>Экран входа / регистрации с ошибкой</em>
</p>
<p align="center">
  <img src="screenshots/image3.png" width="1000">
  <br><em>Страница с выбором места</em>
</p>
<p align="center">
  <img src="screenshots/image4.png" width="1000">
  <br><em>Успешная бронь места</em>
</p>
<p align="center">
  <img src="screenshots/image5.png" width="1000">
  <br><em>Список с отмененным билетом</em>
</p>
<p align="center">
  <img src="screenshots/image6.png" width="1000">
  <br><em>Документация</em>
</p>
<p align="center">
  <img src="screenshots/image7.png" width="1000">
  <br><em>Документация</em>
</p>
<p align="center">
  <img src="screenshots/image8.png" width="1000">
  <br><em>Документация</em>
</p>