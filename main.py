import nest_asyncio
nest_asyncio.apply()

import json, os, hashlib, random, asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8486521103:AAE8AxuKIkZZEgyXn9L_Qy1pSu-pfy7WQTk"
ADMIN_ID = 5162450021
KARTA = "9860176621636107"
DATA_FILE = "bank_data.json"

STARS_SOTISH = 200
STARS_OLISH = 140
KREDIT_FOIZ = 0.10
KREDIT_MUDDAT = 14
KREDIT_MAX = 1000000
OTKAZMA_FOIZ = 0.005
TAKLIF_BONUS = 5  # Do'st taklif qilsa nechta Stars beriladi

PREMIUM_NARX = {
    "1": {"oy": {"uz": "1 oy", "ru": "1 месяц", "en": "1 month"}, "narx": 45000},
    "3": {"oy": {"uz": "3 oy", "ru": "3 месяца", "en": "3 months"}, "narx": 180000},
    "6": {"oy": {"uz": "6 oy", "ru": "6 месяцев", "en": "6 months"}, "narx": 240000},
    "12": {"oy": {"uz": "12 oy", "ru": "12 месяцев", "en": "12 months"}, "narx": 400000},
}

MATNLAR = {
    "uz": {
        "start": "🏦 *SHOMURODOV BANK*ga xush kelibsiz!\n\n/register — Royxatdan otish\n/login — Kirish\n/info — Bank haqida\n/help — Yordam",
        "til_saqlandi": "✅ Til saqlandi! O'zbek tili tanlandi.",
        "captcha": "🤖 Bot emasligingizni isbotlang:\n\n❓ {} + {} = ?",
        "captcha_togri": "✅ Togri!\n\n📞 Telefon raqamingizni yuboring:\nMisol: +998901234567",
        "captcha_xato": "❌ Xato! /register qayta bosing",
        "faqat_son": "❌ Faqat son kiriting!",
        "telefon_format": "❌ Format: +998901234567",
        "telefon_band": "❌ Bu telefon raqam allaqachon royxatdan otgan!",
        "username_sora": "👤 Username kiriting (min 3 belgi, bosh joy yoq):",
        "username_xato": "❌ Min 3 belgi, bosh joy yoq!",
        "username_band": "❌ Username band!",
        "parol_sora": "🔑 Parol yarating (min 6 belgi):",
        "parol_xato": "❌ Min 6 belgi!",
        "pin_sora": "🔢 4 xonali PIN yarating:",
        "pin_xato": "❌ 4 raqam bolishi kerak!",
        "account_yaratildi": "✅ *Account yaratildi!*\n\n👤 {}\n📞 {}\n💳 **** **** **** {}\n\nKirish uchun:\n/login {} {}",
        "login_format": "❌ Format: /login username parol",
        "user_topilmadi": "❌ User topilmadi!",
        "bloklangan": "🔒 Account bloklangan!",
        "vaqtincha_bloklangan": "⏳ Account vaqtincha bloklangan! {} daqiqadan keyin urinib koring.",
        "parol_xato2": "❌ Parol xato! Qolgan urinish: {}",
        "xush_kelibsiz": "✅ Xush kelibsiz, *{}*!\n\nBuyruqni tanlang:",
        "balans": "💰 *Balans:* {:,.0f} so'm\n⭐ *Stars:* {} ta\n💳 *Kredit qarz:* {:,.0f} so'm\n📊 *Kredit limit:* {:,.0f} so'm qolgan",
        "karta": "💳 *Karta:* `{}`\n💰 *Balans:* {:,.0f} so'm\n📞 *Telefon:* {}",
        "karta_ochish": "🔓 Ochish",
        "karta_yopish": "🔒 Yopish",
        "karta_ozgartirildi": "✅ Ozgartirildi!",
        "otkazma_format": "❌ Format: /otkazma karta_raqam summa",
        "summa_xato": "❌ Summa notogri!",
        "musbat_summa": "❌ Musbat summa!",
        "ozingizga": "❌ Ozingizga yubora olmaysiz!",
        "karta_bloklangan": "❌ Karta bloklangan!",
        "karta_topilmadi": "❌ Karta topilmadi!",
        "balans_yetmaydi": "❌ Balans yetmaydi! Kerak: {:,.0f} so'm",
        "otkazma_bajarildi": "✅ *Otkazma bajarildi!*\n💸 Summa: {:,.0f} so'm\n💳 Komissiya (0.5%): {:,.0f} so'm\n💰 Qolgan: {:,.0f} so'm",
        "kredit_info": "📋 *Kredit olish:*\n\n📌 Max limit: {:,.0f} so'm\n📌 Qolgan limitingiz: {:,.0f} so'm\n📌 Foiz: 10%\n📌 Muddat: 2 hafta\n\n⚠️ Gift kafolat talab qilinadi!\nGift narxidan 30% arzon kredit beriladi.\n2 haftadan otsa gift musodara.\nTolasangiz gift qaytariladi!\n\nFormat: /kredit summa",
        "kredit_tola_format": "❌ Format: /kredit_tola summa",
        "kredit_yoq": "✅ Kreditingiz yoq!",
        "kredit_tola_ok": "✅ *Kredit tolandi!*\n\n💳 Tolandi: {:,.0f} so'm\n💳 Qolgan qarz: {:,.0f} so'm",
        "kredit_tola_tugadi": "✅ *Kredit toliq tolandi!* 🎉\n\n🎁 Giftingiz qaytariladi!\n📊 Yangi limit: {:,.0f} so'm",
        "kredit_limit_tugagan": "❌ Kredit limitingiz tugagan!",
        "kredit_limit_oz": "❌ Faqat {:,.0f} so'm olishingiz mumkin!",
        "kredit_ariza": "✅ *Ariza yuborildi!*\n\n🆔 #{}\n💰 {:,.0f} so'm\n💸 Foiz: {:,.0f} so'm\n💳 Qaytarish: {:,.0f} so'm\n📅 {} kun\n\n🎁 @shomurodav ga {:,.0f} so'm qiymatida Gift yuboring!\n✅ Tolasangiz gift qaytariladi!\n❌ {} kundan otsa gift musodara!",
        "kredit_tasdiqlandi": "✅ *Kredit tasdiqlandi!*\n\n💰 {:,.0f} so'm\n💳 Qaytarish: {:,.0f} so'm\n📅 {} kun",
        "kredit_rad": "❌ *Kredit rad etildi!*\n📩 @shomurodav",
        "stars_info": "⭐ *Stars xizmati*\n\nSotib olish: *{} so'm/star*\nSotish: *{} so'm/star*\nSizda: *{} stars*\nBalans: *{:,.0f} so'm*",
        "stars_sotib_ol": "⭐ *Stars sotib olish*\n\nNarx: *{} so'm/star*\nBalans: *{:,.0f} so'm*\n\nNechta Stars sotib olmoqchisiz?",
        "stars_sot": "💰 *Stars sotish*\n\nNarx: *{} so'm/star*\nSizda: *{} stars*\n\nNechta Stars sotmoqchisiz?",
        "stars_karta": "💳 *Karta orqali Stars*\n\nNarx: *{} so'm/star*\n\nNechta Stars sotib olmoqchisiz?",
        "stars_yetmaydi": "❌ Stars yetmaydi! Sizda: {}",
        "stars_sotildi": "✅ *{} Stars sotildi!*\n💰 +{:,.0f} so'm\n⭐ Qolgan: {}",
        "stars_sotib_olindi": "✅ *{} Stars sotib olindi!*\n💵 -{:,.0f} so'm\n⭐ Jami: {}",
        "premium_info": "💎 *Telegram Premium xarid*\n\nMuddatni tanlang:",
        "tolov_usul": "💎 *Premium — {}*\n💵 Narx: {:,.0f} so'm\n💰 Balansingiz: {:,.0f} so'm\n\nTolov usulini tanlang:",
        "balansdan_tolov": "💰 Balansdan tolash",
        "karta_tolov": "💳 Karta orqali",
        "balans_yetmaydi2": "❌ Balans yetmaydi!",
        "premium_ariza": "✅ *Ariza yuborildi!*\n\n💎 {}\n💵 {:,.0f} so'm\n🆔 #{}\n⏳ 10 daqiqa ichida!",
        "karta_tolov_info": "💳 *Karta orqali tolov*\n\n{} — {:,.0f} so'm\n\n📋 Karta:\n`{}`\n\nTolov qilib chekni yuboring!\n⏳ 10 daqiqa ichida",
        "chek_yuborildi": "✅ *Chek yuborildi!*\n🆔 #{}\n⏳ 10 daqiqa ichida!",
        "tasdiqlandi": "✅ *Tasdiqlandi!*\n\n🎁 {} berildi!\n📩 @shomurodav",
        "rad_etildi": "❌ *Rad etildi!*\n\n⚠️ Tolov qilmadingiz!\n📩 @shomurodav",
        "tarix": "📋 *Oxirgi 5 ta:*\n\n",
        "tarix_bosh": "📋 Tarix bosh!",
        "chiqildi": "👋 Chiqildi!",
        "login_qiling": "❌ Avval /login qiling!",
        "ruxsat_yoq": "❌ Ruxsat yoq!",
        "cmd_balans": "💰 Balans",
        "cmd_karta": "💳 Karta",
        "cmd_otkazma": "💸 O'tkazma",
        "cmd_kredit": "📋 Kredit",
        "cmd_stars": "⭐ Stars",
        "cmd_premium": "💎 Premium",
        "cmd_tarix": "📜 Tarix",
        "cmd_chiqish": "🚪 Chiqish",
        "til_ozgartirish": "🌐 Til",
        "cmd_taklif": "🎁 Taklif",
        "cmd_hisobot": "📊 Hisobot",
        "parol_yangi": "🔑 Yangi parolni kiriting (min 6 belgi):",
        "parol_ozgartirildi": "✅ Parol muvaffaqiyatli ozgartirildi!",
        "pin_yangi": "🔢 Yangi 4 xonali PIN kiriting:",
        "pin_ozgartirildi": "✅ PIN muvaffaqiyatli ozgartirildi!",
        "eski_parol": "🔑 Avval eski parolni kiriting:",
        "eski_pin": "🔢 Avval eski PIN kiriting:",
        "parol_noto_gri": "❌ Eski parol notogri!",
        "pin_noto_gri": "❌ Eski PIN notogri!",
        "taklif_info": "🎁 *Do'st taklif qilish*\n\nHar bir do'stingiz royxatdan otsa sizga *{} Stars* beriladi!\n\nSizning taklif kodingiz:\n`{}`\n\nDo'stingizga shu kodni /start dan keyin yuboring!",
        "taklif_bonus_olindi": "🎁 *Bonus!* Do'stingiz royxatdan otdi! +{} Stars berildi!",
        "hisobot": "📊 *Oylik hisobot*\n\n💰 Kirim: {:,.0f} so'm\n💸 Chiqim: {:,.0f} so'm\n💳 O'tkazmalar: {} ta\n⭐ Stars olindi: {}\n⭐ Stars sotildi: {}",
    },
    "ru": {
        "start": "🏦 Добро пожаловать в *SHOMURODOV BANK*!\n\n/register — Регистрация\n/login — Войти\n/info — О банке\n/help — Помощь",
        "til_saqlandi": "✅ Язык сохранён! Выбран русский.",
        "captcha": "🤖 Докажите что вы не бот:\n\n❓ {} + {} = ?",
        "captcha_togri": "✅ Верно!\n\n📞 Отправьте номер:\nПример: +998901234567",
        "captcha_xato": "❌ Неверно! Нажмите /register снова",
        "faqat_son": "❌ Только цифры!",
        "telefon_format": "❌ Формат: +998901234567",
        "telefon_band": "❌ Этот номер уже зарегистрирован!",
        "username_sora": "👤 Введите username (мин 3 символа, без пробелов):",
        "username_xato": "❌ Мин 3 символа, без пробелов!",
        "username_band": "❌ Username занят!",
        "parol_sora": "🔑 Создайте пароль (мин 6 символов):",
        "parol_xato": "❌ Мин 6 символов!",
        "pin_sora": "🔢 Создайте 4-значный PIN:",
        "pin_xato": "❌ Должно быть 4 цифры!",
        "account_yaratildi": "✅ *Аккаунт создан!*\n\n👤 {}\n📞 {}\n💳 **** **** **** {}\n\nДля входа:\n/login {} {}",
        "login_format": "❌ Формат: /login username пароль",
        "user_topilmadi": "❌ Пользователь не найден!",
        "bloklangan": "🔒 Аккаунт заблокирован!",
        "vaqtincha_bloklangan": "⏳ Аккаунт временно заблокирован! Попробуйте через {} минут.",
        "parol_xato2": "❌ Неверный пароль! Осталось попыток: {}",
        "xush_kelibsiz": "✅ Добро пожаловать, *{}*!\n\nВыберите команду:",
        "balans": "💰 *Баланс:* {:,.0f} сум\n⭐ *Stars:* {} шт\n💳 *Долг:* {:,.0f} сум\n📊 *Лимит:* {:,.0f} сум",
        "karta": "💳 *Карта:* `{}`\n💰 *Баланс:* {:,.0f} сум\n📞 *Телефон:* {}",
        "karta_ochish": "🔓 Открыть",
        "karta_yopish": "🔒 Закрыть",
        "karta_ozgartirildi": "✅ Изменено!",
        "otkazma_format": "❌ Формат: /otkazma номер_карты сумма",
        "summa_xato": "❌ Неверная сумма!",
        "musbat_summa": "❌ Положительная сумма!",
        "ozingizga": "❌ Нельзя отправить себе!",
        "karta_bloklangan": "❌ Карта заблокирована!",
        "karta_topilmadi": "❌ Карта не найдена!",
        "balans_yetmaydi": "❌ Недостаточно! Нужно: {:,.0f} сум",
        "otkazma_bajarildi": "✅ *Перевод выполнен!*\n💸 {:,.0f} сум\n💳 Комиссия: {:,.0f} сум\n💰 Остаток: {:,.0f} сум",
        "kredit_info": "📋 *Кредит:*\n\n📌 Макс: {:,.0f} сум\n📌 Остаток: {:,.0f} сум\n📌 Процент: 10%\n📌 Срок: 2 недели\n\nФормат: /kredit сумма",
        "kredit_tola_format": "❌ Формат: /kredit_tola сумма",
        "kredit_yoq": "✅ Кредита нет!",
        "kredit_tola_ok": "✅ *Кредит погашен!*\n\n💳 Оплачено: {:,.0f} сум\n💳 Остаток: {:,.0f} сум",
        "kredit_tola_tugadi": "✅ *Кредит полностью погашен!* 🎉\n\n🎁 Gift возвращается!\n📊 Новый лимит: {:,.0f} сум",
        "kredit_limit_tugagan": "❌ Лимит исчерпан!",
        "kredit_limit_oz": "❌ Можете взять только {:,.0f} сум!",
        "kredit_ariza": "✅ *Заявка отправлена!*\n\n🆔 #{}\n💰 {:,.0f} сум\n💸 Процент: {:,.0f} сум\n💳 Возврат: {:,.0f} сум\n📅 {} дней\n\n🎁 Отправьте Gift {:,.0f} сум @shomurodav!\n✅ При оплате Gift возвращается!\n❌ Через {} дней — конфискация!",
        "kredit_tasdiqlandi": "✅ *Кредит одобрен!*\n\n💰 {:,.0f} сум\n💳 Возврат: {:,.0f} сум\n📅 {} дней",
        "kredit_rad": "❌ *Кредит отклонён!*\n📩 @shomurodav",
        "stars_info": "⭐ *Stars*\n\nКупить: *{} сум/star*\nПродать: *{} сум/star*\nУ вас: *{} stars*\nБаланс: *{:,.0f} сум*",
        "stars_sotib_ol": "⭐ *Купить Stars*\n\nЦена: *{} сум/star*\nБаланс: *{:,.0f} сум*\n\nСколько Stars?",
        "stars_sot": "💰 *Продать Stars*\n\nЦена: *{} сум/star*\nУ вас: *{} stars*\n\nСколько?",
        "stars_karta": "💳 *Stars картой*\n\nЦена: *{} сум/star*\n\nСколько?",
        "stars_yetmaydi": "❌ Недостаточно Stars! У вас: {}",
        "stars_sotildi": "✅ *{} Stars продано!*\n💰 +{:,.0f} сум\n⭐ Остаток: {}",
        "stars_sotib_olindi": "✅ *{} Stars куплено!*\n💵 -{:,.0f} сум\n⭐ Итого: {}",
        "premium_info": "💎 *Telegram Premium*\n\nВыберите срок:",
        "tolov_usul": "💎 *Premium — {}*\n💵 {:,.0f} сум\n💰 Баланс: {:,.0f} сум\n\nСпособ оплаты:",
        "balansdan_tolov": "💰 С баланса",
        "karta_tolov": "💳 Картой",
        "balans_yetmaydi2": "❌ Недостаточно!",
        "premium_ariza": "✅ *Заявка!*\n\n💎 {}\n💵 {:,.0f} сум\n🆔 #{}\n⏳ 10 минут!",
        "karta_tolov_info": "💳 *Оплата картой*\n\n{} — {:,.0f} сум\n\n📋 Карта:\n`{}`\n\nОплатите и отправьте чек!\n⏳ 10 минут",
        "chek_yuborildi": "✅ *Чек отправлен!*\n🆔 #{}\n⏳ 10 минут!",
        "tasdiqlandi": "✅ *Подтверждено!*\n\n🎁 {} выдано!\n📩 @shomurodav",
        "rad_etildi": "❌ *Отклонено!*\n\n⚠️ Оплатите и повторите.\n📩 @shomurodav",
        "tarix": "📋 *Последние 5:*\n\n",
        "tarix_bosh": "📋 История пуста!",
        "chiqildi": "👋 Вышли!",
        "login_qiling": "❌ Сначала /login!",
        "ruxsat_yoq": "❌ Нет доступа!",
        "cmd_balans": "💰 Баланс",
        "cmd_karta": "💳 Карта",
        "cmd_otkazma": "💸 Перевод",
        "cmd_kredit": "📋 Кредит",
        "cmd_stars": "⭐ Stars",
        "cmd_premium": "💎 Premium",
        "cmd_tarix": "📜 История",
        "cmd_chiqish": "🚪 Выйти",
        "til_ozgartirish": "🌐 Язык",
        "cmd_taklif": "🎁 Реферал",
        "cmd_hisobot": "📊 Отчёт",
        "parol_yangi": "🔑 Введите новый пароль (мин 6 символов):",
        "parol_ozgartirildi": "✅ Пароль успешно изменён!",
        "pin_yangi": "🔢 Введите новый 4-значный PIN:",
        "pin_ozgartirildi": "✅ PIN успешно изменён!",
        "eski_parol": "🔑 Сначала введите старый пароль:",
        "eski_pin": "🔢 Сначала введите старый PIN:",
        "parol_noto_gri": "❌ Неверный старый пароль!",
        "pin_noto_gri": "❌ Неверный старый PIN!",
        "taklif_info": "🎁 *Реферальная программа*\n\nЗа каждого приглашённого друга вы получите *{} Stars*!\n\nВаш код:\n`{}`",
        "taklif_bonus_olindi": "🎁 *Бонус!* Друг зарегистрировался! +{} Stars!",
        "hisobot": "📊 *Месячный отчёт*\n\n💰 Приход: {:,.0f} сум\n💸 Расход: {:,.0f} сум\n💳 Переводы: {} шт\n⭐ Stars куплено: {}\n⭐ Stars продано: {}",
    },
    "en": {
        "start": "🏦 Welcome to *SHOMURODOV BANK*!\n\n/register — Register\n/login — Login\n/info — About\n/help — Help",
        "til_saqlandi": "✅ Language saved! English selected.",
        "captcha": "🤖 Prove you are not a bot:\n\n❓ {} + {} = ?",
        "captcha_togri": "✅ Correct!\n\n📞 Send your phone:\nExample: +998901234567",
        "captcha_xato": "❌ Wrong! Press /register again",
        "faqat_son": "❌ Numbers only!",
        "telefon_format": "❌ Format: +998901234567",
        "telefon_band": "❌ This phone is already registered!",
        "username_sora": "👤 Enter username (min 3 chars, no spaces):",
        "username_xato": "❌ Min 3 chars, no spaces!",
        "username_band": "❌ Username is taken!",
        "parol_sora": "🔑 Create password (min 6 chars):",
        "parol_xato": "❌ Min 6 chars!",
        "pin_sora": "🔢 Create 4-digit PIN:",
        "pin_xato": "❌ Must be 4 digits!",
        "account_yaratildi": "✅ *Account created!*\n\n👤 {}\n📞 {}\n💳 **** **** **** {}\n\nTo login:\n/login {} {}",
        "login_format": "❌ Format: /login username password",
        "user_topilmadi": "❌ User not found!",
        "bloklangan": "🔒 Account is blocked!",
        "vaqtincha_bloklangan": "⏳ Temporarily blocked! Try again in {} minutes.",
        "parol_xato2": "❌ Wrong password! Attempts left: {}",
        "xush_kelibsiz": "✅ Welcome, *{}*!\n\nChoose a command:",
        "balans": "💰 *Balance:* {:,.0f} sum\n⭐ *Stars:* {} pcs\n💳 *Credit:* {:,.0f} sum\n📊 *Limit:* {:,.0f} sum left",
        "karta": "💳 *Card:* `{}`\n💰 *Balance:* {:,.0f} sum\n📞 *Phone:* {}",
        "karta_ochish": "🔓 Show",
        "karta_yopish": "🔒 Hide",
        "karta_ozgartirildi": "✅ Changed!",
        "otkazma_format": "❌ Format: /otkazma card amount",
        "summa_xato": "❌ Invalid amount!",
        "musbat_summa": "❌ Positive amount only!",
        "ozingizga": "❌ Cannot send to yourself!",
        "karta_bloklangan": "❌ Card is blocked!",
        "karta_topilmadi": "❌ Card not found!",
        "balans_yetmaydi": "❌ Not enough! Need: {:,.0f} sum",
        "otkazma_bajarildi": "✅ *Transfer done!*\n💸 {:,.0f} sum\n💳 Fee: {:,.0f} sum\n💰 Left: {:,.0f} sum",
        "kredit_info": "📋 *Credit:*\n\n📌 Max: {:,.0f} sum\n📌 Left: {:,.0f} sum\n📌 Interest: 10%\n📌 Term: 2 weeks\n\nFormat: /kredit amount",
        "kredit_tola_format": "❌ Format: /kredit_tola amount",
        "kredit_yoq": "✅ No credit!",
        "kredit_tola_ok": "✅ *Credit paid!*\n\n💳 Paid: {:,.0f} sum\n💳 Left: {:,.0f} sum",
        "kredit_tola_tugadi": "✅ *Credit fully paid!* 🎉\n\n🎁 Gift returned!\n📊 New limit: {:,.0f} sum",
        "kredit_limit_tugagan": "❌ Credit limit exhausted!",
        "kredit_limit_oz": "❌ Can only get {:,.0f} sum!",
        "kredit_ariza": "✅ *Application sent!*\n\n🆔 #{}\n💰 {:,.0f} sum\n💸 Interest: {:,.0f} sum\n💳 Repay: {:,.0f} sum\n📅 {} days\n\n🎁 Send Gift {:,.0f} sum to @shomurodav!\n✅ Paid = Gift returned!\n❌ After {} days = confiscated!",
        "kredit_tasdiqlandi": "✅ *Credit approved!*\n\n💰 {:,.0f} sum\n💳 Repay: {:,.0f} sum\n📅 {} days",
        "kredit_rad": "❌ *Credit rejected!*\n📩 @shomurodav",
        "stars_info": "⭐ *Stars*\n\nBuy: *{} sum/star*\nSell: *{} sum/star*\nYou have: *{} stars*\nBalance: *{:,.0f} sum*",
        "stars_sotib_ol": "⭐ *Buy Stars*\n\nPrice: *{} sum/star*\nBalance: *{:,.0f} sum*\n\nHow many?",
        "stars_sot": "💰 *Sell Stars*\n\nPrice: *{} sum/star*\nYou have: *{} stars*\n\nHow many?",
        "stars_karta": "💳 *Stars by card*\n\nPrice: *{} sum/star*\n\nHow many?",
        "stars_yetmaydi": "❌ Not enough Stars! You have: {}",
        "stars_sotildi": "✅ *{} Stars sold!*\n💰 +{:,.0f} sum\n⭐ Left: {}",
        "stars_sotib_olindi": "✅ *{} Stars bought!*\n💵 -{:,.0f} sum\n⭐ Total: {}",
        "premium_info": "💎 *Telegram Premium*\n\nChoose duration:",
        "tolov_usul": "💎 *Premium — {}*\n💵 {:,.0f} sum\n💰 Balance: {:,.0f} sum\n\nPayment method:",
        "balansdan_tolov": "💰 From balance",
        "karta_tolov": "💳 By card",
        "balans_yetmaydi2": "❌ Not enough!",
        "premium_ariza": "✅ *Sent!*\n\n💎 {}\n💵 {:,.0f} sum\n🆔 #{}\n⏳ 10 min!",
        "karta_tolov_info": "💳 *Card payment*\n\n{} — {:,.0f} sum\n\n📋 Card:\n`{}`\n\nPay and send receipt!\n⏳ 10 minutes",
        "chek_yuborildi": "✅ *Receipt sent!*\n🆔 #{}\n⏳ 10 min!",
        "tasdiqlandi": "✅ *Confirmed!*\n\n🎁 {} given!\n📩 @shomurodav",
        "rad_etildi": "❌ *Rejected!*\n\n⚠️ Pay and retry.\n📩 @shomurodav",
        "tarix": "📋 *Last 5:*\n\n",
        "tarix_bosh": "📋 History empty!",
        "chiqildi": "👋 Logged out!",
        "login_qiling": "❌ Please /login first!",
        "ruxsat_yoq": "❌ No permission!",
        "cmd_balans": "💰 Balance",
        "cmd_karta": "💳 Card",
        "cmd_otkazma": "💸 Transfer",
        "cmd_kredit": "📋 Credit",
        "cmd_stars": "⭐ Stars",
        "cmd_premium": "💎 Premium",
        "cmd_tarix": "📜 History",
        "cmd_chiqish": "🚪 Logout",
        "til_ozgartirish": "🌐 Language",
        "cmd_taklif": "🎁 Referral",
        "cmd_hisobot": "📊 Report",
        "parol_yangi": "🔑 Enter new password (min 6 chars):",
        "parol_ozgartirildi": "✅ Password changed!",
        "pin_yangi": "🔢 Enter new 4-digit PIN:",
        "pin_ozgartirildi": "✅ PIN changed!",
        "eski_parol": "🔑 Enter old password first:",
        "eski_pin": "🔢 Enter old PIN first:",
        "parol_noto_gri": "❌ Wrong old password!",
        "pin_noto_gri": "❌ Wrong old PIN!",
        "taklif_info": "🎁 *Referral Program*\n\nGet *{} Stars* for each friend!\n\nYour code:\n`{}`",
        "taklif_bonus_olindi": "🎁 *Bonus!* Friend registered! +{} Stars!",
        "hisobot": "📊 *Monthly Report*\n\n💰 Income: {:,.0f} sum\n💸 Expense: {:,.0f} sum\n💳 Transfers: {} pcs\n⭐ Stars bought: {}\n⭐ Stars sold: {}",
    }
}

