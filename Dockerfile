# ابدأ من صورة بايثون مع الأدوات الأساسية (مثل debian-slim)
FROM python:3.11-slim

# قم بتحديث نظام التشغيل وتثبيت حزم التشغيل اللازمة لـ Xvfb و Playwright
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # Xvfb و xvfb-run
        xvfb \
        # **الإضافة الجديدة هنا لحل مشكلة 'xauth command not found'**
        xauth \
        # بديل محتمل في حالة عدم وجود xauth كحزمة منفصلة: x11-utils
        # x11-utils \
        # متطلبات Chromium الأساسية
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libdrm2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libglib2.0-0 \
        libjpeg-dev \
        libpng-dev \
        libwebp-dev \
        libxkbcommon0 \
        # تنظيف لتقليل حجم الصورة
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تعيين دليل العمل
WORKDIR /app

# نسخ ملف متطلبات بايثون
COPY requirements.txt .

# تثبيت متطلبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفحات Playwright (اختياري، يمكنك ترك Zeabur يفعلها)
# إذا كنت تريد التأكد من الإصدار الصحيح:
RUN playwright install chromium

# نسخ الكود الخاص بك
COPY main.py .

# الأمر لتشغيل الكود باستخدام Xvfb
# Xvfb-run هو الأمر الذي يشغل البرنامج داخل بيئة عرض وهمية

CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "-u", "main.py"]

