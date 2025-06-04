import os
import openai



# 1) تهيئة المفتاح
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_story_openai(prompt: str, max_tokens: int = 300) -> str:
    """
    يولد قصة باستخدام واجهة chat.completions في openai>=1.0.0
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",              # أو "gpt-4" إذا متوفر
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        n=1,
    )
    # المحتوى يعود في response.choices[0].message.content
    return response.choices[0].message.content.strip()

def generate_image_openai(prompt: str, size: str = "512x512") -> bytes:
    """
    يولد صورة باستخدام واجهة images.generate في openai>=1.0.0 ويعيد البايت.
    """
    response = openai.images.generate(
        prompt=prompt,
        n=1,
        size=size
    )
    image_url = response.data[0].url
    import requests
    img_resp = requests.get(image_url)
    img_resp.raise_for_status()
    return img_resp.content
