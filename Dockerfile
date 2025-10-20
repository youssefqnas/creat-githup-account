# Dockerfile

# -----------------
# 1. مرحلة البناء (Build Stage)
# -----------------

FROM python:3.9-slim-bullseye

# عيّن مجلد العمل داخل الحاوية. جميع الأوامر التالية ستنفذ من هذا المسار.
WORKDIR /app

# ----------------------------------------------------
# 2. تثبيت متصفح Chromium والاعتماديات الهامة لتشغيله (الإضافة الجديدة)
# ----------------------------------------------------
RUN apt-get update && apt-get install -y \
    chromium \
    # هذه الحزم ضرورية لتشغيل Chromium في بيئة لينكس Headless
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    # تنظيف ملفات الحزم لتقليل حجم الصورة النهائية
    && rm -rf /var/lib/apt/lists/*

# -----------------
# 3. تثبيت الاعتماديات (Dependencies)
# -----------------

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------
# 4. نسخ الكود وتشغيل التطبيق
# -----------------

COPY . .

# الأمر الذي سيتم تنفيذه عند بدء تشغيل الحاوية.
CMD ["python", "main.py"]
