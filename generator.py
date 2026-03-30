# -*- coding: utf-8 -*-
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta

AGE_GROUPS = ["до 18", "18–25", "25+"]
RELATIONSHIPS = ["single", "taken"]
FOCUSES = ["money", "love", "career"]

BUTTONS = {
    "start_chat": ["!прогноз", "/start"],
    "questions": [
        "до 18", "18–25", "25+",
        "single", "taken",
        "💰 Деньги", "❤️ Любовь", "🚀 Карьера",
        "Загрузить фото", "Пропустить"
    ],
    "free_to_paid": [
        "Открыть полный прогноз – 49⭐",
        "Поделиться в чат",
        "Пропустить / позже"
    ],
    "upsell": [
        "📍 Узнать детали – 99⭐",
        "Ежедневный прогноз – 199⭐ / неделя"
    ]
}

LIVE_INSERTIONS = [
    "Не говори, что я тебя не предупреждал.",
    "Ха, думал будет легко?",
    "Серьёзно, готовься к этому.",
    "Я не злюсь. Просто знаю больше.",
    "Сейчас будет момент истины.",
    "Да-да, именно это ты и ждал.",
    "Запомни этот момент, потом пригодится.",
    "Ты бы удивился, как часто я прав.",
    "Не спорь со мной, спорь с судьбой."
]

PSYCH_TEMPLATES = [
    ("Ты из тех, кто делает вид, что всё под контролем, а внутри — стратег с легкой паранойей. Возраст: {age_group}, статус: {relationship}. Ты умеешь быть {tone}, особенно когда речь о {focus_emoji}.", 3),
    ("Снаружи — спокойствие, внутри — вечный просчёт ходов. {age_group} и {relationship} — значит, ты уже знаешь цену вниманию. Твой радар на {focus_emoji} всегда включён.", 2),
    ("Ты не наивный романтик и не робот. Ты тот, кто проверяет и перепроверяет. {age_group}, {relationship} — у тебя своя логика, и она часто выигрывает. {focus_emoji} для тебя — не игрушка.", 2),
    ("Ты умеешь улыбаться так, будто всё ок, но внутри у тебя план из трёх шагов. {age_group}, {relationship} — и ты явно не из тех, кого легко обвести. {focus_emoji} для тебя важнее пафоса.", 2),
    ("Ты гибрид аналитика и игрока. {age_group}, {relationship} — значит, ты уже видел пару сценариев, где люди теряют контроль. Ты не из них.", 2),
    ("Ты не любишь, когда тебя читают как открытую книгу. {age_group}, {relationship} — и ты умеешь прятать карты. {focus_emoji} для тебя — территория, а не игра.", 2),
    ("Ты выглядишь расслабленным, но у тебя всегда есть запасной ход. {age_group}, {relationship} — это не про наивность, а про опыт. {focus_emoji} держит тебя в тонусе.", 2),
    ("Ты тот, кто замечает мелочи и вытаскивает из них пользу. {age_group}, {relationship} — и ты уже знаешь, что слабость — это роскошь. {focus_emoji} — твоя валюта.", 2),
    ("Ты умеешь резать лишнее без жалости. {age_group}, {relationship} — ты давно понял, что мягкость хороша только дозированно. {focus_emoji} это подтверждает.", 2),
    ("Ты чувствуешь, кто рядом по делу, а кто по шуму. {age_group}, {relationship} — и ты давно не веришь в случайности.", 1),
    ("Ты читаешь людей быстрее, чем они читают себя. {age_group}, {relationship} — и это твой внутренний щит.", 1),
    ("Ты не ищешь лёгких путей — ты ищешь правильные. {age_group}, {relationship} — ты уже видел, как ошибаются другие.", 1),
    ("Ты умеешь быть милым, но только до тех пор, пока это выгодно. {age_group}, {relationship} — и ты не скрываешь это.", 1),
    ("Ты знаешь цену словам, поэтому часто молчишь. {age_group}, {relationship} — и это работает на тебя.", 1),
    ("Ты спокойно смотришь на хаос и наводишь порядок. {age_group}, {relationship} — такой у тебя стиль выживания.", 1),
    ("Ты не терпишь слабых оправданий — ни у других, ни у себя. {age_group}, {relationship} — и это тебя усиливает.", 1),
    ("Ты привык держать дистанцию, пока не увидишь выгоду. {age_group}, {relationship} — и это делает тебя опасным соперником.", 1),
    ("Ты можешь быть дружелюбным, но дружба для тебя — это контракт. {age_group}, {relationship} — и ты это знаешь.", 1),
    ("Ты не любишь хаос, но умеешь из него выжать выгоду. {age_group}, {relationship} — ты умеешь держать форму.", 1),
    ("Ты не терпишь шумных обещаний — тебе нужны факты. {age_group}, {relationship} — и это твой фильтр.", 1),
    ("Ты умеешь казаться мягким, но внутри у тебя сталь. {age_group}, {relationship} — это читается.", 1),
    ("Ты редко просишь помощи, потому что привык рассчитывать на себя. {age_group}, {relationship} — и это твоя сила.", 1),
    ("Ты не ведёшься на дешёвую драму. {age_group}, {relationship} — ты ценишь спокойствие и результат.", 1),
    ("Ты видишь слабые места раньше других. {age_group}, {relationship} — и это даёт тебе преимущество.", 1),
    ("Ты умеешь быть жёстким, но справедливым. {age_group}, {relationship} — поэтому к тебе тянутся.", 1),
    ("Ты часто думаешь наперёд, и это спасает тебя. {age_group}, {relationship} — ты стратег, не наблюдатель.", 1),
    ("Ты не любишь, когда тебя торопят — ты сам выбираешь темп. {age_group}, {relationship} — и это видно.", 1),
    ("Ты привык держать маску, но внутри живёт голод к {focus_emoji}. {age_group}, {relationship}.", 1),
    ("Ты видишь чужие мотивы и редко ошибаешься. {age_group}, {relationship} — твоя интуиция не спит.", 1),
    ("Ты давно понял, что доверие — это ресурс. {age_group}, {relationship} — ты распоряжаешься им аккуратно.", 1)
]

