# -*- coding: utf-8 -*-
import json
import os
import sqlite3
from pathlib import Path

from generator import ForecastInput, generate_bundle, build_free_text, build_paid_text
from telegram_api import TelegramAPI


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return value


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id INTEGER PRIMARY KEY,
                    age_group TEXT,
                    relationship TEXT,
                    focus TEXT,
                    photo INTEGER DEFAULT 0,
                    awaiting_photo INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_payload (
                    user_id INTEGER PRIMARY KEY,
                    payload_json TEXT,
                    updated_at TEXT DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    free_text TEXT,
                    paid_text TEXT,
                    meta_json TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
                """
            )

    def get(self, user_id: int) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM user_state WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if row is None:
                state = {
                    "age_group": None,
                    "relationship": None,
                    "focus": None,
                    "photo": False,
                    "awaiting_photo": False
                }
                self.save(user_id, state)
                return state
            return {
                "age_group": row["age_group"],
                "relationship": row["relationship"],
                "focus": row["focus"],
                "photo": bool(row["photo"]),
                "awaiting_photo": bool(row["awaiting_photo"])
            }

    def save(self, user_id: int, state: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_state (user_id, age_group, relationship, focus, photo, awaiting_photo, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    age_group = excluded.age_group,
                    relationship = excluded.relationship,
                    focus = excluded.focus,
                    photo = excluded.photo,
                    awaiting_photo = excluded.awaiting_photo,
                    updated_at = datetime('now')
                """,
                (
                    user_id,
                    state.get("age_group"),
                    state.get("relationship"),
                    state.get("focus"),
                    1 if state.get("photo") else 0,
                    1 if state.get("awaiting_photo") else 0
                )
            )

    def set_payload(self, user_id: int, payload: dict) -> None:
        payload_json = json.dumps(payload, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_payload (user_id, payload_json, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at = datetime('now')
                """,
                (user_id, payload_json)
            )

    def get_payload(self, user_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM user_payload WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if row is None:
                return None
            return json.loads(row["payload_json"])

    def add_history(self, user_id: int, free_text: str, paid_text: str, meta: dict) -> None:
        meta_json = json.dumps(meta, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_history (user_id, free_text, paid_text, meta_json, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (user_id, free_text, paid_text, meta_json)
            )


def _build_group_prompt(bot_username: str) -> dict:
    url = TelegramAPI.deep_link(bot_username, "forecast")
    return {
        "message": "Хочешь, я загляну в твою линию событий? Нажми кнопку и не делай вид, что тебе всё равно.",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Открыть прогноз", "url": url}]
            ]
        }
    }


def _build_questions() -> dict:
    return {
        "text": "Давай по-честному. Ответь быстро — я не люблю ждать.",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "до 18", "callback_data": "age:до 18"},
                 {"text": "18–25", "callback_data": "age:18–25"},
                 {"text": "25+", "callback_data": "age:25+"}],
                [{"text": "single", "callback_data": "rel:single"},
                 {"text": "taken", "callback_data": "rel:taken"}],
                [{"text": "💰 Деньги", "callback_data": "focus:money"},
                 {"text": "❤️ Любовь", "callback_data": "focus:love"},
                 {"text": "🚀 Карьера", "callback_data": "focus:career"}],
                [{"text": "Загрузить фото", "callback_data": "photo:upload"},
                 {"text": "Пропустить", "callback_data": "photo:skip"}]
            ]
        }
    }


def _build_free_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Открыть полный прогноз – 49⭐", "callback_data": "pay:full_49"}],
            [{"text": "Поделиться в чат", "callback_data": "share:!прогноз"},
             {"text": "Пропустить / позже", "callback_data": "skip:later"}],
            [{"text": "📍 Узнать детали – 99⭐", "callback_data": "pay:details_99"},
             {"text": "Ежедневный прогноз – 199⭐ / неделя", "callback_data": "pay:daily_199"}]
        ]
    }


def _build_paid_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "📍 Узнать детали – 99⭐", "callback_data": "pay:details_99"},
             {"text": "Ежедневный прогноз – 199⭐ / неделя", "callback_data": "pay:daily_199"}]
        ]
    }


def _build_payments() -> dict:
    return {
        "full_49": {
            "title": "Полный прогноз",
            "description": "Полное раскрытие: даты, буквы, предупреждения.",
            "payload": "pay_full_49",
            "currency": "XTR",
            "prices": [{"label": "49⭐", "amount": 49}]
        },
        "details_99": {
            "title": "Детали прогноза",
            "description": "Подробности: точные даты и тактика.",
            "payload": "pay_details_99",
            "currency": "XTR",
            "prices": [{"label": "99⭐", "amount": 99}]
        },
        "daily_199": {
            "title": "Ежедневный прогноз",
            "description": "7 дней: ежедневные короткие прогнозы.",
            "payload": "pay_daily_199",
            "currency": "XTR",
            "prices": [{"label": "199⭐", "amount": 199}]
        }
    }


def _ready_to_generate(state: dict) -> bool:
    return bool(state["age_group"] and state["relationship"] and state["focus"] and not state.get("awaiting_photo"))


def _handle_message(api: TelegramAPI, store: SQLiteStore, message: dict, bot_username: str) -> None:
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user = message.get("from", {})
    user_id = user.get("id")
    text = message.get("text")

    if not chat_id or not user_id:
        return

    state = store.get(user_id)

    if message.get("photo") and state.get("awaiting_photo"):
        state["photo"] = True
        state["awaiting_photo"] = False
        store.save(user_id, state)
        if _ready_to_generate(state):
            _send_forecast(api, store, chat_id, user_id, state)
        else:
            api.send_message(chat_id, "Фото принято. Теперь выбери возраст, отношения и фокус.")
        return

    if text in ("/start", "!прогноз"):
        if chat.get("type") in ("group", "supergroup"):
            prompt = _build_group_prompt(bot_username)
            api.send_message(chat_id, prompt["message"], prompt["reply_markup"])
        else:
            questions = _build_questions()
            api.send_message(chat_id, questions["text"], questions["reply_markup"])
        return


def _send_forecast(api: TelegramAPI, store: SQLiteStore, chat_id: int, user_id: int, state: dict) -> None:
    data = ForecastInput(
        age_group=state["age_group"],
        relationship=state["relationship"],
        focus=state["focus"],
        photo=state.get("photo", False)
    )
    payload = generate_bundle(data)
    store.set_payload(user_id, payload["paid"])

    free_text = build_free_text({
        "psych": payload["free"]["psych"],
        "situation": payload["free"]["situation"],
        "event": payload["free"]["event"],
        "intrigue": payload["free"]["intrigue"],
        "live_insertions": payload["free"]["live_insertions"],
        "meta": payload["paid"]["meta"]
    })
    paid_text = build_paid_text(payload["paid"])

    store.add_history(user_id, free_text, paid_text, payload["paid"]["meta"])
    api.send_message(chat_id, free_text, _build_free_keyboard())


def _handle_callback(api: TelegramAPI, store: SQLiteStore, callback: dict, provider_token: str) -> None:
    data = callback.get("data", "")
    callback_id = callback.get("id")
    message = callback.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user = callback.get("from", {})
    user_id = user.get("id")
    if not chat_id or not user_id:
        return

    state = store.get(user_id)

    if data.startswith("share:"):
        if callback_id:
            api.answer_callback_query(callback_id, "Вбей !прогноз в чате — и поехали.")
        return
    if data.startswith("skip:"):
        if callback_id:
            api.answer_callback_query(callback_id, "Ок, позже так позже.")
        return

    if data.startswith("age:"):
        state["age_group"] = data.split(":", 1)[1]
    elif data.startswith("rel:"):
        state["relationship"] = data.split(":", 1)[1]
    elif data.startswith("focus:"):
        state["focus"] = data.split(":", 1)[1]
    elif data == "photo:upload":
        state["awaiting_photo"] = True
        store.save(user_id, state)
        api.send_message(chat_id, "Окей, кидай фото. Я посмотрю и усилю эффект.")
        return
    elif data == "photo:skip":
        state["photo"] = False
    elif data.startswith("pay:"):
        key = data.split(":", 1)[1]
        payments = _build_payments()
        if key in payments:
            pay = payments[key]
            api.send_invoice(
                chat_id=chat_id,
                title=pay["title"],
                description=pay["description"],
                payload=pay["payload"],
                currency=pay["currency"],
                prices=pay["prices"],
                provider_token=provider_token
            )
        return

    if callback_id:
        api.answer_callback_query(callback_id)

    if _ready_to_generate(state):
        store.save(user_id, state)
        _send_forecast(api, store, chat_id, user_id, state)
    else:
        store.save(user_id, state)


def _handle_pre_checkout(api: TelegramAPI, pre_checkout: dict) -> None:
    query_id = pre_checkout.get("id")
    if not query_id:
        return
    api.answer_pre_checkout_query(query_id, ok=True)


def _handle_successful_payment(api: TelegramAPI, store: SQLiteStore, message: dict) -> None:
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    user = message.get("from", {})
    user_id = user.get("id")
    if not chat_id or not user_id:
        return

    payload = store.get_payload(user_id)
    if not payload:
        api.send_message(chat_id, "Оплата прошла. Напиши /start, и я перегенерирую детали.")
        return

    paid_text = build_paid_text(payload)
    if not paid_text:
        paid_text = "Оплата прошла. Детали скоро будут."
    api.send_message(chat_id, paid_text, _build_paid_keyboard())


def run():
    token = _env("TELEGRAM_BOT_TOKEN")
    bot_username = _env("TELEGRAM_BOT_USERNAME")
    provider_token = os.getenv("TELEGRAM_PROVIDER_TOKEN", "")
    db_path = os.getenv("BOT_DB_PATH", "bot.sqlite3")

    api = TelegramAPI(token)
    store = SQLiteStore(db_path)

    offset = None
    while True:
        updates = api.get_updates(offset=offset, timeout=20)
        for upd in updates:
            offset = upd["update_id"] + 1
            if "message" in upd:
                msg = upd["message"]
                if "successful_payment" in msg:
                    _handle_successful_payment(api, store, msg)
                else:
                    _handle_message(api, store, msg, bot_username)
            elif "callback_query" in upd:
                _handle_callback(api, store, upd["callback_query"], provider_token)
            elif "pre_checkout_query" in upd:
                _handle_pre_checkout(api, upd["pre_checkout_query"])

        TelegramAPI.sleep(0.4)


if __name__ == "__main__":
    run()
