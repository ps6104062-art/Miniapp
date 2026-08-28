import asyncio
import json
import os
import random
import re
import string
import time as _time
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    FSInputFile,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MessageEntity,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import formatting as fmt
from aiogram.fsm.storage.base import StorageKey
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import logging

import locales
from database import db

# Короткий алиас для премиум-эмодзи в текстах сообщений
e = locales.e

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"
ADMINS_FILE = "admins.json"
PANEL_ADMINS_FILE = "panel_admins.json"
SETTINGS_FILE = "settingsadm.json"
users_data_file = "users_data.json"
deals_file = "deals.json"

# ─── Настройки ─────────────────────────────────────────────────────────────────
NOTIFICATION_CHANNEL_ID = -1003707650124
MANAGER_TON_WALLET  = "UQBqWH8izPM-mpf8deVo-cFSU1iUUOWukgsrPv3geSCQIUw"
MANAGER_CARD        = "2204120122508217"
MANAGER_USDT_WALLET = "TManagerUSDTWalletAddressHere"
MANAGER_BTC_WALLET  = "bc1qManagerBTCAddressHere"
MIN_DEALS_FOR_WITHDRAW = 3

# ─── ID кастомных эмодзи для кнопок ───────────────────────────────────────────
# Используются в icon_custom_emoji_id для InlineKeyboardButton
_BEID = {
    "cross":        "5210952531676504517",
    "check":        "5902002809573740949",
    "bridge":       "5240428351063081133",
    "usdt":         "5814556334829343625",
    "btc":          "5816788957614053645",
    "money_bag":    "5375296873982604963",
    "person":       "6032693626394382504",
    "person2":      "5884366771913233289",
    "down":         "5406745015365943482",
    "star":         "4983746717313664194",
    "diamond":      "5427168083074628963",
    "people":       "6032609071373226027",
    "writing":      "5197269100878907942",
    "back":         "5924683191834121281",
    "cart":         "5312361253610475399",
    "handshake":    "5395732581780040886",
    "edit":         "5395444784611480792",
    "card":         "5445353829304387411",
    "package":      "5778672437122045013",
    "chat":         "5443038326535759644",
    "chart":        "5190806721286657692",
    "megaphone":    "5424818078833715060",
    "flag_ru":      "5449408995691341691",
    "flag_ua":      "5447309366568953338",
    "flag_kz":      "5228718354658769982",
    "flag_by":      "5382219601054544127",
    "link":         "5902449142575141204",
    "timer":        "5386367538735104399",
    "hammer":       "5836997023554870252",
    "crown":        "5217822164362739968",
    "bell":         "5458603043203327669",
    "no":           "5260293700088511294",
    "coin":         "5224257782013769471",
    "tag":          "5888620056551625531",
    "mail":         "5253742260054409879",
    "mailbox":      "5350421256627838238",
    "question":     "5436113877181941026",
    "tv":           "6039391078136681499",
    "pin":          "5397782960512444700",
    "finish":       "5411520005386806155",
    "globe":        "5776233299424843260",
    "star2":        "5924870095925942277",
    "warning":      "5420323339723881652",
    "sparkle":      "5325547803936572038",
    "flag_us":      "5202021044105257611",
    "globe2":       "5447410659077661506",
    "gift":         "6037175527846975726",
    "confetti":     "5193018401810822951",
    "target":       "5310278924616356636",
    "bank":         "5332455502917949981",
    "broken_heart": "5316583309541651465",
    "heart_spark":  "5470080737711502911",
    "heart":        "5406926593698312391",
    "heart_gift":   "5192879906295397710",
    "briefcase":    "5445221832074483553",
    "writing2":     "5470060791883374114",
    "outbox":       "6043874504302661409",
    "inbox":        "6039420807900303010",
    "shield":       "5893365724830765382",
    "flying_money": "5375296873982604963",
    "gear":         "5902432207519093015",
    "lock":         "5296369303661067030",
    "sparkle2":     "5778647930038653243",
    "plane":        "5927118708873892465",
    "gem":          "5891105528356018797",
    # ── Расширенный набор ──────────────────────────────────────────────────────────
    "shield2":      "5902016123972358349",
    "phone":        "5895652322469482989",
    "phone2":       "5895266423952904371",
    "phone3":       "5893100690988863311",
    "check2":       "5895514131896733546",
    "check3":       "5895713431264170680",
    "check4":       "5893431652578758294",
    "cross2":       "5893163582194978381",
    "cross3":       "5893081007153746175",
    "briefcase2":   "5893255507380014983",
    "sleep":        "5774138454896022007",
    "money2":       "5893473283696759404",
    "search":       "5893382531037794941",
    "pin2":         "5895440460322706085",
    "idea":         "5893290369629556374",
    "coin2":        "6039802097916974085",
    "gear2":        "5893161718179173515",
    "stop":         "5904238507555033712",
    "person3":      "5902335789798265487",
    "next":         "5893368370530621889",
    "heart2":       "5893406892092297627",
    "heart3":       "5895213106228891182",
    "eyes":         "5210956306952758910",
    "lightning":    "5456140674028019486",
    "smile":        "5461117441612462242",
    "exclaim":      "5274099962655816924",
    "ban":          "5240241223632954241",
    "think":        "5467538555158943525",
    "trending":     "5244837092042750681",
    "snowflake":    "5449449325434266744",
    "gold":         "5440539497383087970",
    "silver":       "5447203607294265305",
    "bronze":       "5453902265922376865",
    "n0":           "5794375786743995258",
    "n1":           "5794164805065514131",
    "n2":           "5794085322400733645",
    "n3":           "5794280000383358988",
    "n4":           "5794241397217304511",
    "n5":           "5793985348446984682",
    "n6":           "5794324702402976226",
    "n7":           "5793942849745591465",
    "n8":           "5793926687783655907",
    "n9":           "5793979472931723221",
}


def mkbtn(text: str, emoji_key: str = None, **kwargs) -> InlineKeyboardButton:
    """Создать InlineKeyboardButton с кастомным эмодзи (icon_custom_emoji_id)."""
    eid = _BEID.get(emoji_key) if emoji_key else None
    if eid:
        return InlineKeyboardButton(text=text, icon_custom_emoji_id=eid, **kwargs)
    return InlineKeyboardButton(text=text, **kwargs)


# ─── Загрузка / сохранение ─────────────────────────────────────────────────────
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_admins(admins):
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(admins), f)

def load_panel_admins() -> set:
    """Панельные админы (доступ к /admin). Хардкодные владельцы всегда включены."""
    if os.path.exists(PANEL_ADMINS_FILE):
        with open(PANEL_ADMINS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_panel_admins(panel_admins: set):
    with open(PANEL_ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(panel_admins), f)

def load_users_data():
    if os.path.exists(users_data_file):
        with open(users_data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users_data(data):
    pass  # данные хранятся в db.users, сохранение — через db.upsert_user

def load_deals():
    return {}  # данные загружаются из SQLite в db.init()

def save_deals(d):
    pass  # данные хранятся в db.deals, сохранение — через db.schedule_save_deal

_DEFAULT_SETTINGS = {
    "service_name":          "Astral Safe",
    "manager_username":      "AstralTradeSupport",
    "manager_ton_wallet":    "UQBqWH8izPM-mpf8deVo-cFSU1iUUOWukgsrPv3geSCQIUw",
    "manager_card":          "2204120122508217",
    "manager_usdt_wallet":   "TManagerUSDTWalletAddressHere",
    "manager_btc_wallet":    "bc1qManagerBTCAddressHere",
    "notification_channel":  str(NOTIFICATION_CHANNEL_ID),
    "gift_recipient":        "AstralTradeSupport",
    "min_deals_withdraw":    3,
    "log_channel":           "",
    "log_topic_id":          "",
    "admins_list":           [],
    "profit_group_id":       "",   # ID группы куда отправлять НОВЫЙ ПРОФИТ
    "profit_topic_id":       "",   # ID топика (темы) в профит-группе
    "worker_percent":        80,   # % воркера от суммы сделки
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    s = dict(_DEFAULT_SETTINGS)
    save_settings(s)
    return s

def save_settings(s: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=4)


# ─── Баннеры ───────────────────────────────────────────────────────────────────
ALLOWED_BANNER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".mp4"}

# Все слоты баннеров: ключ → (описание, список допустимых имён файлов по расширениям)
BANNER_SLOTS = {
    "menu_ru":    ("Главное меню (RU)",     ["menu_ru.png", "menu_ru.jpg", "menu_ru.gif", "menu_ru.mp4"]),
    "menu_en":    ("Главное меню (EN)",     ["menu_en.png", "menu_en.jpg", "menu_en.gif", "menu_en.mp4"]),
    "menu":       ("Главное меню (резерв)", ["menu.png",    "menu.jpg",    "menu.gif",    "menu.mp4"]),
    "deal_ru":    ("Экран сделки (RU)",     ["deal_ru.png",  "deal_ru.jpg",  "deal_ru.gif",  "deal_ru.mp4"]),
    "deal_en":    ("Экран сделки (EN)",     ["deal_en.png",  "deal_en.jpg",  "deal_en.gif",  "deal_en.mp4"]),
    "balance_ru":    ("Баланс (RU)",           ["balance_ru.png","balance_ru.jpg","balance_ru.gif","balance_ru.mp4"]),
    "balance_en":    ("Баланс (EN)",           ["balance_en.png","balance_en.jpg","balance_en.gif","balance_en.mp4"]),
    "rekvizity_ru":  ("Реквизиты (RU)",        ["rekvizity_ru.png","rekvizity_ru.jpg","rekvizity_ru.gif","rekvizity_ru.mp4"]),
    "rekvizity_en":  ("Реквизиты (EN)",        ["rekvizity_en.png","rekvizity_en.jpg","rekvizity_en.gif","rekvizity_en.mp4"]),
    "rekvizity":     ("Реквизиты (резерв)",    ["rekvizity.png","rekvizity.jpg","rekvizity.gif","rekvizity.mp4"]),
}

def get_banner_path(slot_key: str):
    """Вернуть путь к текущему файлу баннера для слота (или None)."""
    if slot_key not in BANNER_SLOTS:
        return None
    _, names = BANNER_SLOTS[slot_key]
    for name in names:
        path = os.path.join(os.getcwd(), name)
        if os.path.exists(path):
            return path
    return None

def get_banner_status(slot_key: str) -> str:
    path = get_banner_path(slot_key)
    if path:
        fname = os.path.basename(path)
        size_kb = os.path.getsize(path) // 1024
        return f"✅ {fname} ({size_kb} КБ)"
    return "❌ не установлен"

def save_banner_file(slot_key: str, file_bytes: bytes, ext: str) -> str:
    """Сохранить байты файла как баннер. Возвращает итоговый путь."""
    if slot_key not in BANNER_SLOTS:
        raise ValueError(f"Unknown slot: {slot_key}")
    _, names = BANNER_SLOTS[slot_key]
    # Выбираем имя с нужным расширением
    target_name = None
    for name in names:
        if name.endswith(ext):
            target_name = name
            break
    if target_name is None:
        target_name = os.path.splitext(names[0])[0] + ext
    # Удаляем старые файлы этого слота
    for name in names:
        old = os.path.join(os.getcwd(), name)
        if os.path.exists(old):
            os.remove(old)
    target_path = os.path.join(os.getcwd(), target_name)
    with open(target_path, "wb") as f:
        f.write(file_bytes)
    return target_path


config = load_config()
BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_GROUP_ID = config.get("ADMIN_GROUP_ID")

if config.get("NOTIFICATION_CHANNEL_ID") is not None:
    NOTIFICATION_CHANNEL_ID = config["NOTIFICATION_CHANNEL_ID"]
if config.get("MANAGER_USDT_WALLET"):
    MANAGER_USDT_WALLET = config["MANAGER_USDT_WALLET"]
if config.get("MANAGER_BTC_WALLET"):
    MANAGER_BTC_WALLET = config["MANAGER_BTC_WALLET"]

admins = load_admins()
users_data: dict = {}  # алиас — будет привязан к db.users после db.init()
deals: dict = {}       # алиас — будет привязан к db.deals после db.init()
adm_settings = load_settings()
panel_admins = load_panel_admins()  # Панельные админы (доступ к /admin)

# Дедупликация update_id — защита от Telegram-ретрансмитов при плохом соединении
_seen_update_ids: set[int] = set()

# Применяем настройки из settingsadm.json
if adm_settings.get("manager_ton_wallet"):
    MANAGER_TON_WALLET = adm_settings["manager_ton_wallet"]
if adm_settings.get("manager_card"):
    MANAGER_CARD = adm_settings["manager_card"]
if adm_settings.get("manager_usdt_wallet"):
    MANAGER_USDT_WALLET = adm_settings["manager_usdt_wallet"]
if adm_settings.get("manager_btc_wallet"):
    MANAGER_BTC_WALLET = adm_settings["manager_btc_wallet"]
if adm_settings.get("notification_channel"):
    try:
        NOTIFICATION_CHANNEL_ID = int(adm_settings["notification_channel"])
    except ValueError:
        pass
if adm_settings.get("min_deals_withdraw") is not None:
    MIN_DEALS_FOR_WITHDRAW = int(adm_settings["min_deals_withdraw"])

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ─── Автоудаление команд пользователя ──────────────────────────────────────────
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class DeleteCommandMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        msg = getattr(event, "message", None) or event if isinstance(event, types.Message) else None
        if msg and isinstance(msg, types.Message) and msg.text and msg.text.startswith("/"):
            try:
                await msg.delete()
            except Exception:
                pass
        return await handler(event, data)

dp.message.middleware(DeleteCommandMiddleware())


# ─── Дедупликация сообщений (защита от Telegram-ретрансмитов) ──────────────────
class DeduplicateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        msg = event if isinstance(event, types.Message) else None
        if msg and msg.message_id:
            key = (msg.chat.id, msg.message_id)
            if key in _seen_update_ids:
                return  # дубль — игнорируем
            _seen_update_ids.add(key)
            if len(_seen_update_ids) > 10000:
                # чистим старые чтобы не росло бесконечно
                _seen_update_ids.clear()
        return await handler(event, data)

dp.message.middleware(DeduplicateMiddleware())


# ─── Локализация ───────────────────────────────────────────────────────────────
def get_text(key: str, user_id: int, **kwargs) -> str:
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    # Автоматически добавляем currency_emoji если передана currency
    if "currency" in kwargs and "currency_emoji" not in kwargs:
        kwargs["currency_emoji"] = _currency_emoji(str(kwargs["currency"]))
    # Автоматически подставляем настройки сервиса
    kwargs.setdefault("service_name", adm_settings.get("service_name", "Astral Safe"))
    kwargs.setdefault("manager_username", adm_settings.get("manager_username", "AstralTradeSupport"))
    return locales.get_html_text(key, lang, **kwargs)

def get_alert(key: str, user_id: int = None, lang: str = None, **kwargs) -> str:
    """Текст для show_alert — без tg-emoji тегов (Telegram их не рендерит во всплывашках)."""
    import re
    if lang is None:
        lang = users_data.get(str(user_id), {}).get("lang", "ru") if user_id else "ru"
    if "currency" in kwargs and "currency_emoji" not in kwargs:
        kwargs["currency_emoji"] = _currency_emoji(str(kwargs["currency"]))
    kwargs.setdefault("service_name", adm_settings.get("service_name", "Astral Safe"))
    kwargs.setdefault("manager_username", adm_settings.get("manager_username", "AstralTradeSupport"))
    text = locales.get_html_text(key, lang, **kwargs)
    # Убираем <tg-emoji ...>fallback</tg-emoji> — оставляем только fallback
    text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
    return text


# ─── Состояния ─────────────────────────────────────────────────────────────────
class CreateDealStates(StatesGroup):
    choose_role           = State()
    choose_payment_method = State()
    choose_crypto         = State()
    choose_currency       = State()
    enter_amount          = State()
    enter_description     = State()

class DealStates(StatesGroup):
    connected_as_seller           = State()
    payment_confirmed_as_seller   = State()
    connected_as_buyer            = State()
    payment_confirmed_as_buyer    = State()
    item_delivered_to_manager     = State()
    buyer_confirmed_receipt       = State()
    completed                     = State()

class EditCredentialsState(StatesGroup):
    waiting_for_ton_wallet    = State()
    waiting_for_card_number   = State()
    waiting_for_stars_username = State()
    waiting_for_usdt_wallet   = State()
    waiting_for_btc_wallet    = State()

class AdsState(StatesGroup):
    waiting_for_ads_message = State()

class WithdrawState(StatesGroup):
    choose_currency = State()
    enter_amount    = State()
    confirm         = State()

class WorkerPayoutState(StatesGroup):
    """Владелец вводит сумму выплаты воркеру после подтверждения сделки."""
    enter_amount = State()

class OwnerApproveWithdrawState(StatesGroup):
    """Владелец одобряет вывод воркера."""
    waiting = State()

class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

class MyDealsState(StatesGroup):
    search = State()

class AdminStates(StatesGroup):
    # Рассылка
    waiting_for_broadcast_message = State()
    # Поиск пользователя
    waiting_for_user_search       = State()
    # Редактирование пользователя
    edit_user_balance_currency    = State()
    edit_user_balance_amount      = State()
    edit_user_deals_count         = State()
    # Сообщение конкретному пользователю
    send_message_to_user          = State()
    # Настройки
    settings_service_name         = State()
    settings_manager_username     = State()
    settings_ton_wallet           = State()
    settings_card                 = State()
    settings_usdt_wallet          = State()
    settings_btc_wallet           = State()
    settings_channel              = State()
    settings_gift_recipient       = State()
    settings_min_deals            = State()
    settings_log_channel          = State()
    settings_log_topic_id         = State()
    settings_profit_group_id      = State()
    settings_profit_topic_id      = State()
    settings_worker_percent       = State()
    settings_add_admin            = State()
    settings_add_panel_admin      = State()
    deals_search                  = State()
    # Баннеры
    settings_upload_banner        = State()

class GoyStates(StatesGroup):
    choose_currency = State()
    enter_amount    = State()


# ─── Вспомогательные функции ───────────────────────────────────────────────────
def _currency_emoji(currency: str) -> str:
    """Возвращает tg-emoji HTML для указанной валюты."""
    from locales import _E as LE
    m = {
        "STARS": '<tg-emoji emoji-id="5924870095925942277">⭐️</tg-emoji>',
        "TON":   '<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji>',
        "BTC":   '<tg-emoji emoji-id="5816788957614053645">🪙</tg-emoji>',
        "USDT":  "<tg-emoji emoji-id=\"5814556334829343625\">🪙</tg-emoji>",
        "RUB":   LE["flag_ru"],
        "UAH":   LE["flag_ua"],
        "KZT":   LE["flag_kz"],
        "BYN":   LE["flag_by"],
    }
    return m.get(currency, LE.get("coin2", "🪙"))


def _status_emoji(status: str) -> str:
    m = {
        "waiting_for_buyer":          "⏳",
        "waiting_for_seller":         "⏳",
        "waiting_for_payment":        "💳",
        "payment_confirmed_by_admin": "✅",
        "item_delivered_to_manager":  "📦",
        "waiting_for_feedback":       "💬",
        "completed":                  "✅",
        "cancelled":                  "❌",
    }
    return m.get(status, "❓")

def _status_ru(status: str) -> str:
    m = {
        "waiting_for_buyer":          "Ожидает покупателя",
        "waiting_for_seller":         "Ожидает продавца",
        "waiting_for_payment":        "Ожидает оплаты",
        "payment_confirmed_by_admin": "Оплата подтверждена",
        "item_delivered_to_manager":  "Товар передан",
        "waiting_for_feedback":       "Ожидает отзыва",
        "completed":                  "Завершена",
        "cancelled":                  "Отменена",
    }
    return m.get(status, status)

def _status_localized(status: str, user_id: int) -> str:
    ru = {
        "waiting_for_buyer":          "Ожидает покупателя",
        "waiting_for_seller":         "Ожидает продавца",
        "waiting_for_payment":        "Ожидает оплаты",
        "payment_confirmed_by_admin": "Оплата подтверждена",
        "item_delivered_to_manager":  "Товар передан",
        "waiting_for_feedback":       "Ожидает отзыва",
        "completed":                  "Завершена",
        "cancelled":                  "Отменена",
    }
    en = {
        "waiting_for_buyer":          "Waiting for buyer",
        "waiting_for_seller":         "Waiting for seller",
        "waiting_for_payment":        "Waiting for payment",
        "payment_confirmed_by_admin": "Payment confirmed",
        "item_delivered_to_manager":  "Item delivered",
        "waiting_for_feedback":       "Waiting for feedback",
        "completed":                  "Completed",
        "cancelled":                  "Cancelled",
    }
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    m = en if lang == "en" else ru
    return m.get(status, status)

def get_active_deals() -> dict:
    """Вернуть незавершённые сделки."""
    return {
        did: d for did, d in deals.items()
        if d.get("status") not in ("completed", "cancelled")
    }


# ─── Клавиатуры ────────────────────────────────────────────────────────────────
def get_main_menu_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("menu_credentials",  user_id), "inbox",      callback_data="menu_credentials"))
    kb.add(mkbtn(get_text("menu_create_deal",  user_id), "handshake",  callback_data="menu_create_deal"))
    kb.add(mkbtn(get_text("menu_balance",      user_id), "money_bag",  callback_data="menu_balance"))
    kb.add(mkbtn(get_text("menu_my_deals",     user_id), "finish",     callback_data="my_deals_page_0"))
    kb.add(mkbtn(get_text("menu_referral",     user_id), "link",       callback_data="menu_referral"))
    kb.add(mkbtn(get_text("lang_button",       user_id), "globe",      callback_data="menu_language"))
    kb.add(mkbtn(get_text("support_button",    user_id), "shield",     url='https://t.me/' + adm_settings.get('manager_username', 'AstralTradeSupport')))
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def get_user_deals_kb(user_id: int, page: int = 0, search: str = "") -> InlineKeyboardMarkup:
    """Список сделок пользователя с пагинацией (2 столбца, 8 на странице) и поиском."""
    uid_str = str(user_id)
    user_deals = {
        did: d for did, d in deals.items()
        if d.get("seller_id") == user_id or d.get("buyer_id") == user_id
    }
    if search:
        user_deals = {did: d for did, d in user_deals.items() if search.lower() in did.lower()}
    items = sorted(user_deals.items(), key=lambda x: x[1].get("created_at", 0), reverse=True)

    per_page = 8
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    chunk = items[page * per_page:(page + 1) * per_page]

    kb = InlineKeyboardBuilder()
    for did, d in chunk:
        emoji = _status_emoji(d.get("status", ""))
        amount = d.get("amount", "?")
        currency = d.get("currency", "?")
        kb.add(mkbtn(f"{emoji} #{did[:8]} {amount} {currency}", callback_data=f"my_deal_{did}"))
    kb.adjust(2)

    nav = []
    if page > 0:
        nav.append(mkbtn("◀️", callback_data=f"my_deals_page_{page-1}"))
    nav.append(mkbtn(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(mkbtn("▶️", callback_data=f"my_deals_page_{page+1}"))
    kb.row(*nav)
    kb.row(mkbtn(get_text("my_deals_search_button", user_id), callback_data="my_deals_search"))
    kb.row(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="back_to_menu"))
    return kb.as_markup()

def get_edit_credentials_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("edit_ton",   user_id), "diamond",  callback_data="edit_ton_wallet"))
    kb.add(mkbtn(get_text("edit_card",  user_id), "card",     callback_data="edit_card"))
    kb.add(mkbtn(get_text("edit_stars", user_id), "star",     callback_data="edit_stars_username"))
    kb.add(mkbtn(get_text("edit_usdt",  user_id), "coin",     callback_data="edit_usdt_wallet"))
    kb.add(mkbtn(get_text("edit_btc",   user_id), "coin",     callback_data="edit_btc_wallet"))
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox",  callback_data="back_to_menu"))
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()

def get_role_selection_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("role_seller_button", user_id), "crown", callback_data="role_seller"))
    kb.add(mkbtn(get_text("role_buyer_button",  user_id), "cart",  callback_data="role_buyer"))
    kb.add(mkbtn(get_text("back_to_menu", user_id),       "inbox", callback_data="back_to_menu"))
    kb.adjust(2, 1)
    return kb.as_markup()

def get_payment_method_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("payment_method_card",   user_id), "card",     callback_data="payment_method_card"))
    kb.add(mkbtn(get_text("payment_method_stars",  user_id), "star",     callback_data="payment_method_stars"))
    kb.add(mkbtn(get_text("payment_method_crypto", user_id), "coin",     callback_data="payment_method_crypto"))
    kb.add(mkbtn(get_text("back_button",           user_id), "back",     callback_data="back_to_role"))
    kb.add(mkbtn(get_text("back_to_menu",          user_id), "inbox",    callback_data="back_to_menu"))
    kb.adjust(2, 1, 1, 1)
    return kb.as_markup()

def get_crypto_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("crypto_ton",    user_id), "diamond", callback_data="crypto_TON"))
    kb.add(mkbtn(get_text("crypto_usdt",   user_id), "coin",    callback_data="crypto_USDT"))
    kb.add(mkbtn(get_text("crypto_btc",    user_id), "coin",    callback_data="crypto_BTC"))
    kb.add(mkbtn(get_text("back_button",   user_id), "back",    callback_data="back_to_payment_method"))
    kb.add(mkbtn(get_text("back_to_menu",  user_id), "inbox",   callback_data="back_to_menu"))
    kb.adjust(3, 1, 1)
    return kb.as_markup()

def get_currency_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("currency_RUB", user_id), "flag_ru", callback_data="currency_RUB"))
    kb.add(mkbtn(get_text("currency_UAH", user_id), "flag_ua", callback_data="currency_UAH"))
    kb.add(mkbtn(get_text("currency_KZT", user_id), "flag_kz", callback_data="currency_KZT"))
    kb.add(mkbtn(get_text("currency_BYN", user_id), "flag_by", callback_data="currency_BYN"))
    kb.add(mkbtn(get_text("back_button",  user_id), "back",    callback_data="back_to_payment_method"))
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox",   callback_data="back_to_menu"))
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()

def get_change_currency_or_back_kb(user_id: int, currency: str = ""):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("change_currency",        user_id), "coin",  callback_data="change_currency"))
    kb.add(mkbtn(get_text("back_button",            user_id), "back",  callback_data="back_to_payment_method"))
    kb.add(mkbtn(get_text("back_to_menu",           user_id), "inbox", callback_data="back_to_menu"))
    kb.adjust(1)
    return kb.as_markup()

def get_seller_post_payment_kb(deal_id: str, user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("send_item_button",      user_id), "outbox",  url='https://t.me/' + adm_settings.get('manager_username', 'AstralTradeSupport')))
    kb.add(mkbtn(get_text("item_delivered_button", user_id), "check",   callback_data=f"confirm_delivery_{deal_id}"))
    kb.add(mkbtn(get_text("support_button",        user_id), "shield",  url='https://t.me/' + adm_settings.get('manager_username', 'AstralTradeSupport')))
    kb.adjust(1)
    return kb.as_markup()

def get_confirm_receipt_kb(deal_id: str, user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("confirm_receipt_button", user_id), "check", callback_data=f"confirm_receipt_{deal_id}"))
    kb.adjust(1)
    return kb.as_markup()

def get_language_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("language_russian", user_id), "flag_ru", callback_data="set_lang_ru"))
    kb.add(mkbtn(get_text("language_english", user_id), "flag_us", callback_data="set_lang_en"))
    kb.add(mkbtn(get_text("back_to_menu",     user_id), "inbox",   callback_data="back_to_menu"))
    kb.adjust(2, 1)
    return kb.as_markup()

def get_balance_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("withdraw_button", user_id), "flying_money", callback_data="menu_withdraw"))
    kb.add(mkbtn(get_text("transactions_button", user_id), "chart", callback_data="balance_txs_0"))
    kb.add(mkbtn(get_text("back_to_menu",    user_id), "inbox",        callback_data="back_to_menu"))
    kb.adjust(1)
    return kb.as_markup()

def get_withdraw_currency_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("STARS",  "star",    callback_data="withdraw_STARS"))
    kb.add(mkbtn("TON",    "diamond", callback_data="withdraw_TON"))
    kb.add(mkbtn("USDT",   "usdt",    callback_data="withdraw_USDT"))
    kb.add(mkbtn("BTC",    "btc",     callback_data="withdraw_BTC"))
    kb.add(mkbtn("RUB",    "flag_ru", callback_data="withdraw_RUB"))
    kb.add(mkbtn("UAH",    "flag_ua", callback_data="withdraw_UAH"))
    kb.add(mkbtn("KZT",    "flag_kz", callback_data="withdraw_KZT"))
    kb.add(mkbtn("BYN",    "flag_by", callback_data="withdraw_BYN"))
    kb.add(mkbtn(get_text("back_button",  user_id), "back",  callback_data="back_to_balance"))
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="back_to_menu"))
    kb.adjust(2, 2, 2, 2, 1, 1)
    return kb.as_markup()


# ─── Клавиатуры АДМИН-ПАНЕЛИ ──────────────────────────────────────────────────
def get_admin_panel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Активные сделки",  "target",    callback_data="admin_deals"))
    kb.add(mkbtn("Пользователи",     "people",    callback_data="admin_users"))
    kb.add(mkbtn("Поиск юзера",      "pin",       callback_data="admin_search_user"))
    kb.add(mkbtn("Рассылка",         "megaphone", callback_data="admin_broadcast"))
    kb.add(mkbtn("Статистика",       "chart",     callback_data="admin_stats"))
    kb.add(mkbtn("Список админов",   "crown",     callback_data="admin_panel_admins"))
    kb.add(mkbtn("Настройки",        "hammer",    callback_data="admin_settings"))
    kb.add(mkbtn("Закрыть",          "no",        callback_data="admin_close"))
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup()