SITUATION_TEMPLATES = [
    ("Сейчас у тебя фаза «топлю вперёд, но что-то держит». Это {tone} и немного мистично: как пауза перед рывком.", 3),
    ("Текущая ситуация похожа на затишье, но это не пустота, а подготовка. Вибрация {tone}: будто мир набирает обороты.", 2),
    ("Ты между двумя дверями: одну уже прикрыл, вторую ещё не открыл. Атмосфера {tone}, и да, это не случайно.", 2),
    ("Ты пока не видишь всех деталей, и это нормально. {tone} здесь в том, что тишина — просто маска для движения.", 2),
    ("Энергия странная: будто всё на паузе, но на самом деле кто-то уже готовит следующий ход.", 2),
    ("Сейчас у тебя режим «держу спину ровно», хотя внутри кипит. {tone} ощущается как напряжение перед прыжком.", 2),
    ("Текущая точка — не конец и не старт, а развилка. {tone} здесь в том, что выбор уже подсвечен.", 2),
    ("Ты чувствуешь, что что-то созревает, но не видишь сроков. Это {tone} ожидание с правильной тревогой.", 2),
    ("Ситуация не шумная, но плотная: если смотреть внимательно, всё уже движется.", 2),
    ("Твои дела будто стоят, но под капотом всё греется. {tone} здесь про скрытую скорость.", 1),
    ("Слишком много знаков совпадает, чтобы это было случайно. {tone} включён на полную.", 1),
    ("Кто-то рядом ждёт твоего шага, и это чувствуется. {tone} в воздухе заметно.", 1),
    ("Ты держишь план при себе — и правильно. Сейчас это решает.", 1),
    ("Ситуация похожа на шахматы: ход не шумный, но ключевой.", 1),
    ("Сейчас важно не ускоряться, а точнее выбирать направление. {tone} подсказывает это.", 1),
    ("Ты на границе нового витка, и это ощущается в каждом решении.", 1),
    ("Пауза не означает слабость — это подготовка к рывку. {tone} прямо об этом.", 1),
    ("Тишина вокруг — редкий шанс выстроить сильный ход.", 1),
    ("Сейчас важнее наблюдать, чем шуметь. {tone} помогает держать дистанцию.", 1),
    ("Ты словно накапливаешь энергию — потом выстрелишь. {tone} это подтверждает.", 1),
    ("Вокруг много суеты, но ты держишься отдельно. {tone} здесь — твой фильтр.", 1),
    ("Ситуация просит холодной головы, и у тебя она есть. {tone} на твоей стороне.", 1),
    ("Ты чувствуешь, что тебя тестируют. {tone} подсказывает, что это не случайно.", 1),
    ("Сейчас не время рубить с плеча. {tone} и пауза — правильный ход.", 1),
    ("Ты близко к решению, но не показываешь это. {tone} держит интригу.", 1),
    ("События сжимаются, и скоро будет выдох. {tone} намекает на кульминацию.", 1),
    ("Ты как будто в тумане, но шаги слышны. {tone} говорит: смотри внимательно.", 1),
    ("Тебя окружают люди, но ты один на один со своим выбором. {tone} усиливает это.", 1),
    ("Сейчас не время для лишних слов, время для точных движений. {tone} это поддерживает.", 1),
    ("Мир проверяет тебя на выдержку, и ты её показываешь.", 1)
]

