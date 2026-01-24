# 🚀 Инструкция по деплою на сервер

## Быстрый старт

### 1. Подключитесь к серверу

```bash
ssh root@176.120.21.138
# Пароль: 15051004
```

### 2. Первоначальная установка (только один раз!)

```bash
# Скачайте setup скрипт
curl -O https://raw.githubusercontent.com/PavelBelove/factorial_52/main/setup_server.sh

# Запустите установку
bash setup_server.sh
```

Скрипт попросит:
1. Добавить SSH ключ на GitHub (скопирует публичный ключ, откройте https://github.com/settings/keys)
2. Отредактировать `.env` файл - **ВАЖНО!** Вставьте ключи:
   ```bash
   nano /home/plexmem/plexmem/.env
   ```
   Замените:
   - `OPENROUTER_API_KEY=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`
   - `TELEGRAM_BOT_TOKEN=6602937806:AAFqIbi_sEkpHKJuWBkWLIAJY4Qf9l6Cyqc`

3. Подтвердить что DNS настроен (если еще нет - настройте у регистратора):
   - A запись: `@` → `176.120.21.138`
   - CNAME: `factorial` → `agints.ru`

### 3. Проверка работы

```bash
# Статус сервисов
sudo systemctl status plexmem-api plexmem-bot

# Логи
sudo journalctl -u plexmem-api -f
sudo journalctl -u plexmem-bot -f

# Или файловые логи
tail -f /home/plexmem/plexmem/logs/api.log
tail -f /home/plexmem/plexmem/logs/bot.log
```

### 4. Проверка работы бота

Откройте Telegram и найдите бота: `@factorial_52_bot`

Отправьте `/start`

## Обновление кода (после изменений)

```bash
ssh root@176.120.21.138
cd /home/plexmem/plexmem
./deploy.sh
```

Или вручную:
```bash
su - plexmem
cd ~/plexmem
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
exit

sudo systemctl restart plexmem-api plexmem-bot
```

## Полезные команды

```bash
# Перезапуск сервисов
sudo systemctl restart plexmem-api
sudo systemctl restart plexmem-bot

# Остановка
sudo systemctl stop plexmem-api plexmem-bot

# Логи в реальном времени
sudo journalctl -u plexmem-api -f
sudo journalctl -u plexmem-bot -f

# Проверка Nginx
sudo nginx -t
sudo systemctl reload nginx

# Обновление SSL сертификата (автоматически, но можно вручную)
sudo certbot renew

# Проверка портов
sudo netstat -tlnp | grep 8000
sudo lsof -i :8000

# Если порт занят
sudo fuser -k 8000/tcp
sudo systemctl restart plexmem-api

# Резервная копия базы
cp /home/plexmem/plexmem/data/plexmem.db /home/plexmem/plexmem/data/backup_$(date +%Y%m%d).db
```

## Мониторинг

```bash
# Использование диска
df -h

# Использование памяти
free -h

# Процессы Python
ps aux | grep python

# Размер базы
ls -lh /home/plexmem/plexmem/data/plexmem.db

# Размер логов
du -sh /home/plexmem/plexmem/logs/
```

## Endpoints

- **API**: https://factorial.agints.ru/
- **Health**: https://factorial.agints.ru/health
- **Docs**: https://factorial.agints.ru/docs
- **Bot**: https://t.me/factorial_52_bot

## Важно! ⚠️

1. **VPN (Amnesia) уже настроен на сервере** - не трогайте его конфигурацию
2. **Секреты в .env** - никогда не коммитить в git!
3. **Бекапы базы** - делать регулярно перед обновлениями
4. **Логи растут** - периодически чистить старые: `find logs/ -name "*.log" -mtime +30 -delete`

## Troubleshooting

**Проблема: Bot не запускается**
```bash
# Проверьте TELEGRAM_BOT_TOKEN в .env
cat /home/plexmem/plexmem/.env | grep TELEGRAM

# Проверьте логи
sudo journalctl -u plexmem-bot -n 50
```

**Проблема: API возвращает 500**
```bash
# Проверьте OPENROUTER_API_KEY
cat /home/plexmem/plexmem/.env | grep OPENROUTER

# Проверьте логи
tail -50 /home/plexmem/plexmem/logs/api.log
```

**Проблема: SSL не работает**
```bash
# Проверьте DNS
dig factorial.agints.ru

# Перевыпустите сертификат
sudo certbot --nginx -d factorial.agints.ru --force-renewal
```

**Проблема: База данных заблокирована**
```bash
# Остановите все сервисы
sudo systemctl stop plexmem-api plexmem-bot

# Подождите 5 секунд
sleep 5

# Запустите снова
sudo systemctl start plexmem-api plexmem-bot
```

## Структура на сервере

```
/home/plexmem/plexmem/
├── core/               # Код приложения
├── telegram/           # Telegram bot
├── data/               # База данных
│   └── plexmem.db
├── logs/               # Логи
│   ├── api.log
│   ├── bot.log
│   └── agents/         # Debug логи агентов (только в DEBUG режиме)
├── venv/               # Virtual environment
├── .env                # Секреты (НЕ в git!)
└── deploy.sh           # Скрипт обновления
```

## Контакты

- GitHub: https://github.com/PavelBelove/factorial_52
- Telegram: @pavel_belove

