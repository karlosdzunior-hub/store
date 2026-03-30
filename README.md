# Telegram Prediction Bot Generator

## Run

```bash
python main.py --age-group "18–25" --relationship single --focus money --photo --seed 42
```

## Modes

```bash
# Full bundle: free + paid + telegram payloads (default)
python main.py --age-group "18–25" --relationship single --focus money --mode bundle

# Flat JSON (legacy)
python main.py --age-group "18–25" --relationship single --focus money --mode single

# Only Telegram payloads
python main.py --age-group "18–25" --relationship single --focus money --mode telegram
```

Outputs ready-to-use JSON for Telegram integration. Telegram payloads include inline keyboards and Stars invoice templates (currency `XTR`).

## Bot (long polling)

Set environment variables:

```bash
set TELEGRAM_BOT_TOKEN=your_bot_token
set TELEGRAM_BOT_USERNAME=your_bot_username
set TELEGRAM_PROVIDER_TOKEN=
set BOT_DB_PATH=bot.sqlite3
```

For Telegram Stars (`XTR`) you can keep `TELEGRAM_PROVIDER_TOKEN` empty. If Telegram rejects invoices, set a valid provider token.

Run:

```bash
python bot.py
```

Send `!прогноз` in a group or `/start` in DM to trigger the flow.
Use `/history` in DM to see the last 3 forecasts.

## Storage

The bot stores user state, last paid payload, and history in SQLite (`BOT_DB_PATH`). It also avoids repeating the same template on the next forecast for the same user.
