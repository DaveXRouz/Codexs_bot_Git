from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, List, Optional


class Language(Enum):
    EN = "en"
    FA = "fa"


LANGUAGE_BUTTONS: Dict[Language, str] = {
    Language.EN: "🇬🇧 English",
    Language.FA: "🇮🇷 فارسی",
}

BILINGUAL_WELCOME = (
    "Select your language to continue · زبان خود را برای ادامه انتخاب کنید"
)

LANGUAGE_PROMPT = {
    Language.EN: "Tap a language below to continue.",
    Language.FA: "لطفاً یکی از زبان‌ها را از دکمه‌های زیر انتخاب کنید.",
}

WELCOME_MESSAGE = {
    Language.EN: (
        "Welcome to <b>Codexs</b> — global automation studio.\n"
        "Tell me what you'd like to do and I'll guide you."
    ),
    Language.FA: (
        "به <b>Codexs</b> خوش آمدید — استودیوی جهانی اتوماسیون.\n"
        "بفرمایید به دنبال چه هستید تا راهنمایی‌تان کنم."
    ),
}

RESUME_PROMPT = {
    Language.EN: (
        "📋 <b>Incomplete Application Found</b>\n\n"
        "You have an incomplete application with {progress} questions answered.\n\n"
        "Would you like to resume where you left off?"
    ),
    Language.FA: (
        "📋 <b>درخواست ناتمام یافت شد</b>\n\n"
        "شما یک درخواست ناتمام با {progress} سؤال پاسخ داده شده دارید.\n\n"
        "آیا می‌خواهید از جایی که متوقف شدید ادامه دهید؟"
    ),
}

RESUME_YES = {
    Language.EN: "✅ Yes, resume application",
    Language.FA: "✅ بله، ادامه درخواست",
}

RESUME_NO = {
    Language.EN: "🔄 No, start fresh",
    Language.FA: "🔄 خیر، شروع جدید",
}

APPLICATION_HISTORY_HEADER = {
    Language.EN: "<b>📋 Your Applications</b>",
    Language.FA: "<b>📋 درخواست‌های شما</b>",
}

APPLICATION_HISTORY_EMPTY = {
    Language.EN: "You haven't submitted any applications yet.\n\nUse 💼 Apply for jobs to get started!",
    Language.FA: "شما هنوز درخواستی ارسال نکرده‌اید.\n\nاز 💼 ارسال درخواست همکاری استفاده کنید تا شروع کنید!",
}

APPLICATION_HISTORY_ITEM = {
    Language.EN: (
        "<b>Application {number}</b>\n"
        "🆔 ID: {app_id}\n"
        "📅 Submitted: {date}\n"
        "👤 Name: {name}\n"
        "📧 Email: {email}\n"
        "🎤 Voice: {voice_status}"
    ),
    Language.FA: (
        "<b>درخواست {number}</b>\n"
        "🆔 شناسه: {app_id}\n"
        "📅 ارسال شده: {date}\n"
        "👤 نام: {name}\n"
        "📧 ایمیل: {email}\n"
        "🎤 صدا: {voice_status}"
    ),
}

APPLICATION_HISTORY_VOICE_RECEIVED = {
    Language.EN: "✅ Received",
    Language.FA: "✅ دریافت شد",
}

APPLICATION_HISTORY_VOICE_SKIPPED = {
    Language.EN: "⚠️ Skipped",
    Language.FA: "⚠️ رد شده",
}

LANDING_CARD_CAPTION = (
    "<b>Codexs · Global automation studio</b>\n"
    "Apply for remote roles, explore AI launches, and reach our team across time zones.\n\n"
    "<b>Codexs · استودیوی جهانی اتوماسیون</b>\n"
    "برای موقعیت‌های دورکار اقدام کنید، پروژه‌های هوشمند را ببینید و با تیم در تماس باشید."
)

BACK_TO_MENU = {
    Language.EN: "⬅️ Back to main menu",
    Language.FA: "⬅️ بازگشت به منوی اصلی",
}

YES_LABEL = {
    Language.EN: "✅ Yes",
    Language.FA: "✅ بله",
}
NO_LABEL = {
    Language.EN: "♻️ No, edit",
    Language.FA: "♻️ خیر، ویرایش",
}

SKIP_LABEL = {
    Language.EN: "Skip",
    Language.FA: "رد کردن",
}

SKIPPED_TEXT = {
    Language.EN: "(skipped)",
    Language.FA: "(رد شده)",
}

SHARE_CONTACT_BUTTON = {
    Language.EN: "📱 Share my Telegram contact",
    Language.FA: "📱 اشتراک‌گذاری مخاطب تلگرام",
}

SHARE_LOCATION_BUTTON = {
    Language.EN: "📍 Share my location",
    Language.FA: "📍 اشتراک‌گذاری موقعیت مکانی",
}

CONTACT_SHARED_ACK = {
    Language.EN: "✅ Contact received! Moving to the next question.",
    Language.FA: "✅ مخاطب دریافت شد! به سؤال بعدی می‌رویم.",
}

LOCATION_SHARED_ACK = {
    Language.EN: "✅ Location received! Moving to the next question.",
    Language.FA: "✅ موقعیت دریافت شد! به سؤال بعدی می‌رویم.",
}

CONTACT_SHARED_NOTIFICATION = {
    Language.EN: "📞 New contact message",
    Language.FA: "📞 پیام جدید",
}

MENU_LABELS: Dict[str, Dict[Language, str]] = {
    "apply": {
        Language.EN: "💼 Apply for jobs",
        Language.FA: "💼 ارسال درخواست همکاری",
    },
    "about": {
        Language.EN: "🏢 About Codex",
        Language.FA: "🏢 درباره Codex",
    },
    "updates": {
        Language.EN: "📢 Updates & news",
        Language.FA: "📢 به‌روزرسانی‌ها و خبرها",
    },
    "contact": {
        Language.EN: "📞 Contact & support",
        Language.FA: "📞 تماس و پشتیبانی",
    },
    "history": {
        Language.EN: "📋 My applications",
        Language.FA: "📋 درخواست‌های من",
    },
    "switch": {
        Language.EN: "🔁 Switch to فارسی",
        Language.FA: "🔁 تغییر به English",
    },
}

MENU_TOPIC_TITLES = {
    "apply": {
        Language.EN: "applications and open roles",
        Language.FA: "فرم درخواست و موقعیت‌های شغلی",
    },
    "about": {
        Language.EN: "Codexs profile",
        Language.FA: "معرفی Codexs",
    },
    "updates": {
        Language.EN: "news and launches",
        Language.FA: "خبرها و لانچ‌ها",
    },
    "contact": {
        Language.EN: "contact and support",
        Language.FA: "تماس و پشتیبانی",
    },
    "history": {
        Language.EN: "application history",
        Language.FA: "تاریخچه درخواست‌ها",
    },
}

ROLE_CHOICES = {
    Language.EN: [
        ["Engineering", "Design"],
        ["Product", "Support"],
        ["Marketing", "Other"],
    ],
    Language.FA: [
        ["مهندسی", "طراحی"],
        ["محصول", "پشتیبانی"],
        ["مارکتینگ", "سایر"],
    ],
}

EXPERIENCE_CHOICES = {
    Language.EN: [["0-1 yrs", "2-4 yrs"], ["5-7 yrs", "8+ yrs"]],
    Language.FA: [["۰-۱ سال", "۲-۴ سال"], ["۵-۷ سال", "۸+ سال"]],
}