EVENT_TEMPLATES = [
    ("Ключевой момент: через {days_low}–{days_high} дней появится человек с инициативой. В имени может быть буква «{initial}». Он принесёт вариант, который сначала покажется мелочью — но это рычаг.", 3),
    ("Событие: в диапазоне {days_low}–{days_high} дней всплывёт предложение, которое ты не ждал. Буква «{initial}» будет как подсказка на обложке.", 2),
    ("Событие: в ближайшие {days_low}–{days_high} дней ты получишь знак — сообщение, встречу или подработку. Имя с «{initial}» проскочит не просто так.", 2),
    ("Событие: на горизонте {days_low}–{days_high} дней всплывёт шанс, который выглядит буднично. Это ловушка только для невнимательных.", 2),
    ("Ключевой момент: кто-то попробует сыграть слишком резко. В имени — «{initial}», а в голове — быстрый ход.", 2),
    ("Событие: через {days_low}–{days_high} дней ты получишь предложение с подвохом. Буква «{initial}» будет подсказкой, но решать всё равно тебе.", 2),
    ("Ключевой момент: к тебе вернётся тема, которую ты считал закрытой. Имя с «{initial}» всплывёт как знак.", 2),
    ("Событие: в ближайшие {days_low}–{days_high} дней появится шанс, где важно не торговаться, а диктовать правила.", 2),
    ("Ключевой момент: в окно возможностей влетит человек с буквой «{initial}». Он принесёт риск, но и пользу.", 2),
    ("Событие: в ближайшие {days_low}–{days_high} дней от тебя потребуют ясного ответа. Буква «{initial}» будет рядом.", 1),
    ("Ключевой момент: ты услышишь фразу, которая изменит решение. Имя с «{initial}» — не случайность.", 1),
    ("Событие: в ближайшие {days_low}–{days_high} дней появится выгода, если не спешить.", 1),
    ("Ключевой момент: ты получишь предложение, где важно сказать «нет» первому пункту.", 1),
    ("Событие: кто-то попробует вернуть старый долг. Буква «{initial}» даст подсказку.", 1),
    ("Ключевой момент: появится контакт, который откроет дверь. В имени — «{initial}».", 1),
    ("Событие: шанс придёт через знакомого знакомого. Буква «{initial}» — метка.", 1),
    ("Ключевой момент: ты увидишь, кто играет против. Имя с «{initial}» выдаст его.", 1),
    ("Событие: в ближайшие {days_low}–{days_high} дней всплывёт ситуация, где победит тот, кто выдержит паузу.", 1),
    ("Событие: в ближайшие {days_low}–{days_high} дней появится повод пересмотреть договорённости. Буква «{initial}» мелькнёт в переписке.", 1),
    ("Ключевой момент: ты услышишь «да», но с условием. Имя с «{initial}» будет ключом.", 1),
    ("Событие: кто-то предложит быстрый ход, но выиграет тот, кто выдержит паузу.", 1),
    ("Ключевой момент: в ближайшие {days_low}–{days_high} дней ты получишь сообщение, которое нельзя игнорировать.", 1),
    ("Событие: шанс появится в неудобное время — и именно поэтому он настоящий.", 1),
    ("Ключевой момент: ты столкнёшься с проверкой на лояльность. Имя с «{initial}» рядом.", 1),
    ("Событие: в ближайшие {days_low}–{days_high} дней появится партнёр, который захочет играть по своим правилам.", 1),
    ("Ключевой момент: ты увидишь скрытый интерес там, где раньше было ровно.", 1),
    ("Событие: предложение придёт через посредника. Буква «{initial}» будет в его имени.", 1),
    ("Ключевой момент: тебе предложат выбор между выгодой и комфортом — и тут важно не дрогнуть.", 1),
    ("Событие: в ближайшие {days_low}–{days_high} дней всплывёт старый контакт с новым смыслом.", 1),
    ("Ключевой момент: ты окажешься в нужном месте на 10 минут раньше — и это решит исход.", 1)
]

