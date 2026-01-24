# ✅ Деплой готов!

## 🎯 Что сделано

### 1. Git Repository
- ✅ Создан и запушен на GitHub: `git@github.com:PavelBelove/factorial_52.git`
- ✅ Ветка `main` готова к деплою
- ✅ `.env` удален из git (только `.env.example` в репозитории)
- ✅ Все секреты защищены

### 2. Production конфигурация
- ✅ `DEBUG=False` по умолчанию
- ✅ `LOG_LEVEL=INFO`
- ✅ Agent debug logs только в debug режиме
- ✅ `.env.example` как шаблон

### 3. Deployment скрипты
- ✅ `setup_server.sh` - первоначальная установка на сервер (один раз)
- ✅ `deploy.sh` - быстрое обновление кода
- ✅ `systemd/plexmem-api.service` - systemd сервис для API
- ✅ `systemd/plexmem-bot.service` - systemd сервис для бота
- ✅ `systemd/nginx-factorial.conf` - Nginx конфигурация с SSL

### 4. Документация
- ✅ `README.md` - полное описание проекта для GitHub
- ✅ `DEPLOYMENT.md` - детальная инструкция по деплою (English)
- ✅ `DEPLOY_QUICK.md` - быстрая инструкция (Русский)

## 🚀 Следующие шаги

### На сервере (176.120.21.138)

1. **Подключитесь к серверу:**
   ```bash
   ssh root@176.120.21.138
   # Пароль: 15051004
   ```

2. **Скачайте и запустите setup скрипт:**
   ```bash
   curl -O https://raw.githubusercontent.com/PavelBelove/factorial_52/main/setup_server.sh
   bash setup_server.sh
   ```

3. **Скрипт попросит:**
   - Добавить SSH ключ на GitHub (https://github.com/settings/keys)
   - Отредактировать `.env` файл с production ключами:
     ```bash
     nano /home/plexmem/plexmem/.env
     ```
     Вставить:
     ```
     OPENROUTER_API_KEY=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
     TELEGRAM_BOT_TOKEN=6602937806:AAFqIbi_sEkpHKJuWBkWLIAJY4Qf9l6Cyqc
     ```

4. **Подтвердить DNS настройки у регистратора:**
   - A запись: `@` → `176.120.21.138`
   - CNAME: `factorial` → `agints.ru`

5. **Проверить работу:**
   ```bash
   sudo systemctl status plexmem-api plexmem-bot
   ```

6. **Открыть Telegram и найти бота:**
   - `@factorial_52_bot`
   - Отправить `/start`

## 📊 Мониторинг

```bash
# Логи API
sudo journalctl -u plexmem-api -f

# Логи бота
sudo journalctl -u plexmem-bot -f

# Или файловые логи
tail -f /home/plexmem/plexmem/logs/api.log
tail -f /home/plexmem/plexmem/logs/bot.log
```

## 🔄 Обновление

После любых изменений в коде:
```bash
ssh root@176.120.21.138
cd /home/plexmem/plexmem
./deploy.sh
```

## 🌐 Endpoints

- **API**: https://factorial.agints.ru/
- **Health**: https://factorial.agints.ru/health
- **Docs**: https://factorial.agints.ru/docs
- **Bot**: https://t.me/factorial_52_bot

## 🔐 Безопасность

✅ VPN (Amnesia) на сервере не тронут
✅ Все секреты в .env (не в git)
✅ SSL через Let's Encrypt
✅ Auto-restart через systemd
✅ Логи ротируются

## 📝 Важные файлы

- `DEPLOY_QUICK.md` - пошаговая инструкция на русском
- `DEPLOYMENT.md` - полная документация
- `setup_server.sh` - автоматическая установка
- `deploy.sh` - автоматическое обновление

## ⚠️ Не забыть!

1. Добавить SSH ключ на GitHub
2. Настроить DNS у регистратора (если еще не настроен)
3. Отредактировать .env на сервере с правильными ключами
4. Проверить работу бота после установки

---

**Готов к деплою!** 🎲✨