SHIFT_CHOICES = {
    Language.EN: [["🌅 Morning shift", "🌙 Night shift"], ["🔄 Flexible / Both"]],
    Language.FA: [["🌅 شیفت صبح", "🌙 شیفت شب"], ["🔄 انعطاف‌پذیر / هر دو"]],
}

START_DATE_CHOICES = {
    Language.EN: [
        ["Immediately", "Within 2 weeks"],
        ["Within 1 month", "Within 2-3 months"],
        ["Custom date (type below)"]
    ],
    Language.FA: [
        ["فوری", "ظرف ۲ هفته"],
        ["ظرف ۱ ماه", "ظرف ۲-۳ ماه"],
        ["تاریخ دلخواه (پایین بنویسید)"]
    ],
}


@dataclass(frozen=True)
class Question:
    key: str
    prompts: Dict[Language, str]
    summary_labels: Dict[Language, str]
    keyboard: Optional[Dict[Language, List[List[str]]]] = None
    optional: bool = False
    input_type: str = "text"  # "text", "contact", "location"


HIRING_QUESTIONS: List[Question] = [
    Question(
        key="full_name",
        prompts={
            Language.EN: "<b>What's your full legal name?</b>\n<i>First and last name as it appears on official documents</i>",
            Language.FA: "<b>نام و نام خانوادگی کامل شما چیست؟</b>\n<i>نام و نام خانوادگی طبق مدارک رسمی</i>",
        },
        summary_labels={
            Language.EN: "Full name",
            Language.FA: "نام و نام خانوادگی",
        },
    ),
    Question(
        key="email",
        prompts={
            Language.EN: "<b>What's your primary email address?</b>\n<i>We'll use this for all official Codexs communication</i>",
            Language.FA: "<b>آدرس ایمیل اصلی شما چیست؟</b>\n<i>برای تمام ارتباطات رسمی Codexs استفاده می‌شود</i>",
        },
        summary_labels={
            Language.EN: "Email",
            Language.FA: "ایمیل",
        },
    ),
    Question(
        key="contact",
        prompts={
            Language.EN: "<b>How can we reach you?</b>\n<i>Tap 📱 Share Contact or type your phone number with country code</i>",
            Language.FA: "<b>چگونه می‌توانیم با شما تماس بگیریم؟</b>\n<i>روی دکمه 📱 اشتراک مخاطب بزنید یا شماره تلفن همراه با کد کشور را بنویسید</i>",
        },
        summary_labels={
            Language.EN: "Contact method",
            Language.FA: "راه ارتباطی",
        },
        input_type="contact",
    ),
    Question(
        key="location",
        prompts={
            Language.EN: "<b>Where are you based?</b>\n<i>Tap 📍 Share Location or type: City, Country (Timezone)</i>",
            Language.FA: "<b>کجا زندگی می‌کنید؟</b>\n<i>روی دکمه 📍 اشتراک موقعیت بزنید یا بنویسید: شهر، کشور (منطقه زمانی)</i>",
        },
        summary_labels={
            Language.EN: "Location & time zone",
            Language.FA: "مکان و منطقه زمانی",
        },
        input_type="location",
    ),
    Question(
        key="role_category",
        prompts={
            Language.EN: "<b>What's your primary role?</b>\n<i>Select the category that best matches your expertise</i>",
            Language.FA: "<b>نقش اصلی شما چیست؟</b>\n<i>دسته‌ای را انتخاب کنید که بیشتر با تخصص شما مطابقت دارد</i>",
        },
        summary_labels={
            Language.EN: "Role category",
            Language.FA: "دسته‌بندی نقش",
        },
        keyboard=ROLE_CHOICES,
    ),
    Question(
        key="skills",
        prompts={
            Language.EN: "<b>What are your core skills?</b>\n<i>List technologies, frameworks, or methodologies (comma-separated)</i>\n\nExample: Python, React, AWS, Figma",
            Language.FA: "<b>مهارت‌های اصلی شما کدام‌اند؟</b>\n<i>تکنولوژی‌ها، فریم‌ورک‌ها یا متدولوژی‌ها را لیست کنید (با ویرگول جدا شوند)</i>\n\nمثال: Python, React, AWS, Figma",
        },
        summary_labels={
            Language.EN: "Skills / tech stack",
            Language.FA: "مهارت‌ها / تکنولوژی‌ها",
        },
    ),
    Question(
        key="experience",
        prompts={
            Language.EN: "<b>How many years of relevant experience do you have?</b>\n<i>Select the range that matches your professional background</i>",
            Language.FA: "<b>چند سال سابقه کاری مرتبط دارید؟</b>\n<i>بازه‌ای را انتخاب کنید که با پیشینه حرفه‌ای شما مطابقت دارد</i>",
        },
        summary_labels={
            Language.EN: "Experience",
            Language.FA: "سابقه",
        },
        keyboard=EXPERIENCE_CHOICES,
    ),
    Question(
        key="portfolio",
        prompts={
            Language.EN: "<b>Show us your work</b>\n<i>Share a portfolio link, GitHub, Behance, or brief description of past projects</i>",
            Language.FA: "<b>کارهای خود را به ما نشان دهید</b>\n<i>لینک پورتفولیو، GitHub، Behance یا توضیح مختصری از پروژه‌های گذشته بدهید</i>",
        },
        summary_labels={
            Language.EN: "Portfolio / work samples",
            Language.FA: "نمونه‌کارها",
        },
    ),
    Question(
        key="start_date",
        prompts={
            Language.EN: "<b>When can you start?</b>\n<i>Choose your earliest availability or specify a custom date</i>",
            Language.FA: "<b>چه زمانی می‌توانید شروع کنید؟</b>\n<i>زودترین زمان آمادگی خود را انتخاب کنید یا تاریخ دلخواه را مشخص کنید</i>",
        },
        summary_labels={
            Language.EN: "Earliest start date",
            Language.FA: "زودترین زمان شروع",
        },
        keyboard=START_DATE_CHOICES,
    ),
    Question(
        key="working_hours",
        prompts={
            Language.EN: "<b>What's your preferred work shift?</b>\n<i>Choose the schedule that matches your productivity rhythm</i>",
            Language.FA: "<b>شیفت کاری ترجیحی شما چیست؟</b>\n<i>برنامه‌ای را انتخاب کنید که با ریتم بهره‌وری شما هماهنگ است</i>",
        },
        summary_labels={
            Language.EN: "Preferred shift",
            Language.FA: "شیفت ترجیحی",
        },
        keyboard=SHIFT_CHOICES,
    ),
    Question(
        key="motivation",
        prompts={
            Language.EN: "<b>Why Codexs?</b>\n<i>What excites you about joining our team? What makes this a strong fit?</i>",
            Language.FA: "<b>چرا Codexs؟</b>\n<i>چه چیزی در مورد پیوستن به تیم ما شما را هیجان‌زده می‌کند؟ چرا این همکاری مناسب است؟</i>",
        },
        summary_labels={
            Language.EN: "Motivation",
            Language.FA: "انگیزه",
        },
    ),
    Question(
        key="salary",
        prompts={
            Language.EN: "<b>Salary expectations (Optional)</b>\n<i>Share your expected range in USD/month, or type 'Skip' if you prefer to discuss later</i>",
            Language.FA: "<b>انتظار حقوق (اختیاری)</b>\n<i>بازه مورد انتظار خود را به دلار در ماه بنویسید، یا «رد کردن» بنویسید اگر ترجیح می‌دهید بعداً صحبت کنیم</i>",
        },
        summary_labels={
            Language.EN: "Salary expectations",
            Language.FA: "انتظار حقوق",
        },
        optional=True,
    ),
]