INTRIGUE_TEMPLATES = [
    ("Я знаю точные даты, кто это и как не потерять своё. Хочешь детали — они уже готовы.", 3),
    ("В платной части есть точные дни и короткий совет, который сэкономит тебе нервы и деньги.", 2),
    ("Если хочешь знать, где именно ловить шанс и кого избегать — открою детали.", 2),
    ("Не притворяйся, что тебе не интересно. Внутри спрятаны конкретные числа и буквы.", 2),
    ("В этой истории есть одна скрытая деталь — и она меняет всё. Дальше только за ⭐.", 2),
    ("Есть причина, почему сейчас важно не тормозить. Детали — в полном прогнозе.", 2),
    ("Я вижу, кто именно сыграет роль триггера. Хочешь имя и дату — открывай полную часть.", 2),
    ("Если хочешь точный момент, когда стоит сказать «да» — в платной части.", 2),
    ("У тебя есть шанс обойти чужую игру. Но точные ходы — только в деталях.", 2),
    ("Есть одна фраза, которую ты услышишь. Я знаю её заранее.", 1),
    ("Скрытая часть — это не «вау», это конкретная польза. И да, она платная.", 1),
    ("Детали — это момент, когда ты перестаёшь угадывать и начинаешь знать.", 1),
    ("У тебя на носу выбор, и в платной части я скажу, какой лучше.", 1),
    ("Есть человек, который не такой, как кажется. Имя — в полной версии.", 1),
    ("Хочешь точные числа и буквы — открывай следующий слой.", 1),
    ("Полная часть покажет, где именно ловить выгоду.", 1),
    ("Ты близко к развилке — в деталях есть подсказка.", 1),
    ("Я оставлю намёк здесь, а ключ — за ⭐.", 1),
    ("У меня есть точный промежуток часов, когда лучше всего действовать. Это в полной части.", 1),
    ("Есть одна буква, которая объясняет всё. Хочешь знать — открывай.", 1),
    ("Я вижу два сценария, и один явно сильнее. Скажу какой — за ⭐.", 1),
    ("Ты близко к правильному решению, но нужна подсказка. Она платная.", 1),
    ("Детали дадут тебе конкретный план, а не туман.", 1),
    ("Полная версия покажет, кто реально на твоей стороне.", 1),
    ("В деталях есть предупреждение, которое экономит деньги.", 1),
    ("Я знаю, где именно ты можешь перегнуть. Подскажу в полной части.", 1),
    ("Есть имя, которое нельзя перепутать. Оно в деталях.", 1),
    ("Ты хочешь знать точный день — он уже есть у меня.", 1),
    ("В платной части есть короткая фраза-ключ для разговора.", 1),
    ("Если хочешь избежать ошибки, которую делают все — открывай.", 1)
]

