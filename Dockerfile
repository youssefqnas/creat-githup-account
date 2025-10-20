# استخدام نسخة مستقرة من Python
FROM python:3.12-slim-bullseye

# تعيين متغير البيئة لجعل تثبيت الحزم غير تفاعلي
ENV DEBIAN_FRONTEND=noninteractive

# ⚡️ تفعيل الطباعة الفورية (منع buffering)
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# تثبيت المتصفح والتبعيات (Xvfb و Google Chrome)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        unzip \
        xvfb \
        xauth \
        libnss3 \
        libxss1 \
        libappindicator3-1 \
        libayatana-indicator7 \
        fonts-liberation \
        xdg-utils \
        libgbm-dev \
        libu2f-udev \
        libcups2 \
        libgtk-3-0 \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /tmp/chrome.deb || true \
    && apt-get install -fy \
    && rm /tmp/chrome.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# إعداد دليل العمل داخل الحاوية
WORKDIR /app

# نسخ المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود بالكامل (بدون هروب المسافات)
COPY . .

# إنشاء ملف نطاقات افتراضي
RUN echo "@yopmail.com" > "yopmail domain.txt"

# ⚙️ إعداد نقطة الدخول لتشغيل Xvfb
ENTRYPOINT ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24"]

# 🧠 تشغيل البرنامج في وضع غير مكدس الـ stdout
CMD ["python", "-u", "main.py"]