HIRING_INTRO = {
    Language.EN: (
        "<b>💼 Codexs</b>\n\n"
        "This form has <b>12 short questions</b> (~3 minutes)\n"
        "Plus a mandatory <b>English voice test</b>\n\n"
        "🔒 Your answers stay confidential with the Codexs hiring team\n"
        "✅ You can edit before final submission"
    ),
    Language.FA: (
        "<b>💼 Codexs</b>\n\n"
        "این فرم <b>۱۲ سؤال کوتاه</b> دارد (حدود ۳ دقیقه)\n"
        "به اضافه <b>تست صوتی انگلیسی اجباری</b>\n\n"
        "🔒 پاسخ‌ها نزد تیم استخدام Codexs محرمانه می‌ماند\n"
        "✅ قبل از ارسال نهایی می‌توانید ویرایش کنید"
    ),
}

QUESTION_PROGRESS = {
    Language.EN: "Question {current}/{total}",
    Language.FA: "سؤال {current}/{total}",
}

VOICE_SAMPLE_TEXT = (
    "At Codexs, we build intelligent automation systems for global teams. "
    "Every project requires clear communication, async collaboration, and proactive problem-solving. "
    "Remote work demands precision in written updates and spoken English. "
    "Our engineers, designers, and operators coordinate across multiple time zones daily."
)

VOICE_PROMPT = {
    Language.EN: (
        "<b>📣 English Voice Test (Required)</b>\n\n"
        "Why this matters: Codexs works with global teams. Clear English communication is essential for remote collaboration, daily standups, and client interactions.\n\n"
        "What to do: Read the text below out loud and send a voice message.\n\n"
        f"<i>\"{VOICE_SAMPLE_TEXT}\"</i>\n\n"
        "⏱ Duration: 30-45 seconds\n"
        "🎯 We evaluate: clarity, fluency, pronunciation\n\n"
        "💡 Tip: Speak naturally and at a comfortable pace."
    ),
    Language.FA: (
        "<b>📣 تست صوتی انگلیسی (اجباری)</b>\n\n"
        "چرا مهم است: Codexs با تیم‌های جهانی کار می‌کند. ارتباط واضح به انگلیسی برای همکاری از راه دور، جلسات روزانه و تعامل با مشتری ضروری است.\n\n"
        "چه کاری انجام دهید: متن زیر را با صدای بلند بخوانید و یک پیام صوتی ارسال کنید.\n\n"
        f"<i>\"{VOICE_SAMPLE_TEXT}\"</i>\n\n"
        "⏱ مدت زمان: ۳۰-۴۵ ثانیه\n"
        "🎯 ما ارزیابی می‌کنیم: وضوح، روانی، تلفظ\n\n"
        "💡 نکته: به صورت طبیعی و با سرعت راحت صحبت کنید."
    ),
}

VOICE_ACK = {
    Language.EN: "Voice sample received and stored for the hiring team. ✅",
    Language.FA: "نمونه صدای شما دریافت و برای تیم استخدام ذخیره شد. ✅",
}

THANK_YOU = {
    Language.EN: (
        "All set! Your application has been submitted.\n\n"
        "📋 <b>Application ID:</b> {app_id}\n\n"
        "The Codexs hiring team will review your profile and reach out via email or Telegram within <b>1-2 business days</b>.\n\n"
        "You can now return to the main menu to explore other sections."
    ),
    Language.FA: (
        "همه چیز ثبت شد! درخواست شما ارسال شد.\n\n"
        "📋 <b>شناسه درخواست:</b> {app_id}\n\n"
        "تیم استخدام Codexs پروفایل شما را بررسی می‌کند و ظرف <b>۱ تا ۲ روز کاری</b> از طریق ایمیل یا تلگرام تماس می‌گیرد.\n\n"
        "اکنون می‌توانید به منوی اصلی برگردید و سایر بخش‌ها را بررسی کنید."
    ),
}

CONFIRMATION_IMAGE_CAPTION = {
    Language.EN: "Thank you for applying to Codexs. We'll be in touch soon.",
    Language.FA: "از درخواست شما متشکریم. به زودی با شما تماس خواهیم گرفت.",
}

SUMMARY_HEADER = {
    Language.EN: "Here is the summary of the data we captured:",
    Language.FA: "خلاصه اطلاعات ثبت‌شده:",
}

CONFIRM_PROMPT = {
    Language.EN: "Is everything correct?",
    Language.FA: "آیا همه موارد درست است؟",
}

EDIT_PROMPT = {
    Language.EN: (
        "Please share the question number (1-12) you would like to edit.\n\n"
        "💡 <b>Tip:</b> You can also re-record your voice sample by selecting 13.\n\n"
        "💬 <b>Cancel:</b> Use 'Back to main menu' to cancel editing and return to confirmation."
    ),
    Language.FA: (
        "لطفاً شماره سوال موردنظر برای ویرایش (۱ تا ۱۲) را بفرستید.\n\n"
        "💡 <b>نکته:</b> می‌توانید نمونه صوتی خود را دوباره ضبط کنید با انتخاب ۱۳.\n\n"
        "💬 <b>لغو:</b> از 'بازگشت به منوی اصلی' برای لغو ویرایش و بازگشت به تأیید استفاده کنید."
    ),
}

INVALID_EDIT = {
    Language.EN: "I couldn't match that number. Please send a value between 1 and 13 (13 = re-record voice).",
    Language.FA: "شماره معتبر نیست. لطفاً عددی بین ۱ تا ۱۳ بفرستید (۱۳ = ضبط مجدد صدا).",
}

RERECORD_VOICE_PROMPT = {
    Language.EN: (
        "You've chosen to re-record your voice sample.\n\n"
        "Please record and send a new English voice message."
    ),
    Language.FA: (
        "شما انتخاب کرده‌اید که نمونه صوتی خود را دوباره ضبط کنید.\n\n"
        "لطفاً یک پیام صوتی انگلیسی جدید ضبط و ارسال کنید."
    ),
}

ABOUT_TEXT = {
    Language.EN: (
        "**Codexs — Global Automation Studio**\n"
        "We build precision systems at the intersection of AI, software, data, and operations. "
        "Remote-first. Tesla-level craft. Always bilingual."
    ),
    Language.FA: (
        "**Codexs — استودیوی جهانی اتوماسیون**\n"
        "در تقاطع هوش مصنوعی، نرم‌افزار، داده و عملیات تجربه‌های دقیق می‌سازیم. "
        "کاملاً ریموت، با کیفیت سطح تسلا و همیشه دو‌زبانه."
    ),
}

