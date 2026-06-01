# Telegram bot — O'zbek ovqat retseptlari
# Kutubxona: pyTelegramBotAPI (telebot)
# O'rnatish: pip install pyTelegramBotAPI

import os
import telebot
from telebot import types


# ============== TOKEN ==============
# Token muhit o'zgaruvchisidan (BOT_TOKEN) o'qiladi.
# Lokal sinov uchun: export BOT_TOKEN="..."
# Railway/Fly.io'da: Variables bo'limida BOT_TOKEN qo'shing.
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN muhit o'zgaruvchisi o'rnatilmagan!")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ============== RETSEPT CLASSI ==============
class Retsept:
    def __init__(self, nomi, taxalluslari, vaqt, qiyinligi, masalliqlar, tayyorlash):
        self.nomi = nomi
        self.taxalluslari = [t.lower() for t in taxalluslari]
        self.vaqt = vaqt
        self.qiyinligi = qiyinligi
        self.masalliqlar = masalliqlar
        self.tayyorlash = tayyorlash

    def mos_keladimi(self, soz):
        soz = soz.lower().strip()
        if soz == self.nomi.lower():
            return True
        for t in self.taxalluslari:
            if t in soz or soz in t:
                return True
        return False

    def matn(self):
        """Telegram uchun HTML formatlangan retsept matni."""
        m = f"🍲 <b>{self.nomi.upper()}</b>\n\n"
        m += f"⏱ <b>Vaqt:</b> {self.vaqt}\n"
        m += f"⚖️ <b>Qiyinligi:</b> {self.qiyinligi}\n\n"
        m += f"📝 <b>Masalliqlar:</b>\n"
        for i in self.masalliqlar:
            m += f"  • {i}\n"
        m += f"\n👨‍🍳 <b>Tayyorlash bosqichlari:</b>\n"
        for n, qadam in enumerate(self.tayyorlash, 1):
            m += f"  <b>{n}.</b> {qadam}\n"
        return m


# ============== RETSEPTLAR BAZASI ==============
RETSEPTLAR = [
    Retsept(
        nomi="Sho'rva",
        taxalluslari=["shorva", "sho'rva", "qaynatma", "soup"],
        vaqt="1 soat 30 daqiqa",
        qiyinligi="Oson",
        masalliqlar=[
            "Mol go'shti — 500 g (suyak bilan)",
            "Kartoshka — 4 dona",
            "Sabzi — 2 dona",
            "Piyoz — 1 dona",
            "Pomidor — 2 dona",
            "Tuz, qora murch, lavr yaprog'i",
            "Yashil ko'kat",
        ],
        tayyorlash=[
            "Go'shtni sovuq suvga soling, qaynating va ko'pikni oling.",
            "Sekin olovda 40 daqiqa pishiring.",
            "Piyoz va sabzini to'g'rab qo'shing.",
            "Kartoshkani yirik bo'laklarga to'g'rab soling.",
            "Pomidor va ziravorlarni qo'shing.",
            "Yana 20 daqiqa qaynating.",
            "Ko'kat sepib torting.",
        ],
    ),
    Retsept(
        nomi="Mastava",
        taxalluslari=["mastava", "guruchli shorva", "mastoba"],
        vaqt="1 soat 15 daqiqa",
        qiyinligi="Oson",
        masalliqlar=[
            "Mol go'shti — 400 g",
            "Guruch — 1 stakan",
            "Kartoshka — 3 dona",
            "Sabzi — 2 dona",
            "Piyoz — 2 dona",
            "Tomat pastasi — 2 osh qoshiq",
            "Tuz, zira, qora murch",
            "Qatiq va ko'kat",
        ],
        tayyorlash=[
            "Go'shtni mayda to'g'rab qozonga soling.",
            "Piyoz qo'shib qovuring.",
            "Sabzini to'g'rab qo'shing va qovuring.",
            "Tomat pastasini qo'shing.",
            "Suv quying va qaynating.",
            "Kartoshka soling, 15 daqiqadan keyin guruch qo'shing.",
            "Guruch pishguncha sekin olovda pishiring.",
            "Qatiq bilan torting.",
        ],
    ),
    Retsept(
        nomi="Norin",
        taxalluslari=["norin", "naryn"],
        vaqt="2 soat",
        qiyinligi="O'rta",
        masalliqlar=[
            "Mol yoki qo'y go'shti — 600 g",
            "Qazi — 200 g (ixtiyoriy)",
            "Un — 500 g",
            "Tuxum — 1 dona",
            "Piyoz — 2 dona",
            "Tuz, qora murch",
        ],
        tayyorlash=[
            "Go'sht va qazini qaynatib pishiring (1-1.5 soat).",
            "Un, tuxum, tuz va suvdan qattiq xamir qoring.",
            "Xamirni yupqa yoyib, sho'rvada pishiring.",
            "Sovugach, ingichka qilib to'g'rang.",
            "Go'shtni ham ingichka to'g'rang.",
            "Piyozni halqalab sho'rvada qaynating.",
            "Hammasini laganda aralashtiring, qora murch seping.",
            "Yoniga issiq sho'rva quying.",
        ],
    ),
    Retsept(
        nomi="Xonim",
        taxalluslari=["xonim", "hanim", "honim"],
        vaqt="1 soat 30 daqiqa",
        qiyinligi="O'rta",
        masalliqlar=[
            "Un — 500 g",
            "Suv — 1 stakan",
            "Tuz — 1 choy qoshiq",
            "Mol qiymasi — 400 g",
            "Piyoz — 3 dona",
            "Sariyog' yoki o'simlik moyi",
            "Tuz, qora murch, zira",
        ],
        tayyorlash=[
            "Un, suv, tuzdan qattiq xamir qoring, 20 daqiqa dam bering.",
            "Qiymaga to'g'ralgan piyoz va ziravor qo'shing.",
            "Xamirni yupqa yoying.",
            "Yuziga moy surting, qiymani teng yoying.",
            "Rulet shaklida o'rang va manti qozonga joylang.",
            "Bug'da 45-50 daqiqa pishiring.",
            "To'g'rab, qatiq yoki pomidor sousi bilan torting.",
        ],
    ),
    Retsept(
        nomi="Osh (Palov)",
        taxalluslari=["osh", "palov", "plov", "qovurma osh"],
        vaqt="2 soat",
        qiyinligi="O'rta",
        masalliqlar=[
            "Guruch (devzira/lazar) — 1 kg",
            "Mol/qo'y go'shti — 700 g",
            "Sabzi — 1 kg",
            "Piyoz — 3 dona",
            "O'simlik moyi — 300 ml",
            "Sarimsoq — 2 boshcha",
            "Zira, tuz, qora murch",
        ],
        tayyorlash=[
            "Guruchni yuving va iliq tuzli suvda 1 soat ivitib qo'ying.",
            "Qozonni qizdirib, moyni quying.",
            "Piyozni halqalab oltin rangga qadar qovuring.",
            "Go'shtni qo'shib qovuring.",
            "Sabzini somonchaga to'g'rab qo'shing.",
            "Issiq suv quying (zirvak), ziravorlar soling.",
            "Sarimsoqni butunligicha qo'shib 30 daqiqa pishiring.",
            "Sarimsoqni oling, guruchni teng yoying.",
            "Suv guruch ustidan 1.5 sm bo'lsin, suv singguncha qaynating.",
            "Guruchni do'mboqlab, sarimsoqni qaytaring, qopqoq yoping.",
            "Sekin olovda 20-25 daqiqa damga qo'ying.",
            "Aralashtirib laganga suzing, ustiga go'sht va sarimsoq qo'ying.",
        ],
    ),
]


