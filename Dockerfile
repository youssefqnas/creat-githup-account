FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 1) أدوات النظام + Xvfb + خطوط + إضافة مستودع جوجل كروم وتثبيته
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    xvfb x11-utils x11-apps python3-tk gnome-screenshot \
    fonts-noto fonts-noto-color-emoji fonts-liberation \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 2) مجلد العمل
WORKDIR /app

# 3) تثبيت بايثون دِبندنسيز (requirements + PyAutoGUI)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "pillow>=9.2.0" pyautogui

# 4) نسخ الكود
COPY . .

# 5) (اختياري أفضل أمانًا) مستخدم غير root
RUN useradd -m app && chown -R app:app /app
USER app

# 6) افتراضيًا نشغّل داخل Xvfb علشان PyAutoGUI يلاقي DISPLAY
# لو عايز Headless Chrome فقط: غيّر الأمر وقت التشغيل لـ: python main.py
CMD xvfb-run -a python main.py