ABOUT_SECTIONS = {
    Language.EN: [
        {
            "title": "Mission Control",
            "body": (
                "Codexs builds distributed automation layers for ambitious product, data, and ops teams.\n"
                "• Hybrid squads of AI engineers, product thinkers, and operators\n"
                "• 4–6 week launch windows with live telemetry dashboards\n"
                "• Preferred stack: PyTorch, LangChain, Temporal, Supabase, Svelte"
            ),
        },
        {
            "title": "Operating Principles",
            "body": (
                "• Tesla / SpaceX-level quality bar, minimalist comms\n"
                "• Bilingual workflows (English / Farsi) baked into every artifact\n"
                "• Humans + agents paired for reliability, traceability, and speed"
            ),
        },
        {
            "title": "Proof of Work",
            "body": (
                "• Designed a self-healing data ops mesh for a Middle East fintech\n"
                "• Launched a multi-agent CX cockpit that triages 1M+ yearly tickets\n"
                "• Embedded with deep-tech funds to validate AI-native venture bets"
            ),
        },
    ],
    Language.FA: [
        {
            "title": "اتاق فرمان",
            "body": (
                "Codexs لایه‌های اتوماسیون توزیع‌شده برای تیم‌های محصول، داده و عملیات می‌سازد.\n"
                "• اسکادران‌های ترکیبی شامل مهندسان هوش مصنوعی، طراحان محصول و اپراتورها\n"
                "• پنجره‌های راه‌اندازی ۴ تا ۶ هفته‌ای همراه با داشبورد تله‌متری\n"
                "• استک محبوب: PyTorch، LangChain، Temporal، Supabase، Svelte"
            ),
        },
        {
            "title": "اصول عملکردی",
            "body": (
                "• استاندارد کیفیت در سطح Tesla / SpaceX با ارتباطات مینیمال\n"
                "• کار دو‌زبانه (انگلیسی / فارسی) در همه مستندات و تحویل‌ها\n"
                "• همکاری انسان + ایجنت برای پایداری، ردیابی و سرعت"
            ),
        },
        {
            "title": "اثبات کار",
            "body": (
                "• ساخت مش داده‌ی خودترمیم برای یک فین‌تک خاورمیانه‌ای\n"
                "• لانچ کوپیت چندایجنتی پشتیبانی که سالانه بالای ۱ میلیون تیکت را مدیریت می‌کند\n"
                "• همکاری با صندوق‌های دیپ‌تک برای اعتبارسنجی سرمایه‌گذاری‌های AI-native"
            ),
        },
    ],
}

ABOUT_MEDIA = {
    Language.EN: {
        "photo": None,  # No photo for About section
        "caption": "",
    },
    Language.FA: {
        "photo": None,  # No photo for About section
        "caption": "",
    },
}

ABOUT_CTA = {
    Language.EN: "Would you like to view open roles?",
    Language.FA: "مایلید فرصت‌های شغلی باز را ببینید؟",
}

VIEW_ROLES_YES = {
    Language.EN: "✅ Yes, show me open roles",
    Language.FA: "✅ بله، فرصت‌های شغلی را نشان بده",
}

VIEW_ROLES_NO = {
    Language.EN: "⬅️ Back to main menu",
    Language.FA: "⬅️ بازگشت به منوی اصلی",
}

UPDATES = {
    Language.EN: [
        "⚡ Released a new AI automation layer for a fintech scale-up.",
        "🌍 Expanded remote squads across EMEA & APAC time zones.",
        "🧠 Hiring senior engineers, designers, and product operators for 2025.",
    ],
    Language.FA: [
        "⚡ لایه جدید اتوماسیون هوش مصنوعی برای یک فین‌تک توسعه یافت.",
        "🌍 تیم‌های ریموت در مناطق زمانی EMEA و APAC گسترش یافتند.",
        "🧠 جذب مهندسان، طراحان و مدیران محصول ارشد برای سال ۲۰۲۵ ادامه دارد.",
    ],
}

UPDATES_LINK = "https://codexs.ai"

UPDATES_CTA = {
    Language.EN: "More launches:",
    Language.FA: "اطلاعات بیشتر:",
}

UPDATE_CARDS = {
    Language.EN: [
        {
            "title": "System X Automation Layer",
            "body": (
                "We shipped a Temporal + LLM mesh that closes the loop on KYC reviews in <4 minutes "
                "for a regulated fintech. Human supervisors now audit via a single Codexs cockpit."
            ),
            "cta_label": "Read build notes",
            "cta_url": "https://codexs.ai/case/system-x",
            "photo": None,  # No photo for this card
        },
        {
            "title": "Global Ops Pods",
            "body": (
                "New pods spun up in Dubai, Warsaw, and Kuala Lumpur give 24/6 coverage without "
                "compromising Codexs craft. Every pod pairs PM, AI lead, designer, and automation ops."
            ),
            "cta_label": "Meet the pods",
            "cta_url": "https://codexs.ai/ops",
            "photo": "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?auto=format&fit=crop&w=1600&q=80",
        },
        {
            "title": "Culture Reel 2025",
            "body": (
                "A two-minute reel that shows how we run bilingual standups, async critiques, "
                "and Tesla-level QA rituals from anywhere on the planet."
            ),
            "cta_label": "Watch the reel",
            "cta_url": "https://codexs.ai/culture",
            "photo": None,  # No photo for this card
        },
    ],
    Language.FA: [
        {
            "title": "لایه اتوماسیون System X",
            "body": (
                "یک مش Temporal + LLM پیاده‌سازی کردیم که بررسی KYC را برای فین‌تکی تحت نظارت "
                "در کمتر از ۴ دقیقه می‌بندد. ناظران انسانی همه چیز را در یک کوپیت Codexs مشاهده می‌کنند."
            ),
            "cta_label": "یادداشت‌های ساخت",
            "cta_url": "https://codexs.ai/case/system-x",
            "photo": None,  # No photo for this card
        },
        {
            "title": "پادهای عملیات جهانی",
            "body": (
                "پادهای تازه در دبی، ورشو و کوالالامپور راه‌اندازی شد تا پوشش ۶ روزه ۲۴ ساعته "
                "با همان کیفیت Codexs فراهم شود. هر پاد شامل PM، رهبر AI، طراح و اپراتور اتوماسیون است."
            ),
            "cta_label": "آشنایی با پادها",
            "cta_url": "https://codexs.ai/ops",
            "photo": "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?auto=format&fit=crop&w=1600&q=80",
        },
        {
            "title": "ریل فرهنگ ۲۰۲۵",
            "body": (
                "فیلم دو دقیقه‌ای که نشان می‌دهد استنداپ‌های دو‌زبانه، کریتیک‌های غیرهمزمان "
                "و روتین‌های QA در سطح تسلا را از هرجای دنیا چگونه اجرا می‌کنیم."
            ),
            "cta_label": "مشاهده ویدیو",
            "cta_url": "https://codexs.ai/culture",
            "photo": None,  # No photo for this card
        },
    ],
}

CONTACT_INFO = {
    Language.EN: (
        "You can email contact@codexs.ai or visit https://codexs.ai.\n"
        "Would you like to send a short message here?"
    ),
    Language.FA: (
        "می‌توانید به contact@codexs.ai ایمیل بزنید یا به https://codexs.ai سر بزنید.\n"
        "مایلید همین‌جا پیام کوتاهی بگذارید؟"
    ),
}

CONTACT_THANKS = {
    Language.EN: (
        "✅ Message saved for the Codexs ops team.\n\n"
        "We'll review your message and respond within <b>1-2 business days</b> via email or Telegram."
    ),
    Language.FA: (
        "✅ پیام شما برای تیم عملیات Codexs ثبت شد.\n\n"
        "پیام شما را بررسی می‌کنیم و ظرف <b>۱ تا ۲ روز کاری</b> از طریق ایمیل یا تلگرام پاسخ می‌دهیم."
    ),
}

CONTACT_SKIP = {
    Language.EN: "No worries. Let me know if you need anything else.",
    Language.FA: "اشکالی ندارد. اگر مورد دیگری بود حتماً بگویید.",
}