def t(user_or_til, kalit, *args):
    if isinstance(user_or_til, dict):
        til = user_or_til.get("til", "uz")
    else:
        til = "uz"
        for u in database["users"].values():
            if u.get("telegram_id") == user_or_til:
                til = u.get("til", "uz")
                break
    matn = MATNLAR.get(til, MATNLAR["uz"]).get(kalit, kalit)
    if args:
        return matn.format(*args)
    return matn

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"users": {}, "kredit_arizalar": {}, "tolovlar": {}}
    return {"users": {}, "kredit_arizalar": {}, "tolovlar": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_p(p):
    return hashlib.sha256(p.encode()).hexdigest()

def create_card():
    return "8600" + "".join(str(random.randint(0, 9)) for _ in range(12))

def add_history(user, text):
    vaqt = datetime.now().strftime("%d.%m.%Y %H:%M")
    user["history"].append(f"{vaqt} | {text}")
    if len(user["history"]) > 100:
        user["history"].pop(0)

def get_user(telegram_id):
    for username, user in database["users"].items():
        if user.get("telegram_id") == telegram_id:
            return username, user
    return None, None

def get_user_by_phone(phone):
    for username, user in database["users"].items():
        if user.get("phone") == phone:
            return username, user
    return None, None

def get_user_by_card(card):
    for username, user in database["users"].items():
        if user.get("card") == card:
            return username, user
    return None, None

def is_blocked_temp(user):
    blocked_until = user.get("blocked_until")
    if blocked_until:
        if datetime.now() < datetime.fromisoformat(blocked_until):
            remaining = (datetime.fromisoformat(blocked_until) - datetime.now()).seconds // 60
            return True, remaining
        else:
            user["blocked_until"] = None
            user["login_attempts"] = 0
    return False, 0

database = load_data()
captcha_store = {}
tolov_store = {}
action_store = {}

def til_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="til_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="til_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="til_en")]
    ])