PAID_DETAILS_TEMPLATES = [
    ("Точная дата: {exact_date}. Имя/буква: «{initial}». Совет: не соглашайся на первый вариант — потребуй вторую итерацию.", 3),
    ("Точный день: {exact_date}. Буква в имени: «{initial}». Предупреждение: не делись планами с тем, кто задаёт слишком много вопросов.", 2),
    ("Точный день: {exact_date}. Буква: «{initial}». Тактика: действуй быстро, но оставь себе право на откат.", 2),
    ("Точная дата: {exact_date}. Буква: «{initial}». Трюк: держи паузу 2–3 часа перед ответом.", 2),
    ("Точная дата: {exact_date}. Буква: «{initial}». Совет: фиксируй договорённости текстом, не на словах.", 2),
    ("Точная дата: {exact_date}. Буква: «{initial}». Важный ход: сначала узнай условия, потом показывай свою карту.", 2),
    ("Точный день: {exact_date}. Буква: «{initial}». Предупреждение: избегай спешки во второй половине дня.", 2),
    ("Точная дата: {exact_date}. Буква: «{initial}». Тактика: выбери один канал связи и держи его под контролем.", 2),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: не соглашайся на «мы потом оформим».", 2),
    ("Точная дата: {exact_date}. Буква: «{initial}». Совет: проговори условия вслух — так меньше манипуляций.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Тактика: сначала выслушай, потом выдай своё.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Предупреждение: не соглашайся на «договоримся позже».", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: держи дистанцию до конца разговора.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Ход: выведи разговор в конкретику.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: не подписывайся на неясные условия.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Тактика: прояви холодную вежливость.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Предупреждение: избегай длинных переписок.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Совет: перепроверь цифры, даже если «всё ясно».", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Ход: не называй цену первым.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: попроси подтверждение письменно.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Тактика: держи разговор в личных сообщениях.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Предупреждение: избегай ультиматумов.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Ход: обозначь границы сразу.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: не соглашайся на устные обещания.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Тактика: спроси про сроки в первом сообщении.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Предупреждение: не принимай решение на эмоциях.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Совет: держи запасной план.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Ход: зафиксируй ключевую цифру.", 1),
    ("Точная дата: {exact_date}. Буква: «{initial}». Тактика: сохрани переписку.", 1),
    ("Точный день: {exact_date}. Буква: «{initial}». Совет: проверь, кто принимает финальное решение.", 1)
]

FOCUS_MAP = {
    "money": "💰 денег",
    "love": "❤️ любви",
    "career": "🚀 карьеры"
}

FOCUS_EMOJI = {
    "money": "💰 Деньги",
    "love": "❤️ Любовь",
    "career": "🚀 Карьера"
}

TONE_VARIANTS = [
    "саркастично",
    "грубовато",
    "дружески",
    "мистически",
    "на грани колкости"
]

INITIALS = ["А", "К", "М", "С", "Н", "Д", "И", "Р", "Т", "Л"]

WEEKDAY_TONES = [
    "мистически",        # Monday
    "саркастично",       # Tuesday
    "дружески",          # Wednesday
    "на грани колкости", # Thursday
    "грубовато",         # Friday
    "мистически",        # Saturday
    "дружески"           # Sunday
]

@dataclass
class ForecastInput:
    age_group: str
    relationship: str
    focus: str
    photo: bool = False
    seed: int | None = None


def _pick(rng, items):
    if not items:
        raise ValueError("items must not be empty")
    if isinstance(items[0], tuple):
        total = sum(w for _, w in items)
        r = rng.uniform(0, total)
        upto = 0.0
        for item, weight in items:
            upto += weight
            if r <= upto:
                return item
        return items[-1][0]
    return items[rng.randrange(len(items))]