CONTACT_DECISION_REMINDER = {
    Language.EN: "Please tap Yes or No so I know whether to collect a message.",
    Language.FA: "لطفاً دکمه بله یا خیر را بزنید تا بدانم باید پیام بگیرم یا خیر.",
}

FALLBACK_MESSAGE = {
    Language.EN: (
        "I couldn't understand that. Here are your options:\n\n"
        "• Use the buttons below to navigate\n"
        "• Type /menu to return to main menu\n"
        "• Type /help for context-aware assistance\n"
        "• Type /commands to see all available commands"
    ),
    Language.FA: (
        "نتوانستم درخواست شما را درک کنم. گزینه‌های شما:\n\n"
        "• از دکمه‌های زیر برای ناوبری استفاده کنید\n"
        "• /menu را بزنید تا به منوی اصلی برگردید\n"
        "• /help را بزنید برای راهنمایی\n"
        "• /commands را بزنید تا همه دستورات را ببینید"
    ),
}

SMART_FALLBACK_HINT = {
    Language.EN: "It sounds like you need <b>{topic}</b>. I’ll open that section for you.",
    Language.FA: "به نظر می‌رسد دنبال <b>{topic}</b> هستید. همان بخش را برایتان باز می‌کنم.",
}

AI_RATE_LIMIT_MESSAGE = {
    Language.EN: "⚠️ I’m handling a lot right now. Please use the menu or try again shortly.",
    Language.FA: "⚠️ در حال پاسخ‌گویی زیاد هستم. لطفاً از منو استفاده کنید یا چند لحظه بعد دوباره تلاش کنید.",
}

HELP_TEXT_APPLY = {
    Language.EN: (
        "You're in the <b>application flow</b>.\n\n"
        "• Answer each question one by one\n"
        "• Use buttons when available\n"
        "• Voice recording is mandatory\n"
        "• You can edit answers before submitting\n\n"
        "Type /menu to cancel and return to main menu."
    ),
    Language.FA: (
        "شما در <b>فرم درخواست</b> هستید.\n\n"
        "• به هر سؤال یکی یکی پاسخ دهید\n"
        "• از دکمه‌ها استفاده کنید\n"
        "• ضبط صدا اجباری است\n"
        "• می‌توانید قبل از ارسال ویرایش کنید\n\n"
        "دستور /menu را برای لغو و بازگشت به منوی اصلی بفرستید."
    ),
}

HELP_TEXT_VOICE = {
    Language.EN: (
        "You need to <b>record a voice message</b>.\n\n"
        "• Read the English text provided\n"
        "• Record 30-45 seconds\n"
        "• Send as a voice message (not audio file)\n\n"
        "This is mandatory to complete your application."
    ),
    Language.FA: (
        "شما باید <b>یک پیام صوتی ضبط کنید</b>.\n\n"
        "• متن انگلیسی ارائه شده را بخوانید\n"
        "• ۳۰-۴۵ ثانیه ضبط کنید\n"
        "• به عنوان پیام صوتی ارسال کنید (نه فایل صوتی)\n\n"
        "این بخش برای تکمیل درخواست شما اجباری است."
    ),
}

ERROR_EMAIL_INVALID = {
    Language.EN: (
        "⚠️ Please enter a valid email address (e.g., name@example.com).\n"
        "Use the standard format or tap ⬅️ Back / type /menu to exit this form."
    ),
    Language.FA: (
        "⚠️ لطفاً یک آدرس ایمیل معتبر وارد کنید (مثال: name@example.com).\n"
        "آدرس را با فرمت استاندارد بنویسید یا با ⬅️ بازگشت / دستور ‎/menu‎ فرم را ترک کنید."
    ),
}

RATE_LIMIT_MESSAGE = {
    Language.EN: "⚠️ Too many requests. Please wait a moment and try again.",
    Language.FA: "⚠️ درخواست‌های زیادی ارسال شده. لطفاً کمی صبر کنید و دوباره تلاش کنید.",
}

LANGUAGE_REMINDER = {
    Language.EN: "Please select a language with the buttons below.",
    Language.FA: "لطفاً با دکمه‌های زیر زبان را انتخاب کنید.",
}

MAIN_MENU_PROMPT = {
    Language.EN: "Main menu · Pick a focus area.",
    Language.FA: "منوی اصلی · یکی از بخش‌ها را انتخاب کنید.",
}

MENU_HELPER = {
    Language.EN: "Use the blue buttons below. Tap ⬅️ Back to main menu anytime.",
    Language.FA: "از دکمه‌های آبی زیر استفاده کنید و هر لحظه می‌توانید ⬅️ بازگشت به منوی اصلی را بزنید.",
}

MISSING_ANSWER = {
    Language.EN: (
        "Please share a short answer so we can continue.\n"
        "Need to stop? Tap ⬅️ Back or type /menu."
    ),
    Language.FA: (
        "لطفاً یک پاسخ کوتاه بدهید تا ادامه دهیم.\n"
        "اگر می‌خواهید خارج شوید، ⬅️ بازگشت یا ‎/menu‎ را بزنید."
    ),
}

VOICE_WAITING_REMINDER = {
    Language.EN: (
        "<b>⏳ Voice recording required</b>\n\n"
        "Please record and send your English voice sample.\n"
        "This is <b>mandatory</b> to complete your application.\n\n"
        "Or tap ⬅️ Back to cancel and return to main menu."
    ),
    Language.FA: (
        "<b>⏳ ضبط صدا الزامی است</b>\n\n"
        "لطفاً نمونه صوتی انگلیسی خود را ضبط و ارسال کنید.\n"
        "این بخش برای تکمیل درخواست شما <b>اجباری</b> است.\n\n"
        "یا روی ⬅️ بازگشت بزنید تا لغو کنید و به منوی اصلی برگردید."
    ),
}

CONTACT_MESSAGE_PROMPT = {
    Language.EN: "Great — type your message. A human teammate will read it shortly.",
    Language.FA: "عالی، لطفاً پیام خود را بنویسید. یکی از اعضای تیم به‌زودی آن را می‌خواند.",
}

VOICE_STATUS_LINE = {
    Language.EN: "- Voice sample: {status}",
    Language.FA: "- نمونه صدا: {status}",
}

VOICE_STATUS_RECEIVED = {
    Language.EN: "✅ received",
    Language.FA: "✅ دریافت شد",
}

VOICE_STATUS_PENDING = {
    Language.EN: "Pending",
    Language.FA: "در انتظار",
}
VOICE_STATUS_SKIPPED = {
    Language.EN: "Skipped (team may request later)",
    Language.FA: "رد شده (ممکن است بعداً درخواست شود)",
}

HELP_TEXT = {
    Language.EN: (
        "I can help you:\n"
        "• Apply for Codexs roles\n"
        "• Learn about the studio\n"
        "• Read updates & news\n"
        "• Send a contact message\n\n"
        "Commands: /start · /menu · /help · /commands"
    ),
    Language.FA: (
        "می‌توانم کمک کنم:\n"
        "• ارسال درخواست همکاری Codexs\n"
        "• آشنایی با استودیو\n"
        "• دیدن خبرها و به‌روزرسانی‌ها\n"
        "• ارسال پیام برای تیم\n\n"
        "دستورات: ‎/start · ‎/menu · ‎/help · ‎/commands"
    ),
}

