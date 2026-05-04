import os
import sqlite3
from datetime import datetime

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_PATH = os.getenv('FEEDBACK_DB_PATH', '/data/feedback.sqlite3')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')


def get_connection():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            '''
        )
        connection.commit()


def row_to_dict(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        'message': row['message'],
        'created_at': row['created_at'],
    }


def send_to_telegram(name, email, message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False, 'Telegram не настроен'

    text = (
        'Новое сообщение с сайта\n'
        f'Имя: {name}\n'
        f'Email: {email}\n'
        f'Сообщение: {message}'
    )

    try:
        response = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': text},
            timeout=2,
        )
        if response.ok:
            return True, ''
        return False, f'Telegram вернул статус {response.status_code}'
    except requests.RequestException as error:
        return False, str(error)


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'feedback-service'})


@app.post('/feedback')
def create_feedback():
    data = request.get_json(silent=True) or {}

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    if not name or not email or not message:
        return jsonify({'status': 'error', 'message': 'Заполните все поля'}), 400

    created_at = datetime.now().strftime('%d.%m.%Y %H:%M')

    with get_connection() as connection:
        cursor = connection.execute(
            'INSERT INTO feedbacks (name, email, message, created_at) VALUES (?, ?, ?, ?)',
            (name, email, message, created_at),
        )
        connection.commit()
        feedback_id = cursor.lastrowid

    telegram_sent, telegram_error = send_to_telegram(name, email, message)

    return jsonify({
        'status': 'ok',
        'saved_to_db': True,
        'telegram_sent': telegram_sent,
        'telegram_error': telegram_error,
        'feedback': {
            'id': feedback_id,
            'name': name,
            'email': email,
            'message': message,
            'created_at': created_at,
        },
    })


@app.get('/feedback/list')
def feedback_list():
    limit = request.args.get('limit', default=10, type=int)

    with get_connection() as connection:
        rows = connection.execute(
            'SELECT * FROM feedbacks ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()

    return jsonify({'feedbacks': [row_to_dict(row) for row in rows]})


@app.get('/feedback/by-email')
def feedback_by_email():
    email = (request.args.get('email') or '').strip()

    if not email:
        return jsonify({'feedbacks': []})

    with get_connection() as connection:
        rows = connection.execute(
            'SELECT * FROM feedbacks WHERE email = ? ORDER BY id DESC',
            (email,),
        ).fetchall()

    return jsonify({'feedbacks': [row_to_dict(row) for row in rows]})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)