def _pick_indexed(rng, items, exclude_idx: int | None = None) -> tuple[int, str]:
    if not items:
        raise ValueError("items must not be empty")
    indexed = list(enumerate(items))
    if exclude_idx is not None and 0 <= exclude_idx < len(items):
        indexed = [pair for pair in indexed if pair[0] != exclude_idx]
        if not indexed:
            indexed = list(enumerate(items))
    if isinstance(items[0], tuple):
        total = sum(item[1][1] for item in indexed)
        r = rng.uniform(0, total)
        upto = 0.0
        for idx, (text, weight) in indexed:
            upto += weight
            if r <= upto:
                return idx, text
        last_idx, last_item = indexed[-1]
        return last_idx, last_item[0]
    idx, text = indexed[rng.randrange(len(indexed))]
    return idx, text


def _weekday_tone() -> str:
    return WEEKDAY_TONES[date.today().weekday()]


def _format_block(template: str, **kwargs) -> str:
    return template.format(**kwargs)


def _build_live_insertions(rng) -> list[str]:
    live_count = rng.randint(1, 3)
    return rng.sample(LIVE_INSERTIONS, k=live_count)


def generate_forecast(data: ForecastInput, exclude: dict | None = None) -> dict:
    if data.age_group not in AGE_GROUPS:
        raise ValueError("age_group must be one of: %s" % ", ".join(AGE_GROUPS))
    if data.relationship not in RELATIONSHIPS:
        raise ValueError("relationship must be one of: %s" % ", ".join(RELATIONSHIPS))
    if data.focus not in FOCUSES:
        raise ValueError("focus must be one of: %s" % ", ".join(FOCUSES))

    exclude = exclude or {}
    rng = random.Random(data.seed)

    base_tone = _weekday_tone()
    tone_pool = [base_tone, base_tone, base_tone] + TONE_VARIANTS
    psych_tone = _pick(rng, tone_pool)
    situation_tone = _pick(rng, tone_pool)
    event_tone = _pick(rng, tone_pool)
    focus_text = FOCUS_MAP[data.focus]
    focus_emoji = FOCUS_EMOJI[data.focus]

    days_low = rng.randint(2, 4)
    days_high = days_low + rng.randint(2, 4)

    initial = _pick(rng, INITIALS)

    psych_idx, psych_tpl = _pick_indexed(rng, PSYCH_TEMPLATES, exclude.get("psych"))
    psych = _format_block(psych_tpl,
        age_group=data.age_group,
        relationship=data.relationship,
        tone=psych_tone,
        focus_emoji=focus_text
    )
    situation_idx, situation_tpl = _pick_indexed(rng, SITUATION_TEMPLATES, exclude.get("situation"))
    situation = _format_block(situation_tpl, tone=situation_tone)
    event_idx, event_tpl = _pick_indexed(rng, EVENT_TEMPLATES, exclude.get("event"))
    event = _format_block(event_tpl,
        days_low=days_low,
        days_high=days_high,
        initial=initial,
        tone=event_tone
    )
    intrigue_idx, intrigue_tpl = _pick_indexed(rng, INTRIGUE_TEMPLATES, exclude.get("intrigue"))
    intrigue = intrigue_tpl

    live_insertions = _build_live_insertions(rng)

    exact_date = date.today() + timedelta(days=days_high)
    paid_idx, paid_tpl = _pick_indexed(rng, PAID_DETAILS_TEMPLATES, exclude.get("paid"))
    paid_details = _format_block(paid_tpl,
        exact_date=exact_date.strftime("%Y-%m-%d"),
        initial=initial
    )

    result = {
        "psych": psych,
        "situation": situation,
        "event": event,
        "intrigue": intrigue,
        "live_insertions": live_insertions,
        "buttons": BUTTONS,
        "paid_details": paid_details,
        "meta": {
            "age_group": data.age_group,
            "relationship": data.relationship,
            "focus": data.focus,
            "focus_label": focus_emoji,
            "base_tone": base_tone,
            "days_range": f"{days_low}–{days_high}",
            "initial": initial,
            "exact_date": exact_date.strftime("%Y-%m-%d"),
            "template_idx": {
                "psych": psych_idx,
                "situation": situation_idx,
                "event": event_idx,
                "intrigue": intrigue_idx,
                "paid": paid_idx
            }
        }
    }

    if data.photo:
        result["photo_note"] = "Фото усилило эффект: образ совпал с тем, что я чувствую."

    return result