COMMANDS_TEXT = {
    Language.EN: (
        "<b>Command palette</b>\n"
        "/start – Restart and choose a language\n"
        "/menu – Jump back to the main menu\n"
        "/help – Context-aware tips\n"
        "/commands – Show this list"
    ),
    Language.FA: (
        "<b>فهرست دستورات</b>\n"
        "/start – شروع دوباره و انتخاب زبان\n"
        "/menu – بازگشت به منوی اصلی\n"
        "/help – راهنمای متناسب با وضعیت شما\n"
        "/commands – نمایش همین فهرست"
    ),
}

ADMIN_ACCESS_DENIED = {
    Language.EN: "⚠️ Admin access denied. This command is only available to administrators.",
    Language.FA: "⚠️ دسترسی ادمین رد شد. این دستور فقط برای مدیران در دسترس است.",
}

ADMIN_MENU = {
    Language.EN: (
        "<b>🔧 Admin Panel</b>\n\n"
        "Available commands:\n"
        "/admin – Show this menu\n"
        "/status – Bot status and health\n"
        "/stats – Application and user statistics\n"
        "/debug &lt;user_id&gt; – Debug user session\n"
        "/sessions – List active sessions\n"
        "/cleanup – Clean up old session files\n"
        "/testgroup – Test group notification\n\n"
        "All commands require admin privileges."
    ),
    Language.FA: (
        "<b>🔧 پنل مدیریت</b>\n\n"
        "دستورات موجود:\n"
        "/admin – نمایش این منو\n"
        "/status – وضعیت و سلامت ربات\n"
        "/stats – آمار درخواست‌ها و کاربران\n"
        "/debug &lt;user_id&gt; – اشکال‌زدایی جلسه کاربر\n"
        "/sessions – لیست جلسات فعال\n"
        "/cleanup – پاکسازی فایل‌های جلسه قدیمی\n"
        "/testgroup – تست اعلان گروه\n\n"
        "همه دستورات نیاز به دسترسی ادمین دارند."
    ),
}

ADMIN_STATUS = {
    Language.EN: (
        "<b>🤖 Bot Status</b>\n\n"
        "✅ Bot is running\n"
        "📊 Applications: {app_count}\n"
        "💬 Contact messages: {contact_count}\n"
        "💾 Active sessions: {session_count}\n"
        "🎤 Voice samples: {voice_count}\n\n"
        "Last updated: {timestamp}"
    ),
    Language.FA: (
        "<b>🤖 وضعیت ربات</b>\n\n"
        "✅ ربات در حال اجرا است\n"
        "📊 درخواست‌ها: {app_count}\n"
        "💬 پیام‌های تماس: {contact_count}\n"
        "💾 جلسات فعال: {session_count}\n"
        "🎤 نمونه‌های صوتی: {voice_count}\n\n"
        "آخرین به‌روزرسانی: {timestamp}"
    ),
}

ADMIN_STATS = {
    Language.EN: (
        "<b>📊 Statistics</b>\n\n"
        "📝 Total applications: {total_apps}\n"
        "✅ Completed: {completed_apps}\n"
        "⏳ Incomplete: {incomplete_apps}\n"
        "💬 Contact messages: {contact_count}\n"
        "👥 Unique users: {unique_users}\n"
        "🌍 Languages:\n"
        "  • English: {en_count}\n"
        "  • Farsi: {fa_count}"
    ),
    Language.FA: (
        "<b>📊 آمار</b>\n\n"
        "📝 کل درخواست‌ها: {total_apps}\n"
        "✅ تکمیل شده: {completed_apps}\n"
        "⏳ ناتمام: {incomplete_apps}\n"
        "💬 پیام‌های تماس: {contact_count}\n"
        "👥 کاربران منحصر به فرد: {unique_users}\n"
        "🌍 زبان‌ها:\n"
        "  • انگلیسی: {en_count}\n"
        "  • فارسی: {fa_count}"
    ),
}

ADMIN_DEBUG_USER = {
    Language.EN: (
        "<b>🐛 User Debug Info</b>\n\n"
        "User ID: {user_id}\n"
        "Username: @{username}\n"
        "Name: {name}\n\n"
        "<b>Session:</b>\n"
        "Language: {language}\n"
        "Flow: {flow}\n"
        "Question: {question_index}/12\n"
        "Answers: {answer_count}\n"
        "Waiting voice: {waiting_voice}\n"
        "Voice skipped: {voice_skipped}\n"
        "Edit mode: {edit_mode}\n\n"
        "<b>Applications:</b>\n"
        "Total: {app_count}"
    ),
    Language.FA: (
        "<b>🐛 اطلاعات اشکال‌زدایی کاربر</b>\n\n"
        "شناسه کاربر: {user_id}\n"
        "نام کاربری: @{username}\n"
        "نام: {name}\n\n"
        "<b>جلسه:</b>\n"
        "زبان: {language}\n"
        "جریان: {flow}\n"
        "سؤال: {question_index}/12\n"
        "پاسخ‌ها: {answer_count}\n"
        "در انتظار صدا: {waiting_voice}\n"
        "صدا رد شده: {voice_skipped}\n"
        "حالت ویرایش: {edit_mode}\n\n"
        "<b>درخواست‌ها:</b>\n"
        "کل: {app_count}"
    ),
}

ADMIN_SESSIONS_LIST = {
    Language.EN: (
        "<b>💾 Active Sessions</b>\n\n"
        "Total: {count}\n\n"
        "{sessions_list}"
    ),
    Language.FA: (
        "<b>💾 جلسات فعال</b>\n\n"
        "کل: {count}\n\n"
        "{sessions_list}"
    ),
}

ADMIN_NO_SESSIONS = {
    Language.EN: "No active sessions found.",
    Language.FA: "هیچ جلسه فعالی یافت نشد.",
}

EXIT_CONFIRM_PROMPT = {
    Language.EN: "You have an in-progress flow. Exit and discard it?",
    Language.FA: "یک فرم در حال تکمیل دارید. می‌خواهید خارج شوید و آن را حذف کنید؟",
}

EXIT_CONFIRM_CANCEL = {
    Language.EN: "No problem. Let’s continue where we left off.",
    Language.FA: "اشکالی ندارد. ادامه می‌دهیم.",
}

EXIT_CONFIRM_DONE = {
    Language.EN: "Draft cleared. Returning to main menu.",
    Language.FA: "پیش‌نویس پاک شد. به منوی اصلی برمی‌گردیم.",
}

# Error messages
ERROR_VOICE_TOO_LARGE = {
    Language.EN: (
        "⚠️ Voice file is too large (max 20MB).\n"
        "Please record a shorter message (30-45 seconds) and try again."
    ),
    Language.FA: (
        "⚠️ فایل صوتی خیلی بزرگ است (حداکثر ۲۰ مگابایت).\n"
        "لطفاً پیام کوتاه‌تری ضبط کنید (۳۰-۴۵ ثانیه) و دوباره تلاش کنید."
    ),
}

ERROR_TEXT_TOO_LONG = {
    Language.EN: "⚠️ Your message is too long. Maximum length is 1000 characters. Please shorten your response.",
    Language.FA: "⚠️ پیام شما خیلی طولانی است. حداکثر طول ۱۰۰۰ کاراکتر است. لطفاً پاسخ خود را کوتاه کنید.",
}

ERROR_VOICE_INVALID = {
    Language.EN: "⚠️ Unable to process this audio file. Please send a voice message (not a file) and try again.",
    Language.FA: "⚠️ نمی‌توانم این فایل صوتی را پردازش کنم. لطفاً یک پیام صوتی (نه فایل) ارسال کنید و دوباره تلاش کنید.",
}

