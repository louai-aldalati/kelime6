# gemini_api.py

import os
import base64
import logging
from google import genai
from google.genai import types

# تهيئة الـ Client لاستخدام Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# إنشاء لوججر خاص للمكتبة كي نتمكن من تتبع الاستجابات
logger = logging.getLogger(__name__)


def generate_story_gemini(prompt: str, max_tokens: int = 300) -> str:
    """
    يولد قصة باستخدام نموذج Gemini عبر واجهة generate_content.
    استخدمنا هنا نموذج 'gemini-2.0-flash' لأنه مدعوم لطباعة المحتوى النصي.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0.7
        ),
    )
    return response.text


def generate_image_gemini(prompt: str, size: str = "512x512") -> bytes:
    """
    يولّد صورة باستخدام نموذج Gemini 2.0 Flash Preview Image Generation،
    مع إخراج نصّ وصورة معًا كما توصي الوثائق الرسمية.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",  # اسم الموديل الدقيق لإنشاء الصور
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],  # يجب تضمين TEXT و IMAGE
            max_output_tokens=1  # القائمة النصيّة صغيرة لأننا نركّز على الصورة
        ),
    )

    # سجّل الاستجابة كاملة في اللوج لتتأكد من البنية
    logger.debug("Gemini IMAGE full response: %s", response)

    # تحقق من وجود مرشحين
    if not response.candidates:
        raise RuntimeError("Gemini أرجع استجابة بدون مرشحين (candidates)")

    # ابحث في الأجزاء عن بيانات الصورة
    for part in response.candidates[0].content.parts:
        # إذا وجدت inline_data فهذا هو البايت باقة للصورة
        if getattr(part, "inline_data", None) is not None:
            return part.inline_data.data

        # إذا كانت البيانات في حقل image.image_bytes
        if hasattr(part, "image") and part.image is not None:
            image_bytes = getattr(part.image, "image_bytes", None)
            if image_bytes:
                return image_bytes

    # إذا ما وُجدت بايتات الصورة
    raise RuntimeError("Gemini أرجع استجابة دون صورة")