def _stable_seed(meta: dict) -> int:
    seed_str = f"{meta.get('exact_date', '')}|{meta.get('initial', '')}|{meta.get('days_range', '')}"
    return sum(ord(ch) for ch in seed_str) or 1


def build_free_text(payload: dict) -> str:
    rng = random.Random(_stable_seed(payload.get("meta", {})))
    live = payload["live_insertions"][:]
    rng.shuffle(live)
    if not live:
        live = LIVE_INSERTIONS[:]
        rng.shuffle(live)
    inserts = [
        live[0 % len(live)],
        live[1 % len(live)],
        live[2 % len(live)]
    ]
    parts = [
        payload["psych"],
        inserts[0],
        payload["situation"],
        inserts[1],
        payload["event"],
        inserts[2],
        payload["intrigue"]
    ]
    return "\n\n".join(parts)


def build_paid_text(payload: dict) -> str:
    return payload["paid_details"]


def generate_bundle(data: ForecastInput, exclude: dict | None = None) -> dict:
    base = generate_forecast(data, exclude=exclude)
    free = {
        "psych": base["psych"],
        "situation": base["situation"],
        "event": base["event"],
        "intrigue": base["intrigue"],
        "live_insertions": base["live_insertions"],
        "buttons": {
            "free_to_paid": BUTTONS["free_to_paid"],
            "upsell": BUTTONS["upsell"]
        }
    }
    paid = {
        "paid_details": base["paid_details"],
        "meta": base["meta"],
        "buttons": {
            "upsell": BUTTONS["upsell"]
        }
    }
    if data.photo:
        free["photo_note"] = base.get("photo_note")
        paid["photo_note"] = base.get("photo_note")

    telegram = build_telegram_payloads(base)

    return {
        "free": free,
        "paid": paid,
        "telegram": telegram,
        "buttons": BUTTONS
    }


def build_telegram_payloads(payload: dict) -> dict:
    group_message = "Хочешь, я загляну в твою линию событий? Нажми кнопку и не делай вид, что тебе всё равно."
    group_keyboard = {
        "inline_keyboard": [
            [{"text": "Открыть прогноз", "url": "https://t.me/your_bot?start=forecast"}]
        ]
    }

    dm_questions = {
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

    free_message = {
        "text": build_free_text(payload),
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Открыть полный прогноз – 49⭐", "callback_data": "pay:full_49"}],
                [{"text": "Поделиться в чат", "callback_data": "share:!прогноз"},
                 {"text": "Пропустить / позже", "callback_data": "skip:later"}],
                [{"text": "📍 Узнать детали – 99⭐", "callback_data": "pay:details_99"},
                 {"text": "Ежедневный прогноз – 199⭐ / неделя", "callback_data": "pay:daily_199"}]
            ]
        }
    }

    paid_message = {
        "text": build_paid_text(payload),
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "📍 Узнать детали – 99⭐", "callback_data": "pay:details_99"},
                 {"text": "Ежедневный прогноз – 199⭐ / неделя", "callback_data": "pay:daily_199"}]
            ]
        }
    }

    payments = {
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

    return {
        "group": {
            "command": "!прогноз",
            "message": group_message,
            "reply_markup": group_keyboard
        },
        "dm_questions": dm_questions,
        "free_message": free_message,
        "paid_message": paid_message,
        "payments": payments
    }


def to_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