ERROR_CONTACT_INVALID = {
    Language.EN: (
        "⚠️ Please enter a valid phone number with country code.\n"
        "Example: +1 234 567 8900 or +98 912 345 6789\n"
        "Or use the 📱 Share Contact button above."
    ),
    Language.FA: (
        "⚠️ لطفاً شماره تلفن معتبر با کد کشور وارد کنید.\n"
        "مثال: +1 234 567 8900 یا +98 912 345 6789\n"
        "یا از دکمه 📱 اشتراک مخاطب استفاده کنید."
    ),
}

ERROR_LOCATION_INVALID = {
    Language.EN: (
        "⚠️ Please enter location in format: City, Country (Timezone)\n"
        "Example: Tehran, Iran (UTC+3:30) or New York, USA (EST)\n"
        "Or use the 📍 Share Location button above."
    ),
    Language.FA: (
        "⚠️ لطفاً موقعیت را به فرمت: شهر، کشور (منطقه زمانی) بنویسید\n"
        "مثال: تهران، ایران (UTC+3:30) یا نیویورک، آمریکا (EST)\n"
        "یا از دکمه 📍 اشتراک موقعیت استفاده کنید."
    ),
}

ERROR_URL_INVALID = {
    Language.EN: (
        "⚠️ Please enter a valid URL or portfolio link.\n"
        "Examples: https://github.com/username, https://behance.net/portfolio, or your website URL."
    ),
    Language.FA: (
        "⚠️ لطفاً یک لینک معتبر یا آدرس پورتفولیو وارد کنید.\n"
        "مثال: https://github.com/username، https://behance.net/portfolio یا آدرس وب‌سایت شما."
    ),
}

ERROR_GROUP_NOTIFICATION_FAILED = {
    Language.EN: "⚠️ Your application was saved, but we couldn't send a notification to the team. Don't worry, your data is safe and will be reviewed.",
    Language.FA: "⚠️ درخواست شما ذخیره شد، اما نتوانستیم به تیم اطلاع دهیم. نگران نباشید، اطلاعات شما امن است و بررسی خواهد شد.",
}

ERROR_GENERIC = {
    Language.EN: "⚠️ Something went wrong. Please try again or use /menu to return to the main menu.",
    Language.FA: "⚠️ مشکلی پیش آمد. لطفاً دوباره تلاش کنید یا از /menu برای بازگشت به منوی اصلی استفاده کنید.",
}


def get_language_from_button(label: str) -> Optional[Language]:
    normalized = label.strip()
    for lang, button in LANGUAGE_BUTTONS.items():
        if normalized == button:
            return lang
    return None


def main_menu_labels(language: Language) -> List[List[str]]:
    return [
        [
            MENU_LABELS["apply"][language],
            MENU_LABELS["about"][language],
        ],
        [
            MENU_LABELS["updates"][language],
            MENU_LABELS["contact"][language],
        ],
        [
            MENU_LABELS["history"][language],
        ],
        [
            MENU_LABELS["switch"][language],
        ],
    ]


def language_keyboard() -> List[List[str]]:
    return [[LANGUAGE_BUTTONS[Language.EN], LANGUAGE_BUTTONS[Language.FA]]]


def yes_no_keyboard(language: Language) -> List[List[str]]:
    return [[YES_LABEL[language], NO_LABEL[language]]]


def voice_keyboard(language: Language) -> List[List[str]]:
    """Voice recording is now MANDATORY - no skip button."""
    return [[BACK_TO_MENU[language]]]


def back_keyboard(language: Language) -> List[List[str]]:
    return [[BACK_TO_MENU[language]]]


def switch_language(language: Language) -> Language:
    return Language.FA if language == Language.EN else Language.EN


def is_back_button(text: str, language: Language) -> bool:
    return text.strip() == BACK_TO_MENU[language]


_YES_KEYWORDS = {
    Language.EN: {"yes", "y", "yeah", "yep", "sure", "ok", "okay", "affirmative", "confirm"},
    Language.FA: {"بله", "بلی", "اره", "آره", "اوکی", "باشه", "حتما", "حتماً"},
}

_NO_KEYWORDS = {
    Language.EN: {"no", "n", "nope", "nah"},
    Language.FA: {"خیر", "نه", "نخیر"},
}

_SKIP_KEYWORDS = {
    Language.EN: {"skip", "pass", "later", "notnow"},
    Language.FA: {"رد", "ردکردن", "بعدا", "بعداً", "فعلاخیر", "بیخیال"},
}

_QUESTION_KEYWORDS = {
    Language.EN: {"what", "why", "how", "help", "explain", "where", "who"},
    Language.FA: {"چی", "چطور", "چرا", "کمک", "کجا", "کی"},
}


def _normalize_answer(text: str) -> str:
    lowered = text.strip().lower()
    cleaned = re.sub(r"[^\w\u0600-\u06FF]+", "", lowered)
    return cleaned


def is_yes(text: str, language: Language) -> bool:
    stripped = text.strip()
    if stripped == YES_LABEL[language]:
        return True
    normalized = _normalize_answer(stripped)
    return normalized in _YES_KEYWORDS[language]


def is_no(text: str, language: Language) -> bool:
    stripped = text.strip()
    if stripped == NO_LABEL[language]:
        return True
    normalized = _normalize_answer(stripped)
    return normalized in _NO_KEYWORDS[language]


def is_skip(text: str, language: Language) -> bool:
    stripped = text.strip()
    if stripped.lower() == SKIP_LABEL[language].lower():
        return True
    normalized = _normalize_answer(stripped)
    return normalized in _SKIP_KEYWORDS[language]


PERSIAN_DIGITS = {
    "0": "۰",
    "1": "۱",
    "2": "۲",
    "3": "۳",
    "4": "۴",
    "5": "۵",
    "6": "۶",
    "7": "۷",
    "8": "۸",
    "9": "۹",
}


def localize_number(number: int, language: Language) -> str:
    if language == Language.EN:
        return str(number)
    return "".join(PERSIAN_DIGITS.get(ch, ch) for ch in str(number))


def edit_keyboard(language: Language) -> List[List[str]]:
    rows: List[List[str]] = []
    numbers = [localize_number(i, language) for i in range(1, 13)]
    rows.append(numbers[0:3])
    rows.append(numbers[3:6])
    rows.append(numbers[6:9])
    rows.append(numbers[9:12])
    # Add option 13 for voice re-recording
    rows.append([localize_number(13, language)])  # "Re-record voice"
    rows.append([BACK_TO_MENU[language]])
    return rows


# Group command strings
GROUP_ONLY_COMMAND = {
    Language.EN: "⚠️ This command is only available in group chats.",
    Language.FA: "⚠️ این دستور فقط در چت‌های گروهی در دسترس است.",
}

GROUP_ADMIN_REQUIRED = {
    Language.EN: "⚠️ This command requires group administrator privileges.",
    Language.FA: "⚠️ این دستور نیاز به دسترسی مدیر گروه دارد.",
}