def main_keyboard(til="uz"):
    m = MATNLAR[til]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(m["cmd_balans"], callback_data="cmd_balans"),
         InlineKeyboardButton(m["cmd_karta"], callback_data="cmd_karta")],
        [InlineKeyboardButton(m["cmd_otkazma"], callback_data="cmd_otkazma"),
         InlineKeyboardButton(m["cmd_kredit"], callback_data="cmd_kredit")],
        [InlineKeyboardButton(m["cmd_stars"], callback_data="cmd_stars"),
         InlineKeyboardButton(m["cmd_premium"], callback_data="cmd_premium")],
        [InlineKeyboardButton(m["cmd_tarix"], callback_data="cmd_tarix"),
         InlineKeyboardButton(m["cmd_chiqish"], callback_data="cmd_chiqish")],
        [InlineKeyboardButton(m["cmd_taklif"], callback_data="cmd_taklif"),
         InlineKeyboardButton(m["cmd_hisobot"], callback_data="cmd_hisobot")],
        [InlineKeyboardButton(m["til_ozgartirish"], callback_data="cmd_til")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    tid = update.effective_user.id
    if args:
        taklif_kod = args[0]
        if tid not in captcha_store:
            captcha_store[tid] = {"answer": 0, "step": "til_saqlandi", "data": {"taklif_kod": taklif_kod, "til": "uz"}}
        else:
            captcha_store[tid]["data"]["taklif_kod"] = taklif_kod
    await update.message.reply_text(
        "🌐 Tilni tanlang / Choose language / Выберите язык:",
        reply_markup=til_keyboard()
    )

async def til_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tid = query.from_user.id
    til = query.data.replace("til_", "")
    username, user = get_user(tid)
    if user:
        user["til"] = til
        save_data(database)
    else:
        if tid not in captcha_store:
            captcha_store[tid] = {"answer": 0, "step": "til_saqlandi", "data": {"til": til}}
        else:
            captcha_store[tid]["data"]["til"] = til
    await query.edit_message_text(
        MATNLAR[til]["til_saqlandi"] + "\n\n" + MATNLAR[til]["start"],
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    til = user.get("til", "uz") if user else "uz"
    if til == "ru":
        text = ("📖 *SHOMURODOV BANK*\n\n"
                "1. /register — Регистрация\n"
                "2. /login — Войти\n"
                "3. 💰 Баланс\n4. 💳 Карта\n"
                "5. 💸 Перевод (0.5%)\n"
                "6. 📋 Кредит (10%, 2 нед)\n"
                "7. 📊 Погасить: /kredit_tola сумма\n"
                "8. ⭐ Stars\n9. 💎 Premium\n"
                "10. 🎁 Реферал\n"
                "11. /parol_ozgartir — Пароль\n"
                "12. /pin_ozgartir — PIN\n\n"
                "📞 @shomurodav | 08:00-22:00")
    elif til == "en":
        text = ("📖 *SHOMURODOV BANK*\n\n"
                "1. /register\n2. /login\n"
                "3. 💰 Balance\n4. 💳 Card\n"
                "5. 💸 Transfer (0.5%)\n"
                "6. 📋 Credit (10%, 2 weeks)\n"
                "7. 📊 Pay: /kredit_tola amount\n"
                "8. ⭐ Stars\n9. 💎 Premium\n"
                "10. 🎁 Referral\n"
                "11. /parol_ozgartir — Password\n"
                "12. /pin_ozgartir — PIN\n\n"
                "📞 @shomurodav | 08:00-22:00")
    else:
        text = ("📖 *SHOMURODOV BANK*\n\n"
                "1. /register\n2. /login\n"
                "3. 💰 Balans\n4. 💳 Karta\n"
                "5. 💸 Otkazma (0.5%)\n"
                "6. 📋 Kredit (10%, 2 hafta)\n"
                "7. 📊 Tolash: /kredit_tola summa\n"
                "8. ⭐ Stars\n9. 💎 Premium\n"
                "10. 🎁 Taklif\n"
                "11. /parol_ozgartir — Parol\n"
                "12. /pin_ozgartir — PIN\n\n"
                "📞 @shomurodav | 08:00-22:00")
    await update.message.reply_text(text, parse_mode="Markdown")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    til = user.get("til", "uz") if user else "uz"
    if til == "ru":
        text = "🏦 *SHOMURODOV BANK*\n\nКредит без паспорта!\n\n📞 +998933381783\n⏰ 08:00-22:00\n\n✅ Без проверки оборота\n✅ Кредит без паспорта\n✅ Stars купить/продать\n✅ Telegram Premium\n\n📩 @shomurodav"
    elif til == "en":
        text = "🏦 *SHOMURODOV BANK*\n\nCredit without passport!\n\n📞 +998933381783\n⏰ 08:00-22:00\n\n✅ No turnover check\n✅ Credit without passport\n✅ Buy/sell Stars\n✅ Telegram Premium\n\n📩 @shomurodav"
    else:
        text = "🏦 *SHOMURODOV BANK*\n\nBez pasport kredit!\n\n📞 +998933381783\n⏰ 08:00-22:00\n\n✅ Pul aylanmasi tekshirilmaydi\n✅ Bez pasport kredit\n✅ Stars sotib olish/sotish\n✅ Telegram Premium\n\n📩 @shomurodav"
    await update.message.reply_text(text, parse_mode="Markdown")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = update.effective_user.id
    til = "uz"
    if tid in captcha_store:
        til = captcha_store[tid].get("data", {}).get("til", "uz")
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    taklif_kod = captcha_store.get(tid, {}).get("data", {}).get("taklif_kod", None)
    captcha_store[tid] = {"answer": a + b, "step": "captcha", "data": {"til": til, "taklif_kod": taklif_kod}}
    await update.message.reply_text(t({"til": til}, "captcha", a, b), parse_mode="Markdown")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    tid = update.effective_user.id
    if len(args) < 2:
        await update.message.reply_text(t(tid, "login_format"))
        return
    username, password = args[0], args[1]
    if username not in database["users"]:
        await update.message.reply_text(t(tid, "user_topilmadi"))
        return
    user = database["users"][username]
    if user["blocked"]:
        await update.message.reply_text(t(tid, "bloklangan"))
        return
    is_temp, remaining = is_blocked_temp(user)
    if is_temp:
        await update.message.reply_text(t(tid, "vaqtincha_bloklangan", remaining))
        return
    if hash_p(password) != user["password"]:
        user["login_attempts"] = user.get("login_attempts", 0) + 1
        if user["login_attempts"] >= 3:
            user["blocked_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
            user["login_attempts"] = 0
            save_data(database)
            await update.message.reply_text(t(tid, "vaqtincha_bloklangan", 30))
        else:
            qolgan = 3 - user["login_attempts"]
            save_data(database)
            await update.message.reply_text(t(tid, "parol_xato2", qolgan))
        return
    user["login_attempts"] = 0
    user["telegram_id"] = tid
    save_data(database)
    til = user.get("til", "uz")
    await update.message.reply_text(
        t(user, "xush_kelibsiz", username),
        parse_mode="Markdown",
        reply_markup=main_keyboard(til)
    )

async def parol_ozgartir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    action_store[update.effective_user.id] = {"step": "eski_parol"}
    await update.message.reply_text(t(user, "eski_parol"))

async def pin_ozgartir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    action_store[update.effective_user.id] = {"step": "eski_pin"}
    await update.message.reply_text(t(user, "eski_pin"))

async def kredit_tola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    if user["credit"] <= 0:
        await update.message.reply_text(t(user, "kredit_yoq"))
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            t(user, "kredit_tola_format") + f"\n\nMavjud qarz: {user['credit']:,.0f} so'm"
        )
        return
    try:
        amount = int(args[0])
    except:
        await update.message.reply_text(t(user, "summa_xato"))
        return
    if amount <= 0:
        await update.message.reply_text(t(user, "musbat_summa"))
        return
    if amount > user["balance"]:
        await update.message.reply_text(t(user, "balans_yetmaydi", amount))
        return
    if amount >= user["credit"]:
        amount = user["credit"]
        user["balance"] -= amount
        user["credit"] = 0
        user["jami_kredit"] = max(0, user.get("jami_kredit", 0) - amount)
        add_history(user, f"Kredit toliq tolandi: -{amount:,.0f}")
        save_data(database)
        qolgan_limit = KREDIT_MAX - user.get("jami_kredit", 0)
        await update.message.reply_text(
            t(user, "kredit_tola_tugadi", qolgan_limit),
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            ADMIN_ID,
            f"✅ Kredit toliq tolandi!\n👤 {username}\n💳 {amount:,.0f} so'm"
        )
    else:
        user["balance"] -= amount
        user["credit"] -= amount
        add_history(user, f"Kredit tolandi: -{amount:,.0f} | Qoldi: {user['credit']:,.0f}")
        save_data(database)
        await update.message.reply_text(
            t(user, "kredit_tola_ok", amount, user["credit"]),
            parse_mode="Markdown"
        )

async def til_ozgartir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Tilni tanlang / Choose language / Выберите язык:",
        reply_markup=til_keyboard()
    )

async def cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cmd = query.data
    username, user = get_user(query.from_user.id)
    if not user:
        await query.message.reply_text("❌ /login")
        return
    til = user.get("til", "uz")

    if cmd == "cmd_til":
        await query.message.reply_text(
            "🌐 Tilni tanlang / Choose language / Выберите язык:",
            reply_markup=til_keyboard()
        )
    elif cmd == "cmd_balans":
        qolgan = KREDIT_MAX - user.get("jami_kredit", 0)
        await query.message.reply_text(
            t(user, "balans", user["balance"], user.get("stars", 0), user["credit"], qolgan),
            parse_mode="Markdown"
        )
    elif cmd == "cmd_karta":
        karta_text = user["card"] if user.get("karta_ochiq") else "**** **** **** " + user["card"][-4:]
        kb = [[InlineKeyboardButton(
            t(user, "karta_ochish") if not user.get("karta_ochiq") else t(user, "karta_yopish"),
            callback_data="karta_toggle"
        )]]
        await query.message.reply_text(
            t(user, "karta", karta_text, user["balance"], user.get("phone", "?")),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    elif cmd == "cmd_otkazma":
        await query.message.reply_text(t(user, "otkazma_format").replace("❌ ", "ℹ️ "))
    elif cmd == "cmd_kredit":
        qolgan = KREDIT_MAX - user.get("jami_kredit", 0)
        await query.message.reply_text(
            t(user, "kredit_info", KREDIT_MAX, qolgan),
            parse_mode="Markdown"
        )
    elif cmd == "cmd_stars":
        kb = [
            [InlineKeyboardButton("⭐ " + ("Sotib olish" if til == "uz" else "Купить" if til == "ru" else "Buy"), callback_data="stars_sotib_ol")],
            [InlineKeyboardButton("💰 " + ("Sotish" if til == "uz" else "Продать" if til == "ru" else "Sell"), callback_data="stars_sot")],
            [InlineKeyboardButton("💳 " + ("Karta orqali" if til == "uz" else "Через карту" if til == "ru" else "By card"), callback_data="stars_karta")]
        ]
        await query.message.reply_text(
            t(user, "stars_info", STARS_SOTISH, STARS_OLISH, user.get("stars", 0), user["balance"]),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    elif cmd == "cmd_premium":
        kb = [
            [InlineKeyboardButton(f"💎 1 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 45,000", callback_data="premium_1")],
            [InlineKeyboardButton(f"💎 3 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 180,000", callback_data="premium_3")],
            [InlineKeyboardButton(f"💎 6 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 240,000", callback_data="premium_6")],
            [InlineKeyboardButton(f"💎 12 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 400,000", callback_data="premium_12")],
        ]
        await query.message.reply_text(
            t(user, "premium_info"),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    elif cmd == "cmd_tarix":
        if not user["history"]:
            await query.message.reply_text(t(user, "tarix_bosh"))
            return
        text = t(user, "tarix")
        for i, item in enumerate(user["history"][-5:], 1):
            text += f"{i}. {item}\n"
        await query.message.reply_text(text, parse_mode="Markdown")
    elif cmd == "cmd_taklif":
        taklif_kod = f"ref_{username}"
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        link = f"https://t.me/{bot_username}?start={taklif_kod}"
        await query.message.reply_text(
            t(user, "taklif_info", TAKLIF_BONUS, taklif_kod) + f"\n\n🔗 Link:\n{link}",
            parse_mode="Markdown"
        )
    elif cmd == "cmd_hisobot":
        oy = datetime.now().strftime("%m.%Y")
        kirim = 0
        chiqim = 0
        otkazma_count = 0
        stars_olindi = 0
        stars_sotildi = 0
        for item in user["history"]:
            if oy in item:
                if "Qabul" in item or "+" in item and "Stars" not in item:
                    try:
                        summa = int(''.join(filter(str.isdigit, item.split("+")[1].split()[0])))
                        kirim += summa
                    except:
                        pass
                if "Otkazma" in item or "Transfer" in item:
                    otkazma_count += 1
                    try:
                        summa = int(''.join(filter(str.isdigit, item.split("-")[1].split()[0])))
                        chiqim += summa
                    except:
                        pass
                if "Stars sotib olindi" in item or "Stars bought" in item or "Stars куплено" in item:
                    try:
                        s = int(item.split("⭐")[0].strip().split()[-1])
                        stars_olindi += s
                    except:
                        pass
                if "Stars sotildi" in item or "Stars sold" in item or "Stars продано" in item:
                    try:
                        s = int(item.split("Stars")[0].strip().split()[-1])
                        stars_sotildi += s
                    except:
                        pass
        await query.message.reply_text(
            t(user, "hisobot", kirim, chiqim, otkazma_count, stars_olindi, stars_sotildi),
            parse_mode="Markdown"
        )
    elif cmd == "cmd_chiqish":
        user["telegram_id"] = None
        save_data(database)
        await query.message.reply_text(t(user, "chiqildi"))

async def karta_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username, user = get_user(query.from_user.id)
    if not user:
        await query.answer("❌")
        return
    user["karta_ochiq"] = not user.get("karta_ochiq", False)
    save_data(database)
    await query.answer(t(user, "karta_ozgartirildi"))
    karta_text = user["card"] if user["karta_ochiq"] else "**** **** **** " + user["card"][-4:]
    kb = [[InlineKeyboardButton(
        t(user, "karta_ochish") if not user.get("karta_ochiq") else t(user, "karta_yopish"),
        callback_data="karta_toggle"
    )]]
    await query.edit_message_text(
        t(user, "karta", karta_text, user["balance"], user.get("phone", "?")),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def otkazma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(t(user, "otkazma_format"))
        return
    target_card, amount_str = args[0], args[1]
    try:
        amount = int(amount_str)
    except:
        await update.message.reply_text(t(user, "summa_xato"))
        return
    if amount <= 0:
        await update.message.reply_text(t(user, "musbat_summa"))
        return
    if target_card == user["card"]:
        await update.message.reply_text(t(user, "ozingizga"))
        return
    found, found_name = None, None
    for uname, u in database["users"].items():
        if u["card"] == target_card:
            if u["blocked"]:
                await update.message.reply_text(t(user, "karta_bloklangan"))
                return
            found, found_name = u, uname
            break
    if not found:
        await update.message.reply_text(t(user, "karta_topilmadi"))
        return
    fee = round(amount * OTKAZMA_FOIZ)
    total = amount + fee
    if total > user["balance"]:
        await update.message.reply_text(t(user, "balans_yetmaydi", total))
        return
    user["balance"] -= total
    found["balance"] += amount
    add_history(user, f"Otkazma: -{amount:,.0f} -> {target_card[-4:]}")
    add_history(found, f"Qabul: +{amount:,.0f} <- {username}")
    save_data(database)
    await update.message.reply_text(
        t(user, "otkazma_bajarildi", amount, fee, user["balance"]),
        parse_mode="Markdown"
    )

async def kredit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    qolgan = KREDIT_MAX - user.get("jami_kredit", 0)
    args = context.args
    if not args:
        await update.message.reply_text(t(user, "kredit_info", KREDIT_MAX, qolgan), parse_mode="Markdown")
        return
    try:
        amount = int(args[0])
    except:
        await update.message.reply_text(t(user, "summa_xato"))
        return
    if amount <= 0:
        await update.message.reply_text(t(user, "musbat_summa"))
        return
    if qolgan <= 0:
        await update.message.reply_text(t(user, "kredit_limit_tugagan"))
        return
    if amount > qolgan:
        await update.message.reply_text(t(user, "kredit_limit_oz", qolgan))
        return
    foiz = round(amount * KREDIT_FOIZ)
    total = amount + foiz
    gift_kerak = round(amount / 0.70)
    ariza_id = str(random.randint(10000, 99999))
    database["kredit_arizalar"][ariza_id] = {
        "username": username,
        "telegram_id": update.effective_user.id,
        "amount": amount, "foiz": foiz, "total": total,
        "gift_kerak": gift_kerak,
        "vaqt": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "muddat": KREDIT_MUDDAT
    }
    save_data(database)
    kb = [[
        InlineKeyboardButton("✅", callback_data=f"kredit_ok_{ariza_id}"),
        InlineKeyboardButton("❌", callback_data=f"kredit_rad_{ariza_id}")
    ]]
    await context.bot.send_message(
        ADMIN_ID,
        f"🔔 *Kredit!*\n\n👤 {username}\n📞 {user.get('phone', '?')}\n"
        f"💰 {amount:,.0f}\n💸 {foiz:,.0f}\n💳 {total:,.0f}\n"
        f"🎁 {gift_kerak:,.0f}\n📅 {KREDIT_MUDDAT} kun\n🆔 #{ariza_id}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    await update.message.reply_text(
        t(user, "kredit_ariza", ariza_id, amount, foiz, total, KREDIT_MUDDAT, gift_kerak, KREDIT_MUDDAT),
        parse_mode="Markdown"
    )

async def kredit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    data = query.data
    if data.startswith("kredit_ok_"):
        ariza_id = data.replace("kredit_ok_", "")
        if ariza_id not in database["kredit_arizalar"]:
            await query.answer("❌")
            return
        ariza = database["kredit_arizalar"][ariza_id]
        user = database["users"][ariza["username"]]
        user["balance"] += ariza["amount"]
        user["credit"] = user.get("credit", 0) + ariza["total"]
        user["jami_kredit"] = user.get("jami_kredit", 0) + ariza["amount"]
        user["kredit_sana"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        add_history(user, f"Kredit +{ariza['amount']:,.0f}")
        del database["kredit_arizalar"][ariza_id]
        save_data(database)
        await context.bot.send_message(
            ariza["telegram_id"],
            t(user, "kredit_tasdiqlandi", ariza["amount"], ariza["total"], KREDIT_MUDDAT),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ #{ariza_id}")
    elif data.startswith("kredit_rad_"):
        ariza_id = data.replace("kredit_rad_", "")
        if ariza_id not in database["kredit_arizalar"]:
            await query.answer("❌")
            return
        ariza = database["kredit_arizalar"][ariza_id]
        user = database["users"][ariza["username"]]
        del database["kredit_arizalar"][ariza_id]
        save_data(database)
        await context.bot.send_message(ariza["telegram_id"], t(user, "kredit_rad"), parse_mode="Markdown")
        await query.edit_message_text(f"❌ #{ariza_id}")

async def stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    til = user.get("til", "uz")
    kb = [
        [InlineKeyboardButton("⭐ " + ("Sotib olish" if til == "uz" else "Купить" if til == "ru" else "Buy"), callback_data="stars_sotib_ol")],
        [InlineKeyboardButton("💰 " + ("Sotish" if til == "uz" else "Продать" if til == "ru" else "Sell"), callback_data="stars_sot")],
        [InlineKeyboardButton("💳 " + ("Karta orqali" if til == "uz" else "Через карту" if til == "ru" else "By card"), callback_data="stars_karta")]
    ]
    await update.message.reply_text(
        t(user, "stars_info", STARS_SOTISH, STARS_OLISH, user.get("stars", 0), user["balance"]),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def stars_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username, user = get_user(query.from_user.id)
    if not user:
        await query.answer("❌")
        return
    data = query.data
    if data == "stars_sotib_ol":
        tolov_store[query.from_user.id] = {"step": "stars_sotib_ol_miqdor"}
        await query.edit_message_text(
            t(user, "stars_sotib_ol", STARS_SOTISH, user["balance"]),
            parse_mode="Markdown"
        )
    elif data == "stars_sot":
        tolov_store[query.from_user.id] = {"step": "stars_sot_miqdor"}
        await query.edit_message_text(
            t(user, "stars_sot", STARS_OLISH, user.get("stars", 0)),
            parse_mode="Markdown"
        )
    elif data == "stars_karta":
        tolov_store[query.from_user.id] = {"step": "stars_karta_miqdor"}
        await query.edit_message_text(
            t(user, "stars_karta", STARS_SOTISH),
            parse_mode="Markdown"
        )

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    til = user.get("til", "uz")
    kb = [
        [InlineKeyboardButton(f"💎 1 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 45,000", callback_data="premium_1")],
        [InlineKeyboardButton(f"💎 3 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 180,000", callback_data="premium_3")],
        [InlineKeyboardButton(f"💎 6 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 240,000", callback_data="premium_6")],
        [InlineKeyboardButton(f"💎 12 {'oy' if til == 'uz' else 'мес' if til == 'ru' else 'mo'} — 400,000", callback_data="premium_12")],
    ]
    await update.message.reply_text(t(user, "premium_info"), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def premium_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username, user = get_user(query.from_user.id)
    if not user:
        await query.answer("❌")
        return
    til = user.get("til", "uz")
    data = query.data
    if data.startswith("premium_") and not data.startswith("prem"):
        muddat = data.replace("premium_", "")
        p = PREMIUM_NARX[muddat]
        oy = p["oy"][til]
        kb = [
            [InlineKeyboardButton(t(user, "balansdan_tolov"), callback_data=f"prem_balans_{muddat}")],
            [InlineKeyboardButton(t(user, "karta_tolov"), callback_data=f"prem_karta_{muddat}")]
        ]
        await query.edit_message_text(
            t(user, "tolov_usul", oy, p["narx"], user["balance"]),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("prem_balans_"):
        muddat = data.replace("prem_balans_", "")
        p = PREMIUM_NARX[muddat]
        oy = p["oy"][til]
        if user["balance"] < p["narx"]:
            await query.answer(t(user, "balans_yetmaydi2"))
            return
        user["balance"] -= p["narx"]
        add_history(user, f"Premium {oy} -{p['narx']:,.0f}")
        ariza_id = str(random.randint(10000, 99999))
        database["tolovlar"][ariza_id] = {
            "username": username, "telegram_id": query.from_user.id,
            "tur": f"Premium {oy}", "narx": p["narx"], "usul": "balans",
            "vaqt": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        save_data(database)
        kb = [[
            InlineKeyboardButton("✅", callback_data=f"tolov_ok_{ariza_id}"),
            InlineKeyboardButton("❌", callback_data=f"tolov_rad_{ariza_id}")
        ]]
        await context.bot.send_message(
            ADMIN_ID,
            f"💎 Premium!\n👤 {username}\n📞 {user.get('phone', '?')}\n"
            f"💵 {p['narx']:,.0f}\n📅 {oy}\n🆔 #{ariza_id}",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        await query.edit_message_text(
            t(user, "premium_ariza", oy, p["narx"], ariza_id),
            parse_mode="Markdown"
        )
    elif data.startswith("prem_karta_"):
        muddat = data.replace("prem_karta_", "")
        p = PREMIUM_NARX[muddat]
        oy = p["oy"][til]
        tolov_store[query.from_user.id] = {"step": "chek_kutish", "narx": p["narx"], "nom": f"Premium {oy}"}
        await query.edit_message_text(
            t(user, "karta_tolov_info", oy, p["narx"], KARTA),
            parse_mode="Markdown"
        )

async def tolov_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    data = query.data
    if data.startswith("tolov_ok_"):
        ariza_id = data.replace("tolov_ok_", "")
        if ariza_id not in database["tolovlar"]:
            await query.answer("❌")
            return
        ariza = database["tolovlar"][ariza_id]
        user = database["users"].get(ariza["username"])
        del database["tolovlar"][ariza_id]
        save_data(database)
        if user:
            await context.bot.send_message(
                ariza["telegram_id"],
                t(user, "tasdiqlandi", ariza["tur"]),
                parse_mode="Markdown"
            )
        await query.edit_message_text(f"✅ {ariza['tur']} — {ariza['username']}")
    elif data.startswith("tolov_rad_"):
        ariza_id = data.replace("tolov_rad_", "")
        if ariza_id not in database["tolovlar"]:
            await query.answer("❌")
            return
        ariza = database["tolovlar"][ariza_id]
        if ariza.get("usul") == "balans" and ariza["username"] in database["users"]:
            database["users"][ariza["username"]]["balance"] += ariza["narx"]
        user = database["users"].get(ariza["username"])
        del database["tolovlar"][ariza_id]
        save_data(database)
        if user:
            await context.bot.send_message(
                ariza["telegram_id"],
                t(user, "rad_etildi"),
                parse_mode="Markdown"
            )
        await query.edit_message_text(f"❌ {ariza['username']}")

async def tarix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    if not user["history"]:
        await update.message.reply_text(t(user, "tarix_bosh"))
        return
    text = t(user, "tarix")
    for i, item in enumerate(user["history"][-5:], 1):
        text += f"{i}. {item}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def chiqish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username, user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text(t(update.effective_user.id, "login_qiling"))
        return
    user["telegram_id"] = None
    save_data(database)
    await update.message.reply_text(t(user, "chiqildi"))

# ================= ADMIN =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    await update.message.reply_text(
        f"👑 *Admin Panel*\n\n"
        f"👥 Users: {len(database['users'])}\n"
        f"📋 Kredit: {len(database.get('kredit_arizalar', {}))}\n"
        f"💳 Tolov: {len(database.get('tolovlar', {}))}\n\n"
        f"📋 *Buyruqlar:*\n"
        f"/userlar — Barcha userlar\n"
        f"/bloklash username — Bloklash\n"
        f"/arizalar — Kredit arizalar\n"
        f"/karta_kir karta — Karta info\n"
        f"/karta_qosh karta summa — Pul qoshish\n"
        f"/karta_ochi karta summa — Pul ochirish\n"
        f"/kredit_yop username — Kredit yopish\n"
        f"/stars_qosh karta miqdor — Stars qoshish\n"
        f"/stars_ochi karta miqdor — Stars ochirish\n"
        f"/xabar username matn — Xabar yuborish\n"
        f"/hammaga matn — Hammaga xabar\n"
        f"/statistika — Kunlik statistika",
        parse_mode="Markdown"
    )

async def userlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not database["users"]:
        await update.message.reply_text("Yoq!")
        return
    text = "👥 *Users:*\n\n"
    for uname, u in database["users"].items():
        s = "🔒" if u["blocked"] else "✅"
        text += f"{s} {uname} | {u['balance']:,.0f} | ⭐{u.get('stars', 0)} | {u.get('phone', '?')} | {u.get('til', 'uz')}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def bloklash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not context.args:
        await update.message.reply_text("Format: /bloklash username")
        return
    username = context.args[0]
    if username not in database["users"]:
        await update.message.reply_text("❌ Topilmadi!")
        return
    u = database["users"][username]
    u["blocked"] = not u["blocked"]
    save_data(database)
    await update.message.reply_text("🔒 Bloklandi" if u["blocked"] else "✅ Blok ochildi")

async def arizalar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not database.get("kredit_arizalar"):
        await update.message.reply_text("Yoq!")
        return
    text = "📋 *Kredit:*\n\n"
    for aid, a in database["kredit_arizalar"].items():
        text += f"#{aid} | {a['username']} | {a['amount']:,.0f}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def karta_kir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not context.args:
        await update.message.reply_text("Format: /karta_kir karta")
        return
    found_name, found_user = get_user_by_card(context.args[0])
    if not found_user:
        await update.message.reply_text("❌ Topilmadi!")
        return
    qolgan = KREDIT_MAX - found_user.get("jami_kredit", 0)
    await update.message.reply_text(
        f"💳 *{found_name}*\n📞 {found_user.get('phone', '?')}\n"
        f"💳 {found_user['card']}\n💰 {found_user['balance']:,.0f}\n"
        f"⭐ Stars: {found_user.get('stars', 0)}\n"
        f"💳 Kredit: {found_user['credit']:,.0f}\n"
        f"📊 Limit qoldi: {qolgan:,.0f}\n"
        f"{'🔒' if found_user['blocked'] else '✅'}",
        parse_mode="Markdown"
    )

async def karta_qosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /karta_qosh karta summa")
        return
    found_name, found_user = get_user_by_card(context.args[0])
    if not found_user:
        await update.message.reply_text("❌ Topilmadi!")
        return
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Summa xato!")
        return
    found_user["balance"] += amount
    add_history(found_user, f"Admin +{amount:,.0f}")
    save_data(database)
    await update.message.reply_text(f"✅ {found_name} +{amount:,.0f} | Balans: {found_user['balance']:,.0f}")
    if found_user.get("telegram_id"):
        await context.bot.send_message(
            found_user["telegram_id"],
            f"💰 +{amount:,.0f}\n💰 Balans: {found_user['balance']:,.0f}"
        )

async def karta_ochi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /karta_ochi karta summa")
        return
    found_name, found_user = get_user_by_card(context.args[0])
    if not found_user:
        await update.message.reply_text("❌ Topilmadi!")
        return
    try:
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Summa xato!")
        return
    if amount > found_user["balance"]:
        await update.message.reply_text(f"❌ Balans yetmaydi! {found_user['balance']:,.0f}")
        return
    found_user["balance"] -= amount
    add_history(found_user, f"Admin -{amount:,.0f}")
    save_data(database)
    await update.message.reply_text(f"✅ {found_name} -{amount:,.0f} | Balans: {found_user['balance']:,.0f}")
    if found_user.get("telegram_id"):
        await context.bot.send_message(
            found_user["telegram_id"],
            f"⚠️ -{amount:,.0f}\n💰 Balans: {found_user['balance']:,.0f}"
        )

async def kredit_yop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not context.args:
        await update.message.reply_text("Format: /kredit_yop username")
        return
    username = context.args[0]
    if username not in database["users"]:
        await update.message.reply_text("❌ Topilmadi!")
        return
    user = database["users"][username]
    if user["credit"] <= 0:
        await update.message.reply_text("✅ Krediti yoq!")
        return
    old = user["credit"]
    user["credit"] = 0
    user["jami_kredit"] = max(0, user.get("jami_kredit", 0) - old)
    add_history(user, f"Admin kredit yopdi {old:,.0f}")
    save_data(database)
    qolgan = KREDIT_MAX - user.get("jami_kredit", 0)
    await update.message.reply_text(f"✅ {username} kredit yopildi: {old:,.0f}\nYangi limit: {qolgan:,.0f}")
    if user.get("telegram_id"):
        await context.bot.send_message(
            user["telegram_id"],
            f"✅ Kreditingiz yopildi: {old:,.0f}\n🎁 Giftingiz qaytariladi!\n📊 Yangi limit: {qolgan:,.0f}"
        )

async def stars_qosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /stars_qosh karta miqdor")
        return
    found_name, found_user = get_user_by_card(context.args[0])
    if not found_user:
        await update.message.reply_text("❌ Topilmadi!")
        return
    try:
        miqdor = int(context.args[1])
    except:
        await update.message.reply_text("❌ Miqdor xato!")
        return
    found_user["stars"] = found_user.get("stars", 0) + miqdor
    add_history(found_user, f"Admin +{miqdor}⭐")
    save_data(database)
    await update.message.reply_text(f"✅ {found_name} +{miqdor}⭐ | Jami: {found_user['stars']}⭐")
    if found_user.get("telegram_id"):
        await context.bot.send_message(found_user["telegram_id"], f"⭐ +{miqdor} Stars! Jami: {found_user['stars']}⭐")

async def stars_ochi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /stars_ochi karta miqdor")
        return
    found_name, found_user = get_user_by_card(context.args[0])
    if not found_user:
        await update.message.reply_text("❌ Topilmadi!")
        return
    try:
        miqdor = int(context.args[1])
    except:
        await update.message.reply_text("❌ Miqdor xato!")
        return
    if miqdor > found_user.get("stars", 0):
        await update.message.reply_text(f"❌ Stars yetmaydi! Mavjud: {found_user.get('stars', 0)}")
        return
    found_user["stars"] -= miqdor
    add_history(found_user, f"Admin -{miqdor}⭐")
    save_data(database)
    await update.message.reply_text(f"✅ {found_name} -{miqdor}⭐ | Qolgan: {found_user['stars']}⭐")
    if found_user.get("telegram_id"):
        await context.bot.send_message(found_user["telegram_id"], f"⚠️ -{miqdor} Stars! Qolgan: {found_user['stars']}⭐")

async def xabar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /xabar username matn")
        return
    username = context.args[0]
    matn = " ".join(context.args[1:])
    if username not in database["users"]:
        await update.message.reply_text("❌ User topilmadi!")
        return
    user = database["users"][username]
    if not user.get("telegram_id"):
        await update.message.reply_text("❌ User hozir online emas!")
        return
    await context.bot.send_message(
        user["telegram_id"],
        f"📩 *Admin xabari:*\n\n{matn}",
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ {username} ga xabar yuborildi!")

async def hammaga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    if not context.args:
        await update.message.reply_text("Format: /hammaga matn")
        return
    matn = " ".join(context.args)
    yuborildi = 0
    for uname, u in database["users"].items():
        if u.get("telegram_id"):
            try:
                await context.bot.send_message(
                    u["telegram_id"],
                    f"📢 *SHOMURODOV BANK:*\n\n{matn}",
                    parse_mode="Markdown"
                )
                yuborildi += 1
            except:
                pass
    await update.message.reply_text(f"✅ {yuborildi} ta usergа xabar yuborildi!")

async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌")
        return
    bugun = datetime.now().strftime("%d.%m.%Y")
    jami_balans = sum(u["balance"] for u in database["users"].values())
    jami_kredit = sum(u["credit"] for u in database["users"].values())
    jami_stars = sum(u.get("stars", 0) for u in database["users"].values())
    faol = sum(1 for u in database["users"].values() if u.get("telegram_id"))
    bugungi_amallar = 0
    for u in database["users"].values():
        for h in u["history"]:
            if bugun in h:
                bugungi_amallar += 1
    await update.message.reply_text(
        f"📊 *Statistika — {bugun}*\n\n"
        f"👥 Jami users: {len(database['users'])}\n"
        f"🟢 Faol: {faol}\n"
        f"💰 Jami balans: {jami_balans:,.0f} so'm\n"
        f"💳 Jami kredit: {jami_kredit:,.0f} so'm\n"
        f"⭐ Jami Stars: {jami_stars}\n"
        f"📋 Bugungi amallar: {bugungi_amallar}\n"
        f"📋 Kredit arizalar: {len(database.get('kredit_arizalar', {}))}\n"
        f"💳 Tolov arizalar: {len(database.get('tolovlar', {}))}",
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = update.effective_user.id

    if update.message.photo:
        if tid in tolov_store and tolov_store[tid].get("step") == "chek_kutish":
            username, user = get_user(tid)
            store = tolov_store[tid]
            ariza_id = str(random.randint(10000, 99999))
            database["tolovlar"][ariza_id] = {
                "username": username, "telegram_id": tid,
                "tur": store["nom"], "narx": store["narx"],
                "usul": "karta", "vaqt": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            save_data(database)
            kb = [[
                InlineKeyboardButton("✅", callback_data=f"tolov_ok_{ariza_id}"),
                InlineKeyboardButton("❌", callback_data=f"tolov_rad_{ariza_id}")
            ]]
            await context.bot.send_photo(
                ADMIN_ID, update.message.photo[-1].file_id,
                caption=f"💳 Chek!\n👤 {username}\n🎁 {store['nom']}\n💵 {store['narx']:,.0f}\n🆔 #{ariza_id}",
                reply_markup=InlineKeyboardMarkup(kb)
            )
            del tolov_store[tid]
            await update.message.reply_text(
                t(user, "chek_yuborildi", ariza_id) if user else f"✅ #{ariza_id}",
                parse_mode="Markdown"
            )
        return

    text = update.message.text if update.message.text else ""

    # PAROL / PIN OZGARTIRISH
    if tid in action_store:
        action = action_store[tid]
        step = action.get("step")
        username, user = get_user(tid)
        if not user:
            del action_store[tid]
            return

        if step == "eski_parol":
            if hash_p(text) == user["password"]:
                action_store[tid]["step"] = "yangi_parol"
                await update.message.reply_text(t(user, "parol_yangi"))
            else:
                await update.message.reply_text(t(user, "parol_noto_gri"))
                del action_store[tid]
        elif step == "yangi_parol":
            if len(text) < 6:
                await update.message.reply_text(t(user, "parol_xato"))
            else:
                user["password"] = hash_p(text)
                save_data(database)
                del action_store[tid]
                await update.message.reply_text(t(user, "parol_ozgartirildi"))
        elif step == "eski_pin":
            if hash_p(text) == user.get("pin", ""):
                action_store[tid]["step"] = "yangi_pin"
                await update.message.reply_text(t(user, "pin_yangi"))
            else:
                await update.message.reply_text(t(user, "pin_noto_gri"))
                del action_store[tid]
        elif step == "yangi_pin":
            if not (text.isdigit() and len(text) == 4):
                await update.message.reply_text(t(user, "pin_xato"))
            else:
                user["pin"] = hash_p(text)
                save_data(database)
                del action_store[tid]
                await update.message.reply_text(t(user, "pin_ozgartirildi"))
        return

    # CAPTCHA / REGISTER
    if tid in captcha_store:
        store = captcha_store[tid]
        step = store["step"]
        til = store.get("data", {}).get("til", "uz")

        if step == "til_saqlandi":
            captcha_store[tid]["step"] = "captcha"
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            captcha_store[tid]["answer"] = a + b
            await update.message.reply_text(t({"til": til}, "captcha", a, b), parse_mode="Markdown")
            return

        if step == "captcha":
            try:
                if int(text) == store["answer"]:
                    captcha_store[tid]["step"] = "phone"
                    await update.message.reply_text(t({"til": til}, "captcha_togri"))
                else:
                    await update.message.reply_text(t({"til": til}, "captcha_xato"))
                    del captcha_store[tid]
            except:
                await update.message.reply_text(t({"til": til}, "faqat_son"))
        elif step == "phone":
            ex_name, ex_user = get_user_by_phone(text)
            if ex_user:
                await update.message.reply_text(t({"til": til}, "telefon_band"))
                del captcha_store[tid]
                return
            if text.startswith("+998") and len(text) == 13:
                captcha_store[tid]["data"]["phone"] = text
                captcha_store[tid]["step"] = "username"
                await update.message.reply_text(t({"til": til}, "username_sora"))
            else:
                await update.message.reply_text(t({"til": til}, "telefon_format"))
        elif step == "username":
            if len(text) < 3 or " " in text:
                await update.message.reply_text(t({"til": til}, "username_xato"))
            elif text in database["users"]:
                await update.message.reply_text(t({"til": til}, "username_band"))
            else:
                captcha_store[tid]["data"]["username"] = text
                captcha_store[tid]["step"] = "password"
                await update.message.reply_text(t({"til": til}, "parol_sora"))
        elif step == "password":
            if len(text) < 6:
                await update.message.reply_text(t({"til": til}, "parol_xato"))
            else:
                captcha_store[tid]["data"]["password"] = text
                captcha_store[tid]["step"] = "pin"
                await update.message.reply_text(t({"til": til}, "pin_sora"))
        elif step == "pin":
            if not (text.isdigit() and len(text) == 4):
                await update.message.reply_text(t({"til": til}, "pin_xato"))
            else:
                d = captcha_store[tid]["data"]
                card = create_card()
                database["users"][d["username"]] = {
                    "password": hash_p(d["password"]),
                    "pin": hash_p(text),
                    "phone": d["phone"],
                    "card": card,
                    "balance": 0, "stars": 0, "credit": 0,
                    "jami_kredit": 0, "history": [],
                    "blocked": False, "telegram_id": tid,
                    "karta_ochiq": False, "til": til,
                    "login_attempts": 0
                }
                save_data(database)
                # Taklif bonusi
                taklif_kod = d.get("taklif_kod")
                if taklif_kod and taklif_kod.startswith("ref_"):
                    ref_username = taklif_kod.replace("ref_", "")
                    if ref_username in database["users"] and ref_username != d["username"]:
                        ref_user = database["users"][ref_username]
                        ref_user["stars"] = ref_user.get("stars", 0) + TAKLIF_BONUS
                        add_history(ref_user, f"Taklif bonus +{TAKLIF_BONUS}⭐")
                        save_data(database)
                        if ref_user.get("telegram_id"):
                            await context.bot.send_message(
                                ref_user["telegram_id"],
                                t(ref_user, "taklif_bonus_olindi", TAKLIF_BONUS),
                                parse_mode="Markdown"
                            )
                del captcha_store[tid]
                await update.message.reply_text(
                    t({"til": til}, "account_yaratildi", d["username"], d["phone"], card[-4:], d["username"], d["password"]),
                    parse_mode="Markdown"
                )
        return

    # STARS / TOLOV
    if tid in tolov_store:
        store = tolov_store[tid]
        step = store.get("step", "")
        username, user = get_user(tid)

        if step == "stars_sotib_ol_miqdor":
            try:
                miqdor = int(text)
                narx = miqdor * STARS_SOTISH
                if user["balance"] < narx:
                    await update.message.reply_text(t(user, "balans_yetmaydi", narx))
                    del tolov_store[tid]
                    return
                user["balance"] -= narx
                user["stars"] = user.get("stars", 0) + miqdor
                add_history(user, f"{miqdor}⭐ sotib olindi -{narx:,.0f}")
                save_data(database)
                del tolov_store[tid]
                await update.message.reply_text(
                    t(user, "stars_sotib_olindi", miqdor, narx, user["stars"]),
                    parse_mode="Markdown"
                )
            except:
                await update.message.reply_text(t(user, "faqat_son"))

        elif step == "stars_sot_miqdor":
            try:
                miqdor = int(text)
                if user.get("stars", 0) < miqdor:
                    await update.message.reply_text(t(user, "stars_yetmaydi", user.get("stars", 0)))
                    del tolov_store[tid]
                    return
                narx = miqdor * STARS_OLISH
                user["stars"] -= miqdor
                user["balance"] += narx
                add_history(user, f"{miqdor}⭐ sotildi +{narx:,.0f}")
                save_data(database)
                del tolov_store[tid]
                await update.message.reply_text(
                    t(user, "stars_sotildi", miqdor, narx, user["stars"]),
                    parse_mode="Markdown"
                )
            except:
                await update.message.reply_text(t(user, "faqat_son"))

        elif step == "stars_karta_miqdor":
            try:
                miqdor = int(text)
                narx = miqdor * STARS_SOTISH
                tolov_store[tid] = {"step": "chek_kutish", "narx": narx, "nom": f"{miqdor} Stars"}
                await update.message.reply_text(
                    t(user, "karta_tolov_info", f"{miqdor} Stars", narx, KARTA),
                    parse_mode="Markdown"
                )
            except:
                await update.message.reply_text(t(user, "faqat_son"))

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("register", register))
app.add_handler(CommandHandler("til", til_ozgartir))
app.add_handler(CommandHandler("otkazma", otkazma))
app.add_handler(CommandHandler("kredit", kredit))
app.add_handler(CommandHandler("kredit_tola", kredit_tola))
app.add_handler(CommandHandler("parol_ozgartir", parol_ozgartir))
app.add_handler(CommandHandler("pin_ozgartir", pin_ozgartir))
app.add_handler(CommandHandler("stars", stars))
app.add_handler(CommandHandler("premium", premium))
app.add_handler(CommandHandler("tarix", tarix))
app.add_handler(CommandHandler("chiqish", chiqish))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("userlar", userlar))
app.add_handler(CommandHandler("bloklash", bloklash))
app.add_handler(CommandHandler("arizalar", arizalar))
app.add_handler(CommandHandler("karta_kir", karta_kir))
app.add_handler(CommandHandler("karta_qosh", karta_qosh))
app.add_handler(CommandHandler("karta_ochi", karta_ochi))
app.add_handler(CommandHandler("kredit_yop", kredit_yop))
app.add_handler(CommandHandler("stars_qosh", stars_qosh))
app.add_handler(CommandHandler("stars_ochi", stars_ochi))
app.add_handler(CommandHandler("xabar", xabar))
app.add_handler(CommandHandler("hammaga", hammaga))
app.add_handler(CommandHandler("statistika", statistika))
app.add_handler(CallbackQueryHandler(til_callback, pattern="^til_"))
app.add_handler(CallbackQueryHandler(cmd_callback, pattern="^cmd_"))
app.add_handler(CallbackQueryHandler(karta_toggle, pattern="^karta_toggle$"))
app.add_handler(CallbackQueryHandler(kredit_callback, pattern="^kredit_"))
app.add_handler(CallbackQueryHandler(premium_callback, pattern="^premium_|^prem_"))
app.add_handler(CallbackQueryHandler(stars_callback, pattern="^stars_"))
app.add_handler(CallbackQueryHandler(tolov_callback, pattern="^tolov_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, message_handler))

print("✅ Bot ishga tushdi!")
asyncio.get_event_loop().run_until_complete(app.run_polling())
