"""Urgency triage + step-by-step action plans.

This module turns a classified intent into:
  * an urgency level (critical / urgent / standard) with a color
  * a concrete, time-bound action plan in EN or AR

The legal text alone tells a citizen what their rights *are*; this tells them
what to *do* about it, today/this week/this month. That is the difference
between an info kiosk and a tool people will actually use.

Keyword-based on purpose: it's auditable, runs in microseconds, and is easy
for a non-engineer (lawyer, paralegal) to extend.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Words that mean "this is happening RIGHT NOW" — escalate to critical.
_CRITICAL_TRIGGERS = {
    "en": [
        r"\barrested\b", r"\bdetained\b", r"\bin (?:custody|jail|prison)\b",
        r"\btortur", r"\bbeaten\b", r"\bthreaten(?:ing|ed)?\b",
        r"\bevict(?:ed|ing) (?:today|now|tonight)\b",
        r"\b(?:right )?now\b", r"\btoday\b", r"\bthis (?:morning|evening)\b",
        r"\b(?:police|soldiers?) (?:are|came|broke)\b",
    ],
    "ar": [
        r"اعتقل", r"احتجز", r"يعتقل", r"معتقل",
        r"تعذيب", r"عذبو", r"ضرب",
        r"الآن", r"اليوم", r"هذه الليلة", r"الليلة",
        r"الشرطة (?:جاء|تأتي|اقتحم)",
    ],
}

# Topics that are inherently urgent even without "now" wording.
_URGENT_INTENTS = {"criminal", "eviction", "emergency"}


@dataclass
class Triage:
    level: str          # "critical" | "urgent" | "standard"
    color: str          # "red" | "amber" | "green"
    label: str          # localized human-readable label
    deadline_hint: str  # short note about typical legal deadline


def _has_critical_trigger(text: str, language: str) -> bool:
    bank = _CRITICAL_TRIGGERS.get(language, [])
    return any(re.search(p, text, flags=re.IGNORECASE) for p in bank)


def assess(text: str, intent: str, language: str = "en") -> Triage:
    """Return a Triage record for the situation described by `text`."""
    text = text or ""
    if _has_critical_trigger(text, language):
        return Triage(
            level="critical",
            color="red",
            label=("حرج — تصرف فوراً" if language == "ar" else "Critical — act now"),
            deadline_hint=(
                "خلال ساعات: اتصل بمحامٍ أو منظمة حقوق إنسان فوراً."
                if language == "ar"
                else "Within hours: call a lawyer or a human-rights org immediately."
            ),
        )
    if intent in _URGENT_INTENTS:
        return Triage(
            level="urgent",
            color="amber",
            label=("عاجل" if language == "ar" else "Urgent"),
            deadline_hint=(
                "خلال 7 أيام: اجمع الأدلة وتواصل مع محامٍ."
                if language == "ar"
                else "Within 7 days: gather evidence and contact a lawyer."
            ),
        )
    return Triage(
        level="standard",
        color="green",
        label=("استشارة عامة" if language == "ar" else "General inquiry"),
        deadline_hint=(
            "خلال 30 يوماً: راجع المستندات واطلب استشارة قانونية."
            if language == "ar"
            else "Within 30 days: review documents and seek legal counsel."
        ),
    )


# --- Action plans -----------------------------------------------------------

# Keys: intent label -> language -> ordered list of (timeframe, action) pairs.
_PLANS: dict[str, dict[str, list[tuple[str, str]]]] = {
    "eviction": {
        "en": [
            ("Today", "Do not leave. A verbal eviction order has no legal standing in Palestine."),
            ("Today", "Photograph any written notices and save messages from the landlord."),
            ("This week", "Send a written reply citing Articles 17, 21, 23 of the Basic Law."),
            ("Within 30 days", "File a complaint with the local court if a formal eviction notice arrives."),
        ],
        "ar": [
            ("اليوم", "لا تغادر. الإنذار الشفهي بالإخلاء لا قيمة قانونية له في فلسطين."),
            ("اليوم", "صوّر أي إنذارات مكتوبة واحفظ الرسائل من المالك."),
            ("هذا الأسبوع", "أرسل رداً مكتوباً مستنداً إلى المواد 17 و21 و23 من القانون الأساسي."),
            ("خلال 30 يوماً", "قدّم شكوى إلى المحكمة المحلية في حال وصول إنذار إخلاء رسمي."),
        ],
    },
    "criminal": {
        "en": [
            ("Right now", "Stay completely silent — Art. 97 & 217 of Penal Procedure Law No. 3/2001 guarantee your right to silence."),
            ("Right now", "Demand a lawyer immediately — Art. 102 guarantees counsel during investigation; Art. 244 requires court-appointed defence for felonies."),
            ("Within 24 hours", "You must be brought before the Deputy-Prosecutor within 24 hours (Art. 34). Demand this if it has not happened."),
            ("Within 24 hours", "Insist on being told the charges — Art. 96 requires the Prosecutor to inform you before any interrogation."),
            ("Within 48 hours", "Detention beyond 24 hours requires a Magistrate order — maximum 15 days per Art. 119, and 45 days total per Art. 120."),
            ("This week", "Any confession obtained by coercion is void under Art. 214 and Art. 273. Document any mistreatment immediately."),
            ("This week", "You have the right to contact your family (Art. 123). A communication ban cannot last more than 10 days (Art. 103)."),
        ],
        "ar": [
            ("الآن", "التزم الصمت التام — المادة 97 والمادة 217 من قانون الإجراءات الجزائية رقم 3 لسنة 2001 تكفلان حقك في الصمت."),
            ("الآن", "اطلب محامياً فوراً — المادة 102 تكفل حق التمثيل خلال التحقيق، والمادة 244 تُلزم المحكمة بتعيين محامٍ للجنايات."),
            ("خلال 24 ساعة", "يجب تقديمك أمام نائب النيابة خلال 24 ساعة (المادة 34). اطلب ذلك إذا لم يحدث."),
            ("خلال 24 ساعة", "أصرّ على إبلاغك بالتهم — المادة 96 تُلزم النيابة بإخطارك قبل أي استجواب."),
            ("خلال 48 ساعة", "الاحتجاز أكثر من 24 ساعة يستوجب أمراً قضائياً — الحد الأقصى 15 يوماً (المادة 119) وإجمالاً 45 يوماً (المادة 120)."),
            ("هذا الأسبوع", "أي اعتراف انتُزع تحت الإكراه باطل بموجب المادة 214 والمادة 273. وثّق أي سوء معاملة فوراً."),
            ("هذا الأسبوع", "لك الحق في التواصل مع أسرتك (المادة 123). حظر التواصل لا يتجاوز 10 أيام (المادة 103)."),
        ],
    },
    "labor": {
        "en": [
            ("Today", "Save your contract, payslips and any termination message."),
            ("This week", "Send a written demand to the employer for unpaid wages or notice pay."),
            ("Within 30 days", "File a complaint at the Ministry of Labor under Law No. 7 of 2000."),
        ],
        "ar": [
            ("اليوم", "احتفظ بنسخة من العقد وقسائم الراتب ورسالة الفصل إن وُجدت."),
            ("هذا الأسبوع", "أرسل مطالبة مكتوبة لصاحب العمل بالأجور المتأخرة أو بدل الإنذار."),
            ("خلال 30 يوماً", "تقدّم بشكوى لوزارة العمل بموجب قانون رقم 7 لسنة 2000."),
        ],
    },
    "family": {
        "en": [
            ("Today", "Keep yourself and your children safe; identify a trusted relative."),
            ("This week", "Contact WCLAC or a Sharia court legal aid clinic."),
            ("Within 30 days", "Collect IDs, marriage certificate, financial records before filing."),
        ],
        "ar": [
            ("اليوم", "حافظ على سلامتك وسلامة أطفالك، وحدّد قريباً موثوقاً."),
            ("هذا الأسبوع", "تواصل مع مركز المرأة للإرشاد القانوني (WCLAC) أو محكمة شرعية."),
            ("خلال 30 يوماً", "اجمع الهويات وعقد الزواج والسجلات المالية قبل تقديم الدعوى."),
        ],
    },
    "property": {
        "en": [
            ("This week", "Locate title deeds (tabu / kushan) and any tax receipts."),
            ("Within 30 days", "Article 21: expropriation requires fair compensation — demand it in writing."),
            ("Within 60 days", "File at the Magistrate Court if compensation is denied or unfair."),
        ],
        "ar": [
            ("هذا الأسبوع", "أحضر سند الملكية (الطابو / الكوشان) وإيصالات الضريبة."),
            ("خلال 30 يوماً", "المادة 21: نزع الملكية يستوجب تعويضاً عادلاً — اطلبه كتابياً."),
            ("خلال 60 يوماً", "تقدّم بدعوى أمام محكمة الصلح إذا رُفض التعويض أو كان غير عادل."),
        ],
    },
    "emergency": {
        "en": [
            ("Now", "Articles 110–113 protect core rights even during emergency."),
            ("This week", "Document curfew violations or arbitrary searches with photos and witnesses."),
            ("Within 30 days", "Submit a complaint to a human-rights organization (Al-Haq, Al-Mezan)."),
        ],
        "ar": [
            ("الآن", "المواد 110 إلى 113 تحمي الحقوق الأساسية حتى أثناء الطوارئ."),
            ("هذا الأسبوع", "وثّق انتهاكات حظر التجول أو التفتيش التعسفي بالصور والشهود."),
            ("خلال 30 يوماً", "قدّم شكوى إلى منظمة حقوق إنسان (الحق، الميزان)."),
        ],
    },
    "education": {
        "en": [
            ("This week", "Article 24 guarantees free basic education — keep enrollment records."),
            ("Within 30 days", "If a school refuses enrollment, file with the Ministry of Education."),
        ],
        "ar": [
            ("هذا الأسبوع", "المادة 24 تكفل التعليم الأساسي المجاني — احتفظ بأوراق التسجيل."),
            ("خلال 30 يوماً", "إذا رفضت المدرسة التسجيل، تقدّم بشكوى لوزارة التربية والتعليم."),
        ],
    },
    "discrimination": {
        "en": [
            ("Today", "Write down what was said or done, by whom, and any witnesses."),
            ("Within 30 days", "Article 9 guarantees equality — file at the Independent Commission for Human Rights."),
        ],
        "ar": [
            ("اليوم", "اكتب ما قيل أو حدث ومن قام به وأسماء الشهود."),
            ("خلال 30 يوماً", "المادة 9 تكفل المساواة — تقدّم بشكوى للهيئة المستقلة لحقوق الإنسان."),
        ],
    },
    "general": {
        "en": [
            ("Today", "Write down what happened, dates, names, and any documents you have."),
            ("This week", "Visit a legal aid clinic for a free initial consultation."),
        ],
        "ar": [
            ("اليوم", "اكتب ما حدث والتواريخ والأسماء وأي مستندات لديك."),
            ("هذا الأسبوع", "زر مركز مساعدة قانونية للحصول على استشارة أولية مجانية."),
        ],
    },
}


def action_plan(intent: str, language: str = "en") -> list[dict]:
    """Return an ordered list of {timeframe, action} steps for the given intent."""
    plan = _PLANS.get(intent) or _PLANS["general"]
    steps = plan.get(language) or plan["en"]
    return [{"timeframe": t, "action": a} for t, a in steps]
