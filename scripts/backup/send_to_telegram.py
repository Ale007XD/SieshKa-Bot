#!/usr/bin/env python3
"""Send backup to Telegram."""

import sys
import os
import asyncio
import aiohttp

from app.config import settings


async def send_backup_to_telegram(backup_path: str, file_size_mb: int):
    """Send backup file to Telegram."""
    chat_id = settings.backup_tg_chat_id
    thread_id = settings.backup_tg_thread_id
    max_size_mb = settings.backup_max_tg_mb
    
    if not chat_id:
        print("BACKUP_TG_CHAT_ID not set, skipping Telegram notification")
        return
    
    # Validate path is within backup directory (security check)
    backup_dir = os.path.abspath(settings.backup_dir)
    file_path = os.path.abspath(backup_path)
    if not file_path.startswith(backup_dir):
        raise ValueError(f"Invalid backup path: {backup_path}")
    
    # Check file size
    if file_size_mb > max_size_mb:
        print(f"Backup file too large ({file_size_mb} MB > {max_size_mb} MB)")
        # Send alert text instead
        await send_alert_text(chat_id, thread_id, backup_path, file_size_mb)
        return
    
    # Send file
    try:
        await send_document(chat_id, thread_id, backup_path, file_size_mb)
        print(f"Backup sent to Telegram successfully")
    except Exception as e:
        print(f"Failed to send backup to Telegram: {e}")
        # Send alert as fallback
        await send_alert_text(chat_id, thread_id, backup_path, file_size_mb, error=str(e))


async def send_document(chat_id: str, thread_id: int, file_path: str, file_size_mb: int):
    """Send document via Telegram Bot API."""
    bot_token = settings.bot_token
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    filename = os.path.basename(file_path)
    caption = f"📁 <b>Бэкап базы данных</b>\n\n"
    caption += f"Файл: <code>{filename}</code>\n"
    caption += f"Размер: {file_size_mb} MB\n"
    caption += f"Дата: {filename.split('_')[1]}"
    
    # Read file content to ensure it's properly closed before async operations
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    data = aiohttp.FormData()
    data.add_field('chat_id', chat_id)
    data.add_field('caption', caption)
    data.add_field('parse_mode', 'HTML')
    
    if thread_id:
        data.add_field('message_thread_id', str(thread_id))
    
    data.add_field('document', file_content, filename=filename)
    
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                result = await response.json()
                raise Exception(f"Telegram API error: {result}")


async def send_alert_text(chat_id: str, thread_id: int, file_path: str, file_size_mb: int, error: str = None):
    """Send alert text when file is too large."""
    bot_token = settings.bot_token
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    filename = os.path.basename(file_path)
    
    if error:
        text = f"⚠️ <b>Бэкап завершен с ошибкой отправки</b>\n\n"
        text += f"Ошибка: {error}\n"
    else:
        text = f"⚠️ <b>Бэкап завершен</b>\n\n"
    
    text += f"Файл: <code>{filename}</code>\n"
    text += f"Размер: {file_size_mb} MB\n\n"
    text += f"Файл слишком большой для отправки в Telegram. Хранится локально."
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if thread_id:
        payload['message_thread_id'] = str(thread_id)
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                print(f"Failed to send alert: {await response.text()}")


def main():
    if len(sys.argv) < 3:
        print("Usage: send_to_telegram.py <backup_path> <file_size_mb>")
        sys.exit(1)
    
    backup_path = sys.argv[1]
    file_size_mb = int(sys.argv[2])
    
    asyncio.run(send_backup_to_telegram(backup_path, file_size_mb))


if __name__ == "__main__":
    main()
