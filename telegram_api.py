# -*- coding: utf-8 -*-
import json
import time
import urllib.parse
import urllib.request


class TelegramAPI:
    def __init__(self, token: str):
        self._token = token
        self._base = f"https://api.telegram.org/bot{token}/"

    def _request(self, method: str, payload: dict | None = None) -> dict:
        url = self._base + method
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
        result = json.loads(raw)
        if not result.get("ok"):
            raise RuntimeError(f"Telegram API error: {result}")
        return result["result"]

    def get_updates(self, offset: int | None = None, timeout: int = 20) -> list:
        payload = {"timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        return self._request("getUpdates", payload)

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> dict:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._request("sendMessage", payload)

    def edit_message_reply_markup(self, chat_id: int, message_id: int, reply_markup: dict | None = None) -> dict:
        payload = {"chat_id": chat_id, "message_id": message_id}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._request("editMessageReplyMarkup", payload)

    def send_invoice(self, chat_id: int, title: str, description: str, payload: str,
                     currency: str, prices: list, provider_token: str = "") -> dict:
        data = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "currency": currency,
            "prices": prices,
            "provider_token": provider_token
        }
        return self._request("sendInvoice", data)

    def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool = True,
                                  error_message: str | None = None) -> dict:
        payload = {"pre_checkout_query_id": pre_checkout_query_id, "ok": ok}
        if error_message:
            payload["error_message"] = error_message
        return self._request("answerPreCheckoutQuery", payload)

    def answer_callback_query(self, callback_query_id: str, text: str | None = None) -> dict:
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self._request("answerCallbackQuery", payload)

    @staticmethod
    def deep_link(bot_username: str, start_payload: str = "forecast") -> str:
        payload = urllib.parse.quote(start_payload)
        return f"https://t.me/{bot_username}?start={payload}"

    @staticmethod
    def sleep(seconds: float) -> None:
        time.sleep(seconds)