def retsept_topish(matn):
    for r in RETSEPTLAR:
        if r.mos_keladimi(matn):
            return r
    return None


# ============== KLAVIATURA (TUGMALAR) ==============
def asosiy_menyu():
    """Inline tugmalar — har bir taom uchun alohida tugma."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for r in RETSEPTLAR:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"🍲 {r.nomi}",
                callback_data=f"retsept:{r.nomi}",
            )
        )
    return keyboard


def orqaga_tugmasi():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="⬅️ Orqaga (ro'yxat)",
            callback_data="orqaga",
        )
    )
    return keyboard


# ============== BOT HANDLERLAR ==============
@bot.message_handler(commands=["start"])
def start_handler(message):
    salom = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 👋\n\n"
        f"Men <b>O'zbek ovqatlari retseptlari</b> botiman 🍽️\n\n"
        f"Quyidan taom tanlang yoki taom nomini yozib yuboring:"
    )
    bot.send_message(message.chat.id, salom, reply_markup=asosiy_menyu())


@bot.message_handler(commands=["help"])
def help_handler(message):
    matn = (
        "<b>Botdan foydalanish:</b>\n\n"
        "/start — boshlash va ro'yxat\n"
        "/menu — taomlar ro'yxati\n"
        "/help — yordam\n\n"
        "Taom nomini yozsangiz ham bo'ladi (masalan: <i>osh</i>, <i>shorva</i>)."
    )
    bot.send_message(message.chat.id, matn)


@bot.message_handler(commands=["menu"])
def menu_handler(message):
    bot.send_message(
        message.chat.id,
        "📋 <b>Taomlar ro'yxati:</b>",
        reply_markup=asosiy_menyu(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("retsept:"))
def retsept_tugma(call):
    nom = call.data.split(":", 1)[1]
    retsept = retsept_topish(nom)
    if retsept:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=retsept.matn(),
            reply_markup=orqaga_tugmasi(),
        )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "orqaga")
def orqaga_tugma(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="📋 <b>Taomlar ro'yxati:</b>",
        reply_markup=asosiy_menyu(),
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: True, content_types=["text"])
def matn_handler(message):
    """Foydalanuvchi oddiy matn yozsa — taom qidiramiz."""
    matn = message.text.strip().lower()

    salomlar = ["salom", "assalom", "hi", "hello"]
    if any(s in matn for s in salomlar):
        bot.send_message(
            message.chat.id,
            "Va alaykum assalom! Qaysi taomni bilmoqchisiz? 🍽️",
            reply_markup=asosiy_menyu(),
        )
        return

    if "rahmat" in matn or "tashakkur" in matn:
        bot.send_message(message.chat.id, "Arzimaydi! 😊")
        return

    retsept = retsept_topish(matn)
    if retsept:
        bot.send_message(
            message.chat.id,
            retsept.matn(),
            reply_markup=orqaga_tugmasi(),
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❓ <i>{message.text}</i> degan taomni topa olmadim.\n"
            f"Quyidagi ro'yxatdan tanlang:",
            reply_markup=asosiy_menyu(),
        )


# ============== ISHGA TUSHIRISH ==============
if __name__ == "__main__":
    print(f"Bot ishga tushdi... ({len(RETSEPTLAR)} ta retsept yuklandi)")
    bot.infinity_polling()