GROUP_HELP_TEXT = {
    Language.EN: (
        "<b>📊 Group Commands</b>\n\n"
        "Available commands for group administrators:\n\n"
        "/daily or /report – Daily report (applications and messages today)\n"
        "/gstats – Detailed statistics (all-time and by period)\n"
        "/recent – List recent applications (last 10)\n"
        "/app &lt;id&gt; – View application details by ID\n"
        "/ghelp – Show this help message\n\n"
        "All commands require group administrator privileges."
    ),
    Language.FA: (
        "<b>📊 دستورات گروه</b>\n\n"
        "دستورات موجود برای مدیران گروه:\n\n"
        "/daily یا /report – گزارش روزانه (درخواست‌ها و پیام‌های امروز)\n"
        "/gstats – آمار تفصیلی (همه‌زمان و بر اساس دوره)\n"
        "/recent – لیست درخواست‌های اخیر (آخرین ۱۰ مورد)\n"
        "/app &lt;id&gt; – مشاهده جزئیات درخواست با شناسه\n"
        "/ghelp – نمایش این پیام راهنما\n\n"
        "همه دستورات نیاز به دسترسی مدیر گروه دارند."
    ),
}

GROUP_DAILY_REPORT = {
    Language.EN: (
        "<b>📊 Daily Report</b>\n\n"
        "<b>Today ({date})</b>\n"
        "📝 Applications: {today_apps}\n"
        "💬 Contact messages: {today_contacts}\n"
        "🎤 Voice samples: {today_voices} received, {today_skipped} skipped\n"
        "🌐 Language breakdown: {en_count} EN, {fa_count} FA\n\n"
        "<b>This Week</b>\n"
        "📝 Applications: {week_apps}\n"
        "💬 Contact messages: {week_contacts}\n\n"
        "<b>This Month</b>\n"
        "📝 Applications: {month_apps}\n"
        "💬 Contact messages: {month_contacts}\n\n"
        "{recent_list}"
    ),
    Language.FA: (
        "<b>📊 گزارش روزانه</b>\n\n"
        "<b>امروز ({date})</b>\n"
        "📝 درخواست‌ها: {today_apps}\n"
        "💬 پیام‌های تماس: {today_contacts}\n"
        "🎤 نمونه‌های صوتی: {today_voices} دریافت شده، {today_skipped} رد شده\n"
        "🌐 تقسیم‌بندی زبان: {en_count} انگلیسی، {fa_count} فارسی\n\n"
        "<b>این هفته</b>\n"
        "📝 درخواست‌ها: {week_apps}\n"
        "💬 پیام‌های تماس: {week_contacts}\n\n"
        "<b>این ماه</b>\n"
        "📝 درخواست‌ها: {month_apps}\n"
        "💬 پیام‌های تماس: {month_contacts}\n\n"
        "{recent_list}"
    ),
}

GROUP_STATS_REPORT = {
    Language.EN: (
        "<b>📈 Statistics Report</b>\n\n"
        "<b>All-Time Totals</b>\n"
        "📝 Total applications: {total_apps}\n"
        "💬 Total contact messages: {total_contacts}\n"
        "👥 Unique applicants: {unique_users}\n"
        "🎤 Voice samples: {total_voices} received, {total_skipped} skipped\n\n"
        "<b>Language Breakdown</b>\n"
        "🇬🇧 English: {en_count} ({en_percent}%)\n"
        "🇮🇷 Farsi: {fa_count} ({fa_percent}%)\n\n"
        "<b>By Period</b>\n"
        "📅 Today: {today_apps} applications\n"
        "📅 This week: {week_apps} applications\n"
        "📅 This month: {month_apps} applications\n"
        "📅 All time: {total_apps} applications"
    ),
    Language.FA: (
        "<b>📈 گزارش آمار</b>\n\n"
        "<b>مجموع همه‌زمان</b>\n"
        "📝 کل درخواست‌ها: {total_apps}\n"
        "💬 کل پیام‌های تماس: {total_contacts}\n"
        "👥 متقاضیان منحصر به فرد: {unique_users}\n"
        "🎤 نمونه‌های صوتی: {total_voices} دریافت شده، {total_skipped} رد شده\n\n"
        "<b>تقسیم‌بندی زبان</b>\n"
        "🇬🇧 انگلیسی: {en_count} ({en_percent}%)\n"
        "🇮🇷 فارسی: {fa_count} ({fa_percent}%)\n\n"
        "<b>بر اساس دوره</b>\n"
        "📅 امروز: {today_apps} درخواست\n"
        "📅 این هفته: {week_apps} درخواست\n"
        "📅 این ماه: {month_apps} درخواست\n"
        "📅 همه‌زمان: {total_apps} درخواست"
    ),
}

GROUP_RECENT_APPLICATIONS = {
    Language.EN: (
        "<b>📋 Recent Applications</b>\n\n"
        "{applications_list}\n\n"
        "Total shown: {count} of {total}"
    ),
    Language.FA: (
        "<b>📋 درخواست‌های اخیر</b>\n\n"
        "{applications_list}\n\n"
        "نمایش داده شده: {count} از {total}"
    ),
}

GROUP_APPLICATION_DETAILS = {
    Language.EN: (
        "<b>📄 Application Details</b>\n\n"
        "<b>Application ID:</b> <code>{application_id}</code>\n"
        "<b>Submitted:</b> {submitted_at}\n"
        "<b>Language:</b> {language}\n\n"
        "<b>Applicant Information</b>\n"
        "👤 Name: {name}\n"
        "📧 Email: {email}\n"
        "📱 Contact: {contact}\n"
        "🌐 Location: {location}\n"
        "🔗 Portfolio: {portfolio}\n"
        "💬 Telegram: @{username} ({telegram_id})\n\n"
        "<b>Application Answers</b>\n"
        "{answers}\n\n"
        "<b>Voice Sample</b>\n"
        "{voice_status}"
    ),
    Language.FA: (
        "<b>📄 جزئیات درخواست</b>\n\n"
        "<b>شناسه درخواست:</b> <code>{application_id}</code>\n"
        "<b>ارسال شده:</b> {submitted_at}\n"
        "<b>زبان:</b> {language}\n\n"
        "<b>اطلاعات متقاضی</b>\n"
        "👤 نام: {name}\n"
        "📧 ایمیل: {email}\n"
        "📱 تماس: {contact}\n"
        "🌐 موقعیت: {location}\n"
        "🔗 نمونه کار: {portfolio}\n"
        "💬 تلگرام: @{username} ({telegram_id})\n\n"
        "<b>پاسخ‌های درخواست</b>\n"
        "{answers}\n\n"
        "<b>نمونه صوتی</b>\n"
        "{voice_status}"
    ),
}

GROUP_APPLICATION_NOT_FOUND = {
    Language.EN: "❌ Application not found. Please check the application ID.",
    Language.FA: "❌ درخواست یافت نشد. لطفاً شناسه درخواست را بررسی کنید.",
}

GROUP_APPLICATION_ITEM = {
    Language.EN: (
        "• <b>{name}</b> ({email})\n"
        "  ID: <code>{application_id}</code> | {date} | {language} | {voice_status}"
    ),
    Language.FA: (
        "• <b>{name}</b> ({email})\n"
        "  شناسه: <code>{application_id}</code> | {date} | {language} | {voice_status}"
    ),
}

def contact_keyboard(language: Language) -> List[List[str]]:
    """Keyboard for requesting contact sharing."""
    return [[SHARE_CONTACT_BUTTON[language]], [BACK_TO_MENU[language]]]


def location_keyboard(language: Language) -> List[List[str]]:
    """Keyboard for requesting location sharing."""
    return [[SHARE_LOCATION_BUTTON[language]], [BACK_TO_MENU[language]]]