def get_panel_admins_kb() -> InlineKeyboardMarkup:
    """Список панельных админов (доступ к /admin)."""
    kb = InlineKeyboardBuilder()
    all_panel = PANEL_OWNER_IDS | panel_admins  # HIDDEN_OWNER_IDS намеренно не включены
    for uid in sorted(all_panel):
        udata = users_data.get(str(uid), {})
        uname = udata.get("username")
        label = f"@{uname}" if uname else str(uid)
        is_owner = uid in PANEL_OWNER_IDS
        owner_mark = " 👑" if is_owner else ""
        if is_owner:
            # Суперовнера нельзя удалить — только показываем
            kb.row(mkbtn(f"{label} ({uid}){owner_mark}", "crown", callback_data=f"padm_info_{uid}"))
        else:
            kb.row(
                mkbtn(f"{label} ({uid})", "person", callback_data=f"padm_info_{uid}"),
                mkbtn("Удалить", "cross", callback_data=f"padm_kick_{uid}")
            )
    kb.row(mkbtn("Добавить админа", "check", callback_data="padm_add"))
    kb.row(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    return kb.as_markup()

def get_admin_deals_kb(page: int = 0, search: str = "") -> InlineKeyboardMarkup:
    """Список активных сделок: 2 столбца, пагинация с номером страницы, поиск по коду."""
    active = get_active_deals()
    items = sorted(active.items(), key=lambda x: x[1].get("created_at", 0), reverse=True)
    if search:
        items = [(did, d) for did, d in items if search.lower() in did.lower()]
    per_page = 8
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    chunk = items[page * per_page:(page + 1) * per_page]

    kb = InlineKeyboardBuilder()
    for did, d in chunk:
        emoji = _status_emoji(d.get("status", ""))
        amount = d.get("amount", "?")
        currency = d.get("currency", "?")
        kb.add(mkbtn(f"{emoji} #{did[:8]} {amount} {currency}", callback_data=f"admin_deal_{did}"))
    kb.adjust(2)

    nav = []
    if page > 0:
        nav.append(mkbtn("◀️", callback_data=f"admin_deals_page_{page-1}"))
    nav.append(mkbtn(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(mkbtn("▶️", callback_data=f"admin_deals_page_{page+1}"))
    kb.row(*nav)
    kb.row(mkbtn("🔍 Поиск по коду", callback_data="admin_deals_search"))
    kb.row(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    return kb.as_markup()

def get_admin_deal_actions_kb(deal_id: str) -> InlineKeyboardMarkup:
    """Действия с конкретной сделкой."""
    deal = deals.get(deal_id, {})
    status = deal.get("status", "")
    kb = InlineKeyboardBuilder()

    if status == "waiting_for_payment":
        kb.add(mkbtn("Подтвердить оплату",    "check",        callback_data=f"adm_pay_{deal_id}"))
    if status in ("payment_confirmed_by_admin", "waiting_for_payment", "waiting_for_buyer", "waiting_for_seller"):
        kb.add(mkbtn("Подтвердить передачу",  "package",      callback_data=f"adm_deliver_{deal_id}"))
    if status == "item_delivered_to_manager":
        kb.add(mkbtn("Подтвердить получение", "check",        callback_data=f"adm_receipt_{deal_id}"))
    if status == "waiting_for_feedback":
        kb.add(mkbtn("Напомнить об отзыве",   "bell",         callback_data=f"adm_remind_{deal_id}"))
    if status not in ("completed", "cancelled"):
        kb.add(mkbtn("Завершить сделку",      "confetti",     callback_data=f"adm_complete_{deal_id}"))
        kb.add(mkbtn("Отменить сделку",       "cross",        callback_data=f"adm_cancel_{deal_id}"))

    kb.add(mkbtn("К списку сделок", "target", callback_data="admin_deals"))
    kb.adjust(1)
    return kb.as_markup()

def get_admin_users_kb(page: int = 0) -> InlineKeyboardMarkup:
    """Список пользователей с пагинацией."""
    items = list(users_data.items())
    per_page = 10
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    chunk = items[start:start + per_page]

    kb = InlineKeyboardBuilder()
    for uid, udata in chunk:
        uname = udata.get("username") or uid
        deals_count = udata.get("completed_deals", 0)
        kb.add(mkbtn(
            f"@{uname} | сделок: {deals_count}",
            "person",
            callback_data=f"admin_user_{uid}"
        ))
    nav = []
    if page > 0:
        nav.append(mkbtn("Назад", callback_data=f"admin_users_page_{page-1}"))
    if page < total_pages - 1:
        nav.append(mkbtn("Вперёд", callback_data=f"admin_users_page_{page+1}"))
    if nav:
        kb.row(*nav)
    kb.row(mkbtn("Поиск", "person", callback_data="admin_search_user"))
    kb.row(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    kb.adjust(1)
    return kb.as_markup()

def get_admin_user_actions_kb(uid: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Изменить баланс",  "money_bag",  callback_data=f"adm_edit_bal_{uid}"))
    kb.add(mkbtn("Кол-во сделок",    "handshake",  callback_data=f"adm_edit_deals_{uid}"))
    kb.add(mkbtn("Написать юзеру",   "mail",       callback_data=f"adm_msg_user_{uid}"))
    kb.add(mkbtn("Назад к списку",   "people",     callback_data="admin_users"))
    kb.adjust(1)
    return kb.as_markup()

def get_admin_balance_currency_kb(uid: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cur, emoji_key in [("STARS","star"),("TON","diamond"),("USDT","usdt"),
                           ("BTC","btc"),("RUB","flag_ru"),("UAH","flag_ua"),
                           ("KZT","flag_kz"),("BYN","flag_by")]:
        kb.add(mkbtn(cur, emoji_key, callback_data=f"adm_bal_cur_{uid}_{cur}"))
    kb.add(mkbtn("Отмена", "cross", callback_data=f"admin_user_{uid}"))
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


# ─── Баланс ────────────────────────────────────────────────────────────────────
_EMPTY_BALANCE = {
    "STARS": 0.0, "TON": 0.0,
    "USDT":  0.0, "BTC": 0.0,
    "RUB":   0.0, "UAH": 0.0,
    "KZT":   0.0, "BYN": 0.0,
}

def get_user_balance(user_id: str) -> dict:
    uid = str(user_id)
    users_data.setdefault(uid, {})
    balance = users_data[uid].get("balance", {})
    for k, v in _EMPTY_BALANCE.items():
        balance.setdefault(k, v)
    users_data[uid]["balance"] = balance
    return balance  # save убран — I/O только через db

def add_to_balance(user_id: str, currency: str, amount: float, deal_id: str = "", comment: str = ""):
    asyncio.create_task(
        db.add_balance(user_id, currency, amount, deal_id=deal_id, comment=comment)
    )

def subtract_from_balance(user_id: str, currency: str, amount: float,
                          deal_id: str = "", comment: str = "") -> bool:
    # Синхронная проверка и оптимистичное обновление кэша
    balance = get_user_balance(user_id)
    if balance.get(currency, 0.0) < amount:
        return False
    balance[currency] = round(balance[currency] - amount, 8)
    users_data[str(user_id)]["balance"] = balance
    # Async сохранение в БД
    asyncio.create_task(
        db.subtract_balance(user_id, currency, amount, deal_id=deal_id, comment=comment)
    )
    return True

def add_transaction(user_id: str, tx_type: str, currency: str, amount: float,
                    deal_id: str = "", comment: str = ""):
    """Добавить запись транзакции в историю пользователя.
    tx_type: 'credit' (начисление) | 'debit' (списание) | 'withdraw' (вывод)
    """
    asyncio.create_task(
        db.add_transaction(user_id, tx_type, currency, amount, deal_id, comment)
    )

def format_balance(balance: dict) -> str:
    from locales import _E as LE
    emoji_map = {
        "STARS": LE["star"],
        "TON":   LE["diamond"],
        "USDT":  LE["usdt"],
        "BTC":   LE["btc"],
        "RUB":   LE["flag_ru"],
        "UAH":   LE["flag_ua"],
        "KZT":   LE["flag_kz"],
        "BYN":   LE["flag_by"],
    }
    lines = [
        f"{emoji_map.get(cur, cur)} <b>{cur}:</b> <code>{amt}</code>"
        for cur, amt in balance.items() if amt > 0
    ]
    return "\n".join(lines) if lines else get_text("balance_empty", 0)


# ─── Инициализация пользователя ────────────────────────────────────────────────
def _default_user(user_id: int, username: str, bot_username: str) -> dict:
    return {
        "ton_wallet":        "",
        "card":              "",
        "stars_username":    "",
        "usdt_wallet":       "",
        "btc_wallet":        "",
        "ref_link":          f"https://t.me/{bot_username}?start=ref_{user_id}",
        "referrals":         [],
        "referral_earnings": 0.0,
        "completed_deals":   0,
        "username":          username,
        "lang":              "ru",
        "balance":           dict(_EMPTY_BALANCE),
    }

async def ensure_user(user_id: int, username: str):
    uid = str(user_id)
    if uid not in users_data:
        bot_info = await bot.get_me()
        new_user = _default_user(user_id, username, bot_info.username)
        users_data[uid] = new_user
        await db.upsert_user(user_id, new_user)
    else:
        changed = False
        if users_data[uid].get("username") != username:
            users_data[uid]["username"] = username
            changed = True
        for f_name in ("usdt_wallet", "btc_wallet"):
            if f_name not in users_data[uid]:
                users_data[uid][f_name] = ""
                changed = True
        # Инициализируем баланс без I/O
        bal = users_data[uid].setdefault("balance", dict(_EMPTY_BALANCE))
        for k in _EMPTY_BALANCE:
            bal.setdefault(k, 0.0)
        if changed:
            asyncio.create_task(db.upsert_user(user_id, users_data[uid]))


# ─── Отправка главного меню ────────────────────────────────────────────────────
async def _send_menu_media(chat_id: int, photo_path: str, caption: str, kb):
    """Отправить баннер главного меню с учётом формата файла."""
    ext = os.path.splitext(photo_path)[1].lower()
    f = FSInputFile(photo_path)
    if ext == ".mp4":
        await bot.send_video(chat_id=chat_id, video=f, caption=caption, reply_markup=kb, parse_mode="HTML")
    elif ext == ".gif":
        await bot.send_animation(chat_id=chat_id, animation=f, caption=caption, reply_markup=kb, parse_mode="HTML")
    else:
        await bot.send_photo(chat_id=chat_id, photo=f, caption=caption, reply_markup=kb, parse_mode="HTML")

async def _answer_menu_media(message: types.Message, photo_path: str, caption: str, kb):
    """Ответить баннером главного меню с учётом формата файла."""
    ext = os.path.splitext(photo_path)[1].lower()
    f = FSInputFile(photo_path)
    if ext == ".mp4":
        await message.answer_video(video=f, caption=caption, reply_markup=kb, parse_mode="HTML")
    elif ext == ".gif":
        await message.answer_animation(animation=f, caption=caption, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer_photo(photo=f, caption=caption, reply_markup=kb, parse_mode="HTML")

async def _send_banner(chat_id: int, photo_path: str | None, text: str, kb, fallback_send):
    """
    Универсальная отправка баннера с поддержкой .mp4/.gif/.png.
    fallback_send — корутина без аргументов для отправки чистого текста.
    """
    if not photo_path or not os.path.exists(photo_path):
        await fallback_send()
        return
    ext = os.path.splitext(photo_path)[1].lower()
    f = FSInputFile(photo_path)
    try:
        if ext == ".mp4":
            await bot.send_video(chat_id=chat_id, video=f, caption=text, reply_markup=kb, parse_mode="HTML")
        elif ext == ".gif":
            await bot.send_animation(chat_id=chat_id, animation=f, caption=text, reply_markup=kb, parse_mode="HTML")
        else:
            await bot.send_photo(chat_id=chat_id, photo=f, caption=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await fallback_send()


async def _answer_banner(message: types.Message, photo_path: str | None, text: str, kb):
    """
    Универсальный ответ баннером с поддержкой .mp4/.gif/.png.
    Если баннера нет — отправляет чистый текст.
    """
    if not photo_path or not os.path.exists(photo_path):
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
        return
    ext = os.path.splitext(photo_path)[1].lower()
    f = FSInputFile(photo_path)
    try:
        if ext == ".mp4":
            await message.answer_video(video=f, caption=text, reply_markup=kb, parse_mode="HTML")
        elif ext == ".gif":
            await message.answer_animation(animation=f, caption=text, reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer_photo(photo=f, caption=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


async def _edit_or_send_banner(callback_query: types.CallbackQuery, photo_path: str | None, text: str, kb):
    """
    Для callback: редактирует текущее сообщение (edit_media + edit_caption),
    если не получилось — удаляет старое и отправляет новое.
    """
    if not photo_path or not os.path.exists(photo_path):
        try:
            await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest as ex:
            if "no caption" in str(ex).lower() or "message is not modified" not in str(ex).lower():
                try:
                    await callback_query.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
                except Exception:
                    await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
        return
    ext = os.path.splitext(photo_path)[1].lower()
    f = FSInputFile(photo_path)
    try:
        if ext == ".mp4":
            media = types.InputMediaVideo(media=f, caption=text, parse_mode="HTML")
        elif ext == ".gif":
            media = types.InputMediaAnimation(media=f, caption=text, parse_mode="HTML")
        else:
            media = types.InputMediaPhoto(media=f, caption=text, parse_mode="HTML")
        await callback_query.message.edit_media(media=media, reply_markup=kb)
    except Exception:
        try:
            # Если edit_media не сработал — удаляем старое и шлём новое
            try:
                await callback_query.message.delete()
            except Exception:
                pass
            if ext == ".mp4":
                await callback_query.message.answer_video(video=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
            elif ext == ".gif":
                await callback_query.message.answer_animation(animation=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
            else:
                await callback_query.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            try:
                await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")


async def send_main_menu(user_id: int, state: FSMContext):
    await state.clear()
    user_info = users_data.get(str(user_id), {})
    lang = user_info.get("lang", "ru")
    start_text = get_text("welcome", user_id)
    photo_path = (
        get_banner_path(f"menu_{lang}")
        or get_banner_path("menu")
    )
    kb = get_main_menu_kb(user_id)
    try:
        await _send_banner(
            chat_id=user_id,
            photo_path=photo_path,
            text=start_text,
            kb=kb,
            fallback_send=lambda: bot.send_message(chat_id=user_id, text=start_text, reply_markup=kb, parse_mode="HTML"),
        )
    except TelegramForbiddenError:
        pass
    except Exception:
        try:
            await bot.send_message(chat_id=user_id, text=start_text, reply_markup=kb, parse_mode="HTML")
        except TelegramForbiddenError:
            pass

async def show_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    start_text = get_text("welcome", user_id)
    photo_path = (
        get_banner_path(f"menu_{lang}")
        or get_banner_path("menu")
    )
    kb = get_main_menu_kb(user_id)
    try:
        await _answer_banner(message, photo_path, start_text, kb)
    except TelegramForbiddenError:
        pass
    except Exception:
        try:
            await message.answer(start_text, reply_markup=kb, parse_mode="HTML")
        except TelegramForbiddenError:
            pass


# ─── Отображение реквизитов ────────────────────────────────────────────────────
async def show_credentials(message: types.Message):
    user_id = message.from_user.id
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    info = users_data.get(str(user_id), {})
    text = get_text(
        "my_credentials", user_id,
        ton_wallet=info.get("ton_wallet") or "—",
        card=info.get("card") or "—",
        stars_username=info.get("stars_username") or "—",
        usdt_wallet=info.get("usdt_wallet") or "—",
        btc_wallet=info.get("btc_wallet") or "—",
    )
    photo = get_banner_path(f"rekvizity_{lang}") or get_banner_path("rekvizity")
    await _answer_banner(message, photo, text, get_edit_credentials_kb(user_id))


# ─── Команды ───────────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id  = message.from_user.id
    username = message.from_user.username or ""
    await ensure_user(user_id, username)

    args = message.text.split(maxsplit=1)
    param = args[1].strip() if len(args) > 1 else ""

    if param.startswith("deal_"):
        deal_id = param[5:]
        uid_str = str(user_id)
        if deal_id not in deals:
            await message.answer(get_text("deal_not_found", user_id), parse_mode="HTML")
            await show_main_menu(message, state)
            return

        deal = deals[deal_id]
        creator_role = deal.get("creator_role", "seller")

        if creator_role == "seller":
            # Подключаемся как покупатель
            if deal.get("buyer_id") is not None:
                await message.answer(get_text("already_connected", user_id), parse_mode="HTML")
                await show_main_menu(message, state)
                return
            if deal["seller_id"] == user_id:
                await message.answer(get_text("already_connected", user_id), parse_mode="HTML")
                await show_main_menu(message, state)
                return
            deal["buyer_id"]       = user_id
            deal["buyer_username"] = username or str(user_id)
            deal["status"]         = "waiting_for_payment"
            # Автопривязка воркера если покупатель — воркер
            if user_id in admins and not deal.get("worker_id"):
                deal["worker_id"]       = user_id
                deal["worker_username"] = username or str(user_id)
            db.schedule_save_deal(deal_id)
            await send_log("Покупатель подключился к сделке",
                f"Подключился как покупатель", deal_id,
                user_id=user_id, username=username or None)

            seller_id_val = deal.get("seller_id", "")
            seller_completed_deals_val = users_data.get(str(seller_id_val), {}).get("completed_deals", 0)
            deal_text = _build_buyer_deal_text(deal_id, user_id)
            deal_kb   = _build_buyer_deal_kb(deal_id, user_id)
            lang_buyer = users_data.get(str(user_id), {}).get("lang", "ru")
            deal_banner = get_banner_path(f"deal_{lang_buyer}")
            await _answer_banner(message, deal_banner, deal_text, deal_kb)

            try:
                await bot.send_message(
                    chat_id=deal["seller_id"],
                    text=get_text("buyer_joined_notify_seller", deal["seller_id"],
                                  username=username or str(user_id), deal_id=deal_id,
                                  buyer_deals=users_data.get(str(user_id), {}).get("completed_deals", 0)),
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Failed to notify seller: {e}")
        else:
            # Подключаемся как продавец
            if deal.get("seller_id") is not None:
                await message.answer(get_text("already_connected", user_id), parse_mode="HTML")
                await show_main_menu(message, state)
                return
            if deal["buyer_id"] == user_id:
                await message.answer(get_text("already_connected", user_id), parse_mode="HTML")
                await show_main_menu(message, state)
                return

            seller_username = username or str(user_id)
            deal["seller_id"]       = user_id
            deal["seller_username"] = seller_username
            deal["status"]          = "waiting_for_payment"
            # Автопривязка воркера если продавец — воркер
            if user_id in admins and not deal.get("worker_id"):
                deal["worker_id"]       = user_id
                deal["worker_username"] = seller_username
            await send_log("Продавец подключился к сделке",
                f"Подключился как продавец", deal_id,
                user_id=user_id, username=seller_username if seller_username != str(user_id) else None)

            # Обновляем реквизиты продавца
            payment_method = deal.get("payment_method", "TON")
            currency       = deal.get("currency", "TON")
            if payment_method == "STARS":
                mgr_stars = adm_settings.get("gift_recipient") or adm_settings.get("manager_username", "")
                deal["requisites"] = f"@{mgr_stars}" if mgr_stars else "—"
            elif payment_method == "TON" or currency == "TON":
                deal["requisites"] = MANAGER_TON_WALLET
            elif currency == "USDT":
                deal["requisites"] = MANAGER_USDT_WALLET
            elif currency == "BTC":
                deal["requisites"] = MANAGER_BTC_WALLET
            else:
                deal["requisites"] = MANAGER_CARD
            db.schedule_save_deal(deal_id)

            buyer_id_val = deal.get("buyer_id", "")
            buyer_username_val = deal.get("buyer_username", str(buyer_id_val))
            buyer_completed_deals_val = users_data.get(str(buyer_id_val), {}).get("completed_deals", 0)
            text = get_text(
                "connected_as_seller", user_id,
                deal_id=deal_id,
                requisites=deal["requisites"],
                amount=deal["amount"],
                currency=deal["currency"],
                description=deal["description"],
                buyer_username=buyer_username_val,
                buyer_id=buyer_id_val,
                buyer_completed_deals=buyer_completed_deals_val,
            )
            kb = InlineKeyboardBuilder()
            kb.add(mkbtn(get_text("support_button", user_id), "shield", url='https://t.me/' + adm_settings.get('manager_username', 'AstralTradeSupport')))
            kb.add(mkbtn(get_text("back_to_menu",   user_id), "inbox",  callback_data="back_to_menu"))
            kb.adjust(1)
            await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

            seller_deals = users_data.get(str(user_id), {}).get("completed_deals", 0)
            try:
                # Кнопка оплаты с баланса для покупателя
                buyer_id_notify = deal.get("buyer_id")
                await bot.send_message(
                    chat_id=deal["buyer_id"],
                    text=get_text(
                        "seller_joined_notify_buyer", deal["buyer_id"],
                        username=seller_username,
                        deal_id=deal_id,
                        requisites=deal["requisites"],
                        seller_deals=seller_deals,
                    ),
                    reply_markup=_build_buyer_deal_kb(deal_id, buyer_id_notify),
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Failed to notify buyer: {e}")
        return

    if param.startswith("ref_"):
        referrer_id = param[4:]
        uid_str = str(user_id)
        referrer_str = str(referrer_id)
        if referrer_str != uid_str and referrer_str in users_data:
            if uid_str not in users_data.get(referrer_str, {}).get("referrals", []):
                users_data[referrer_str].setdefault("referrals", []).append(uid_str)
                db.schedule_save_user(uid_str)

    await show_main_menu(message, state)


# ─── HTML → (plain_text, [MessageEntity]) ─────────────────────────────────────
# Конвертирует HTML с <tg-emoji>, <b>, <i>, <code>, <blockquote> и т.д.
# в пару (plain_text, entities) для передачи в Bot API без parse_mode.
# Использует aiogram.utils.formatting для корректного рендера CustomEmoji.

from aiogram.utils.formatting import (
    Text as FmtText,
    Bold, Italic, Code, Pre, Underline, Strikethrough,
    CustomEmoji as FmtEmoji,
    BlockQuote,
)

def html_to_fmt(html: str) -> FmtText:
    """
    Парсит HTML-строку с тегами <tg-emoji>, <b>, <i>, <u>, <s>, <code>,
    <pre>, <blockquote> и возвращает aiogram fmt.Text-дерево.
    """
    import re as _re
    from html import unescape as _u

    _TOKEN = _re.compile(
        r'<tg-emoji\s+emoji-id="(\d+)">(.*?)</tg-emoji>'
        r'|<(/)?(b|strong|i|em|u|s|del|code|pre|blockquote)(?:\s[^>]*)?>',
        _re.DOTALL | _re.IGNORECASE,
    )

    # Карта тег → обёртка
    _WRAP = {
        "b": Bold, "strong": Bold,
        "i": Italic, "em": Italic,
        "u": Underline,
        "s": Strikethrough, "del": Strikethrough,
        "code": Code,
        "pre": Pre,
        "blockquote": BlockQuote,
    }

    # Разбираем в плоский список нод: либо строка, либо (emoji_id, fallback), либо (open/close, tag)
    nodes = []
    pos = 0
    for m in _TOKEN.finditer(html):
        if m.start() > pos:
            nodes.append(("text", _u(html[pos:m.start()])))
        pos = m.end()
        emoji_id, emoji_fb, closing, tag = m.group(1), m.group(2), m.group(3), m.group(4)
        if emoji_id:
            nodes.append(("emoji", emoji_id, _u(emoji_fb)))
        else:
            nodes.append(("tag", bool(closing), tag.lower()))
    if pos < len(html):
        nodes.append(("text", _u(html[pos:])))

    # Строим дерево рекурсивно
    def _build(idx: int, stop_tag: str | None):
        parts = []
        i = idx
        while i < len(nodes):
            n = nodes[i]
            if n[0] == "text":
                if n[1]:
                    parts.append(n[1])
                i += 1
            elif n[0] == "emoji":
                parts.append(FmtEmoji(n[2], custom_emoji_id=n[1]))
                i += 1
            elif n[0] == "tag":
                _, is_close, tag = n
                if is_close:
                    if tag == stop_tag:
                        return parts, i + 1
                    i += 1  # несогласованный тег — пропускаем
                else:
                    wrap = _WRAP.get(tag)
                    if wrap:
                        inner, i = _build(i + 1, tag)
                        if inner:
                            parts.append(wrap(*inner))
                    else:
                        i += 1
            else:
                i += 1
        return parts, i

    parts, _ = _build(0, None)
    return FmtText(*parts) if parts else FmtText("")


def html_to_entities(html: str) -> tuple[str, list]:
    """
    Конвертирует HTML → (plain_text, entities) через aiogram fmt.
    Используется в inline-режиме вместо ручного парсера.
    """
    fmt_obj = html_to_fmt(html)
    kwargs  = fmt_obj.as_kwargs()          # {'text': '...', 'entities': [...]}
    return kwargs["text"], kwargs.get("entities") or []


# ─── Inline-режим ──────────────────────────────────────────────────────────────
@dp.inline_query()
async def inline_handler(inline_query: InlineQuery):
    query      = inline_query.query.strip()
    user_id    = inline_query.from_user.id
    lang       = users_data.get(str(user_id), {}).get("lang", "ru")
    bot_info   = await bot.get_me()
    bot_username = bot_info.username
    results    = []

    if query.startswith("#"):
        # ── Поиск сделки по коду ──────────────────────────────────────────────
        deal_id = query[1:].strip()
        deal    = deals.get(deal_id)

        if deal:
            creator_role = deal.get("creator_role", "seller")
            invite_key   = "invite_as_buyer" if creator_role == "seller" else "invite_as_seller"
            invite_html  = locales.get_html_text(
                invite_key, lang,
                inviter        = inline_query.from_user.username or str(user_id),
                deal_id        = deal_id,
                currency       = deal.get("currency", ""),
                currency_emoji = _currency_emoji(deal.get("currency", "")),
                amount         = deal.get("amount", ""),
                description    = deal.get("description", ""),
                service_name   = adm_settings.get("service_name", "Astral Safe"),
                manager_username = adm_settings.get("manager_username", "AstralTradeSupport"),
            )
            plain, ents = html_to_entities(invite_html)
            join_url    = f"https://t.me/{bot_username}?start=deal_{deal_id}"
            keyboard    = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=get_alert("join_deal_button", lang=lang),
                    url=join_url,
                )
            ]])
            results.append(InlineQueryResultArticle(
                id          = str(uuid.uuid4()),
                title       = get_alert("inline_invite_title",  lang=lang),
                description = f"#{deal_id} · {deal.get('amount','')} {deal.get('currency','')}",
                input_message_content=InputTextMessageContent(
                    message_text = plain,
                    entities     = ents,
                ),
                reply_markup = keyboard,
            ))
        else:
            # Сделка не найдена
            not_found_html = (
                f"{e['cross']} Сделка <code>#{deal_id}</code> не найдена."
            )
            plain, ents = html_to_entities(not_found_html)
            results.append(InlineQueryResultArticle(
                id          = str(uuid.uuid4()),
                title       = get_alert("inline_no_deal_title", lang=lang),
                description = get_alert("inline_no_deal_desc",  lang=lang),
                input_message_content=InputTextMessageContent(
                    message_text = plain,
                    entities     = ents,
                ),
            ))

    else:
        # ── Дефолтные результаты: инструкция + реферальная ссылка ────────────

        # 1. Инструкция по инлайн-режиму
        help_html  = locales.get_html_text(
            "inline_default_text", lang,
            bot_username = bot_username,
            service_name = adm_settings.get("service_name", "Astral Safe"),
            manager_username = adm_settings.get("manager_username", "AstralTradeSupport"),
        )
        plain_help, ents_help = html_to_entities(help_html)
        results.append(InlineQueryResultArticle(
            id          = str(uuid.uuid4()),
            title       = get_alert("inline_default_title", lang=lang),
            description = get_alert("inline_default_desc",  lang=lang),
            input_message_content=InputTextMessageContent(
                message_text = plain_help,
                entities     = ents_help,
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=get_alert("inline_referral_button", lang=lang),
                    url=f"https://t.me/{bot_username}?start=help",
                )
            ]]),
        ))

        # 2. Реферальная ссылка
        uid_str  = str(user_id)
        ref_link = users_data.get(uid_str, {}).get(
            "ref_link", f"https://t.me/{bot_username}?start=ref_{user_id}"
        )
        ref_html = locales.get_html_text(
            "inline_referral_text", lang,
            ref_link     = ref_link,
            bot_username = bot_username,
            service_name = adm_settings.get("service_name", "Astral Safe"),
            manager_username = adm_settings.get("manager_username", "AstralTradeSupport"),
        )
        plain_ref, ents_ref = html_to_entities(ref_html)
        results.append(InlineQueryResultArticle(
            id          = str(uuid.uuid4()),
            title       = get_alert("inline_referral_title", lang=lang),
            description = get_alert("inline_referral_desc",  lang=lang),
            input_message_content=InputTextMessageContent(
                message_text = plain_ref,
                entities     = ents_ref,
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=get_alert("inline_referral_button", lang=lang),
                    url=ref_link,
                )
            ]]),
        ))

    await inline_query.answer(results, cache_time=5, is_personal=True)



# ─── Меню: главные пункты ──────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await send_main_menu(callback_query.from_user.id, state)
    await callback_query.answer()

# ─── Навигация назад в создании сделки ────────────────────────────────────────
async def _edit_msg(callback_query, text, kb):
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        try:
            await callback_query.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "back_to_role")
async def back_to_role(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.set_state(CreateDealStates.choose_role)
    await _edit_msg(callback_query, get_text("choose_role", user_id), get_role_selection_kb(user_id))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "back_to_payment_method")
async def back_to_payment_method(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    role = data.get("creator_role", "seller")
    await state.set_state(CreateDealStates.choose_payment_method)
    text = get_text("choose_payment_method" if role == "seller" else "choose_payment_method_buyer", user_id)
    await _edit_msg(callback_query, text, get_payment_method_kb(user_id))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "back_to_enter_amount")
async def back_to_enter_amount(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()
    currency = data.get("currency", "")
    payment_method = data.get("payment_method", "")
    await state.set_state(CreateDealStates.enter_amount)
    key_map = {"TON": "enter_ton_amount", "STARS": "enter_stars_amount",
               "USDT": "enter_crypto_amount_usdt", "BTC": "enter_crypto_amount_btc"}
    text_key = key_map.get(currency) or ("enter_amount" if currency else "enter_ton_amount")
    text = get_text(text_key, user_id, currency=currency)
    try:
        await callback_query.message.edit_text(text=text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(text=text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

# ─── Кнопка вывода назад к балансу ────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "back_to_balance")
async def back_to_balance(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    uid_str = str(user_id)
    balance = get_user_balance(uid_str)
    balance_text = format_balance(balance)
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    text = (
        f"{get_text('balance_title', user_id)}\n\n"
        f"{balance_text}\n\n"
        f"{get_text('completed_deals_count', user_id, count=completed)}"
    )
    if completed < MIN_DEALS_FOR_WITHDRAW:
        text += f"\n\n{get_text('min_deals_warning', user_id, min_deals=MIN_DEALS_FOR_WITHDRAW)}"
    try:
        await callback_query.message.edit_text(text=text, reply_markup=get_balance_kb(user_id), parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(text=text, reply_markup=get_balance_kb(user_id), parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "menu_language")
async def menu_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    text = get_text("choose_language", user_id)
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=get_language_kb(user_id), parse_mode="HTML")
    except TelegramBadRequest as e:
        if "no caption" in str(e).lower():
            await callback_query.message.edit_text(text=text, reply_markup=get_language_kb(user_id), parse_mode="HTML")
        else:
            raise
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("set_lang_"))
async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    lang = callback_query.data.split("_", 2)[2]
    users_data[str(user_id)]["lang"] = lang
    db.schedule_save_user(user_id)
    await callback_query.answer(get_alert("lang_changed", lang=lang))
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await send_main_menu(user_id, state)

@dp.callback_query(lambda c: c.data.startswith("menu_") and c.data not in ("menu_withdraw", "menu_language"))
async def process_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    action  = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id
    lang    = users_data.get(str(user_id), {}).get("lang", "ru")

    async def edit_cap(text, kb):
        try:
            await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest as e:
            if "no caption" in str(e).lower():
                await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
            elif "message is not modified" not in str(e).lower():
                raise

    async def switch_photo(photo_path, text, kb):
        # Если файла нет — fallback на текст
        if not photo_path or not os.path.exists(photo_path):
            try:
                await callback_query.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                try:
                    await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
                except Exception:
                    await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
            return
        # Файл есть — редактируем медиа
        ext = os.path.splitext(photo_path)[1].lower()
        try:
            if ext == ".mp4":
                media = types.InputMediaVideo(media=FSInputFile(photo_path), caption=text, parse_mode="HTML")
            elif ext == ".gif":
                media = types.InputMediaAnimation(media=FSInputFile(photo_path), caption=text, parse_mode="HTML")
            else:
                media = types.InputMediaPhoto(media=FSInputFile(photo_path), caption=text, parse_mode="HTML")
            await callback_query.message.edit_media(media=media, reply_markup=kb)
        except Exception:
            try:
                # Не удалось edit_media — удаляем старое, шлём новое
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
                if ext == ".mp4":
                    await callback_query.message.answer_video(video=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
                elif ext == ".gif":
                    await callback_query.message.answer_animation(animation=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
                else:
                    await callback_query.message.answer_photo(photo=FSInputFile(photo_path), caption=text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                try:
                    await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
                except Exception:
                    await callback_query.message.answer(text=text, reply_markup=kb, parse_mode="HTML")

    if action == "credentials":
        info = users_data.get(str(user_id), {})
        text = get_text(
            "my_credentials", user_id,
            ton_wallet=info.get("ton_wallet") or "—",
            card=info.get("card") or "—",
            stars_username=info.get("stars_username") or "—",
            usdt_wallet=info.get("usdt_wallet") or "—",
            btc_wallet=info.get("btc_wallet") or "—",
        )
        photo = get_banner_path(f"rekvizity_{lang}") or get_banner_path("rekvizity")
        await switch_photo(photo, text, get_edit_credentials_kb(user_id))

    elif action == "create_deal":
        photo = f"sozd_sdelki_{lang}.png" if os.path.exists(f"sozd_sdelki_{lang}.png") else ("sozd_sdelki.png" if os.path.exists("sozd_sdelki.png") else None)
        text = get_text("choose_role", user_id)
        try:
            await switch_photo(photo, text, get_role_selection_kb(user_id))
        except Exception:
            await edit_cap(text, get_role_selection_kb(user_id))
        await state.set_state(CreateDealStates.choose_role)

    elif action == "balance":
        uid_str = str(user_id)
        balance = get_user_balance(uid_str)
        balance_text = format_balance(balance)
        completed = users_data.get(uid_str, {}).get("completed_deals", 0)
        text = (
            f"{get_text('balance_title', user_id)}\n\n"
            f"{balance_text}\n\n"
            f"{get_text('completed_deals_count', user_id, count=completed)}"
        )
        if completed < MIN_DEALS_FOR_WITHDRAW:
            text += f"\n\n{get_text('min_deals_warning', user_id, min_deals=MIN_DEALS_FOR_WITHDRAW)}"
        photo = get_banner_path(f"balance_{lang}") or get_banner_path("balance")
        await switch_photo(photo, text, get_balance_kb(user_id))

    elif action == "referral":
        info = users_data.get(str(user_id), {})
        ref_link = info.get("ref_link", "")
        text = get_text(
            "referral", user_id,
            ref_link=ref_link,
            referrals_count=len(info.get("referrals", [])),
            earnings=info.get("referral_earnings", 0.0),
        )
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(
            text=get_text("copy_ref_link_button", user_id),
            copy_text=types.CopyTextButton(text=ref_link)
        ))
        kb.row(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="back_to_menu"))
        await edit_cap(text, kb.as_markup())

    await callback_query.answer()


# ─── Выбор роли при создании сделки ───────────────────────────────────────────
@dp.callback_query(lambda c: c.data in ("role_seller", "role_buyer"))
async def process_role_selection(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    role = "seller" if callback_query.data == "role_seller" else "buyer"
    await state.update_data(creator_role=role)
    await state.set_state(CreateDealStates.choose_payment_method)
    text = get_text("choose_payment_method" if role == "seller" else "choose_payment_method_buyer", user_id)
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=get_payment_method_kb(user_id), parse_mode="HTML")
    except TelegramBadRequest as e:
        if "no caption" in str(e).lower():
            await callback_query.message.answer(text=text, reply_markup=get_payment_method_kb(user_id), parse_mode="HTML")
        else:
            raise
    await callback_query.answer()


# ─── Методы оплаты ────────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "payment_method_stars")
async def process_payment_method_stars(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    stars_un = users_data.get(str(user_id), {}).get("stars_username", "").strip()
    if not stars_un:
        info = users_data.get(str(user_id), {})
        text = get_text("my_credentials", user_id,
                        ton_wallet=info.get("ton_wallet") or "—", card=info.get("card") or "—",
                        stars_username="—", usdt_wallet=info.get("usdt_wallet") or "—",
                        btc_wallet=info.get("btc_wallet") or "—")
        try:
            await callback_query.message.edit_caption(caption=text, reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(text=text, reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return

    await state.update_data(payment_method="STARS", currency="STARS")
    await state.set_state(CreateDealStates.enter_amount)
    try:
        await callback_query.message.edit_caption(caption=get_text("enter_stars_amount", user_id),
                                                  reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(get_text("enter_stars_amount", user_id),
                                            reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "payment_method_ton")
async def process_payment_method_ton(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if not users_data.get(str(user_id), {}).get("ton_wallet"):
        try:
            await callback_query.message.edit_caption(caption=get_text("add_ton_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("add_ton_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return
    await state.update_data(payment_method="TON")
    await state.set_state(CreateDealStates.enter_amount)
    try:
        await callback_query.message.edit_caption(caption=get_text("enter_ton_amount", user_id), reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(get_text("enter_ton_amount", user_id), reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "payment_method_card")
async def process_payment_method_card(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if not users_data.get(str(user_id), {}).get("card"):
        try:
            await callback_query.message.edit_caption(caption=get_text("add_card_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("add_card_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return
    await state.update_data(payment_method="CARD")
    await state.set_state(CreateDealStates.choose_currency)
    try:
        await callback_query.message.edit_caption(caption=get_text("enter_card_currency", user_id), reply_markup=get_currency_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(get_text("enter_card_currency", user_id), reply_markup=get_currency_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "payment_method_crypto")
async def process_payment_method_crypto(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await state.update_data(payment_method="CRYPTO")
    await state.set_state(CreateDealStates.choose_crypto)
    try:
        await callback_query.message.edit_caption(caption=get_text("choose_crypto", user_id), reply_markup=get_crypto_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(get_text("choose_crypto", user_id), reply_markup=get_crypto_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("crypto_"))
async def process_crypto_selection(callback_query: types.CallbackQuery, state: FSMContext):
    coin    = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id
    if coin == "TON" and not users_data.get(str(user_id), {}).get("ton_wallet"):
        try:
            await callback_query.message.edit_caption(caption=get_text("add_ton_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("add_ton_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return
    if coin == "USDT" and not users_data.get(str(user_id), {}).get("usdt_wallet"):
        try:
            await callback_query.message.edit_caption(caption=get_text("add_usdt_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("add_usdt_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return
    if coin == "BTC" and not users_data.get(str(user_id), {}).get("btc_wallet"):
        try:
            await callback_query.message.edit_caption(caption=get_text("add_btc_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("add_btc_first", user_id), reply_markup=get_edit_credentials_kb(user_id), parse_mode="HTML")
        await callback_query.answer(); return
    await state.update_data(payment_method="CRYPTO", currency=coin)
    await state.set_state(CreateDealStates.enter_amount)
    key_map = {"TON": "enter_crypto_amount_ton", "USDT": "enter_crypto_amount_usdt", "BTC": "enter_crypto_amount_btc"}
    text = get_text(key_map.get(coin, "enter_amount"), user_id, currency=coin)
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("currency_"))
async def process_currency(callback_query: types.CallbackQuery, state: FSMContext):
    currency = callback_query.data.split("_", 1)[1]
    user_id  = callback_query.from_user.id
    await state.update_data(currency=currency)
    await state.set_state(CreateDealStates.enter_amount)
    text = get_text("enter_amount", user_id, currency=currency)
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_change_currency_or_back_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "change_currency")
async def change_currency(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data    = await state.get_data()
    payment_method = data.get("payment_method", "CARD")
    await state.set_state(CreateDealStates.choose_currency)
    if payment_method == "CRYPTO":
        try:
            await callback_query.message.edit_caption(caption=get_text("choose_crypto", user_id), reply_markup=get_crypto_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("choose_crypto", user_id), reply_markup=get_crypto_kb(user_id), parse_mode="HTML")
    else:
        try:
            await callback_query.message.edit_caption(caption=get_text("enter_card_currency", user_id), reply_markup=get_currency_kb(user_id), parse_mode="HTML")
        except Exception:
            await callback_query.message.answer(get_text("enter_card_currency", user_id), reply_markup=get_currency_kb(user_id), parse_mode="HTML")
    await callback_query.answer()


# ─── Ввод суммы ────────────────────────────────────────────────────────────────
@dp.message(CreateDealStates.enter_amount)
async def process_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(get_text("invalid_number", user_id), parse_mode="HTML")
        return
    await state.update_data(amount=amount)
    await state.set_state(CreateDealStates.enter_description)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("back_button",   user_id), "back",  callback_data="back_to_enter_amount"))
    kb.add(mkbtn(get_text("back_to_menu",  user_id), "inbox", callback_data="back_to_menu"))
    kb.adjust(1)
    await message.answer(get_text("enter_description", user_id), reply_markup=kb.as_markup(), parse_mode="HTML")


# ─── Ввод описания и создание сделки ──────────────────────────────────────────
@dp.message(CreateDealStates.enter_description)
async def process_description(message: types.Message, state: FSMContext):
    user_id     = message.from_user.id
    uid_str     = str(user_id)
    description = message.text.strip()
    if not description:
        await message.answer(get_text("invalid_description", user_id), parse_mode="HTML")
        return
    data           = await state.get_data()
    payment_method = data.get("payment_method", "TON")
    currency       = data.get("currency") or "TON"
    amount         = data.get("amount")
    creator_role   = data.get("creator_role", "seller")
    username = message.from_user.username or "N/A"
    users_data.setdefault(uid_str, {})["username"] = username
    db.schedule_save_user(uid_str)
    deal_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    if payment_method == "STARS":
        mgr_stars = adm_settings.get("gift_recipient") or adm_settings.get("manager_username", "")
        requisites = f"@{mgr_stars}" if mgr_stars else "—"
    elif payment_method == "TON" or currency == "TON":
        requisites = MANAGER_TON_WALLET
    elif currency == "USDT":
        requisites = MANAGER_USDT_WALLET
    elif currency == "BTC":
        requisites = MANAGER_BTC_WALLET
    else:
        requisites = MANAGER_CARD

    from datetime import datetime, timezone as _tz
    _now_ts = int(datetime.now(_tz.utc).timestamp())

    # Определяем воркера — если создатель сделки является воркером, сохраняем его
    _is_worker = user_id in admins
    _worker_id       = user_id if _is_worker else None
    _worker_username = username if _is_worker else None

    if creator_role == "seller":
        deal_data = {
            "creator_role": "seller", "seller_id": user_id, "seller_username": username,
            "buyer_id": None, "buyer_username": None, "status": "waiting_for_buyer",
            "payment_method": payment_method, "currency": currency, "amount": amount,
            "description": description, "requisites": requisites, "feedback": "",
            "created_at": _now_ts,
            # Поля воркера и NFT
            "worker_id": _worker_id, "worker_username": _worker_username,
            "nft_link": "", "nft_count": 1,
        }
        text_key = "deal_created"
    else:
        deal_data = {
            "creator_role": "buyer", "seller_id": None, "seller_username": None,
            "buyer_id": user_id, "buyer_username": username, "status": "waiting_for_seller",
            "payment_method": payment_method, "currency": currency, "amount": amount,
            "description": description, "requisites": requisites, "feedback": "",
            "created_at": _now_ts,
            # Поля воркера и NFT
            "worker_id": _worker_id, "worker_username": _worker_username,
            "nft_link": "", "nft_count": 1,
        }
        text_key = "deal_created_as_buyer"

    deals[deal_id] = deal_data
    db.schedule_save_deal(deal_id)
    role_ru = "Продавец" if creator_role == "seller" else "Покупатель"
    await send_log("Новая сделка создана",
        f"Роль создателя: {role_ru} | {amount} {currency}\n{description}", deal_id,
        user_id=user_id, username=username if username != "N/A" else None)
    bot_info = await bot.get_me()
    text = get_text(text_key, user_id, deal_id=deal_id, currency=currency, amount=amount,
                    description=description, bot_username=bot_info.username)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("cancel_deal_button", user_id), "cross", callback_data="cancel_deal"))
    kb.add(mkbtn(get_text("back_to_menu",       user_id), "inbox", callback_data="back_to_menu"))
    kb.adjust(1)
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await state.clear()


# ─── Редактирование реквизитов ─────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data in ("edit_ton_wallet", "edit_card", "edit_stars_username",
                                         "edit_usdt_wallet", "edit_btc_wallet"))
async def process_edit_request(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    action  = callback_query.data
    mapping = {
        "edit_ton_wallet":     (EditCredentialsState.waiting_for_ton_wallet,    "new_wallet"),
        "edit_card":           (EditCredentialsState.waiting_for_card_number,   "new_card"),
        "edit_stars_username": (EditCredentialsState.waiting_for_stars_username,"new_stars_username"),
        "edit_usdt_wallet":    (EditCredentialsState.waiting_for_usdt_wallet,   "new_usdt_wallet"),
        "edit_btc_wallet":     (EditCredentialsState.waiting_for_btc_wallet,    "new_btc_wallet"),
    }
    next_state, text_key = mapping[action]
    await state.set_state(next_state)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="menu_credentials"))
    await callback_query.message.answer(get_text(text_key, user_id), reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(EditCredentialsState.waiting_for_ton_wallet)
async def handle_ton_wallet_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    wallet  = message.text.strip()
    if not re.match(r"^[UQEQ][A-Za-z0-9_\-]{32,60}$", wallet):
        await message.answer(get_text("invalid_wallet", user_id), parse_mode="HTML"); return
    users_data[str(user_id)]["ton_wallet"] = wallet
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(get_text("wallet_updated", user_id), parse_mode="HTML")
    await show_credentials(message)

@dp.message(EditCredentialsState.waiting_for_card_number)
async def handle_card_number_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    clean   = re.sub(r"[^\d]", "", message.text.strip())
    if not clean.isdigit() or not (12 <= len(clean) <= 19):
        await message.answer(get_text("invalid_card", user_id), parse_mode="HTML"); return
    users_data[str(user_id)]["card"] = clean
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(get_text("card_updated", user_id), parse_mode="HTML")
    await show_credentials(message)

@dp.message(EditCredentialsState.waiting_for_stars_username)
async def handle_stars_username_input(message: types.Message, state: FSMContext):
    user_id  = message.from_user.id
    username = message.text.strip().lstrip("@")
    if not username or not re.match(r"^[A-Za-z0-9_]{5,32}$", username):
        await message.answer(get_text("invalid_stars_username", user_id), parse_mode="HTML"); return
    users_data[str(user_id)]["stars_username"] = username
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(get_text("stars_username_updated", user_id), parse_mode="HTML")
    await show_credentials(message)

@dp.message(EditCredentialsState.waiting_for_usdt_wallet)
async def handle_usdt_wallet_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    wallet  = message.text.strip()
    if not re.match(r"^T[A-Za-z0-9]{33}$", wallet):
        await message.answer(get_text("invalid_usdt_wallet", user_id), parse_mode="HTML"); return
    users_data[str(user_id)]["usdt_wallet"] = wallet
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(get_text("usdt_wallet_updated", user_id), parse_mode="HTML")
    await show_credentials(message)

@dp.message(EditCredentialsState.waiting_for_btc_wallet)
async def handle_btc_wallet_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    wallet  = message.text.strip()
    if not re.match(r"^(bc1|[13])[A-Za-z0-9]{25,62}$", wallet):
        await message.answer(get_text("invalid_btc_wallet", user_id), parse_mode="HTML"); return
    users_data[str(user_id)]["btc_wallet"] = wallet
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(get_text("btc_wallet_updated", user_id), parse_mode="HTML")
    await show_credentials(message)


# ─── Баланс и вывод средств ────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "menu_balance")
async def show_balance_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    uid_str = str(user_id)
    lang = users_data.get(uid_str, {}).get("lang", "ru")
    balance = get_user_balance(uid_str)
    balance_text = format_balance(balance)
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    text = (
        f"{get_text('balance_title', user_id)}\n\n"
        f"{balance_text}\n\n"
        f"{get_text('completed_deals_count', user_id, count=completed)}"
    )
    if completed < MIN_DEALS_FOR_WITHDRAW:
        text += f"\n\n{get_text('min_deals_warning', user_id, min_deals=MIN_DEALS_FOR_WITHDRAW)}"
    photo = get_banner_path(f"balance_{lang}") or get_banner_path("balance")
    await _edit_or_send_banner(callback_query, photo, text, get_balance_kb(user_id))
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "menu_withdraw")
async def start_withdraw(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    uid_str = str(user_id)
    balance = get_user_balance(uid_str)
    if not any(v > 0 for v in balance.values()):
        await callback_query.answer(
            get_alert("no_funds_for_withdraw", lang=users_data.get(uid_str, {}).get("lang", "ru")), show_alert=True)
        return
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    if completed < MIN_DEALS_FOR_WITHDRAW:
        lang = users_data.get(uid_str, {}).get("lang", "ru")
        await callback_query.answer(
            get_alert("insufficient_completed_deals", lang=lang, min_deals=MIN_DEALS_FOR_WITHDRAW, user_deals=completed),
            show_alert=True)
        return
    await state.set_state(WithdrawState.choose_currency)
    text = f"{get_text('withdraw_choose_currency', user_id)}\n\n{get_text('withdraw_info', user_id, completed_deals=completed)}"
    try:
        await callback_query.message.edit_caption(caption=text, reply_markup=get_withdraw_currency_kb(user_id), parse_mode="HTML")
    except TelegramBadRequest:
        try:
            await callback_query.message.edit_text(text=text, reply_markup=get_withdraw_currency_kb(user_id), parse_mode="HTML")
        except TelegramBadRequest:
            await callback_query.message.answer(text=text, reply_markup=get_withdraw_currency_kb(user_id), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("withdraw_") and not c.data.startswith("withdraw_goto_edit_") and c.data not in ("withdraw_back", "withdraw_confirm_yes"))
async def choose_withdraw_currency(callback_query: types.CallbackQuery, state: FSMContext):
    currency = callback_query.data.split("_", 1)[1]
    user_id  = callback_query.from_user.id
    uid_str  = str(user_id)
    lang     = users_data.get(uid_str, {}).get("lang", "ru")
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    if completed < MIN_DEALS_FOR_WITHDRAW:
        await callback_query.answer(
            get_alert("insufficient_completed_deals", lang=lang, min_deals=MIN_DEALS_FOR_WITHDRAW, user_deals=completed),
            show_alert=True); return
    balance = get_user_balance(uid_str)
    if balance.get(currency, 0.0) <= 0:
        await callback_query.answer(get_alert("no_balance_in_currency", lang=lang, currency=currency), show_alert=True); return
    await state.update_data(withdraw_currency=currency, withdraw_balance=balance[currency])
    await state.set_state(WithdrawState.enter_amount)
    text = get_text("withdraw_enter_amount", user_id, available_balance=balance[currency], currency=currency)
    try:
        await callback_query.message.edit_caption(caption=text, parse_mode="HTML")
    except TelegramBadRequest:
        try:
            await callback_query.message.edit_text(text=text, parse_mode="HTML")
        except TelegramBadRequest:
            await callback_query.message.answer(text=text, parse_mode="HTML")
    await callback_query.answer()

@dp.message(WithdrawState.enter_amount)
async def handle_withdraw_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    uid_str = str(user_id)
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    if completed < MIN_DEALS_FOR_WITHDRAW:
        await message.answer(get_text("insufficient_completed_deals", user_id, min_deals=MIN_DEALS_FOR_WITHDRAW, user_deals=completed), parse_mode="HTML")
        await state.clear(); await send_main_menu(user_id, state); return
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0: raise ValueError
    except ValueError:
        await message.answer(get_text("invalid_number", user_id), parse_mode="HTML"); return
    data      = await state.get_data()
    currency  = data.get("withdraw_currency")
    available = data.get("withdraw_balance", 0)
    if amount > available:
        await message.answer(get_text("amount_exceeds_balance", user_id, available_balance=available, currency=currency), parse_mode="HTML"); return
    info = users_data.get(uid_str, {})
    # Определяем реквизиты
    if currency == "TON":
        recipient = info.get("ton_wallet")
        rtype_key = "recipient_type_ton"
        edit_cb   = "edit_ton_wallet"
    elif currency == "USDT":
        recipient = info.get("usdt_wallet")
        rtype_key = "recipient_type_usdt"
        edit_cb   = "edit_usdt_wallet"
    elif currency == "BTC":
        recipient = info.get("btc_wallet")
        rtype_key = "recipient_type_btc"
        edit_cb   = "edit_btc_wallet"
    elif currency == "STARS":
        raw = info.get("stars_username")
        recipient = f"@{raw}" if raw else None
        rtype_key = "recipient_type_stars"
        edit_cb   = "edit_stars_username"
    elif currency in ("RUB", "UAH", "KZT", "BYN"):
        recipient = info.get("card")
        rtype_key = "recipient_type_card"
        edit_cb   = "edit_card"
    else:
        await message.answer(get_text("unknown_currency", user_id), parse_mode="HTML")
        await state.clear(); return
    if not recipient:
        no_key = {
            "TON": "no_ton_wallet", "USDT": "no_usdt_wallet", "BTC": "no_btc_wallet",
            "STARS": "no_stars_username",
        }.get(currency, "no_card")
        await message.answer(get_text(no_key, user_id), parse_mode="HTML")
        await state.clear(); return
    rtype = get_text(rtype_key, user_id)
    await state.update_data(withdraw_amount=amount, withdraw_recipient=recipient,
                            withdraw_rtype=rtype, withdraw_edit_cb=edit_cb)
    await state.set_state(WithdrawState.confirm)
    text = get_text("withdraw_confirm", user_id,
                    amount=amount, currency=currency,
                    recipient=recipient, recipient_type=rtype)
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn(get_text("withdraw_confirm_button", user_id),     "check",  callback_data="withdraw_confirm_yes"))
    kb.row(mkbtn(get_text("withdraw_edit_requisites", user_id),    "edit",   callback_data=f"withdraw_goto_edit_{edit_cb}"))
    kb.row(mkbtn(get_text("back_to_menu", user_id),                "inbox",  callback_data="back_to_menu"))
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "withdraw_confirm_yes")
async def handle_withdraw_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    uid_str = str(user_id)
    data      = await state.get_data()
    currency  = data.get("withdraw_currency")
    amount    = data.get("withdraw_amount")
    recipient = data.get("withdraw_recipient")
    rtype     = data.get("withdraw_rtype")
    completed = users_data.get(uid_str, {}).get("completed_deals", 0)
    await state.clear()
    if subtract_from_balance(uid_str, currency, amount, comment=f"Вывод {amount} {currency}"):
        text = get_text("withdraw_request_created", user_id,
                        amount=amount, currency=currency,
                        recipient=recipient, recipient_type=rtype,
                        completed_deals=completed)
        # Уведомляем владельца о запросе на вывод
        asyncio.create_task(notify_owner_withdraw_request(user_id, amount, currency, recipient))
    else:
        text = get_text("withdraw_error", user_id)
    try:
        await callback_query.message.edit_text(text, parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(text, parse_mode="HTML")
    await callback_query.answer()
    await send_main_menu(user_id, state)

@dp.callback_query(lambda c: c.data.startswith("withdraw_goto_edit_"))
async def handle_withdraw_goto_edit(callback_query: types.CallbackQuery, state: FSMContext):
    """Переход к редактированию реквизитов из шага подтверждения вывода."""
    edit_cb = callback_query.data[len("withdraw_goto_edit_"):]
    user_id = callback_query.from_user.id
    await state.clear()
    # Маппинг callback → state для редактирования
    edit_state_map = {
        "edit_ton_wallet":      "edit_ton_wallet",
        "edit_usdt_wallet":     "edit_usdt_wallet",
        "edit_btc_wallet":      "edit_btc_wallet",
        "edit_stars_username":  "edit_stars_username",
        "edit_card":            "edit_card",
    }
    text_map = {
        "edit_ton_wallet":     get_text("new_wallet",          user_id),
        "edit_usdt_wallet":    get_text("new_usdt_wallet",     user_id),
        "edit_btc_wallet":     get_text("new_btc_wallet",      user_id),
        "edit_stars_username": get_text("new_stars_username",  user_id),
        "edit_card":           get_text("new_card",            user_id),
    }
    state_map = {
        "edit_ton_wallet":     EditCredentialsState.waiting_for_ton_wallet,
        "edit_usdt_wallet":    EditCredentialsState.waiting_for_usdt_wallet,
        "edit_btc_wallet":     EditCredentialsState.waiting_for_btc_wallet,
        "edit_stars_username": EditCredentialsState.waiting_for_stars_username,
        "edit_card":           EditCredentialsState.waiting_for_card_number,
    }
    target_state = state_map.get(edit_cb)
    prompt = text_map.get(edit_cb, "Введите новое значение:")
    if not target_state:
        await callback_query.answer("❌", show_alert=True); return
    await state.set_state(target_state)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="back_to_menu"))
    try:
        await callback_query.message.edit_text(prompt, reply_markup=kb.as_markup(), parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(prompt, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()


# ─── Мои сделки ────────────────────────────────────────────────────────────────
async def _show_my_deals(target, user_id: int, page: int = 0, search: str = ""):
    uid_str = str(user_id)
    user_deals_all = {
        did: d for did, d in deals.items()
        if d.get("seller_id") == user_id or d.get("buyer_id") == user_id
    }
    if search:
        filtered = {did: d for did, d in user_deals_all.items() if search.lower() in did.lower()}
    else:
        filtered = user_deals_all
    total = len(filtered)
    search_hint = "\n" + get_text("my_deals_search_result", user_id, search=search, count=total) if search else ""
    completed_count = sum(1 for d in user_deals_all.values() if d.get("status") == "completed")
    text = (
        f"{get_text('my_deals_title', user_id)}{search_hint}\n\n"
        f"{e['chart']} <b>{'Всего' if users_data.get(uid_str, {}).get('lang','ru') == 'ru' else 'Total'}:</b> <code>{len(user_deals_all)}</code>  "
        f"{e['check']} <b>{'Завершено' if users_data.get(uid_str, {}).get('lang','ru') == 'ru' else 'Completed'}:</b> <code>{completed_count}</code>"
    )
    kb = get_user_deals_kb(user_id, page, search)
    try:
        if hasattr(target, "message"):
            await target.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        else:
            await target.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        if hasattr(target, "message"):
            await target.message.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            await target.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("my_deals_page_"))
async def cb_my_deals_page(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    page = int(callback_query.data.split("_")[-1])
    await _show_my_deals(callback_query, callback_query.from_user.id, page)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "my_deals_search")
async def cb_my_deals_search(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(MyDealsState.search)
    user_id = callback_query.from_user.id
    text = get_text("my_deals_search_prompt", user_id)
    cancel_text = get_text("my_deals_cancel_search", user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=cancel_text, callback_data="my_deals_page_0")
    ]])
    try:
        await callback_query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback_query.answer()

@dp.message(MyDealsState.search)
async def handle_my_deals_search(message: types.Message, state: FSMContext):
    await state.clear()
    search = message.text.strip()
    await _show_my_deals(message, message.from_user.id, 0, search)

@dp.callback_query(lambda c: c.data == "noop")
async def cb_noop(callback_query: types.CallbackQuery):
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("my_deal_") and not c.data.startswith("my_deals_"))
async def cb_my_deal_detail(callback_query: types.CallbackQuery):
    deal_id = callback_query.data[len("my_deal_"):]
    user_id = callback_query.from_user.id
    deal = deals.get(deal_id)
    if not deal:
        await callback_query.answer(get_alert("deal_not_found", user_id=user_id), show_alert=True); return
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    status = _status_localized(deal.get("status", ""), user_id)
    role = ("продавец" if lang == "ru" else "seller") if deal.get("seller_id") == user_id else ("покупатель" if lang == "ru" else "buyer")
    text = get_text(
        "my_deal_detail", user_id,
        deal_id=deal_id,
        status=status,
        role=role,
        amount=deal.get("amount", "?"),
        currency=deal.get("currency", "?"),
        description=deal.get("description", "—"),
        seller_username=deal.get("seller_username", "—"),
        buyer_username=deal.get("buyer_username", "—"),
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=get_text("my_deals_back_button", user_id), callback_data="my_deals_page_0")
    ]])
    try:
        await callback_query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await callback_query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback_query.answer()



@dp.callback_query(lambda c: c.data.startswith("confirm_delivery_"))
async def confirm_delivery(callback_query: types.CallbackQuery):
    deal_id = callback_query.data.split("_", 2)[2]
    user_id = callback_query.from_user.id
    if deal_id not in deals:
        await callback_query.answer(get_alert("deal_not_found", user_id=user_id), show_alert=True); return
    deal = deals[deal_id]
    if callback_query.from_user.id != deal["seller_id"]:
        await callback_query.answer(get_alert("only_seller_can_confirm_delivery", user_id=user_id), show_alert=True); return
    deal["status"] = "item_delivered_to_manager"
    db.schedule_save_deal(deal_id)
    await send_log(
        "📦 Товар передан менеджеру",
        f"Продавец сообщил о передаче товара\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}\n"
        f"Описание: {deal.get('description','—')}",
        deal_id,
        user_id=user_id,
        username=callback_query.from_user.username or None,
    )
    await bot.send_message(chat_id=deal["seller_id"], text=get_text("delivery_confirmed_seller", deal["seller_id"], deal_id=deal_id), parse_mode="HTML")
    if deal["buyer_id"]:
        await bot.send_message(chat_id=deal["buyer_id"], text=get_text("delivery_confirmed_buyer_notify", deal["buyer_id"], deal_id=deal_id),
                               reply_markup=get_confirm_receipt_kb(deal_id, deal["buyer_id"]), parse_mode="HTML")
    await callback_query.answer(get_alert("item_delivered_alert", user_id=user_id))

@dp.callback_query(lambda c: c.data.startswith("confirm_receipt_"))
async def confirm_receipt(callback_query: types.CallbackQuery, state: FSMContext):
    deal_id = callback_query.data.split("_", 2)[2]
    user_id = callback_query.from_user.id
    if deal_id not in deals:
        await callback_query.answer(get_alert("deal_not_found", user_id=user_id), show_alert=True); return
    deal = deals[deal_id]
    if callback_query.from_user.id != deal["buyer_id"]:
        await callback_query.answer(get_alert("only_buyer_can_confirm_receipt", user_id=user_id), show_alert=True); return
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    deal["status"] = "waiting_for_feedback"
    db.schedule_save_deal(deal_id)
    await send_log(
        "✅ Покупатель подтвердил получение",
        f"Покупатель подтвердил получение товара, ожидается отзыв продавца\n"
        f"Продавец: @{deal.get('seller_username','?')} | Покупатель: @{deal.get('buyer_username','?')}\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}",
        deal_id,
        user_id=user_id,
        username=callback_query.from_user.username or None,
    )
    await bot.send_message(chat_id=deal["buyer_id"], text=get_text("receipt_confirmed_buyer", deal["buyer_id"], deal_id=deal_id), parse_mode="HTML")
    _skip_kb = InlineKeyboardBuilder()
    _skip_kb.add(mkbtn(get_text("skip_feedback_button", deal["seller_id"]), "no", callback_data=f"skip_feedback_{deal_id}"))
    await bot.send_message(chat_id=deal["seller_id"], text=get_text("feedback_seller_reminder", deal["seller_id"], deal_id=deal_id), parse_mode="HTML", reply_markup=_skip_kb.as_markup())
    seller_key   = StorageKey(bot_id=bot.id, chat_id=deal["seller_id"], user_id=deal["seller_id"])
    seller_state = FSMContext(dp.fsm.storage, seller_key)
    await seller_state.update_data(feedback_deal_id=deal_id)
    await seller_state.set_state(FeedbackState.waiting_for_feedback)
    await state.clear()
    await callback_query.answer(get_alert("receipt_confirmed_alert", user_id=user_id))


# ─── Отзывы ────────────────────────────────────────────────────────────────────
@dp.message(FeedbackState.waiting_for_feedback)
async def handle_feedback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    uid_str = str(user_id)
    data    = await state.get_data()
    deal_id = data.get("feedback_deal_id")
    if not deal_id or deal_id not in deals:
        await message.answer(get_text("feedback_deal_not_found_error", user_id), parse_mode="HTML")
        await state.clear(); await send_main_menu(user_id, state); return
    deal = deals[deal_id]
    if user_id != deal["seller_id"]:
        await message.answer(get_text("feedback_only_seller_can_feedback", user_id), parse_mode="HTML")
        await state.clear(); await send_main_menu(user_id, state); return
    feedback = message.text.strip()
    if len(feedback) > 1000:
        await message.answer(get_text("feedback_too_long", user_id), parse_mode="HTML"); return
    deals[deal_id]["feedback"] = feedback
    db.schedule_save_deal(deal_id)
    await message.answer(get_text("feedback_thanks", user_id), parse_mode="HTML")
    # Защита от двойного начисления
    if deal.get("status") == "completed":
        await state.clear()
        await send_main_menu(user_id, state)
        return
    add_to_balance(uid_str, deal["currency"], deal["amount"], deal_id=deal_id, comment="Завершение сделки")
    deal["status"] = "completed"
    db.schedule_save_deal(deal_id)
    users_data.setdefault(uid_str, {})["completed_deals"] = users_data[uid_str].get("completed_deals", 0) + 1
    db.schedule_save_user(uid_str)
    # Уведомление о начислении
    cur = deal["currency"]
    amt = deal["amount"]
    await message.answer(
        get_text("balance_credited", user_id,
                 amount=amt, currency=cur, currency_emoji=_currency_emoji(cur)),
        parse_mode="HTML"
    )
    await bot.send_message(chat_id=deal["buyer_id"], text=get_text("feedback_buyer_notification", deal["buyer_id"], feedback=feedback), parse_mode="HTML")
    _ld = deals.get(deal_id, {})
    await send_log(
        "🎉 Сделка завершена — отзыв получен",
        f"Продавец: @{_ld.get('seller_username','?')} (ID: {_ld.get('seller_id','?')})\n"
        f"Покупатель: @{_ld.get('buyer_username','?')} (ID: {_ld.get('buyer_id','?')})\n"
        f"Сумма: {_ld.get('amount','?')} {_ld.get('currency','?')}\n"
        f"Отзыв: «{feedback[:200]}{'…' if len(feedback) > 200 else ''}»",
        deal_id,
        user_id=user_id,
        username=message.from_user.username or None,
    )
    await send_completed_deal_notification(deal_id)
    await send_profit_notification(deal_id)
    asyncio.create_task(notify_owner_verify_deal(deal_id))
    await state.clear()
    await send_main_menu(user_id, state)



# ─── Пропуск отзыва ────────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data.startswith("skip_feedback_"))
async def handle_skip_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    deal_id = callback_query.data[len("skip_feedback_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    if user_id != deal.get("seller_id"):
        await callback_query.answer("❌ Только продавец может пропустить отзыв", show_alert=True); return
    if deal.get("status") not in ("waiting_for_feedback",):
        await callback_query.answer("❌ Действие недоступно", show_alert=True); return

    uid_str = str(user_id)
    # Защита от двойного начисления
    if deal.get("status") == "completed":
        await state.clear()
        await callback_query.answer("❌ Сделка уже завершена", show_alert=True)
        return
    deals[deal_id]["feedback"] = ""
    add_to_balance(uid_str, deal["currency"], deal["amount"], deal_id=deal_id, comment="Завершение сделки (отзыв пропущен)")
    deal["status"] = "completed"
    db.schedule_save_deal(deal_id)
    users_data.setdefault(uid_str, {})["completed_deals"] = users_data[uid_str].get("completed_deals", 0) + 1
    db.schedule_save_user(uid_str)

    await state.clear()
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback_query.answer(
        "✅ Вы пропустили отзыв. Средства начислены на ваш баланс." if users_data.get(uid_str, {}).get("lang", "ru") == "ru"
        else "✅ Review skipped. Funds credited to your balance.",
        show_alert=True
    )
    # Уведомление о начислении
    cur = deal["currency"]
    amt = deal["amount"]
    try:
        await bot.send_message(
            chat_id=user_id,
            text=get_text("balance_credited", user_id,
                          amount=amt, currency=cur, currency_emoji=_currency_emoji(cur)),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await send_log(
        "⏭ Продавец пропустил отзыв",
        f"Продавец: @{deal.get('seller_username','?')} (ID: {deal.get('seller_id','?')})\n"
        f"Покупатель: @{deal.get('buyer_username','?')} (ID: {deal.get('buyer_id','?')})\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}",
        deal_id,
        user_id=user_id,
        username=callback_query.from_user.username or None,
    )
    await send_completed_deal_notification(deal_id)
    await send_profit_notification(deal_id)
    asyncio.create_task(notify_owner_verify_deal(deal_id))
    await send_main_menu(user_id, state)



async def send_completed_deal_notification(deal_id: str):
    if not NOTIFICATION_CHANNEL_ID:
        return
    deal = deals.get(deal_id)
    if not deal:
        return
    try:
        bot_info = await bot.get_me()
        buyer_u  = deal.get("buyer_username")  or "скрыт"
        seller_u = deal.get("seller_username") or "скрыт"
        amount   = deal.get("amount", "?")
        currency = deal.get("currency", "?")
        desc     = deal.get("description", "—")
        feedback = deal.get("feedback", "")
        svc      = adm_settings.get("service_name", "Astral Safe")

        text = (
            f'<tg-emoji emoji-id="5193018401810822951">🎉</tg-emoji> <b>Сделка успешно завершена!</b>\n\n'
            f'<blockquote><tg-emoji emoji-id="5395732581780040886">🤝</tg-emoji> <b>Гарант:</b> {svc}\n'
            f'{_currency_emoji(currency)} <b>Сумма:</b> <code>{amount} {currency}</code>\n'
            f'<tg-emoji emoji-id="5470060791883374114">✍️</tg-emoji> <b>Предмет:</b> {desc}</blockquote>\n\n'
            f'<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji> <b>Продавец:</b> @{seller_u}\n'
            f'<tg-emoji emoji-id="5312361253610475399">🛒</tg-emoji> <b>Покупатель:</b> @{buyer_u}\n'
        )
        if feedback:
            text += (
                f'\n<tg-emoji emoji-id="5443038326535759644">💬</tg-emoji> <b>Отзыв продавца:</b>\n'
                f'<blockquote><i>{feedback}</i></blockquote>\n'
            )
        bot_link = f"https://t.me/{bot_info.username}"
        text += (
            f'\n<tg-emoji emoji-id="5325547803936572038">✨</tg-emoji> <i>Спасибо за доверие {svc}!</i>\n'
            f'<code>#{deal_id}</code> • <a href="{bot_link}">@{bot_info.username}</a>'
        )

        # Настройки превью ссылки (показываем превью бота)
        link_preview = types.LinkPreviewOptions(
            is_disabled=False,
            url=bot_link,
            prefer_small_media=True,
            show_above_text=False,
        )

        # Сначала отправляем в лог-канал (там работают премиум-эмодзи)
        log_channel_id = None
        try:
            log_channel_id = int(adm_settings.get("log_channel") or 0)
        except (ValueError, TypeError):
            log_channel_id = 0
        try:
            log_topic_id = int(adm_settings.get("log_topic_id") or 0) or None
        except (ValueError, TypeError):
            log_topic_id = None

        sent_msg = None
        if log_channel_id:
            try:
                sent_msg = await bot.send_message(
                    chat_id=log_channel_id,
                    text=text,
                    parse_mode="HTML",
                    link_preview_options=link_preview,
                    message_thread_id=log_topic_id,
                )
            except Exception as ex:
                logging.error(f"Log channel deal notification failed: {ex}", exc_info=True)

        # Пересылаем из лог-канала в канал уведомлений через forward (сохраняет премиум-эмодзи)
        if sent_msg is not None:
            try:
                await bot.forward_message(
                    chat_id=NOTIFICATION_CHANNEL_ID,
                    from_chat_id=log_channel_id,
                    message_id=sent_msg.message_id,
                )
            except Exception as ex:
                logging.error(f"Forward to notification channel failed: {ex}", exc_info=True)
        else:
            # Лог-канал не настроен — отправляем напрямую в канал уведомлений
            try:
                await bot.send_message(
                    chat_id=NOTIFICATION_CHANNEL_ID,
                    text=text,
                    parse_mode="HTML",
                    link_preview_options=link_preview,
                )
            except Exception as ex:
                logging.error(f"Channel notification failed: {ex}", exc_info=True)
    except Exception as ex:
        logging.error(f"send_completed_deal_notification error: {ex}", exc_info=True)


# ─── АВТОВЫПЛАТА TON ВОРКЕРУ ──────────────────────────────────────────────────
# Мнемоника кошелька менеджера берётся из переменной окружения PAYOUT_MNEMONIC
# Пример: PAYOUT_MNEMONIC="word1 word2 word3 ... word24"

async def _send_ton_to_worker(to_address: str, amount_ton: float, comment: str = "") -> str | None:
    """
    Отправляет TON с кошелька менеджера на адрес воркера.
    Возвращает хеш транзакции или None при ошибке.
    Использует библиотеку tonsdk + httpx для работы с TON API.
    """
    try:
        from tonsdk.contract.wallet import Wallets, WalletVersionEnum
        from tonsdk.utils import to_nano
        import base64, httpx

        mnemonic_str = os.environ.get("PAYOUT_MNEMONIC", "")
        if not mnemonic_str:
            logging.error("PAYOUT_MNEMONIC не задана в переменных окружения!")
            return None

        mnemonic = mnemonic_str.strip().split()
        if len(mnemonic) not in (12, 24):
            logging.error(f"PAYOUT_MNEMONIC должна содержать 12 или 24 слова, получено {len(mnemonic)}")
            return None

        # Создаём кошелёк из мнемоники
        _mnemonic, pub_k, priv_k, wallet = Wallets.from_mnemonics(
            mnemonic, WalletVersionEnum.v4r2, workchain=0
        )

        # Получаем seqno через TON API
        wallet_address = wallet.address.to_string(True, True, True)
        toncenter_token = os.environ.get("TONCENTER_API_KEY", "")
        headers = {"X-API-Key": toncenter_token} if toncenter_token else {}

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"https://toncenter.com/api/v2/getWalletInformation?address={wallet_address}",
                headers=headers
            )
            data = r.json()
            seqno = data.get("result", {}).get("seqno", 0) or 0

            # Формируем транзакцию
            nano = to_nano(amount_ton, "ton")
            query = wallet.create_transfer_message(
                to_addr=to_address,
                amount=nano,
                seqno=seqno,
                payload=comment,
            )
            boc = base64.b64encode(query["message"].to_boc(False)).decode()

            # Отправляем в сеть
            r2 = await client.post(
                "https://toncenter.com/api/v2/sendBoc",
                json={"boc": boc},
                headers=headers,
            )
            result = r2.json()
            if result.get("ok"):
                tx_hash = result.get("result", {}).get("hash", "sent")
                logging.info(f"TON выплата: {amount_ton} TON → {to_address}, hash={tx_hash}")
                return tx_hash
            else:
                logging.error(f"TON sendBoc ошибка: {result}")
                return None

    except ImportError:
        logging.error("tonsdk не установлен! Добавь в requirements.txt: tonsdk httpx")
        return None
    except Exception as ex:
        logging.error(f"_send_ton_to_worker ошибка: {ex}", exc_info=True)
        return None


async def _autopayout_worker(deal_id: str):
    """
    Автовыплата воркеру после завершения сделки.
    Берёт ton_wallet воркера из его профиля, считает долю, отправляет TON.
    """
    deal = deals.get(deal_id)
    if not deal:
        return

    # Определяем воркера
    worker_id = deal.get("worker_id") or deal.get("seller_id")
    if not worker_id:
        logging.warning(f"Автовыплата #{deal_id}: нет worker_id")
        return

    worker_str = str(worker_id)
    worker_data = users_data.get(worker_str, {})
    ton_wallet = worker_data.get("ton_wallet", "").strip()

    if not ton_wallet:
        # Воркер не указал кошелёк — уведомляем его
        try:
            await bot.send_message(
                chat_id=worker_id,
                text=(
                    f"⚠️ <b>Сделка <code>#{deal_id}</code> завершена!</b>\n\n"
                    f"Но у тебя не указан TON-кошелёк для выплаты.\n"
                    f"Укажи его командой /setwallet и обратись к администратору."
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return

    # Считаем сумму выплаты
    try:
        worker_percent = int(adm_settings.get("worker_percent", 80))
    except (ValueError, TypeError):
        worker_percent = 80

    try:
        amount_ton = round(float(deal.get("amount", 0)) * worker_percent / 100, 4)
    except (ValueError, TypeError):
        logging.error(f"Автовыплата #{deal_id}: не удалось посчитать сумму")
        return

    if amount_ton <= 0:
        return

    currency = deal.get("currency", "TON")
    comment  = f"Выплата по сделке #{deal_id}"

    # Уведомляем воркера что выплата в процессе
    try:
        await bot.send_message(
            chat_id=worker_id,
            text=(
                f"⏳ <b>Выплата по сделке <code>#{deal_id}</code>...</b>\n\n"
                f"💎 Отправляю <b>{amount_ton} {currency}</b> на твой кошелёк.\n"
                f"<code>{ton_wallet}</code>"
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    tx_hash = await _send_ton_to_worker(ton_wallet, amount_ton, comment)

    if tx_hash:
        try:
            await bot.send_message(
                chat_id=worker_id,
                text=(
                    f"✅ <b>Выплата отправлена!</b>\n\n"
                    f"💎 <b>{amount_ton} {currency}</b>\n"
                    f"📬 Кошелёк: <code>{ton_wallet}</code>\n"
                    f"🔗 Транзакция: <code>{tx_hash}</code>"
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass
    else:
        # Выплата не прошла — уведомляем админа
        for admin_id in list(admins):
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"❌ <b>Ошибка автовыплаты по сделке <code>#{deal_id}</code>!</b>\n\n"
                        f"Сумма: <b>{amount_ton} {currency}</b>\n"
                        f"Кошелёк воркера: <code>{ton_wallet}</code>\n\n"
                        f"Проверь PAYOUT_MNEMONIC и баланс кошелька.\n"
                        f"Выплати вручную!"
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass


# ─── ПРОФИТ-УВЕДОМЛЕНИЕ ────────────────────────────────────────────────────────

async def send_profit_notification(deal_id: str):
    """
    Отправляет сообщение «НОВЫЙ ПРОФИТ» в profit_group_id.
    Формат: как на скриншоте — воркер, бот, снято NFT, ссылка, сумма, %.
    """
    profit_group_id = adm_settings.get("profit_group_id", "")
    if not profit_group_id:
        return
    try:
        profit_group_id = int(profit_group_id)
    except (ValueError, TypeError):
        return

    deal = deals.get(deal_id)
    if not deal:
        return
    try:
        bot_info = await bot.get_me()
        worker_u  = deal.get("worker_username") or deal.get("seller_username") or "—"
        amount    = deal.get("amount", "?")
        currency  = deal.get("currency", "?")
        nft_link  = deal.get("nft_link", "")
        nft_count = deal.get("nft_count", 1)
        try:
            worker_percent = int(adm_settings.get("worker_percent", 80))
        except (ValueError, TypeError):
            worker_percent = 80
        try:
            worker_share = round(float(amount) * worker_percent / 100, 2)
        except (ValueError, TypeError):
            worker_share = "?"

        # Строка со ссылкой на NFT
        nft_line = ""
        if nft_link:
            nft_line = f'\n<a href="{nft_link}">{nft_link}</a>'

        text = (
            f"🪄 <b>НОВЫЙ ПРОФИТ!</b>\n\n"
            f"👷 <b>Воркер:</b> @{worker_u}\n"
            f"🤖 <b>Бот:</b> @{bot_info.username}\n"
            f"🎁 <b>Снято NFT:</b> {nft_count} шт.{nft_line}\n\n"
            f"💎 <b>Сумма:</b> {amount} {currency}:\n"
            f"<blockquote>"
            f"• <b>Процент выплаты:</b> {worker_percent}% 💬\n"
            f"• <b>Доля воркера:</b> {worker_share} {currency} 💬"
            f"</blockquote>"
        )

        await bot.send_message(
            chat_id=profit_group_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    except Exception as ex:
        logging.error(f"send_profit_notification error: {ex}", exc_info=True)


# ─── Уведомление владельцу: проверь сделку ────────────────────────────────────

async def notify_owner_verify_deal(deal_id: str):
    """
    Отправляет владельцу уведомление о завершённой сделке с кнопкой «Сделка прошла».
    Владелец проверяет, нажимает кнопку, вводит сумму выплаты воркеру.
    """
    deal = deals.get(deal_id)
    if not deal:
        return

    worker_u  = deal.get("worker_username") or deal.get("seller_username") or "—"
    buyer_u   = deal.get("buyer_username") or str(deal.get("buyer_id", "?"))
    amount    = deal.get("amount", "?")
    currency  = deal.get("currency", "?")
    nft_link  = deal.get("nft_link", "")
    nft_line  = f'\n🔗 <a href="{nft_link}">{nft_link}</a>' if nft_link else ""

    text = (
        f"🔔 <b>Новая сделка завершена — проверь!</b>\n\n"
        f"📋 <b>Сделка:</b> <code>#{deal_id}</code>\n"
        f"👤 <b>Покупатель:</b> @{buyer_u}\n"
        f"👷 <b>Воркер:</b> @{worker_u}\n"
        f"💎 <b>Сумма:</b> {amount} {currency}{nft_line}\n\n"
        f"⬇️ После проверки нажми «Сделка прошла» и введи сумму выплаты воркеру."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Сделка прошла", callback_data=f"owner_deal_ok_{deal_id}"),
        InlineKeyboardButton(text="❌ Проблема",       callback_data=f"owner_deal_problem_{deal_id}"),
    ]])

    for owner_id in PANEL_OWNER_IDS | HIDDEN_OWNER_IDS:
        try:
            await bot.send_message(
                chat_id=owner_id,
                text=text,
                reply_markup=kb,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as ex:
            logging.error(f"notify_owner_verify_deal: {ex}")


@dp.callback_query(lambda c: c.data.startswith("owner_deal_ok_"))
async def cb_owner_deal_ok(callback_query: types.CallbackQuery, state: FSMContext):
    """Владелец нажал «Сделка прошла» — просим ввести сумму выплаты воркеру."""
    uid = callback_query.from_user.id
    if uid not in (PANEL_OWNER_IDS | HIDDEN_OWNER_IDS):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    deal_id = callback_query.data[len("owner_deal_ok_"):]
    deal = deals.get(deal_id)
    if not deal:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True)
        return

    worker_u = deal.get("worker_username") or deal.get("seller_username") or "—"
    amount   = deal.get("amount", "?")
    currency = deal.get("currency", "?")

    try:
        worker_percent = int(adm_settings.get("worker_percent", 80))
    except (ValueError, TypeError):
        worker_percent = 80
    try:
        suggested = round(float(amount) * worker_percent / 100, 2)
    except (ValueError, TypeError):
        suggested = "?"

    await state.update_data(payout_deal_id=deal_id, payout_currency=currency)
    await state.set_state(WorkerPayoutState.enter_amount)

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback_query.message.answer(
        f"💰 <b>Введи сумму выплаты воркеру @{worker_u}</b>\n\n"
        f"Сделка: <code>#{deal_id}</code>\n"
        f"Сумма сделки: <b>{amount} {currency}</b>\n"
        f"Рекомендуемая ({worker_percent}%): <b>{suggested} {currency}</b>\n\n"
        f"Напиши сумму цифрой:",
        parse_mode="HTML",
    )
    await callback_query.answer()


@dp.message(WorkerPayoutState.enter_amount)
async def handle_worker_payout_amount(message: types.Message, state: FSMContext):
    """Владелец вводит сумму — зачисляем на баланс воркера."""
    data      = await state.get_data()
    deal_id   = data.get("payout_deal_id")
    currency  = data.get("payout_currency", "TON")
    await state.clear()

    try:
        payout_amount = round(float(message.text.replace(",", ".")), 4)
        if payout_amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи число больше 0.")
        return

    deal = deals.get(deal_id)
    if not deal:
        await message.answer("❌ Сделка не найдена.")
        return

    worker_id = deal.get("worker_id") or deal.get("seller_id")
    if not worker_id:
        await message.answer("❌ Воркер не найден в сделке.")
        return

    worker_str = str(worker_id)
    worker_u   = deal.get("worker_username") or deal.get("seller_username") or str(worker_id)

    # Зачисляем на баланс воркера
    add_to_balance(worker_str, currency, payout_amount,
                   deal_id=deal_id, comment=f"Выплата по сделке #{deal_id}")

    await message.answer(
        f"✅ <b>Начислено!</b>\n\n"
        f"👷 Воркер: @{worker_u}\n"
        f"💎 Сумма: <b>{payout_amount} {currency}</b>\n"
        f"📋 Сделка: <code>#{deal_id}</code>\n\n"
        f"Воркер увидит баланс и сможет запросить вывод.",
        parse_mode="HTML",
    )

    # Уведомляем воркера
    try:
        new_balance = get_user_balance(worker_str).get(currency, 0)
        await bot.send_message(
            chat_id=worker_id,
            text=(
                f"💰 <b>Тебе начислена выплата!</b>\n\n"
                f"💎 <b>+{payout_amount} {currency}</b> по сделке <code>#{deal_id}</code>\n"
                f"📊 Твой баланс {currency}: <b>{new_balance}</b>\n\n"
                f"Для вывода нажми «Баланс» → «Вывести» в главном меню."
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass


@dp.callback_query(lambda c: c.data.startswith("owner_deal_problem_"))
async def cb_owner_deal_problem(callback_query: types.CallbackQuery, state: FSMContext):
    """Владелец нажал «Проблема» — уведомляем всех."""
    uid = callback_query.from_user.id
    if uid not in (PANEL_OWNER_IDS | HIDDEN_OWNER_IDS):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    deal_id = callback_query.data[len("owner_deal_problem_"):]
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback_query.message.answer(
        f"⚠️ Сделка <code>#{deal_id}</code> отмечена как проблемная.\n"
        f"Разберись вручную и при необходимости начисли выплату через /admin.",
        parse_mode="HTML",
    )
    await callback_query.answer("⚠️ Отмечено", show_alert=False)


# ─── Вывод воркера: владелец одобряет и бот отправляет TON ────────────────────

async def notify_owner_withdraw_request(user_id: int, amount: float, currency: str, recipient: str):
    """
    Когда воркер запрашивает вывод TON — уведомляем владельца с кнопкой «Одобрить».
    """
    username = users_data.get(str(user_id), {}).get("username", str(user_id))
    text = (
        f"💸 <b>Запрос на вывод!</b>\n\n"
        f"👷 Воркер: @{username}\n"
        f"💎 Сумма: <b>{amount} {currency}</b>\n"
        f"📬 Кошелёк: <code>{recipient}</code>\n\n"
        f"Одобри чтобы бот автоматически отправил TON."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Одобрить и отправить",
            callback_data=f"approve_withdraw_{user_id}_{amount}_{currency}_{recipient}"
        ),
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"reject_withdraw_{user_id}"
        ),
    ]])
    for owner_id in PANEL_OWNER_IDS | HIDDEN_OWNER_IDS:
        try:
            await bot.send_message(chat_id=owner_id, text=text, reply_markup=kb, parse_mode="HTML")
        except Exception as ex:
            logging.error(f"notify_owner_withdraw_request: {ex}")


@dp.callback_query(lambda c: c.data.startswith("approve_withdraw_"))
async def cb_approve_withdraw(callback_query: types.CallbackQuery):
    """Владелец одобрил вывод — бот отправляет TON."""
    uid = callback_query.from_user.id
    if uid not in (PANEL_OWNER_IDS | HIDDEN_OWNER_IDS):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    parts     = callback_query.data[len("approve_withdraw_"):].split("_", 3)
    worker_id = int(parts[0])
    amount    = float(parts[1])
    currency  = parts[2]
    recipient = parts[3]

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback_query.answer("⏳ Отправляю...", show_alert=False)

    if currency == "TON":
        tx_hash = await _send_ton_to_worker(recipient, amount, comment="Вывод воркера")
        if tx_hash:
            await callback_query.message.answer(
                f"✅ <b>Отправлено!</b>\n💎 {amount} TON → <code>{recipient}</code>\n🔗 <code>{tx_hash}</code>",
                parse_mode="HTML",
            )
            try:
                await bot.send_message(
                    chat_id=worker_id,
                    text=f"✅ <b>Вывод одобрен и отправлен!</b>\n\n💎 <b>{amount} TON</b>\n📬 <code>{recipient}</code>\n🔗 Транзакция: <code>{tx_hash}</code>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
        else:
            await callback_query.message.answer(
                f"❌ <b>Ошибка отправки!</b>\nПроверь PAYOUT_MNEMONIC и баланс кошелька.\nОтправь вручную: <b>{amount} TON</b> → <code>{recipient}</code>",
                parse_mode="HTML",
            )
    else:
        # Не TON — напоминаем отправить вручную
        await callback_query.message.answer(
            f"📋 <b>Отправь вручную:</b>\n💎 {amount} {currency} → <code>{recipient}</code>",
            parse_mode="HTML",
        )
        try:
            await bot.send_message(
                chat_id=worker_id,
                text=f"✅ <b>Вывод одобрен!</b>\n\n💎 <b>{amount} {currency}</b> будет отправлен вручную.",
                parse_mode="HTML",
            )
        except Exception:
            pass


@dp.callback_query(lambda c: c.data.startswith("reject_withdraw_"))
async def cb_reject_withdraw(callback_query: types.CallbackQuery):
    """Владелец отклонил вывод — возвращаем деньги воркеру на баланс."""
    uid = callback_query.from_user.id
    if uid not in (PANEL_OWNER_IDS | HIDDEN_OWNER_IDS):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    worker_id = int(callback_query.data[len("reject_withdraw_"):])
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback_query.message.answer("❌ Вывод отклонён.")
    try:
        await bot.send_message(
            chat_id=worker_id,
            text="❌ <b>Вывод отклонён администратором.</b>\nОбратись в поддержку.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await callback_query.answer()


# ─── Лог-канал ─────────────────────────────────────────────────────────────────

def mask_username(username: str) -> str:
    """Маскирует юзернейм: @sluts1337 → @slu****337.
    Показывает первые 3 и последние 3 символа, остальное заменяет на ****."""
    if not username:
        return "—"
    # Убираем @ если есть, работаем с чистым именем
    prefix = "@" if username.startswith("@") else ""
    name = username.lstrip("@")
    if len(name) <= 6:
        # Короткие имена: показываем первый и последний символ
        if len(name) <= 2:
            return prefix + "*" * len(name)
        return prefix + name[0] + "****" + name[-1]
    return prefix + name[:3] + "****" + name[-3:]

def mask_usernames_in_text(text: str) -> str:
    """Заменяет все @username в тексте на маскированные версии."""
    import re
    def _mask(m):
        return mask_username(m.group(0))
    return re.sub(r'@[\w]+', _mask, text)

async def send_log(event: str, details: str = "", deal_id: str = "",
                   user_id: int = None, username: str = None):
    """Отправляет структурированное лог-сообщение в настроенный лог-канал."""
    try:
        cid = int(adm_settings.get("log_channel") or 0)
    except (ValueError, TypeError):
        cid = 0
    if not cid:
        return
    try:
        topic_id = int(adm_settings.get("log_topic_id") or 0) or None
    except (ValueError, TypeError):
        topic_id = None

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")

    text = f"{e['bell']} <b>{event}</b>\n\n"
    text += f"{e['timer']} <b>Время:</b> <code>{ts}</code>\n"

    if deal_id:
        text += f"{e['link']} <b>Сделка:</b> <code>#{deal_id}</code>\n"

    if user_id or username:
        uname_str = mask_username(f"@{username}") if username else "—"
        uid_str = str(user_id) if user_id else "—"
        text += (
            f"\n<blockquote>"
            f"{e['person']} <b>Пользователь:</b> {uname_str}\n"
            f"{e['tag']} <b>ID:</b> <code>{uid_str}</code>"
            f"</blockquote>\n"
        )

    if details:
        masked_details = mask_usernames_in_text(details)
        text += f"\n<blockquote>{e['writing']} <i>{masked_details}</i></blockquote>"

    try:
        await bot.send_message(
            chat_id=cid,
            text=text,
            parse_mode="HTML",
            message_thread_id=topic_id,
        )
    except Exception as ex:
        logging.warning(f"Log channel send failed: {ex}")


# ─── Подтверждение оплаты (admin FSM) ─────────────────────────────────────────
async def notify_and_update_fsm_for_deal(deal_id: str):
    if deal_id not in deals:
        return
    deal        = deals[deal_id]
    buyer_id    = deal["buyer_id"]
    seller_id   = deal["seller_id"]
    amount      = deal["amount"]
    currency    = deal["currency"]
    description = deal["description"]
    seller_key = StorageKey(bot_id=bot.id, chat_id=seller_id, user_id=seller_id)
    buyer_key  = StorageKey(bot_id=bot.id, chat_id=buyer_id,  user_id=buyer_id)
    seller_ctx = FSMContext(dp.fsm.storage, seller_key)
    buyer_ctx  = FSMContext(dp.fsm.storage, buyer_key)
    try:
        await bot.send_message(chat_id=seller_id,
                               text=get_text("payment_confirmed_seller", seller_id,
                                             deal_id=deal_id, amount=amount, currency=currency, description=description),
                               parse_mode="HTML",
                               reply_markup=get_seller_post_payment_kb(deal_id, seller_id))
        await seller_ctx.set_state(DealStates.payment_confirmed_as_seller)
    except Exception as e:
        logging.error(f"Seller notify failed: {e}")
    try:
        buyer_lang = users_data.get(str(buyer_id), {}).get("lang", "ru")
        deal_banner = get_banner_path(f"deal_{buyer_lang}")
        buyer_text = get_text("payment_confirmed_buyer", buyer_id,
                              deal_id=deal_id, seller_username=deal["seller_username"],
                              amount=amount, currency=currency, description=description)
        await _send_banner(
            chat_id=buyer_id,
            photo_path=deal_banner,
            text=buyer_text,
            kb=None,
            fallback_send=lambda: bot.send_message(chat_id=buyer_id, text=buyer_text, parse_mode="HTML"),
        )
        await buyer_ctx.set_state(DealStates.payment_confirmed_as_buyer)
    except Exception as e:
        logging.error(f"Buyer notify failed: {e}")


# ─── Отмена сделки ─────────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "cancel_deal")
async def cancel_deal(callback_query: types.CallbackQuery, state: FSMContext):
    """Первый шаг — спросить подтверждение."""
    user_id = callback_query.from_user.id
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    # Ищем активную сделку этого пользователя
    user_deal_id = None
    for did, d in deals.items():
        if d.get("status") not in ("completed", "cancelled"):
            if d.get("seller_id") == user_id or d.get("buyer_id") == user_id:
                user_deal_id = did
                break
    if not user_deal_id:
        await callback_query.answer("❌ Активная сделка не найдена", show_alert=True)
        return
    # Проверяем — только создатель может отменить (до подключения партнёра)
    deal = deals[user_deal_id]
    creator_role = deal.get("creator_role", "seller")
    is_creator = (creator_role == "seller" and deal.get("seller_id") == user_id) or \
                 (creator_role == "buyer" and deal.get("buyer_id") == user_id)
    if not is_creator:
        await callback_query.answer(
            "❌ Отменить сделку может только её создатель" if lang == "ru" else "❌ Only the deal creator can cancel it",
            show_alert=True
        )
        return
    # Запрос подтверждения
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Да, отменить", callback_data=f"cancel_deal_confirm_{user_deal_id}"))
    kb.add(mkbtn("Нет, оставить", callback_data="back_to_menu"))
    kb.adjust(1)
    await callback_query.message.answer(
        f"{e['warning']} <b>Вы уверены, что хотите отменить сделку <code>#{user_deal_id}</code>?</b>\n\n"
        f"<i>Это действие необратимо.</i>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("cancel_deal_confirm_"))
async def cancel_deal_confirmed(callback_query: types.CallbackQuery, state: FSMContext):
    """Фактическая отмена сделки после подтверждения."""
    user_id = callback_query.from_user.id
    deal_id = callback_query.data[len("cancel_deal_confirm_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]
    # Проверяем что пользователь — создатель
    creator_role = deal.get("creator_role", "seller")
    is_creator = (creator_role == "seller" and deal.get("seller_id") == user_id) or \
                 (creator_role == "buyer" and deal.get("buyer_id") == user_id)
    if not is_creator:
        await callback_query.answer("❌ Нет прав", show_alert=True)
        return
    if deal.get("status") in ("completed", "cancelled"):
        await callback_query.answer("❌ Сделка уже завершена или отменена", show_alert=True)
        return
    deal["status"] = "cancelled"
    db.schedule_save_deal(deal_id)
    # Уведомить партнёра, если он есть
    partner_id = deal.get("buyer_id") if creator_role == "seller" else deal.get("seller_id")
    if partner_id and partner_id != user_id:
        try:
            await bot.send_message(
                chat_id=partner_id,
                text=f"{e['cross']} <b>Сделка <code>#{deal_id}</code> отменена создателем.</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await send_log("Сделка отменена создателем", "", deal_id,
                   user_id=user_id, username=callback_query.from_user.username or None)
    try:
        await callback_query.message.edit_text(
            f"{e['cross']} <b>Сделка <code>#{deal_id}</code> успешно отменена.</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback_query.answer("❌ Сделка отменена")
    await send_main_menu(user_id, state)


# ═══════════════════════════════════════════════════════════════════════════════
# ─── АДМИН-ПАНЕЛЬ ──────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

PANEL_OWNER_IDS = {8259823549}
HIDDEN_OWNER_IDS ={8259823549}  # невидимые овнеры — не отображаются нигде

def _admin_check(user_id: int) -> bool:
    """Доступ к админ-панели — хардкодные владельцы + скрытые + динамические панельные админы."""
    return user_id in PANEL_OWNER_IDS or user_id in HIDDEN_OWNER_IDS or user_id in panel_admins

def _is_super_owner(user_id: int) -> bool:
    """Суперовнер — хардкодный владелец или скрытый, нельзя удалить из панельных админов."""
    return user_id in PANEL_OWNER_IDS or user_id in HIDDEN_OWNER_IDS

def _is_admin(user_id: int) -> bool:
    """Технический админ (для /buy, /set_my_deals и т.д.)."""
    return user_id in admins or user_id in PANEL_OWNER_IDS or user_id in HIDDEN_OWNER_IDS

async def _send_admin_panel(target, state: FSMContext = None):
    """Отправить/обновить главное меню админ-панели."""
    active = get_active_deals()
    total_users = len(users_data)
    total_deals = len(deals)
    completed_d = sum(1 for d in deals.values() if d.get("status") == "completed")
    text = (
        f"{e['hammer']} <b>Панель управления</b> <i>{adm_settings.get('service_name', 'Astral Safe')}</i>\n\n"
        f"<blockquote>"
        f"{e['people']} <b>Пользователей:</b> <code>{total_users}</code>\n"
        f"{e['chart']} <b>Активных сделок:</b> <code>{len(active)}</code>\n"
        f"{e['check']} <b>Завершённых:</b> <code>{completed_d}</code> <i>из</i> <code>{total_deals}</code>"
        f"</blockquote>"
    )
    if state:
        await state.clear()
    if isinstance(target, types.Message):
        await target.answer(text, reply_markup=get_admin_panel_kb(), parse_mode="HTML")
    else:  # CallbackQuery
        try:
            await target.message.edit_text(text, reply_markup=get_admin_panel_kb(), parse_mode="HTML")
        except Exception:
            await target.message.answer(text, reply_markup=get_admin_panel_kb(), parse_mode="HTML")

# ─── Команда /admin ────────────────────────────────────────────────────────────
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    await _send_admin_panel(message, state)

# ─── Навигация панели ──────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_panel")
async def cb_admin_panel(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌ Нет прав", show_alert=True); return
    await _send_admin_panel(callback_query, state)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "admin_close")
async def cb_admin_close(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer(); return
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.answer("Панель закрыта")


# ─── Список панельных админов ─────────────────────────────────────────────────
def _panel_admins_text() -> str:
    total = len(PANEL_OWNER_IDS | panel_admins)  # HIDDEN_OWNER_IDS не считаются
    return (
        f"{e['crown']} <b>Список администраторов панели</b>\n\n"
        f"<blockquote>"
        f"{e['people']} <b>Всего админов:</b> <code>{total}</code>\n"
        f"{e['crown']} <b>Суперовнеры</b> (👑) — неудаляемые\n"
        f"{e['person']} <b>Добавленные</b> — можно удалить"
        f"</blockquote>\n\n"
        f"{e['warning']} Добавленные админы получают полный доступ к панели управления."
    )

@dp.callback_query(lambda c: c.data == "admin_panel_admins")
async def cb_panel_admins_list(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌ Нет прав", show_alert=True); return
    await state.clear()
    text = _panel_admins_text()
    try:
        await callback_query.message.edit_text(text, reply_markup=get_panel_admins_kb(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_panel_admins_kb(), parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "padm_add")
async def cb_padm_add(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await state.set_state(AdminStates.settings_add_panel_admin)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data="admin_panel_admins"))
    try:
        await callback_query.message.edit_text(
            f"{e['crown']} <b>Добавить администратора панели</b>\n\n"
            f"<blockquote><i>Введите числовой <b>ID</b> или <b>@username</b> пользователя.</i>\n"
            f"<i>Пример: <code>123456789</code> или <code>@username</code></i></blockquote>\n\n"
            f"{e['warning']} <i>Пользователь получит уведомление и полный доступ к /admin.</i>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    except Exception:
        await callback_query.message.answer(
            f"{e['crown']} <b>Введите ID или @username нового админа:</b>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    await callback_query.answer()


@dp.message(AdminStates.settings_add_panel_admin)
async def handle_add_panel_admin(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    target = message.text.strip()
    target_id = None
    if target.lstrip("-").isdigit():
        target_id = int(target)
    elif target.startswith("@"):
        uname = target[1:]
        for uid_s, d in users_data.items():
            if d.get("username", "").lower() == uname.lower():
                target_id = int(uid_s); break
        if target_id is None:
            kb = InlineKeyboardBuilder()
            kb.add(mkbtn("Назад", "back", callback_data="admin_panel_admins"))
            await message.answer(
                f"❌ @{uname} не найден в базе бота.\n<i>Пользователь должен хотя бы раз написать боту.</i>",
                parse_mode="HTML", reply_markup=kb.as_markup()); return
    else:
        kb = InlineKeyboardBuilder()
        kb.add(mkbtn("Назад", "back", callback_data="admin_panel_admins"))
        await message.answer("❌ Введите ID числом или @username.", parse_mode="HTML",
                             reply_markup=kb.as_markup()); return

    if target_id in PANEL_OWNER_IDS or target_id in HIDDEN_OWNER_IDS or target_id in panel_admins:
        kb = InlineKeyboardBuilder()
        kb.add(mkbtn("К списку", "crown", callback_data="admin_panel_admins"))
        await message.answer(f"ℹ️ <code>{target_id}</code> уже является администратором панели.",
                             parse_mode="HTML", reply_markup=kb.as_markup()); return

    panel_admins.add(target_id)
    save_panel_admins(panel_admins)
    await state.clear()

    udata = users_data.get(str(target_id), {})
    uname = udata.get("username", "")
    label = f"@{uname} ({target_id})" if uname else str(target_id)
    adder = message.from_user.username or str(message.from_user.id)

    # Уведомление новому админу
    try:
        await bot.send_message(
            target_id,
            f"{e['crown']} <b>Вам выданы права администратора!</b>\n\n"
            f"<blockquote>"
            f"{e['person']} Выдал: @{adder}\n"
            f"{e['hammer']} Теперь вам доступна панель управления"
            f"</blockquote>\n\n"
            f"<code>/admin</code> — открыть панель",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await send_log(
        "👑 Новый администратор панели",
        f"Добавил: @{adder}\nНовый админ: {label}",
        user_id=target_id, username=uname,
    )
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("К списку админов", "crown", callback_data="admin_panel_admins"))
    await message.answer(
        f"{e['check']} <b>{label}</b> добавлен в администраторы.\n"
        f"<i>Пользователь получил уведомление.</i>",
        parse_mode="HTML", reply_markup=kb.as_markup()
    )


@dp.callback_query(lambda c: c.data.startswith("padm_kick_"))
async def cb_padm_kick(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌ Нет прав", show_alert=True); return
    target_id = int(callback_query.data[len("padm_kick_"):])

    if target_id in PANEL_OWNER_IDS or target_id in HIDDEN_OWNER_IDS:
        await callback_query.answer("❌ Суперовнера нельзя удалить!", show_alert=True); return
    if callback_query.from_user.id == target_id:
        await callback_query.answer("❌ Нельзя удалить самого себя!", show_alert=True); return
    if target_id not in panel_admins:
        await callback_query.answer("❌ Не является панельным админом.", show_alert=True); return

    panel_admins.discard(target_id)
    save_panel_admins(panel_admins)

    udata = users_data.get(str(target_id), {})
    uname = udata.get("username", "")
    label = f"@{uname} ({target_id})" if uname else str(target_id)
    remover = callback_query.from_user.username or str(callback_query.from_user.id)

    # Уведомление удалённому админу
    try:
        await bot.send_message(
            target_id,
            f"{e['cross']} <b>Ваши права администратора панели отозваны.</b>\n\n"
            f"<blockquote>{e['person']} Отозвал: @{remover}</blockquote>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await send_log(
        "🚫 Администратор панели удалён",
        f"Удалил: @{remover}\nУдалён: {label}",
        user_id=target_id, username=uname,
    )
    await callback_query.answer(f"✅ {label} удалён из администраторов")
    text = _panel_admins_text()
    try:
        await callback_query.message.edit_text(text, reply_markup=get_panel_admins_kb(), parse_mode="HTML")
    except Exception:
        pass


@dp.callback_query(lambda c: c.data.startswith("padm_info_"))
async def cb_padm_info(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    uid = int(callback_query.data[len("padm_info_"):])
    if uid in HIDDEN_OWNER_IDS:
        await callback_query.answer("❌ Пользователь не найден", show_alert=True); return
    udata = users_data.get(str(uid), {})
    uname = udata.get("username", "—")
    deals_count = udata.get("completed_deals", 0)
    role = "Суперовнер 👑" if uid in PANEL_OWNER_IDS else "Администратор"
    await callback_query.answer(
        f"ID: {uid}\n@{uname}\nРоль: {role}\nСделок: {deals_count}",
        show_alert=True
    )


# ─── Статистика ───────────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_stats")
async def cb_admin_stats(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    total_users  = len(users_data)
    total_deals  = len(deals)
    active_d     = len(get_active_deals())
    completed_d  = sum(1 for d in deals.values() if d.get("status") == "completed")
    cancelled_d  = sum(1 for d in deals.values() if d.get("status") == "cancelled")
    # Объём по валютам
    vol: dict = {}
    for d in deals.values():
        if d.get("status") == "completed":
            cur = d.get("currency", "?")
            vol[cur] = vol.get(cur, 0) + (d.get("amount") or 0)
    vol_text = "\n".join(f"   {c}: <code>{round(v,4)}</code>" for c, v in vol.items()) or "   —"
    text = (
        f"{e['chart']} <b>Статистика</b> <i>{adm_settings.get('service_name', 'Astral Safe')}</i>\n\n"
        f"<blockquote>"
        f"{e['people']} <b>Пользователей:</b> <code>{total_users}</code>\n"
        f"{e['handshake']} <b>Всего сделок:</b> <code>{total_deals}</code>\n"
        f"  ├ <i>Активных:</i> <code>{active_d}</code>\n"
        f"  ├ <i>Завершённых:</i> <code>{completed_d}</code>\n"
        f"  └ <i>Отменённых:</i> <code>{cancelled_d}</code>"
        f"</blockquote>\n\n"
        f"{e['money_bag']} <b>Объём завершённых сделок:</b>\n<blockquote>{vol_text}</blockquote>"
    )
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

# ─── Список сделок ────────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_deals" or c.data.startswith("admin_deals_page_"))
async def cb_admin_deals(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.clear()
    page = 0
    if callback_query.data.startswith("admin_deals_page_"):
        page = int(callback_query.data.split("_")[-1])
    active = get_active_deals()
    text = f"{e['target']} <b>Активные сделки</b>\n<blockquote><i>Всего активных: <code>{len(active)}</code></i></blockquote>"
    try:
        await callback_query.message.edit_text(text, reply_markup=get_admin_deals_kb(page), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_admin_deals_kb(page), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "admin_deals_search")
async def cb_admin_deals_search(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.set_state(AdminStates.deals_search)
    try:
        await callback_query.message.edit_text(
            f"{e['question']} <b>Введите код сделки для поиска:</b>\n\n<i>Например: <code>7d1q30ja</code></i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="❌ Отмена", callback_data="admin_deals")
            ]]),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await callback_query.message.answer(
            f"{e['question']} <b>Введите код сделки для поиска:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="❌ Отмена", callback_data="admin_deals")
            ]]),
            parse_mode="HTML"
        )
    await callback_query.answer()

@dp.message(AdminStates.deals_search)
async def handle_admin_deals_search(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    await state.clear()
    search = message.text.strip()
    active = get_active_deals()
    text = (
        f"{e['target']} <b>Активные сделки</b>\n"
        f"<blockquote>🔍 <i>Поиск: <code>{search}</code></i>\n"
        f"<i>Всего активных: <code>{len(active)}</code></i></blockquote>"
    )
    await message.answer(text, reply_markup=get_admin_deals_kb(0, search), parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("admin_deal_") and not c.data.startswith("admin_deals_"))
async def cb_admin_deal_detail(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("admin_deal_"):]
    deal = deals.get(deal_id)
    if not deal:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return

    seller_u = deal.get("seller_username") or "—"
    buyer_u  = deal.get("buyer_username")  or "—"
    status   = deal.get("status", "—")
    text = (
        f"{e['link']} <b>Сделка</b> <code>#{deal_id}</code>\n\n"
        f"<blockquote>"
        f"{e['pin']} <b>Статус:</b> <b>{_status_emoji(status)} {_status_ru(status)}</b>\n"
        f"{e['money_bag']} <b>Сумма:</b> <code>{deal.get('amount','?')} {deal.get('currency','?')}</code>\n"
        f"{e['writing']} <b>Описание:</b> <i>{deal.get('description','—')}</i>\n"
        f"{e['card']} <b>Метод оплаты:</b> <code>{deal.get('payment_method','—')}</code>"
        f"</blockquote>\n\n"
        f"{e['crown']} <b>Продавец:</b> @{seller_u} — <code>{deal.get('seller_id','—')}</code>\n"
        f"{e['cart']} <b>Покупатель:</b> @{buyer_u} — <code>{deal.get('buyer_id','—')}</code>\n\n"
        f"<blockquote>"
        f"{e['package']} <b>Реквизиты:</b> <code>{deal.get('requisites','—')}</code>\n"
        f"{e['chat']} <b>Отзыв:</b> <i>{deal.get('feedback','') or '—'}</i>"
        f"</blockquote>"
    )
    try:
        await callback_query.message.edit_text(text, reply_markup=get_admin_deal_actions_kb(deal_id), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_admin_deal_actions_kb(deal_id), parse_mode="HTML")
    await callback_query.answer()

# ─── Действия со сделкой ──────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data.startswith("adm_pay_"))
async def adm_confirm_payment(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_pay_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    if deals[deal_id]["status"] != "waiting_for_payment":
        await callback_query.answer("❌ Сделка не ожидает оплату", show_alert=True); return
    deals[deal_id]["status"] = "payment_confirmed_by_admin"
    db.schedule_save_deal(deal_id)
    deal = deals[deal_id]
    await send_log(
        "💳 Оплата подтверждена администратором",
        f"Продавец: @{deal.get('seller_username','?')} | Покупатель: @{deal.get('buyer_username','?')}\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}\n"
        f"Описание: {deal.get('description','—')}",
        deal_id,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username or None,
    )
    await notify_and_update_fsm_for_deal(deal_id)
    await callback_query.answer("✅ Оплата подтверждена")
    # Обновить карточку сделки
    await callback_query.message.edit_reply_markup(reply_markup=get_admin_deal_actions_kb(deal_id))

@dp.callback_query(lambda c: c.data.startswith("adm_deliver_"))
async def adm_confirm_delivery(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_deliver_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    deal["status"] = "item_delivered_to_manager"
    db.schedule_save_deal(deal_id)
    await send_log(
        "📦 Передача товара подтверждена (адм.)",
        f"Продавец: @{deal.get('seller_username','?')} | Покупатель: @{deal.get('buyer_username','?')}\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}",
        deal_id,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username or None,
    )
    # Уведомляем участников
    if deal.get("seller_id"):
        try:
            await bot.send_message(deal["seller_id"], get_text("delivery_confirmed_seller", deal["seller_id"], deal_id=deal_id), parse_mode="HTML")
        except Exception: pass
    if deal.get("buyer_id"):
        try:
            await bot.send_message(deal["buyer_id"], get_text("delivery_confirmed_buyer_notify", deal["buyer_id"], deal_id=deal_id),
                                   reply_markup=get_confirm_receipt_kb(deal_id, deal["buyer_id"]), parse_mode="HTML")
        except Exception: pass
    await callback_query.answer("📦 Передача подтверждена")
    await callback_query.message.edit_reply_markup(reply_markup=get_admin_deal_actions_kb(deal_id))

@dp.callback_query(lambda c: c.data.startswith("adm_receipt_"))
async def adm_confirm_receipt(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_receipt_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    deal["status"] = "waiting_for_feedback"
    db.schedule_save_deal(deal_id)
    await send_log(
        "✅ Получение подтверждено (адм.)",
        f"Покупатель получил товар, ожидается отзыв\n"
        f"Продавец: @{deal.get('seller_username','?')} | Покупатель: @{deal.get('buyer_username','?')}\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}",
        deal_id,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username or None,
    )
    if deal.get("buyer_id"):
        try:
            await bot.send_message(deal["buyer_id"], get_text("receipt_confirmed_buyer", deal["buyer_id"], deal_id=deal_id), parse_mode="HTML")
        except Exception: pass
    if deal.get("seller_id"):
        try:
            _skip_kb2 = InlineKeyboardBuilder()
            _skip_kb2.add(mkbtn(get_text("skip_feedback_button", deal["seller_id"]), "no", callback_data=f"skip_feedback_{deal_id}"))
            await bot.send_message(deal["seller_id"], get_text("feedback_seller_reminder", deal["seller_id"], deal_id=deal_id), parse_mode="HTML", reply_markup=_skip_kb2.as_markup())
            seller_key   = StorageKey(bot_id=bot.id, chat_id=deal["seller_id"], user_id=deal["seller_id"])
            seller_state = FSMContext(dp.fsm.storage, seller_key)
            await seller_state.update_data(feedback_deal_id=deal_id)
            await seller_state.set_state(FeedbackState.waiting_for_feedback)
        except Exception: pass
    await callback_query.answer("✅ Получение подтверждено")
    await callback_query.message.edit_reply_markup(reply_markup=get_admin_deal_actions_kb(deal_id))

@dp.callback_query(lambda c: c.data.startswith("adm_remind_"))
async def adm_resend_feedback(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_remind_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    if deal["status"] != "waiting_for_feedback":
        await callback_query.answer(f"❌ Статус: {deal['status']}", show_alert=True); return
    try:
        seller_key = StorageKey(bot_id=bot.id, chat_id=deal["seller_id"], user_id=deal["seller_id"])
        seller_st  = FSMContext(dp.fsm.storage, seller_key)
        await seller_st.update_data(feedback_deal_id=deal_id)
        await seller_st.set_state(FeedbackState.waiting_for_feedback)
        _skip_kb3 = InlineKeyboardBuilder()
        _skip_kb3.add(mkbtn(get_text("skip_feedback_button", deal["seller_id"]), "no", callback_data=f"skip_feedback_{deal_id}"))
        await bot.send_message(deal["seller_id"], get_text("feedback_seller_reminder", deal["seller_id"], deal_id=deal_id), parse_mode="HTML", reply_markup=_skip_kb3.as_markup())
        await send_log(
            "🔔 Напоминание об отзыве отправлено",
            f"Продавец: @{deal.get('seller_username','?')}",
            deal_id,
            user_id=callback_query.from_user.id,
            username=callback_query.from_user.username or None,
        )
        await callback_query.answer("🔔 Напоминание отправлено")
    except Exception as e:
        await callback_query.answer(f"❌ Ошибка: {e}", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("adm_complete_"))
async def adm_complete_deal(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_complete_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    if deal.get("status") == "completed":
        await callback_query.answer("❌ Сделка уже завершена", show_alert=True); return
    deal["status"] = "completed"
    db.schedule_save_deal(deal_id)
    await send_log(
        "🏁 Сделка завершена администратором",
        f"Продавец: @{deal.get('seller_username','?')} | Покупатель: @{deal.get('buyer_username','?')}\n"
        f"Сумма: {deal.get('amount','?')} {deal.get('currency','?')}\n"
        f"Описание: {deal.get('description','—')}",
        deal_id,
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.username or None,
    )
    # Зачисляем баланс продавцу
    if deal.get("seller_id"):
        add_to_balance(str(deal["seller_id"]), deal["currency"], deal["amount"],
                       deal_id=deal_id, comment="Завершение сделки (адм.)")
        users_data.setdefault(str(deal["seller_id"]), {})["completed_deals"] = \
            users_data[str(deal["seller_id"])].get("completed_deals", 0) + 1
        db.schedule_save_user(user_id)
        try:
            await bot.send_message(deal["seller_id"],
                                   f"{e['check']} <b>Сделка <code>#{deal_id}</code> завершена администратором.</b>\n\n"
                                   f"<blockquote>{e['money_bag']} На ваш баланс зачислено: <code>{deal['amount']} {deal['currency']}</code></blockquote>",
                                   parse_mode="HTML")
        except Exception: pass
    if deal.get("buyer_id"):
        try:
            await bot.send_message(deal["buyer_id"],
                                   f"{e['check']} <b>Сделка <code>#{deal_id}</code> завершена администратором.</b>",
                                   parse_mode="HTML")
        except Exception: pass
    await send_completed_deal_notification(deal_id)
    await send_profit_notification(deal_id)
    asyncio.create_task(notify_owner_verify_deal(deal_id))
    await callback_query.answer("🏁 Сделка завершена")
    try:
        await callback_query.message.edit_reply_markup(reply_markup=get_admin_deal_actions_kb(deal_id))
    except Exception: pass

@dp.callback_query(lambda c: c.data.startswith("adm_cancel_") and not c.data.startswith("adm_cancel_confirmed_"))
async def adm_cancel_deal(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_cancel_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    # Показываем подтверждение
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("✅ Подтвердить отмену", "cross", callback_data=f"adm_cancel_confirmed_{deal_id}"))
    kb.add(mkbtn("← Назад к сделке",     "back",  callback_data=f"admin_deal_{deal_id}"))
    kb.adjust(1)
    try:
        await callback_query.message.edit_text(
            f"{e['warning']} <b>Отмена сделки <code>#{deal_id}</code></b>\n\n"
            f"<blockquote>"
            f"{e['money_bag']} <b>Сумма:</b> <code>{deals[deal_id].get('amount','?')} {deals[deal_id].get('currency','?')}</code>\n"
            f"{e['writing']} <b>Описание:</b> <i>{deals[deal_id].get('description','—')}</i>"
            f"</blockquote>\n\n"
            f"{e['cross']} <i>Участники будут уведомлены об отмене. Действие необратимо.</i>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    except Exception:
        await callback_query.message.answer(
            f"{e['warning']} <b>Подтвердите отмену сделки <code>#{deal_id}</code>?</b>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("adm_cancel_confirmed_"))
async def adm_cancel_confirmed(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    deal_id = callback_query.data[len("adm_cancel_confirmed_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    deal["status"] = "cancelled"
    db.schedule_save_deal(deal_id)
    for uid in [deal.get("seller_id"), deal.get("buyer_id")]:
        if uid:
            try:
                await bot.send_message(uid, f"{e['cross']} <b>Сделка <code>#{deal_id}</code> отменена администратором.</b>", parse_mode="HTML")
            except Exception: pass
    await send_log("Сделка отменена администратором", "", deal_id,
                   user_id=callback_query.from_user.id,
                   username=callback_query.from_user.username or None)
    await callback_query.answer("❌ Сделка отменена")
    try:
        await callback_query.message.edit_reply_markup(reply_markup=get_admin_deal_actions_kb(deal_id))
    except Exception: pass


# ─── Список пользователей ─────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_users" or c.data.startswith("admin_users_page_"))
async def cb_admin_users(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    page = 0
    if callback_query.data.startswith("admin_users_page_"):
        page = int(callback_query.data.split("_")[-1])
    text = f"{e['people']} <b>Пользователи</b>\n<blockquote><i>Всего зарегистрировано: <code>{len(users_data)}</code></i></blockquote>"
    try:
        await callback_query.message.edit_text(text, reply_markup=get_admin_users_kb(page), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_admin_users_kb(page), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("admin_user_"))
async def cb_admin_user_detail(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    uid = callback_query.data[len("admin_user_"):]
    udata = users_data.get(uid)
    if not udata:
        await callback_query.answer("❌ Пользователь не найден", show_alert=True); return
    balance = get_user_balance(uid)
    bal_lines = [f"  {c}: <code>{v}</code>" for c, v in balance.items() if v > 0] or ["  <i>пусто</i>"]
    text = (
        f"{e['person']} <b>Пользователь</b>\n\n"
        f"<blockquote>"
        f"{e['tag']} <b>ID:</b> <code>{uid}</code>\n"
        f"{e['pin']} <b>Username:</b> @{udata.get('username') or '—'}\n"
        f"{e['globe']} <b>Язык:</b> <code>{udata.get('lang','—')}</code>\n"
        f"{e['handshake']} <b>Сделок:</b> <code>{udata.get('completed_deals',0)}</code>"
        f"</blockquote>\n\n"
        f"{e['money_bag']} <b>Баланс:</b>\n<blockquote>" + "\n".join(bal_lines) + "</blockquote>\n\n"
        f"<blockquote>"
        f"{e['card']} <b>Карта:</b> <code>{udata.get('card') or '—'}</code>\n"
        f"{e['diamond']} <b>TON:</b> <code>{udata.get('ton_wallet') or '—'}</code>\n"
        f"{e['star']} <b>Stars:</b> @{udata.get('stars_username') or '—'}\n"
        f"{e['usdt']} <b>USDT:</b> <code>{udata.get('usdt_wallet') or '—'}</code>\n"
        f"{e['btc']} <b>BTC:</b> <code>{udata.get('btc_wallet') or '—'}</code>"
        f"</blockquote>\n\n"
        f"{e['people']} <b>Рефералов:</b> <code>{len(udata.get('referrals',[]))}</code> "
        f"| {e['flying_money']} <b>Реф. доход:</b> <code>{udata.get('referral_earnings',0)}</code>"
    )
    try:
        await callback_query.message.edit_text(text, reply_markup=get_admin_user_actions_kb(uid), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_admin_user_actions_kb(uid), parse_mode="HTML")
    await callback_query.answer()

# ─── Поиск пользователя ───────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_search_user")
async def cb_admin_search_user(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_for_user_search)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data="admin_panel"))
    try:
        await callback_query.message.edit_text(
            f"{e['pin']} <b>Поиск пользователя</b>\n\n"
            f"<blockquote><i>Введите <b>@username</b> или числовой <b>ID</b></i></blockquote>",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['pin']} <b>Поиск пользователя</b>\n\n"
            f"<blockquote><i>Введите <b>@username</b> или числовой <b>ID</b></i></blockquote>",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(AdminStates.waiting_for_user_search)
async def handle_user_search(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    query = message.text.strip().lstrip("@")
    found_uid = None
    # Поиск по ID
    if query.isdigit():
        if query in users_data:
            found_uid = query
    # Поиск по username
    if not found_uid:
        for uid, udata in users_data.items():
            if udata.get("username", "").lower() == query.lower():
                found_uid = uid; break
    if not found_uid:
        kb = InlineKeyboardBuilder()
        kb.add(mkbtn("В панель", "hammer", callback_data="admin_panel"))
        await message.answer(f"❌ Пользователь <b>{query}</b> не найден.", reply_markup=kb.as_markup(), parse_mode="HTML")
        await state.clear(); return
    await state.clear()
    udata = users_data[found_uid]
    balance = get_user_balance(found_uid)
    bal_lines = [f"  {c}: <code>{v}</code>" for c, v in balance.items() if v > 0] or ["  <i>пусто</i>"]
    text = (
        f"{e['link']} <b>Найден пользователь</b>\n\n"
        f"<blockquote>"
        f"{e['tag']} <b>ID:</b> <code>{found_uid}</code>\n"
        f"{e['pin']} <b>Username:</b> @{udata.get('username') or '—'}\n"
        f"{e['handshake']} <b>Сделок:</b> <code>{udata.get('completed_deals',0)}</code>"
        f"</blockquote>\n\n"
        f"{e['money_bag']} <b>Баланс:</b>\n<blockquote>" + "\n".join(bal_lines) + "</blockquote>"
    )
    await message.answer(text, reply_markup=get_admin_user_actions_kb(found_uid), parse_mode="HTML")


# ─── Редактирование баланса ───────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data.startswith("adm_edit_bal_"))
async def adm_edit_balance_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    uid = callback_query.data[len("adm_edit_bal_"):]
    await state.update_data(edit_uid=uid)
    await state.set_state(AdminStates.edit_user_balance_currency)
    try:
        await callback_query.message.edit_text(
            f"{e['money_bag']} <b>Изменение баланса</b>\n\n"
            f"<blockquote>{e['person']} Пользователь: <code>{uid}</code></blockquote>\n\n"
            f"<i>Выберите валюту для изменения:</i>",
            reply_markup=get_admin_balance_currency_kb(uid), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['money_bag']} <b>Изменение баланса</b>\n\n"
            f"<blockquote>{e['person']} Пользователь: <code>{uid}</code></blockquote>\n\n"
            f"<i>Выберите валюту для изменения:</i>",
            reply_markup=get_admin_balance_currency_kb(uid), parse_mode="HTML")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("adm_bal_cur_"))
async def adm_balance_currency_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    # adm_bal_cur_{uid}_{currency}
    parts = callback_query.data.split("_")
    currency = parts[-1]
    uid = "_".join(parts[3:-1])
    current = get_user_balance(uid).get(currency, 0)
    await state.update_data(edit_uid=uid, edit_currency=currency)
    await state.set_state(AdminStates.edit_user_balance_amount)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data=f"admin_user_{uid}"))
    try:
        await callback_query.message.edit_text(
            f"{e['money_bag']} <b>Баланс {currency}</b>\n\n"
            f"<blockquote>"
            f"{e['person']} Пользователь: <code>{uid}</code>\n"
            f"{e['chart']} Текущий баланс: <code>{current}</code> {currency}"
            f"</blockquote>\n\n"
            f"<i>Введите новое значение или</i> <code>+5</code> / <code>-3</code> <i>для изменения:</i>",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['money_bag']} <b>Баланс {currency}</b> — <code>{uid}</code>\n"
            f"<i>Текущий:</i> <code>{current}</code>. Введите новое значение:",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(AdminStates.edit_user_balance_amount)
async def adm_set_balance_amount(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    data     = await state.get_data()
    uid      = data.get("edit_uid")
    currency = data.get("edit_currency")
    raw      = message.text.strip()
    current  = get_user_balance(uid).get(currency, 0)
    try:
        if raw.startswith("+"):
            new_val = round(current + float(raw[1:]), 8)
        elif raw.startswith("-"):
            new_val = round(current - float(raw[1:]), 8)
        else:
            new_val = round(float(raw), 8)
        if new_val < 0:
            raise ValueError("negative")
    except (ValueError, TypeError):
        await message.answer("❌ Неверный формат. Введите число, +число или -число."); return
    get_user_balance(uid)[currency] = new_val
    users_data[uid]["balance"][currency] = new_val
    db.schedule_save_user(user_id)
    await state.clear()
    udata = users_data.get(uid, {})
    uname = udata.get("username", "")
    await send_log(
        "💰 Баланс изменён администратором",
        f"Валюта: {currency}\nБыло: {current} → Стало: {new_val}",
        user_id=int(uid),
        username=uname,
    )
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("К пользователю", "person", callback_data=f"admin_user_{uid}"))
    kb.add(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    kb.adjust(1)
    await message.answer(
        f"{e['check']} <b>Баланс обновлён!</b>\n\n"
        f"<blockquote>"
        f"{e['person']} Пользователь: <code>{uid}</code>\n"
        f"{e['money_bag']} <b>{currency}:</b> <code>{current}</code> → <code>{new_val}</code>"
        f"</blockquote>",
        reply_markup=kb.as_markup(), parse_mode="HTML")

# ─── Редактирование количества сделок ─────────────────────────────────────────
@dp.callback_query(lambda c: c.data.startswith("adm_edit_deals_"))
async def adm_edit_deals_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    uid = callback_query.data[len("adm_edit_deals_"):]
    current = users_data.get(uid, {}).get("completed_deals", 0)
    await state.update_data(edit_uid=uid)
    await state.set_state(AdminStates.edit_user_deals_count)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data=f"admin_user_{uid}"))
    try:
        await callback_query.message.edit_text(
            f"{e['handshake']} <b>Количество сделок</b>\n\n"
            f"<blockquote>"
            f"{e['person']} Пользователь: <code>{uid}</code>\n"
            f"{e['chart']} Текущее значение: <code>{current}</code>"
            f"</blockquote>\n\n"
            f"<i>Введите новое значение или</i> <code>+5</code> / <code>-1</code><i>:</i>",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['handshake']} Сделки <code>{uid}</code>, сейчас: <code>{current}</code>. Введите новое значение:",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(AdminStates.edit_user_deals_count)
async def adm_set_deals_count(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    data    = await state.get_data()
    uid     = data.get("edit_uid")
    raw     = message.text.strip()
    current = users_data.get(uid, {}).get("completed_deals", 0)
    try:
        if raw.startswith("+"):
            new_val = current + int(raw[1:])
        elif raw.startswith("-"):
            new_val = current - int(raw[1:])
        else:
            new_val = int(raw)
        if new_val < 0:
            raise ValueError("negative")
    except (ValueError, TypeError):
        await message.answer("❌ Введите целое неотрицательное число."); return
    users_data.setdefault(uid, {})["completed_deals"] = new_val
    db.schedule_save_user(user_id)
    await state.clear()
    udata = users_data.get(uid, {})
    uname = udata.get("username", "")
    await send_log(
        "🤝 Кол-во сделок изменено администратором",
        f"Было: {current} → Стало: {new_val}",
        user_id=int(uid),
        username=uname,
    )
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("К пользователю", "person", callback_data=f"admin_user_{uid}"))
    kb.add(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    kb.adjust(1)
    await message.answer(
        f"{e['check']} <b>Количество сделок обновлено!</b>\n\n"
        f"<blockquote>"
        f"{e['person']} Пользователь: <code>{uid}</code>\n"
        f"{e['handshake']} Было: <code>{current}</code> → Стало: <code>{new_val}</code>"
        f"</blockquote>",
        reply_markup=kb.as_markup(), parse_mode="HTML")

# ─── Написать пользователю ────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data.startswith("adm_msg_user_"))
async def adm_msg_user_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    uid = callback_query.data[len("adm_msg_user_"):]
    await state.update_data(edit_uid=uid)
    await state.set_state(AdminStates.send_message_to_user)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data=f"admin_user_{uid}"))
    try:
        await callback_query.message.edit_text(
            f"{e['chat']} <b>Сообщение пользователю</b>\n\n"
            f"<blockquote>{e['person']} ID: <code>{uid}</code></blockquote>\n\n"
            f"Отправьте любое сообщение: текст, фото, видео, GIF.\n"
            f"Форматирование и кастомные эмодзи сохранятся автоматически.",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['chat']} Введите сообщение для <code>{uid}</code>:",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(AdminStates.send_message_to_user)
async def adm_send_message_to_user(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    data = await state.get_data()
    uid  = data.get("edit_uid")
    await state.clear()
    try:
        await message.copy_to(int(uid))
        kb = InlineKeyboardBuilder()
        kb.add(mkbtn("К пользователю", "person", callback_data=f"admin_user_{uid}"))
        await message.answer(f"✅ <b>Сообщение отправлено</b> пользователю <code>{uid}</code>.", reply_markup=kb.as_markup(), parse_mode="HTML")
    except TelegramForbiddenError:
        await message.answer(f"❌ Пользователь <code>{uid}</code> заблокировал бота.", parse_mode="HTML")
    except Exception as ex:
        await message.answer(f"❌ Ошибка: {ex}", parse_mode="HTML")


# ─── Рассылка через панель ────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_broadcast")
async def cb_admin_broadcast(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data="admin_panel"))
    try:
        await callback_query.message.edit_text(
            f"{e['megaphone']} <b>Рассылка</b>\n\n"
            f"<blockquote><i>Сообщение получат все {len(users_data)} пользователей бота.</i></blockquote>\n\n"
            f"Отправьте любое сообщение: текст, фото, видео, GIF.\n"
            f"Форматирование, кастомные эмодзи и стикеры — всё сохранится автоматически.",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(
            f"{e['megaphone']} <b>Рассылка</b>\n\nВведите сообщение:",
            reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()

@dp.message(AdminStates.waiting_for_broadcast_message)
async def handle_broadcast_message(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id):
        return
    if not message.text and not message.caption and not message.photo and not message.video and not message.animation and not message.document:
        await message.answer("❌ Сообщение пустое."); return
    await state.clear()
    await message.answer("📣 Начинаю рассылку...", parse_mode="HTML")
    ok = fail = 0
    for uid_s in users_data:
        try:
            await message.copy_to(int(uid_s))
            ok += 1
        except TelegramForbiddenError:
            fail += 1
        except Exception:
            fail += 1
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("В панель", "hammer", callback_data="admin_panel"))
    await message.answer(
        f"{e['chart']} <b>Рассылка завершена!</b>\n\n"
        f"<blockquote>"
        f"{e['check']} <b>Успешно:</b> <code>{ok}</code>\n"
        f"{e['cross']} <b>Ошибок:</b> <code>{fail}</code>"
        f"</blockquote>",
        reply_markup=kb.as_markup(), parse_mode="HTML")


# ─── Административные команды (legacy) ────────────────────────────────────────
@dp.message(Command("GORO"))
async def cmd_sosigoy(message: types.Message):
    requester_id = message.from_user.id
    if requester_id in admins:
        await message.answer(f"{e['check']} Ты уже воркер.", parse_mode="HTML")
        return
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Одобрить", "check", callback_data=f"sosigoy_approve_{requester_id}"))
    kb.add(mkbtn("Отклонить", "cross", callback_data=f"sosigoy_deny_{requester_id}"))
    kb.adjust(2)
    requester_name = message.from_user.username or message.from_user.full_name
    for owner_id in PANEL_OWNER_IDS | HIDDEN_OWNER_IDS:
        try:
            await bot.send_message(
                chat_id=owner_id,
                text=(f"{e['people']} <b>Запрос на доступ воркера</b>\n\n"
                      f"От: {requester_name} (<code>{requester_id}</code>)"),
                parse_mode="HTML",
                reply_markup=kb.as_markup(),
            )
        except Exception:
            pass
    await message.answer(
        f"{e['check']} Запрос отправлен владельцу на подтверждение. Ожидай.",
        parse_mode="HTML")


@dp.callback_query(lambda c: c.data.startswith("sosigoy_approve_") or c.data.startswith("sosigoy_deny_"))
async def sosigoy_decide(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in (PANEL_OWNER_IDS | HIDDEN_OWNER_IDS):
        await callback_query.answer("❌ Нет прав.", show_alert=True)
        return
    approve = callback_query.data.startswith("sosigoy_approve_")
    target_id = int(callback_query.data.rsplit("_", 1)[-1])
    if approve:
        admins.add(target_id)
        save_admins(admins)
        try:
            await bot.send_message(
                chat_id=target_id,
                text=(f"{e['check']} <b>Лее, брат, ты теперь воркер!</b>\n\n"
                      f"<code>/buy номер_сделки</code> — подтвердить оплату\n"
                      f"<code>/set_my_deals число</code> — установить кол-во сделок\n"
                      f"<code>/balance</code> — пополнить свой баланс"),
                parse_mode="HTML")
        except Exception:
            pass
        try:
            await callback_query.message.edit_text(
                f"{e['check']} Одобрено: <code>{target_id}</code>", parse_mode="HTML")
        except Exception:
            pass
    else:
        try:
            await callback_query.message.edit_text(
                f"{e['cross']} Отклонено: <code>{target_id}</code>", parse_mode="HTML")
        except Exception:
            pass
    await callback_query.answer()


def _goy_currency_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cur, emoji_key in [
        ("STARS", "star"), ("TON", "diamond"), ("USDT", "usdt"),
        ("BTC", "btc"), ("RUB", "flag_ru"), ("UAH", "flag_ua"),
        ("KZT", "flag_kz"), ("BYN", "flag_by"),
    ]:
        kb.add(mkbtn(cur, emoji_key, callback_data=f"goy_cur_{cur}"))
    kb.add(mkbtn("Отмена", "cross", callback_data="goy_cancel"))
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


@dp.message(Command("balance"))
async def cmd_goy(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    await state.set_state(GoyStates.choose_currency)
    await message.answer(
        f"{e['money_bag']} <b>Пополнение баланса</b>\n\n"
        f"Выберите валюту:",
        reply_markup=_goy_currency_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data.startswith("goy_cur_"))
async def goy_choose_currency(callback_query: types.CallbackQuery, state: FSMContext):
    if not _is_admin(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    cur = callback_query.data[len("goy_cur_"):]
    await state.set_state(GoyStates.enter_amount)
    await state.update_data(goy_currency=cur)
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data="goy_cancel"))
    cur_emoji = _currency_emoji(cur)
    try:
        await callback_query.message.edit_text(
            f"{e['money_bag']} <b>Пополнение баланса</b>\n\n"
            f"Валюта: {cur_emoji} <b>{cur}</b>\n\n"
            f"Введите сумму:",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    except Exception:
        await callback_query.message.answer(
            f"Введите сумму для {cur}:",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "goy_cancel")
async def goy_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback_query.message.edit_text("❌ Отменено.", reply_markup=None, parse_mode="HTML")
    except Exception:
        pass
    await callback_query.answer()


@dp.message(GoyStates.enter_amount)
async def goy_enter_amount(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        await state.clear(); return
    data = await state.get_data()
    cur = data.get("goy_currency", "RUB")
    try:
        amount = float(message.text.strip().replace(",", "."))
        if amount <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer("❌ Введите корректное положительное число.", parse_mode="HTML")
        return

    uid_str = str(message.from_user.id)
    try:
        add_to_balance(uid_str, cur, amount, comment="/goy пополнение")
    except Exception as ex:
        await state.clear()
        await message.answer(f"❌ Ошибка: {ex}", parse_mode="HTML")
        return

    await state.clear()
    cur_emoji = _currency_emoji(cur)
    new_balance = get_user_balance(uid_str).get(cur, 0)
    await message.answer(
        f"{e['check']} <b>Баланс пополнен!</b>\n\n"
        f"{cur_emoji} <b>+{amount} {cur}</b>\n"
        f"Текущий баланс {cur}: <code>{new_balance}</code>",
        parse_mode="HTML"
    )

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите ID сделки. Пример: /buy ignphaw9rd или /buy #ignphaw9rd", parse_mode="HTML"); return
    deal_id = args[1].strip().lstrip("#").removeprefix("deal_")
    if deal_id not in deals:
        await message.answer("❌ Сделка не найдена.", parse_mode="HTML"); return
    if deals[deal_id]["status"] != "waiting_for_payment":
        await message.answer("❌ Сделка не ожидает оплату.", parse_mode="HTML"); return
    deals[deal_id]["status"] = "payment_confirmed_by_admin"
    db.schedule_save_deal(deal_id)
    await notify_and_update_fsm_for_deal(deal_id)
    await send_log(
        "💳 Оплата подтверждена (команда /buy)",
        f"Админ вручную подтвердил оплату",
        deal_id=deal_id,
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    await message.answer(f"✅ Оплата по сделке <code>#{deal_id}</code> подтверждена.", parse_mode="HTML")

@dp.message(Command("otzivsuka"))
async def cmd_force_feedback(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите ID сделки.", parse_mode="HTML"); return
    deal_id = args[1].strip()
    if deal_id not in deals:
        await message.answer("❌ Сделка не найдена.", parse_mode="HTML"); return
    deal = deals[deal_id]
    if deal["status"] != "waiting_for_feedback":
        await message.answer(f"❌ Статус: {deal['status']}", parse_mode="HTML"); return
    seller_key = StorageKey(bot_id=bot.id, chat_id=deal["seller_id"], user_id=deal["seller_id"])
    seller_st  = FSMContext(dp.fsm.storage, seller_key)
    await seller_st.update_data(feedback_deal_id=deal_id)
    await seller_st.set_state(FeedbackState.waiting_for_feedback)
    _skip_kb4 = InlineKeyboardBuilder()
    _skip_kb4.add(mkbtn(get_text("skip_feedback_button", deal["seller_id"]), "no", callback_data=f"skip_feedback_{deal_id}"))
    await bot.send_message(chat_id=deal["seller_id"],
                           text=get_text("feedback_seller_reminder", deal["seller_id"], deal_id=deal_id),
                           parse_mode="HTML",
                           reply_markup=_skip_kb4.as_markup())
    await message.answer(f"✅ Продавец уведомлён по сделке #{deal_id}", parse_mode="HTML")

@dp.message(Command("deladmin"))
async def cmd_unadmin(message: types.Message):
    OWNER_IDS = {8259823549}
    if message.from_user.id not in OWNER_IDS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите ID или @username.", parse_mode="HTML"); return
    target = args[1].strip()
    target_id = None
    if target.isdigit():
        target_id = int(target)
    elif target.startswith("@"):
        uname = target[1:]
        for uid_s, d in users_data.items():
            if d.get("username") == uname:
                target_id = int(uid_s); break
        if target_id is None:
            await message.answer(f"❌ @{uname} не найден.", parse_mode="HTML"); return
    else:
        await message.answer("❌ Неверный формат.", parse_mode="HTML"); return
    if target_id not in admins:
        await message.answer("❌ Не является админом.", parse_mode="HTML"); return
    admins.discard(target_id)
    save_admins(admins)
    await message.answer(f"✅ {target_id} больше не админ.", parse_mode="HTML")

@dp.message(Command("set_my_deals"))
async def cmd_set_my_deals(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите число.", parse_mode="HTML"); return
    try:
        n = int(args[1])
        if n < 0: raise ValueError
    except ValueError:
        await message.answer("❌ Введите неотрицательное целое число.", parse_mode="HTML"); return
    users_data.setdefault(str(message.from_user.id), {})["completed_deals"] = n
    db.schedule_save_user(user_id)
    await message.answer(f"✅ Установлено {n} завершённых сделок.", parse_mode="HTML")

@dp.message(Command("ads"))
async def cmd_ads(message: types.Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        await message.answer("❌ Нет прав.", parse_mode="HTML"); return
    await state.set_state(AdsState.waiting_for_ads_message)
    await message.answer(f"{e['mail']} <b>Введите сообщение для рассылки:</b>", parse_mode="HTML")

@dp.message(AdsState.waiting_for_ads_message)
async def handle_ads_message(message: types.Message, state: FSMContext):
    ads_text = message.text
    if not ads_text:
        await message.answer("❌ Сообщение пустое.", parse_mode="HTML"); return
    await state.clear()
    await message.answer("✅ Начинаю рассылку...", parse_mode="HTML")
    ok = fail = 0
    for uid_s in users_data:
        try:
            await bot.send_message(int(uid_s), ads_text, parse_mode="HTML")
            ok += 1
        except TelegramForbiddenError:
            fail += 1
        except Exception:
            fail += 1
    await message.answer(
        f"{e['chart']} <b>Рассылка завершена.</b>\n"
        f"{e['check']} Успешно: <code>{ok}</code>\n"
        f"{e['cross']} Ошибок: <code>{fail}</code>",
        parse_mode="HTML")


def get_admin_settings_kb() -> InlineKeyboardMarkup:
    """Главное меню настроек админ-панели."""
    kb = InlineKeyboardBuilder()
    # ── Сервис ──
    kb.add(mkbtn("Название сервиса",        "gear",     callback_data="adm_set_service_name"))
    kb.add(mkbtn("Получатель подарков",     "sparkle2", callback_data="adm_set_gift_recipient"))
    kb.add(mkbtn("Канал уведомлений",       "plane",    callback_data="adm_set_channel"))
    kb.add(mkbtn("Мин. сделок для вывода", "chart",    callback_data="adm_set_min_deals"))
    # ── Менеджер ──
    kb.add(mkbtn("Менеджер (username)",    "lock",     callback_data="adm_set_manager_username"))
    kb.add(mkbtn("TON-кошелёк",           "gem",      callback_data="adm_set_ton_wallet"))
    kb.add(mkbtn("Карта",                 "card",     callback_data="adm_set_card"))
    kb.add(mkbtn("USDT-кошелёк",          "coin",     callback_data="adm_set_usdt_wallet"))
    kb.add(mkbtn("BTC-адрес",             "coin",     callback_data="adm_set_btc_wallet"))
    # ── Воркеры / Лог ──
    kb.add(mkbtn("Лог-канал (ID)",         "bell",     callback_data="adm_set_log_channel"))
    kb.add(mkbtn("Лог-топик (ID темы)",    "pin",      callback_data="adm_set_log_topic_id"))
    kb.add(mkbtn("Профит-группа (ID)",     "megaphone",callback_data="adm_set_profit_group"))
    kb.add(mkbtn("Профит-топик (ID темы)", "pin",      callback_data="adm_set_profit_topic"))
    kb.add(mkbtn("% выплаты воркеру",      "chart",    callback_data="adm_set_worker_percent"))
    kb.add(mkbtn("Список воркеров",        "people",   callback_data="adm_workers_list"))
    # ── Баннеры ──
    kb.add(mkbtn("🖼 Баннеры",              "tv",       callback_data="adm_banners"))
    # ── Назад ──
    kb.add(mkbtn("В панель",               "hammer",   callback_data="admin_panel"))
    kb.adjust(2, 2, 1, 1, 2, 2, 2, 2, 2, 1)
    return kb.as_markup()


_WORKERS_PER_PAGE = 20

def get_workers_list_kb(page: int = 0) -> InlineKeyboardMarkup:
    """Список воркеров с пагинацией (макс 20 на страницу) и кнопкой удалить."""
    items = sorted(admins)
    total = len(items)
    per_page = _WORKERS_PER_PAGE
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    chunk = items[page * per_page:(page + 1) * per_page]

    kb = InlineKeyboardBuilder()
    for uid in chunk:
        udata = users_data.get(str(uid), {})
        uname = udata.get("username")
        label = f"@{uname}" if uname else str(uid)
        kb.row(
            mkbtn(f"{label} ({uid})", "person", callback_data=f"adm_admin_info_{uid}"),
            mkbtn("Убрать", "cross", callback_data=f"adm_kick_admin_{uid}")
        )

    nav = []
    if page > 0:
        nav.append(mkbtn("\u25c0\ufe0f", callback_data=f"adm_workers_page_{page - 1}"))
    nav.append(mkbtn(f"{page + 1}/{total_pages}  ({total} всего)", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(mkbtn("\u25b6\ufe0f", callback_data=f"adm_workers_page_{page + 1}"))
    if nav:
        kb.row(*nav)

    kb.row(mkbtn("Добавить воркера", "check", callback_data="adm_add_admin"))
    kb.row(mkbtn("Назад", "back", callback_data="admin_settings"))
    return kb.as_markup()

# Алиас для обратной совместимости
def get_admins_list_kb(page: int = 0) -> InlineKeyboardMarkup:
    return get_workers_list_kb(page)


def _settings_text() -> str:
    s = adm_settings
    admins_list = [str(a) for a in admins]
    # баннеры
    banner_lines = "\n".join(
        f"  • <b>{desc}</b>: {get_banner_status(key)}"
        for key, (desc, _) in BANNER_SLOTS.items()
    )
    return (
        f"{e['gear']} <b>Настройки {s.get('service_name','Astral Safe')}</b>\n\n"
        f"<blockquote>"
        f"{e['gear']} <b>Сервис:</b> {s.get('service_name','—')}\n"
        f"{e['lock']} <b>Менеджер:</b> @{s.get('manager_username','—')}\n"
        f"{e['gem']} <b>TON:</b> <code>{s.get('manager_ton_wallet','—')}</code>\n"
        f"{e['card']} <b>Карта:</b> <code>{s.get('manager_card','—')}</code>\n"
        f"{e['coin']} <b>USDT:</b> <code>{s.get('manager_usdt_wallet','—')}</code>\n"
        f"{e['coin']} <b>BTC:</b> <code>{s.get('manager_btc_wallet','—')}</code>\n"
        f"{e['plane']} <b>Канал:</b> <code>{s.get('notification_channel','—')}</code>\n"
        f"{e['sparkle2']} <b>Товары/подарки → @{s.get('gift_recipient','—')}</b>\n"
        f"{e['chart']} <b>Мин. сделок для вывода:</b> <code>{s.get('min_deals_withdraw', 3)}</code>\n"
        f"{e['bell']} <b>Лог-канал:</b> <code>{s.get('log_channel','') or 'отключён'}</code>\n"
        f"{e['pin']} <b>Лог-топик:</b> <code>{s.get('log_topic_id','') or 'не задан'}</code>\n"
        f"{e['megaphone']} <b>Профит-группа:</b> <code>{s.get('profit_group_id','') or 'не задана'}</code>\n"
        f"{e['pin']} <b>Профит-топик:</b> <code>{s.get('profit_topic_id','') or 'не задан'}</code>\n"
        f"{e['chart']} <b>% воркера:</b> <code>{s.get('worker_percent', 80)}%</code>\n"
        f"{e['people']} <b>Админов:</b> <code>{len(admins_list)}</code>"
        f"</blockquote>"
    )


# ─── Настройки: открыть ────────────────────────────────────────────────────────
@dp.callback_query(lambda c: c.data == "admin_settings")
async def cb_admin_settings(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.clear()
    text = _settings_text()
    try:
        await callback_query.message.edit_text(text, reply_markup=get_admin_settings_kb(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_admin_settings_kb(), parse_mode="HTML")
    await callback_query.answer()


def _settings_back_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn("Отмена", "cross", callback_data="admin_settings"))
    return kb.as_markup()


async def _ask_settings(callback_query: types.CallbackQuery, state: FSMContext, state_obj, prompt: str):
    await state.set_state(state_obj)
    try:
        await callback_query.message.edit_text(prompt, reply_markup=_settings_back_kb(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(prompt, reply_markup=_settings_back_kb(), parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "adm_set_service_name")
async def cb_set_service_name(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_service_name,
                        f"{e['gear']} <b>Введите новое название сервиса:</b>")

@dp.message(AdminStates.settings_service_name)
async def handle_settings_service_name(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["service_name"] = message.text.strip()
    save_settings(adm_settings)
    await state.clear()
    await message.answer(f"✅ Название сервиса обновлено: <b>{adm_settings['service_name']}</b>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_manager_username")
async def cb_set_manager_username(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_manager_username,
                        f"{e['lock']} <b>Введите username менеджера (без @):</b>")

@dp.message(AdminStates.settings_manager_username)
async def handle_settings_manager_username(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["manager_username"] = message.text.strip().lstrip("@")
    save_settings(adm_settings)
    await state.clear()
    await message.answer(f"✅ Менеджер: @{adm_settings['manager_username']}",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_ton_wallet")
async def cb_set_ton_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_ton_wallet,
                        f"{e['gem']} <b>Введите TON-кошелёк менеджера:</b>")

@dp.message(AdminStates.settings_ton_wallet)
async def handle_settings_ton_wallet(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["manager_ton_wallet"] = message.text.strip()
    save_settings(adm_settings)
    global MANAGER_TON_WALLET
    MANAGER_TON_WALLET = adm_settings["manager_ton_wallet"]
    await state.clear()
    await message.answer(f"✅ TON-кошелёк обновлён: <code>{MANAGER_TON_WALLET}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_card")
async def cb_set_card(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_card,
                        f"{e['card']} <b>Введите номер карты менеджера:</b>")

@dp.message(AdminStates.settings_card)
async def handle_settings_card(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["manager_card"] = message.text.strip()
    save_settings(adm_settings)
    global MANAGER_CARD
    MANAGER_CARD = adm_settings["manager_card"]
    await state.clear()
    await message.answer(f"✅ Карта обновлена: <code>{MANAGER_CARD}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_usdt_wallet")
async def cb_set_usdt_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_usdt_wallet,
                        f"{e['coin']} <b>Введите USDT-кошелёк менеджера (TRC20):</b>")

@dp.message(AdminStates.settings_usdt_wallet)
async def handle_settings_usdt_wallet(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["manager_usdt_wallet"] = message.text.strip()
    save_settings(adm_settings)
    global MANAGER_USDT_WALLET
    MANAGER_USDT_WALLET = adm_settings["manager_usdt_wallet"]
    await state.clear()
    await message.answer(f"✅ USDT-кошелёк обновлён: <code>{MANAGER_USDT_WALLET}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_btc_wallet")
async def cb_set_btc_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_btc_wallet,
                        f"{e['coin']} <b>Введите BTC-адрес менеджера:</b>")

@dp.message(AdminStates.settings_btc_wallet)
async def handle_settings_btc_wallet(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["manager_btc_wallet"] = message.text.strip()
    save_settings(adm_settings)
    global MANAGER_BTC_WALLET
    MANAGER_BTC_WALLET = adm_settings["manager_btc_wallet"]
    await state.clear()
    await message.answer(f"✅ BTC-адрес обновлён: <code>{MANAGER_BTC_WALLET}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_channel")
async def cb_set_channel(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_channel,
                        f"{e['plane']} <b>Введите ID канала уведомлений (например: -1001234567890):</b>")

@dp.message(AdminStates.settings_channel)
async def handle_settings_channel(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip()
    try:
        int(val)
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте ещё раз.", parse_mode="HTML"); return
    adm_settings["notification_channel"] = val
    save_settings(adm_settings)
    global NOTIFICATION_CHANNEL_ID
    NOTIFICATION_CHANNEL_ID = int(val)
    await state.clear()
    await message.answer(f"✅ Канал уведомлений: <code>{val}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_gift_recipient")
async def cb_set_gift_recipient(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_gift_recipient,
                        f"{e['sparkle2']} <b>Введите username получателя товаров/подарков (без @):</b>")

@dp.message(AdminStates.settings_gift_recipient)
async def handle_settings_gift_recipient(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    adm_settings["gift_recipient"] = message.text.strip().lstrip("@")
    save_settings(adm_settings)
    await state.clear()
    await message.answer(f"✅ Получатель товаров/подарков: @{adm_settings['gift_recipient']}",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_min_deals")
async def cb_set_min_deals(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_min_deals,
                        f"{e['chart']} <b>Введите минимальное количество сделок для вывода средств:</b>")

@dp.message(AdminStates.settings_min_deals)
async def handle_settings_min_deals(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    try:
        n = int(message.text.strip())
        if n < 0: raise ValueError
    except ValueError:
        await message.answer("❌ Введите неотрицательное целое число.", parse_mode="HTML"); return
    adm_settings["min_deals_withdraw"] = n
    save_settings(adm_settings)
    global MIN_DEALS_FOR_WITHDRAW
    MIN_DEALS_FOR_WITHDRAW = n
    await state.clear()
    await message.answer(f"✅ Мин. сделок для вывода: <code>{n}</code>",
                         reply_markup=get_admin_settings_kb(), parse_mode="HTML")


@dp.callback_query(lambda c: c.data == "adm_set_log_channel")
async def cb_set_log_channel(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    cur = adm_settings.get("log_channel") or "не задан"
    await _ask_settings(
        callback_query, state, AdminStates.settings_log_channel,
        f"{e['bell']} <b>Лог-канал</b>\n\n"
        f"Введите ID канала/чата (например: <code>-1001234567890</code>)\n\n"
        f"<i>Текущий: <code>{cur}</code></i>\n"
        f"<i>Отправьте <code>0</code> чтобы отключить логирование.</i>"
    )

@dp.message(AdminStates.settings_log_channel)
async def handle_settings_log_channel(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip()
    try:
        int(val)
    except ValueError:
        await message.answer("❌ Введите числовой ID канала.", parse_mode="HTML"); return
    adm_settings["log_channel"] = val if val != "0" else ""
    save_settings(adm_settings)
    await state.clear()
    label = f"<code>{val}</code>" if val != "0" else "отключено"
    await message.answer(
        f"{e['check']} Лог-канал: {label}",
        reply_markup=get_admin_settings_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data == "adm_set_log_topic_id")
async def cb_set_log_topic_id(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    cur = adm_settings.get("log_topic_id") or "не задан"
    await _ask_settings(
        callback_query, state, AdminStates.settings_log_topic_id,
        f"{e['pin']} <b>Лог-топик (тема)</b>\n\n"
        f"Введите ID топика (темы) в группе-логах (например: <code>3374</code>)\n\n"
        f"<i>Текущий: <code>{cur}</code></i>\n"
        f"<i>Отправьте <code>0</code> чтобы отключить топик и слать в общий чат.</i>"
    )

@dp.message(AdminStates.settings_log_topic_id)
async def handle_settings_log_topic_id(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip()
    try:
        int(val)
    except ValueError:
        await message.answer("❌ Введите числовой ID топика.", parse_mode="HTML"); return
    adm_settings["log_topic_id"] = val if val != "0" else ""
    save_settings(adm_settings)
    await state.clear()
    label = f"<code>{val}</code>" if val != "0" else "отключено"
    await message.answer(
        f"{e['check']} Лог-топик: {label}",
        reply_markup=get_admin_settings_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data == "adm_set_profit_group")
async def cb_set_profit_group(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    cur = adm_settings.get("profit_group_id") or "не задана"
    await _ask_settings(
        callback_query, state, AdminStates.settings_profit_group_id,
        f"{e['megaphone']} <b>Профит-группа</b>\n\n"
        f"Введите ID группы/канала, куда будут отправляться сообщения «НОВЫЙ ПРОФИТ».\n"
        f"Например: <code>-1001234567890</code>\n\n"
        f"<i>Текущий: <code>{cur}</code></i>\n"
        f"<i>Отправьте <code>0</code> чтобы отключить.</i>"
    )

@dp.message(AdminStates.settings_profit_group_id)
async def handle_settings_profit_group_id(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip()
    try:
        int(val)
    except ValueError:
        await message.answer("❌ Введите числовой ID группы (например: -1001234567890).", parse_mode="HTML"); return
    adm_settings["profit_group_id"] = val if val != "0" else ""
    save_settings(adm_settings)
    await state.clear()
    label = f"<code>{val}</code>" if val != "0" else "отключено"
    await message.answer(
        f"{e['check']} Профит-группа: {label}",
        reply_markup=get_admin_settings_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data == "adm_set_profit_topic")
async def cb_set_profit_topic(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    cur = adm_settings.get("profit_topic_id") or "не задан"
    await _ask_settings(
        callback_query, state, AdminStates.settings_profit_topic_id,
        f"{e['pin']} <b>Профит-топик (тема)</b>\n\n"
        f"Введите ID темы (топика) в профит-группе.\n"
        f"Например: <code>123</code>\n\n"
        f"<i>Текущий: <code>{cur}</code></i>\n"
        f"<i>Отправьте <code>0</code> чтобы слать в общий чат без топика.</i>"
    )

@dp.message(AdminStates.settings_profit_topic_id)
async def handle_settings_profit_topic_id(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip()
    try:
        int(val)
    except ValueError:
        await message.answer("❌ Введите числовой ID топика.", parse_mode="HTML"); return
    adm_settings["profit_topic_id"] = val if val != "0" else ""
    save_settings(adm_settings)
    await state.clear()
    label = f"<code>{val}</code>" if val != "0" else "отключено"
    await message.answer(
        f"{e['check']} Профит-топик: {label}",
        reply_markup=get_admin_settings_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data == "adm_set_worker_percent")
async def cb_set_worker_percent(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    cur = adm_settings.get("worker_percent", 80)
    await _ask_settings(
        callback_query, state, AdminStates.settings_worker_percent,
        f"{e['chart']} <b>% выплаты воркеру</b>\n\n"
        f"Введите процент от суммы сделки, который получает воркер.\n"
        f"Например: <code>80</code> означает 80%.\n\n"
        f"<i>Текущий: <code>{cur}%</code></i>"
    )

@dp.message(AdminStates.settings_worker_percent)
async def handle_settings_worker_percent(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    val = message.text.strip().replace("%", "")
    try:
        n = int(val)
        if not (1 <= n <= 100):
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите число от 1 до 100.", parse_mode="HTML"); return
    adm_settings["worker_percent"] = n
    save_settings(adm_settings)
    await state.clear()
    await message.answer(
        f"{e['check']} % воркера: <code>{n}%</code>",
        reply_markup=get_admin_settings_kb(), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data == "adm_add_admin")
async def cb_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await _ask_settings(callback_query, state, AdminStates.settings_add_admin,
                        f"{e['check']} <b>Введите ID или @username пользователя для выдачи прав воркера:</b>\n\n"
                        "<i>Примеры: <code>123456789</code> или <code>@username</code></i>")

@dp.message(AdminStates.settings_add_admin)
async def handle_add_admin(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    target = message.text.strip()
    target_id = None
    if target.lstrip("-").isdigit():
        target_id = int(target)
    elif target.startswith("@"):
        uname = target[1:]
        for uid_s, d in users_data.items():
            if d.get("username") == uname:
                target_id = int(uid_s); break
        if target_id is None:
            await message.answer(f"❌ @{uname} не найден в базе бота.\n<i>Пользователь должен хотя бы раз написать боту.</i>",
                                 parse_mode="HTML", reply_markup=_settings_back_kb()); return
    else:
        await message.answer("❌ Введите ID числом или @username.", parse_mode="HTML",
                             reply_markup=_settings_back_kb()); return
    if target_id in admins:
        await message.answer(f"ℹ️ <code>{target_id}</code> уже является воркером.",
                             parse_mode="HTML", reply_markup=get_workers_list_kb(0)); return
    admins.add(target_id)
    save_admins(admins)
    adm_settings["admins_list"] = list(admins)
    save_settings(adm_settings)
    await state.clear()
    udata = users_data.get(str(target_id), {})
    uname = udata.get("username", "")
    label = f"@{uname} ({target_id})" if uname else str(target_id)
    await send_log(
        "👷 Новый воркер",
        f"Добавил: @{message.from_user.username or message.from_user.id}\nНовый воркер: {label}",
        user_id=target_id,
        username=uname,
    )
    await message.answer(f"✅ <b>{label}</b> добавлен в воркеры.",
                         parse_mode="HTML", reply_markup=get_workers_list_kb(0))


@dp.callback_query(lambda c: c.data == "adm_workers_list")
async def cb_workers_list(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.clear()
    await _show_workers_page(callback_query, page=0)
    await callback_query.answer()


async def _show_workers_page(callback_query: types.CallbackQuery, page: int = 0):
    """Показать страницу списка воркеров."""
    workers_count = len(admins)
    text = (
        f"{e['people']} <b>Список воркеров</b>\n\n"
        f"<blockquote>{e['people']} <i>Всего воркеров: <code>{workers_count}</code></i></blockquote>\n\n"
        f"{e['warning']} Нажмите <b>Убрать</b> рядом с нужным воркером, чтобы снять права."
    )
    kb = get_workers_list_kb(page)
    try:
        if callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            await callback_query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        try:
            await callback_query.message.answer(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass


@dp.callback_query(lambda c: c.data.startswith("adm_workers_page_"))
async def cb_workers_page(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    try:
        page = int(callback_query.data[len("adm_workers_page_"):])
    except ValueError:
        page = 0
    await _show_workers_page(callback_query, page)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "adm_manage_admins")
async def cb_manage_admins(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id): return
    await state.clear()
    await _show_workers_page(callback_query, page=0)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("adm_kick_admin_"))
async def cb_kick_admin(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id): return
    target_id = int(callback_query.data[len("adm_kick_admin_"):])
    # Нельзя убрать самого себя
    if target_id == callback_query.from_user.id:
        await callback_query.answer("❌ Нельзя убрать самого себя!", show_alert=True); return
    if target_id not in admins:
        await callback_query.answer("❌ Не является администратором", show_alert=True); return
    admins.discard(target_id)
    save_admins(admins)
    adm_settings["admins_list"] = list(admins)
    save_settings(adm_settings)
    udata = users_data.get(str(target_id), {})
    uname = udata.get("username", "")
    label = f"@{uname} ({target_id})" if uname else str(target_id)
    await send_log(
        "🚫 Воркер удалён",
        f"Удалил: @{callback_query.from_user.username or callback_query.from_user.id}\nУдалён: {label}",
        user_id=target_id,
        username=uname,
    )
    await callback_query.answer(f"✅ {label} убран из воркеров")
    # Обновляем список — остаёмся на той же странице, если возможно
    await _show_workers_page(callback_query, page=0)


@dp.callback_query(lambda c: c.data.startswith("adm_admin_info_"))
async def cb_admin_info(callback_query: types.CallbackQuery):
    if not _admin_check(callback_query.from_user.id): return
    uid = int(callback_query.data[len("adm_admin_info_"):])
    udata = users_data.get(str(uid), {})
    uname = udata.get("username", "—")
    deals_count = udata.get("completed_deals", 0)
    await callback_query.answer(
        f"ID: {uid}\n@{uname}\nСделок: {deals_count}",
        show_alert=True
    )


# ─── Баннеры: клавиатура и хендлеры ──────────────────────────────────────────

def get_banners_kb() -> InlineKeyboardMarkup:
    """Меню выбора слота баннера."""
    kb = InlineKeyboardBuilder()
    for key, (desc, _) in BANNER_SLOTS.items():
        status_icon = "✅" if get_banner_path(key) else "❌"
        kb.row(mkbtn(f"{status_icon} {desc}", callback_data=f"adm_banner_slot_{key}"))
    kb.row(mkbtn("Назад к настройкам", "back", callback_data="admin_settings"))
    return kb.as_markup()

def get_banner_slot_kb(slot_key: str) -> InlineKeyboardMarkup:
    """Действия для конкретного слота баннера."""
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn("📤 Загрузить / заменить", callback_data=f"adm_banner_upload_{slot_key}"))
    if get_banner_path(slot_key):
        kb.row(mkbtn("👁 Просмотреть", callback_data=f"adm_banner_preview_{slot_key}"))
        kb.row(mkbtn("🗑 Удалить", callback_data=f"adm_banner_delete_{slot_key}"))
    kb.row(mkbtn("← Назад к баннерам", callback_data="adm_banners"))
    return kb.as_markup()


@dp.callback_query(lambda c: c.data == "adm_banners")
async def cb_adm_banners(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    await state.clear()
    lines = [f"  • <b>{desc}</b>: {get_banner_status(key)}" for key, (desc, _) in BANNER_SLOTS.items()]
    text = (
        f"🖼 <b>Управление баннерами</b>\n\n"
        f"Поддерживаются форматы: <code>.jpg .png .gif .mp4</code>\n\n"
        + "\n".join(lines)
    )
    try:
        await callback_query.message.edit_text(text, reply_markup=get_banners_kb(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_banners_kb(), parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("adm_banner_slot_"))
async def cb_adm_banner_slot(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    slot_key = callback_query.data[len("adm_banner_slot_"):]
    if slot_key not in BANNER_SLOTS:
        await callback_query.answer("❌ Неизвестный слот", show_alert=True); return
    await state.clear()
    desc, names = BANNER_SLOTS[slot_key]
    path = get_banner_path(slot_key)
    example_names = " | ".join(names)
    text = (
        f"🖼 <b>{desc}</b>\n\n"
        f"<b>Возможные имена файла:</b>\n<code>{example_names}</code>\n\n"
        f"<b>Статус:</b> {get_banner_status(slot_key)}"
    )
    try:
        await callback_query.message.edit_text(text, reply_markup=get_banner_slot_kb(slot_key), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=get_banner_slot_kb(slot_key), parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("adm_banner_upload_"))
async def cb_adm_banner_upload(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    slot_key = callback_query.data[len("adm_banner_upload_"):]
    if slot_key not in BANNER_SLOTS:
        await callback_query.answer("❌ Неизвестный слот", show_alert=True); return
    desc, names = BANNER_SLOTS[slot_key]
    await state.set_state(AdminStates.settings_upload_banner)
    await state.update_data(banner_slot=slot_key)
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn("Отмена", "cross", callback_data=f"adm_banner_slot_{slot_key}"))
    example_names = " | ".join(names)
    try:
        await callback_query.message.edit_text(
            f"🖼 <b>Загрузка баннера: {desc}</b>\n\n"
            f"Отправьте файл <b>без сжатия</b> (как документ) или фото/видео.\n"
            f"Поддерживаемые форматы: <code>.jpg .png .gif .mp4</code>\n\n"
            f"Файл будет сохранён как:\n<code>{example_names}</code>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    except Exception:
        await callback_query.message.answer(
            f"🖼 <b>Загрузка баннера: {desc}</b>\n\nОтправьте файл как документ или фото/видео.\nФорматы: <code>.jpg .png .gif .mp4</code>",
            reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    await callback_query.answer()


@dp.message(AdminStates.settings_upload_banner)
async def handle_banner_upload(message: types.Message, state: FSMContext):
    if not _admin_check(message.from_user.id): return
    data = await state.get_data()
    slot_key = data.get("banner_slot")
    if not slot_key or slot_key not in BANNER_SLOTS:
        await state.clear()
        await message.answer("❌ Ошибка слота баннера.", parse_mode="HTML"); return

    file_id = None
    ext = None

    if message.document:
        doc = message.document
        mime = doc.mime_type or ""
        fname = doc.file_name or ""
        fext = os.path.splitext(fname)[1].lower()
        if fext in ALLOWED_BANNER_EXTENSIONS:
            file_id = doc.file_id
            ext = fext
        elif "gif" in mime:
            file_id = doc.file_id; ext = ".gif"
        elif "mp4" in mime or "video" in mime:
            file_id = doc.file_id; ext = ".mp4"
        elif "jpeg" in mime or "jpg" in mime:
            file_id = doc.file_id; ext = ".jpg"
        elif "png" in mime:
            file_id = doc.file_id; ext = ".png"
        else:
            await message.answer(
                f"❌ Неподдерживаемый формат.\nДопустимые: <code>.jpg .png .gif .mp4</code>",
                parse_mode="HTML"
            ); return
    elif message.photo:
        file_id = message.photo[-1].file_id
        ext = ".jpg"
    elif message.video:
        file_id = message.video.file_id
        ext = ".mp4"
    elif message.animation:
        file_id = message.animation.file_id
        ext = ".gif"
    else:
        await message.answer(
            "❌ Пришлите файл как документ, фото или видео.\nФорматы: <code>.jpg .png .gif .mp4</code>",
            parse_mode="HTML"
        ); return

    # Скачиваем файл
    try:
        tg_file = await bot.get_file(file_id)
        file_bytes_io = await bot.download_file(tg_file.file_path)
        file_bytes = file_bytes_io.read()
    except Exception as ex:
        await message.answer(f"❌ Ошибка загрузки файла: {ex}", parse_mode="HTML"); return

    # Сохраняем
    try:
        saved_path = save_banner_file(slot_key, file_bytes, ext)
    except Exception as ex:
        await message.answer(f"❌ Ошибка сохранения: {ex}", parse_mode="HTML"); return

    await state.clear()
    desc, _ = BANNER_SLOTS[slot_key]
    fname = os.path.basename(saved_path)
    size_kb = len(file_bytes) // 1024
    await message.answer(
        f"✅ <b>Баннер «{desc}» сохранён!</b>\n"
        f"Файл: <code>{fname}</code> ({size_kb} КБ)",
        reply_markup=get_banner_slot_kb(slot_key), parse_mode="HTML"
    )


@dp.callback_query(lambda c: c.data.startswith("adm_banner_preview_"))
async def cb_adm_banner_preview(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    slot_key = callback_query.data[len("adm_banner_preview_"):]
    path = get_banner_path(slot_key)
    if not path:
        await callback_query.answer("❌ Баннер не установлен", show_alert=True); return
    desc, _ = BANNER_SLOTS[slot_key]
    ext = os.path.splitext(path)[1].lower()
    try:
        f = FSInputFile(path)
        if ext == ".mp4":
            await callback_query.message.answer_video(f, caption=f"🖼 {desc}")
        elif ext == ".gif":
            await callback_query.message.answer_animation(f, caption=f"🖼 {desc}")
        else:
            await callback_query.message.answer_photo(f, caption=f"🖼 {desc}")
    except Exception as ex:
        await callback_query.message.answer(f"❌ Не удалось показать файл: {ex}", parse_mode="HTML")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("adm_banner_delete_"))
async def cb_adm_banner_delete(callback_query: types.CallbackQuery, state: FSMContext):
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("❌", show_alert=True); return
    slot_key = callback_query.data[len("adm_banner_delete_"):]
    path = get_banner_path(slot_key)
    if not path:
        await callback_query.answer("❌ Баннер уже не установлен", show_alert=True); return
    fname = os.path.basename(path)
    os.remove(path)
    desc, _ = BANNER_SLOTS[slot_key]
    await callback_query.answer(f"🗑 Баннер «{desc}» удалён", show_alert=True)
    # Обновляем сообщение
    try:
        text = (
            f"🖼 <b>{desc}</b>\n\n"
            f"<b>Статус:</b> {get_banner_status(slot_key)}"
        )
        await callback_query.message.edit_text(text, reply_markup=get_banner_slot_kb(slot_key), parse_mode="HTML")
    except Exception:
        pass


# ─── Оплата сделки с баланса ──────────────────────────────────────────────────


def _build_buyer_deal_kb(deal_id: str, user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура экрана сделки для покупателя (waiting_for_payment)."""
    deal = deals.get(deal_id, {})
    kb = InlineKeyboardBuilder()
    kb.add(mkbtn(
        get_text("pay_from_balance_button", user_id,
                 amount=deal.get("amount", ""), currency=deal.get("currency", "")),
        "coin", callback_data=f"pay_from_balance_{deal_id}"
    ))
    kb.add(mkbtn(get_text("support_button", user_id), "shield",
                 url="https://t.me/" + adm_settings.get("manager_username", "AstralTradeSupport")))
    kb.add(mkbtn(get_text("back_to_menu", user_id), "inbox", callback_data="back_to_menu"))
    kb.adjust(1)
    return kb.as_markup()

def _build_buyer_deal_text(deal_id: str, user_id: int) -> str:
    """Текст экрана сделки для покупателя (waiting_for_payment)."""
    deal = deals.get(deal_id, {})
    seller_id_val = deal.get("seller_id", "")
    seller_completed_deals_val = users_data.get(str(seller_id_val), {}).get("completed_deals", 0)
    return get_text(
        "connected_as_buyer", user_id,
        deal_id=deal_id,
        requisites=deal.get("requisites", "—"),
        amount=deal.get("amount", ""),
        currency=deal.get("currency", ""),
        description=deal.get("description", ""),
        seller_username=deal.get("seller_username", ""),
        seller_id=seller_id_val,
        seller_completed_deals=seller_completed_deals_val,
    )

@dp.callback_query(lambda c: c.data.startswith("pay_from_balance_"))
async def pay_from_balance(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    deal_id = callback_query.data[len("pay_from_balance_"):]
    if deal_id not in deals:
        await callback_query.answer(get_alert("pay_from_balance_deal_not_found", user_id=user_id), show_alert=True); return
    deal = deals[deal_id]
    if deal.get("buyer_id") != user_id:
        await callback_query.answer(get_alert("pay_from_balance_not_buyer", user_id=user_id), show_alert=True); return
    if deal.get("status") != "waiting_for_payment":
        await callback_query.answer(get_alert("pay_from_balance_wrong_status", user_id=user_id), show_alert=True); return

    uid_str = str(user_id)
    currency = deal["currency"]
    amount   = deal["amount"]

    # Проверяем баланс
    buyer_balance = get_user_balance(uid_str).get(currency, 0.0)
    if buyer_balance < amount:
        await callback_query.answer(
            get_alert("pay_from_balance_no_funds", user_id=user_id,
                      amount=amount, currency=currency, balance=buyer_balance),
            show_alert=True
        ); return

    # Подтверждение — кастомный эмодзи через icon_custom_emoji_id (ключ из _BEID)
    _cur_emoji_key = {
        "STARS": "star2",
        "TON":   "coin2",
        "USDT":  "usdt",
        "BTC":   "btc",
        "RUB":   "flag_ru",
        "UAH":   "flag_ua",
        "KZT":   "flag_kz",
        "BYN":   "flag_by",
    }.get(currency, "money_bag")
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn(
        get_text("pay_from_balance_confirm_button", user_id,
                 amount=amount, currency=currency),
        emoji_key=_cur_emoji_key,
        callback_data=f"pay_balance_confirm_{deal_id}"
    ))
    kb.row(mkbtn(get_text("pay_from_balance_cancel_button", user_id), "back", callback_data=f"back_to_deal_{deal_id}"))
    await _edit_msg(
        callback_query,
        get_text("pay_from_balance_info", user_id,
                 deal_id=deal_id, amount=amount, currency=currency,
                 currency_emoji=_currency_emoji(currency),
                 balance=buyer_balance),
        kb.as_markup()
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("pay_balance_confirm_"))
async def pay_balance_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    deal_id = callback_query.data[len("pay_balance_confirm_"):]
    if deal_id not in deals:
        await callback_query.answer("❌ Сделка не найдена", show_alert=True); return
    deal = deals[deal_id]
    if deal.get("buyer_id") != user_id:
        await callback_query.answer(get_alert("pay_from_balance_no_rights", user_id=user_id), show_alert=True); return
    if deal.get("status") != "waiting_for_payment":
        await callback_query.answer(get_alert("pay_from_balance_already_paid", user_id=user_id), show_alert=True); return

    uid_str  = str(user_id)
    currency = deal["currency"]
    amount   = deal["amount"]
    cur_emoji = _currency_emoji(currency)

    # Списываем с покупателя
    ok = subtract_from_balance(uid_str, currency, amount,
                                deal_id=deal_id, comment=f"Оплата сделки #{deal_id}")
    if not ok:
        await callback_query.answer(get_alert("pay_from_balance_low_funds_alert", user_id=user_id), show_alert=True); return

    # Подтверждаем оплату
    deals[deal_id]["status"]            = "payment_confirmed_by_admin"
    deals[deal_id]["paid_from_balance"] = True
    db.schedule_save_deal(deal_id)

    await send_log(
        "💳 Оплата с баланса покупателя",
        f"Покупатель: @{deal.get('buyer_username','?')} (ID: {user_id})\n"
        f"Продавец: @{deal.get('seller_username','?')}\n"
        f"Сумма: {amount} {currency}\n"
        f"Списано с баланса покупателя.",
        deal_id, user_id=user_id,
        username=callback_query.from_user.username or None,
    )

    await callback_query.answer(get_alert("pay_from_balance_paid_alert", user_id=user_id), show_alert=True)

    # Уведомляем пользователя — пробуем edit, иначе отправляем новым сообщением
    confirm_text = get_text("pay_from_balance_success", user_id,
                            amount=amount, currency=currency,
                            currency_emoji=cur_emoji)
    try:
        await callback_query.message.edit_text(confirm_text, parse_mode="HTML")
    except Exception:
        try:
            await callback_query.message.edit_caption(caption=confirm_text, parse_mode="HTML")
        except Exception:
            try:
                await callback_query.message.answer(confirm_text, parse_mode="HTML")
            except Exception:
                pass

    # Уведомляем участников сделки — вызывается ВСЕГДА
    await notify_and_update_fsm_for_deal(deal_id)

@dp.callback_query(lambda c: c.data.startswith("back_to_deal_"))
async def cb_back_to_deal(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    deal_id = callback_query.data[len("back_to_deal_"):]
    if deal_id not in deals:
        await callback_query.answer(get_alert("pay_from_balance_deal_not_found", user_id=user_id), show_alert=True)
        return
    deal = deals[deal_id]
    if deal.get("buyer_id") != user_id:
        await callback_query.answer(get_alert("pay_from_balance_no_rights", user_id=user_id), show_alert=True)
        return
    text = _build_buyer_deal_text(deal_id, user_id)
    kb   = _build_buyer_deal_kb(deal_id, user_id)
    await _edit_msg(callback_query, text, kb)
    await callback_query.answer()


# ─── История транзакций ────────────────────────────────────────────────────────

_TX_PER_PAGE = 8

def _tx_icon(tx_type: str) -> str:
    return {"credit": "➕", "debit": "➖", "withdraw": "📤"}.get(tx_type, "•")

def _tx_label(tx: dict) -> str:
    from datetime import datetime
    ts   = tx.get("ts", 0)
    dt   = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
    icon = _tx_icon(tx.get("type", ""))
    cur  = tx.get("currency", "")
    amt  = tx.get("amount", 0)
    deal = tx.get("deal_id", "")
    comm = tx.get("comment", "")
    deal_str = f" | #{deal[:8]}" if deal else ""
    return f"{icon} {dt} | <code>{amt} {cur}</code>{deal_str} <i>{comm}</i>"

def get_transactions_kb(user_id: int, page: int, txs: list, _tx_back_label: str = "← Назад к балансу") -> InlineKeyboardMarkup:
    total = len(txs)
    total_pages = max(1, (total + _TX_PER_PAGE - 1) // _TX_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    chunk = txs[page * _TX_PER_PAGE:(page + 1) * _TX_PER_PAGE]

    kb = InlineKeyboardBuilder()
    for tx in chunk:
        from datetime import datetime
        ts   = tx.get("ts", 0)
        dt   = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
        icon = _tx_icon(tx.get("type",""))
        amt  = tx.get("amount", 0)
        cur  = tx.get("currency","")
        deal = tx.get("deal_id","")
        label = f"{icon} {dt}  {amt} {cur}"
        if deal:
            label += f"  #{deal[:8]}"
        kb.row(mkbtn(label, callback_data="noop"))

    nav = []
    if page > 0:
        nav.append(mkbtn("◀️", callback_data=f"balance_txs_{page-1}"))
    nav.append(mkbtn(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(mkbtn("▶️", callback_data=f"balance_txs_{page+1}"))
    if nav:
        kb.row(*nav)
    # "Назад к балансу" — локализованная кнопка, user_id передаётся снаружи
    kb.row(mkbtn(_tx_back_label, "back", callback_data="menu_balance"))
    return kb.as_markup()


@dp.callback_query(lambda c: c.data.startswith("balance_txs_"))
async def cb_transactions(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    try:
        page = int(callback_query.data[len("balance_txs_"):])
    except ValueError:
        page = 0

    txs = await db.get_transactions(user_id)  # список dict, новые первыми

    if not txs:
        await callback_query.answer(get_alert("transactions_no_txs_alert", user_id=user_id), show_alert=True); return

    # Строим текст
    from datetime import datetime
    total = len(txs)
    total_pages = max(1, (total + _TX_PER_PAGE - 1) // _TX_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    chunk = txs[page * _TX_PER_PAGE:(page + 1) * _TX_PER_PAGE]

    lines = []
    for tx in chunk:
        ts      = tx.get("ts", 0)
        dt      = datetime.fromtimestamp(ts).strftime("%d.%m.%y %H:%M")
        icon    = _tx_icon(tx.get("type",""))
        amt     = tx.get("amount", 0)
        cur     = tx.get("currency","")
        deal_id = tx.get("deal_id","")
        comm    = tx.get("comment","")
        line = f"{icon} <code>{dt}</code>  <b>{amt} {cur}</b>"
        deal_label = get_text("transactions_deal_row", user_id)
        if deal_id:
            line += f"\n    {deal_label} <code>#{deal_id[:12]}</code>"
        if comm:
            line += f"\n    └ <i>{comm}</i>"
        lines.append(line)

    text = (
        get_text("transactions_header", user_id, page=page+1, total_pages=total_pages)
        + "\n\n"
        + "\n\n".join(lines)
    )

    back_label = get_text("transactions_back_button", user_id)
    kb = get_transactions_kb(user_id, page, txs, _tx_back_label=back_label)
    try:
        await callback_query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest as ex:
        ex_str = str(ex).lower()
        if "message is not modified" in ex_str:
            pass
        else:
            try:
                await callback_query.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
            except TelegramBadRequest as ex2:
                if "message is not modified" not in str(ex2).lower():
                    await callback_query.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback_query.answer()


# ─── Webhook от userbot: подтверждение получения NFT ──────────────────────────
# userbot.py отправляет POST на http://localhost:8765/nft_received
# с JSON: {buyer_id, nft_link, nft_name, nft_count, secret}
#
# Бот находит сделку по buyer_id, показывает менеджеру/воркеру
# кнопку «Подтвердить» — после нажатия отправляет профит и завершает сделку.

from aiohttp import web as _web
import asyncio as _asyncio

import os as _os
USERBOT_SECRET       = _os.environ.get("USERBOT_SECRET", "CHANGE_ME_SECRET_KEY")
USERBOT_WEBHOOK_PORT = int(_os.environ.get("WEBHOOK_PORT", "8765"))  # отдельный порт для NFT webhook

# Pending NFT confirmations: deal_id -> {nft_link, nft_name, nft_count}
_pending_nft: dict = {}


def _find_active_deal_by_buyer(buyer_id: int):
    """Ищет активную сделку где buyer_id совпадает и сделка не завершена."""
    for did, d in deals.items():
        if d.get("buyer_id") == buyer_id and d.get("status") not in ("completed", "cancelled"):
            return did, d
    return None


async def _complete_deal_with_nft(deal_id: str, nft_link: str, nft_name: str, nft_count: int):
    """Завершает сделку, отправляет профит в группу, уведомляет участников."""
    deal = deals.get(deal_id)
    if not deal:
        return

    deal["nft_link"]  = nft_link
    deal["nft_count"] = nft_count
    deal["status"]    = "completed"
    db.schedule_save_deal(deal_id)

    # Счётчики завершённых сделок
    for role_key in ("seller_id", "buyer_id"):
        uid = deal.get(role_key)
        if uid:
            uid_str = str(uid)
            users_data.setdefault(uid_str, {})
            users_data[uid_str]["completed_deals"] = users_data[uid_str].get("completed_deals", 0) + 1

    worker_u = deal.get("worker_username") or deal.get("seller_username") or "—"
    buyer_u  = deal.get("buyer_username") or str(deal.get("buyer_id", "?"))
    amount   = deal.get("amount", "?")
    currency = deal.get("currency", "?")
    try:
        worker_percent = int(adm_settings.get("worker_percent", 80))
    except (ValueError, TypeError):
        worker_percent = 80
    try:
        worker_share = round(float(amount) * worker_percent / 100, 2)
    except (ValueError, TypeError):
        worker_share = "?"

    nft_line = f'\n<a href="{nft_link}">{nft_link}</a>' if nft_link else ""
    bot_info = await bot.get_me()

    profit_text = (
        f"🪄 <b>НОВЫЙ ПРОФИТ!</b>\n\n"
        f"👷 <b>Воркер:</b> @{worker_u}\n"
        f"🤖 <b>Бот:</b> @{bot_info.username}\n"
        f"🎁 <b>Снято NFT:</b> {nft_count} шт.{nft_line}\n\n"
        f"💎 <b>Сумма:</b> {amount} {currency}:\n"
        f"<blockquote>"
        f"• <b>Процент выплаты:</b> {worker_percent}% 💬\n"
        f"• <b>Доля воркера:</b> {worker_share} {currency} 💬"
        f"</blockquote>"
    )

    # Отправляем профит в группу (в топик если задан)
    profit_group_id = adm_settings.get("profit_group_id", "")
    profit_topic_id = adm_settings.get("profit_topic_id", "")
    if profit_group_id:
        try:
            kwargs = dict(
                chat_id=int(profit_group_id),
                text=profit_text,
                parse_mode="HTML",
                disable_web_page_preview=False,
            )
            if profit_topic_id:
                kwargs["message_thread_id"] = int(profit_topic_id)
            await bot.send_message(**kwargs)
        except Exception as ex:
            logging.error(f"Profit group send error: {ex}", exc_info=True)

    # Уведомляем покупателя
    buyer_id = deal.get("buyer_id")
    if buyer_id:
        try:
            await bot.send_message(
                chat_id=buyer_id,
                text=(
                    f"✅ <b>NFT получен и сделка завершена!</b>\n\n"
                    f"🎁 <b>{nft_name}</b>\n"
                    f"Сделка <code>#{deal_id}</code> успешно закрыта.\n\n"
                    f"Спасибо за доверие!"
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    # Уведомляем воркера
    seller_id = deal.get("seller_id") or deal.get("worker_id")
    if seller_id and seller_id != buyer_id:
        try:
            await bot.send_message(
                chat_id=seller_id,
                text=(
                    f"✅ <b>Сделка <code>#{deal_id}</code> завершена!</b>\n\n"
                    f"🎁 NFT <b>{nft_name}</b> получен от @{buyer_u}\n"
                    f"💎 Твоя доля: <b>{worker_share} {currency}</b>"
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await send_completed_deal_notification(deal_id)
    # Автовыплата воркеру
    asyncio.create_task(notify_owner_verify_deal(deal_id))
    logging.info(f"Сделка #{deal_id} завершена через NFT gift от buyer={buyer_id}")


# ─── Callback: кнопка «Подтвердить получение NFT» ─────────────────────────────

@dp.callback_query(lambda c: c.data.startswith("confirm_nft_"))
async def cb_confirm_nft(callback_query: types.CallbackQuery):
    """Менеджер/воркер нажимает «Подтвердить» — бот завершает сделку."""
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    deal_id = callback_query.data[len("confirm_nft_"):]
    pending = _pending_nft.pop(deal_id, None)

    if not pending:
        await callback_query.answer("⚠️ Уже обработано или истекло", show_alert=True)
        return

    await callback_query.answer("✅ Подтверждено!", show_alert=False)
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await _complete_deal_with_nft(
        deal_id,
        pending["nft_link"],
        pending["nft_name"],
        pending["nft_count"],
    )


@dp.callback_query(lambda c: c.data.startswith("reject_nft_"))
async def cb_reject_nft(callback_query: types.CallbackQuery):
    """Менеджер отклоняет — NFT не тот или ошибка."""
    if not _admin_check(callback_query.from_user.id):
        await callback_query.answer("⛔ Нет доступа", show_alert=True)
        return

    deal_id = callback_query.data[len("reject_nft_"):]
    _pending_nft.pop(deal_id, None)

    await callback_query.answer("❌ Отклонено", show_alert=False)
    try:
        await callback_query.message.edit_text(
            callback_query.message.text + "\n\n<i>❌ Отклонено менеджером.</i>",
            parse_mode="HTML",
            reply_markup=None,
        )
    except Exception:
        pass


# ─── aiohttp webhook-сервер для приёма сигналов от userbot ────────────────────

async def _handle_nft_received(request: _web.Request) -> _web.Response:
    """
    POST /nft_received
    Body JSON: {secret, buyer_id, nft_link, nft_name, nft_count}
    userbot.py вызывает этот endpoint когда видит входящий gift на аккаунте менеджера.
    """
    try:
        data = await request.json()
    except Exception:
        return _web.Response(status=400, text="bad json")

    if data.get("secret") != USERBOT_SECRET:
        return _web.Response(status=403, text="forbidden")

    buyer_id  = int(data.get("buyer_id", 0))
    nft_link  = data.get("nft_link", "")
    nft_name  = data.get("nft_name", "Unique Gift")
    nft_count = int(data.get("nft_count", 1))

    found = _find_active_deal_by_buyer(buyer_id)
    if not found:
        logging.warning(f"NFT webhook: нет активной сделки для buyer_id={buyer_id}")
        return _web.Response(status=200, text="no active deal")

    deal_id, deal = found
    _pending_nft[deal_id] = {
        "nft_link":  nft_link,
        "nft_name":  nft_name,
        "nft_count": nft_count,
    }

    worker_u = deal.get("worker_username") or deal.get("seller_username") or "—"
    buyer_u  = deal.get("buyer_username") or str(buyer_id)
    amount   = deal.get("amount", "?")
    currency = deal.get("currency", "?")
    nft_line = f'<a href="{nft_link}">{nft_link}</a>' if nft_link else nft_name

    confirm_text = (
        f"🎁 <b>Получен NFT!</b>\n\n"
        f"👤 <b>От:</b> @{buyer_u}\n"
        f"🔗 <b>NFT:</b> {nft_line}\n"
        f"💎 <b>Сумма сделки:</b> {amount} {currency}\n"
        f"👷 <b>Воркер:</b> @{worker_u}\n"
        f"📋 <b>Сделка:</b> <code>#{deal_id}</code>\n\n"
        f"⬇️ Подтверди получение чтобы завершить сделку и отправить профит."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_nft_{deal_id}"),
        InlineKeyboardButton(text="❌ Отклонить",  callback_data=f"reject_nft_{deal_id}"),
    ]])

    # Отправляем уведомление всем воркерам и в ADMIN_GROUP
    notified = set()
    for admin_id in list(admins):
        try:
            await bot.send_message(chat_id=admin_id, text=confirm_text,
                                   reply_markup=kb, parse_mode="HTML",
                                   disable_web_page_preview=True)
            notified.add(admin_id)
        except Exception:
            pass

    if ADMIN_GROUP_ID and ADMIN_GROUP_ID not in notified:
        try:
            await bot.send_message(chat_id=ADMIN_GROUP_ID, text=confirm_text,
                                   reply_markup=kb, parse_mode="HTML",
                                   disable_web_page_preview=True)
        except Exception:
            pass

    logging.info(f"NFT webhook: сделка #{deal_id}, ждём подтверждения от менеджера")
    return _web.Response(status=200, text="ok")


async def _start_webhook_server():
    app = _web.Application()
    app.router.add_post("/nft_received", _handle_nft_received)
    runner = _web.AppRunner(app)
    await runner.setup()
    site = _web.TCPSite(runner, "0.0.0.0", USERBOT_WEBHOOK_PORT)
    await site.start()
    logging.info(f"NFT webhook server listening on 127.0.0.1:{USERBOT_WEBHOOK_PORT}")


# ─── Команда воркера: указать TON-кошелёк для выплат ─────────────────────────

@dp.message(Command("setwallet"))
async def cmd_setwallet(message: types.Message):
    user_id  = message.from_user.id
    args     = message.text.split()[1:]
    if not args:
        uid_str  = str(user_id)
        current  = users_data.get(uid_str, {}).get("ton_wallet", "") or "не указан"
        await message.answer(
            f"💎 <b>Твой TON-кошелёк для выплат</b>\n\n"
            f"Текущий: <code>{current}</code>\n\n"
            f"Чтобы изменить — отправь:\n"
            f"<code>/setwallet UQ...</code>\n\n"
            f"<i>Адрес начинается с UQ или 0: — скопируй из Tonkeeper.</i>",
            parse_mode="HTML",
        )
        return

    address = args[0].strip()
    # Базовая валидация TON-адреса
    if not (address.startswith("UQ") or address.startswith("EQ") or address.startswith("0:")):
        await message.answer(
            "❌ Неверный формат адреса.\n"
            "TON-адрес начинается с <code>UQ</code>, <code>EQ</code> или <code>0:</code>\n\n"
            "Скопируй адрес из Tonkeeper.",
            parse_mode="HTML",
        )
        return

    uid_str = str(user_id)
    users_data.setdefault(uid_str, {})
    users_data[uid_str]["ton_wallet"] = address
    db.schedule_save_user(user_id)

    await message.answer(
        f"✅ <b>TON-кошелёк сохранён!</b>\n\n"
        f"<code>{address}</code>\n\n"
        f"Выплаты после сделок будут автоматически приходить сюда.",
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 👷 ПАНЕЛЬ ВОРКЕРА
# ═══════════════════════════════════════════════════════════════════════════════

class WorkerStates(StatesGroup):
    set_wallet = State()


def get_worker_panel_kb(user_id: int) -> InlineKeyboardMarkup:
    """Красивая клавиатура панели воркера с премиум эмодзи."""
    kb = InlineKeyboardBuilder()
    kb.row(
        mkbtn("💼  Мои сделки",    "finish",      callback_data="worker_my_deals"),
        mkbtn("💰  Баланс",        "money_bag",   callback_data="worker_balance"),
    )
    kb.row(
        mkbtn("📤  Вывести",       "flying_money", callback_data="menu_withdraw"),
        mkbtn("👛  Мой кошелёк",   "card",        callback_data="worker_wallet"),
    )
    kb.row(mkbtn("🔒  Закрыть",    "no",          callback_data="worker_close"))
    return kb.as_markup()


async def send_worker_panel(user_id: int, message_or_cq=None):
    """Отправляет/обновляет панель воркера."""
    uid_str  = str(user_id)
    username = users_data.get(uid_str, {}).get("username", str(user_id))
    balance  = get_user_balance(uid_str)
    wallet   = users_data.get(uid_str, {}).get("ton_wallet", "") or "не указан"

    # Статистика воркера
    active_count = sum(
        1 for d in deals.values()
        if d.get("worker_id") == user_id and d.get("status") not in ("completed", "cancelled")
    )
    completed_count = sum(
        1 for d in deals.values()
        if d.get("worker_id") == user_id and d.get("status") == "completed"
    )

    # Баланс строкой
    bal_lines = "\n".join(
        f"   {cur}: <b>{amt}</b>"
        for cur, amt in balance.items() if amt > 0
    ) or "   пусто"

    text = (
        f"{e['crown']} <b>Панель воркера</b> @{username}\n"
        f"\n"
        f"<blockquote>"
        f"{e['finish']} Активных сделок: <b>{active_count}</b>\n"
        f"{e['check']} Завершённых: <b>{completed_count}</b>\n"
        f"{e['money_bag']} Баланс:\n{bal_lines}\n"
        f"{e['card']} Кошелёк: <code>{wallet[:20]}...</code>" if len(wallet) > 20 else
        f"{e['card']} Кошелёк: <code>{wallet}</code>"
        f"</blockquote>"
    )

    kb = get_worker_panel_kb(user_id)

    if message_or_cq is None:
        return
    if hasattr(message_or_cq, "message"):
        # CallbackQuery
        try:
            await message_or_cq.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await message_or_cq.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await message_or_cq.answer()
    else:
        await message_or_cq.answer(text, reply_markup=kb, parse_mode="HTML")


@dp.message(Command("worker"))
async def cmd_worker_panel(message: types.Message, state: FSMContext):
    """Открыть панель воркера."""
    user_id = message.from_user.id
    if user_id not in admins:
        await message.answer("⛔ Доступ только для воркеров.")
        return
    await state.clear()
    await send_worker_panel(user_id, message)


# ── Закрыть панель ─────────────────────────────────────────────────────────────

@dp.callback_query(lambda c: c.data == "worker_close")
async def cb_worker_close(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.answer("Панель закрыта")


# ── Мои сделки воркера ─────────────────────────────────────────────────────────

@dp.callback_query(lambda c: c.data == "worker_my_deals")
async def cb_worker_my_deals(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in admins:
        await callback_query.answer("⛔", show_alert=True); return

    my_deals = [
        (did, d) for did, d in deals.items()
        if d.get("worker_id") == user_id or d.get("seller_id") == user_id
    ]
    my_deals.sort(key=lambda x: x[1].get("created_at", 0), reverse=True)

    if not my_deals:
        await callback_query.answer("У тебя нет сделок", show_alert=True)
        return

    lines = []
    for did, d in my_deals[:15]:
        status_map = {
            "completed": "✅", "cancelled": "❌",
            "waiting_for_buyer": "⏳", "waiting_for_seller": "⏳",
            "in_progress": "🔄",
        }
        icon   = status_map.get(d.get("status", ""), "❓")
        amount = d.get("amount", "?")
        cur    = d.get("currency", "")
        buyer  = d.get("buyer_username") or "—"
        lines.append(f"{icon} <code>#{did}</code> | {amount} {cur} | @{buyer}")

    text = (
        f"{e['finish']} <b>Мои сделки</b>\n\n" +
        "\n".join(lines) +
        f"\n\n<i>Показаны последние {min(15, len(my_deals))} из {len(my_deals)}</i>"
    )
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn("◀️  Назад", "back", callback_data="worker_panel_back"))
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()


# ── Баланс воркера ─────────────────────────────────────────────────────────────

@dp.callback_query(lambda c: c.data == "worker_balance")
async def cb_worker_balance(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in admins:
        await callback_query.answer("⛔", show_alert=True); return

    uid_str = str(user_id)
    balance = get_user_balance(uid_str)
    bal_lines = "\n".join(
        f"  {e['diamond']} <b>{amt} {cur}</b>"
        for cur, amt in balance.items() if amt > 0
    ) or f"  {e['broken_heart']} пусто"

    text = (
        f"{e['money_bag']} <b>Твой баланс</b>\n\n"
        f"<blockquote>{bal_lines}</blockquote>\n\n"
        f"Для вывода нажми кнопку ниже 👇"
    )
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn("📤  Вывести",  "flying_money", callback_data="menu_withdraw"))
    kb.row(mkbtn("◀️  Назад",   "back",          callback_data="worker_panel_back"))
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()


# ── Кошелёк воркера ────────────────────────────────────────────────────────────

@dp.callback_query(lambda c: c.data == "worker_wallet")
async def cb_worker_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id not in admins:
        await callback_query.answer("⛔", show_alert=True); return

    uid_str = str(user_id)
    wallet  = users_data.get(uid_str, {}).get("ton_wallet", "") or "не указан"
    text = (
        f"{e['card']} <b>Твой TON-кошелёк</b>\n\n"
        f"<blockquote><code>{wallet}</code></blockquote>\n\n"
        f"Введи новый адрес кошелька (начинается с <code>UQ</code> или <code>EQ</code>):"
    )
    kb = InlineKeyboardBuilder()
    kb.row(mkbtn("❌  Отмена", "cross", callback_data="worker_panel_back"))
    await state.set_state(WorkerStates.set_wallet)
    try:
        await callback_query.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await callback_query.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback_query.answer()


@dp.message(WorkerStates.set_wallet)
async def handle_worker_set_wallet(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    address = message.text.strip()
    if not (address.startswith("UQ") or address.startswith("EQ") or address.startswith("0:")):
        await message.answer(
            f"{e['warning']} Неверный формат.\n"
            f"TON-адрес начинается с <code>UQ</code> или <code>EQ</code>\n\n"
            f"Попробуй снова:",
            parse_mode="HTML",
        )
        return
    uid_str = str(user_id)
    users_data.setdefault(uid_str, {})
    users_data[uid_str]["ton_wallet"] = address
    db.schedule_save_user(user_id)
    await state.clear()
    await message.answer(
        f"{e['check']} <b>Кошелёк сохранён!</b>\n\n"
        f"<code>{address}</code>\n\n"
        f"Выплаты будут приходить сюда автоматически.",
        parse_mode="HTML",
    )
    await send_worker_panel(user_id, message)


# ── Назад в панель воркера ─────────────────────────────────────────────────────

@dp.callback_query(lambda c: c.data == "worker_panel_back")
async def cb_worker_panel_back(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_worker_panel(callback_query.from_user.id, callback_query)


# ─── Команда воркера: привязать NFT к сделке (legacy команда) ─────────────────

@dp.message(Command("setnft"))
async def cmd_setnft(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admins:
        await message.answer("⛔ Только воркеры."); return
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer(
            f"{e['gift']} <b>Использование:</b>\n"
            f"<code>/setnft &lt;deal_id&gt; &lt;ссылка&gt;</code>\n\n"
            f"Или открой панель: /worker",
            parse_mode="HTML"
        ); return
    deal_id  = args[0]
    nft_link = args[1]
    deal = deals.get(deal_id)
    if not deal:
        await message.answer(f"❌ Сделка <code>#{deal_id}</code> не найдена.", parse_mode="HTML"); return
    deal["nft_link"]        = nft_link
    deal["nft_count"]       = int(args[2]) if len(args) >= 3 else 1
    deal["worker_id"]       = user_id
    deal["worker_username"] = message.from_user.username or str(user_id)
    db.schedule_save_deal(deal_id)
    await message.answer(
        f"{e['check']} NFT привязан к сделке <code>#{deal_id}</code>\n"
        f"🔗 <a href='{nft_link}'>{nft_link}</a>",
        parse_mode="HTML", disable_web_page_preview=False
    )


@dp.message(Command("setwallet"))
async def cmd_setwallet(message: types.Message):
    user_id = message.from_user.id
    args    = message.text.split()[1:]
    if not args:
        uid_str = str(user_id)
        current = users_data.get(uid_str, {}).get("ton_wallet", "") or "не указан"
        await message.answer(
            f"{e['card']} <b>TON-кошелёк</b>\n\nТекущий: <code>{current}</code>\n\n"
            f"Или открой панель воркера: /worker",
            parse_mode="HTML"
        ); return
    address = args[0].strip()
    if not (address.startswith("UQ") or address.startswith("EQ") or address.startswith("0:")):
        await message.answer("❌ Неверный формат адреса.", parse_mode="HTML"); return
    uid_str = str(user_id)
    users_data.setdefault(uid_str, {})
    users_data[uid_str]["ton_wallet"] = address
    db.schedule_save_user(user_id)
    await message.answer(
        f"{e['check']} Кошелёк сохранён!\n<code>{address}</code>",
        parse_mode="HTML"
    )


@dp.message(Command("claimworker"))
async def cmd_claimworker(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admins:
        await message.answer("⛔ Только воркеры."); return
    args = message.text.split()[1:]
    if not args:
        await message.answer("Использование: <code>/claimworker &lt;deal_id&gt;</code>\n\nИли открой: /worker", parse_mode="HTML"); return
    deal_id  = args[0]
    deal     = deals.get(deal_id)
    if not deal:
        await message.answer(f"❌ Сделка <code>#{deal_id}</code> не найдена.", parse_mode="HTML"); return
    username = message.from_user.username or str(user_id)
    deal["worker_id"]       = user_id
    deal["worker_username"] = username
    db.schedule_save_deal(deal_id)
    await message.answer(
        f"{e['check']} Ты назначен воркером сделки <code>#{deal_id}</code>.",
        parse_mode="HTML"
    )


# Использование: /setnft <deal_id> <nft_link> [кол-во]
# Пример: /setnft abc123 https://t.me/nft/JollyChimp-89459 1

@dp.message(Command("setnft"))
async def cmd_setnft(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admins:
        await message.answer("❌ Только воркеры могут использовать эту команду.", parse_mode="HTML")
        return
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer(
            f"ℹ️ <b>Использование:</b>\n"
            f"<code>/setnft &lt;deal_id&gt; &lt;ссылка_на_NFT&gt; [кол-во]</code>\n\n"
            f"<b>Пример:</b>\n"
            f"<code>/setnft abc123 https://t.me/nft/JollyChimp-89459 1</code>",
            parse_mode="HTML"
        )
        return
    deal_id  = args[0]
    nft_link = args[1]
    try:
        nft_count = int(args[2]) if len(args) >= 3 else 1
    except ValueError:
        nft_count = 1
    deal = deals.get(deal_id)
    if not deal:
        await message.answer(f"❌ Сделка <code>#{deal_id}</code> не найдена.", parse_mode="HTML")
        return
    deal["nft_link"]  = nft_link
    deal["nft_count"] = nft_count
    # Также привязываем воркера, если ещё не привязан
    if not deal.get("worker_id"):
        deal["worker_id"]       = user_id
        deal["worker_username"] = message.from_user.username or str(user_id)
    db.schedule_save_deal(deal_id)
    await message.answer(
        f"✅ <b>NFT привязан к сделке <code>#{deal_id}</code></b>\n\n"
        f"🔗 <a href='{nft_link}'>{nft_link}</a>\n"
        f"🎁 Количество: <b>{nft_count}</b> шт.\n"
        f"👷 Воркер: @{deal['worker_username']}",
        parse_mode="HTML", disable_web_page_preview=False
    )


# ─── Команда воркера: назначить себя воркером сделки ─────────────────────────
# Использование: /claimworker <deal_id>

@dp.message(Command("claimworker"))
async def cmd_claimworker(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admins:
        await message.answer("❌ Только воркеры могут использовать эту команду.", parse_mode="HTML")
        return
    args = message.text.split()[1:]
    if not args:
        await message.answer(
            "ℹ️ <b>Использование:</b> <code>/claimworker &lt;deal_id&gt;</code>",
            parse_mode="HTML"
        )
        return
    deal_id = args[0]
    deal = deals.get(deal_id)
    if not deal:
        await message.answer(f"❌ Сделка <code>#{deal_id}</code> не найдена.", parse_mode="HTML")
        return
    username = message.from_user.username or str(user_id)
    deal["worker_id"]       = user_id
    deal["worker_username"] = username
    db.schedule_save_deal(deal_id)
    await message.answer(
        f"✅ Вы назначены воркером сделки <code>#{deal_id}</code>.\n"
        f"👷 @{username}",
        parse_mode="HTML"
    )


if __name__ == "__main__":
    async def main():
        global users_data, deals

        # Инициализируем БД (при первом запуске — миграция JSON → SQLite)
        await db.init()

        users_data = db.users
        deals      = db.deals

        # Запускаем webhook-сервер для приёма сигналов от userbot
        await _start_webhook_server()

        await bot.set_my_commands([
            types.BotCommand(command="start", description="Главное меню"),
        ])
        await dp.start_polling(bot)
    asyncio.run(main())
