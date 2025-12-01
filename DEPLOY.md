# Установка и запуск через Docker

Самый простой и удобный способ запустить трекер — использовать Docker.

## Предварительные требования

* Сервер с установленными Docker и Docker Compose.

Если Docker еще не установлен:

```bash
# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose-plugin
```

## Установка и запуск

1. **Скопируйте файлы на сервер**
   
   Вам понадобятся файлы:
   * `docker-compose.yml`
   * `Dockerfile` (и все файлы исходного кода: `app.py`, `database.py`, `requirements.txt`, папки `templates` и `static`)

   Вы можете просто склонировать репозиторий:
   
   ```bash
   git clone <ссылка_на_ваш_репозиторий> smoking_tracker
   cd smoking_tracker
   ```

2. **Запустите приложение**

   ```bash
   sudo docker compose up -d --build
   ```
   
   Эта команда соберет образ и запустит контейнер в фоновом режиме.
   
   * Приложение будет доступно на порту `5000`.
   * Данные (база данных) будут сохраняться в папке `data` внутри текущей директории, так что при перезапуске данные не пропадут.

3. **Проверка работы**

   Откройте в браузере `http://<IP-вашего-сервера>:5000`

## Настройка Nginx (Рекомендуется)

Чтобы использовать доменное имя и стандартный порт 80/443, настройте Nginx как прокси.

1. Установите Nginx: `sudo apt install nginx`
2. Создайте конфиг `/etc/nginx/sites-available/smoking_tracker`:

   ```nginx
   server {
       listen 80;
       server_name ваш_домен.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
3. Активируйте:
   ```bash
   sudo ln -s /etc/nginx/sites-available/smoking_tracker /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Обновление

Чтобы обновить код:
1. `git pull`
2. `sudo docker compose up -d --build`
