# Dockerfile
#
# استخدم صورة أساسية تحتوي على Python وبعض الأدوات الأساسية
FROM python:3.10-slim

# ضبط متغيرات البيئة لمنع ظهور النوافذ المنبثقة وتحسين الأداء
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

# تثبيت Chromium و الاعتماديات اللازمة لتشغيل undetected_chromedriver/Selenium في وضع headless
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libfontconfig \
    libnspr4 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل داخل حاوية Docker
WORKDIR /usr/src/app

# نسخ ملفات المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ سكريبت الأتمتة إلى مجلد العمل
# نفترض أن كود Python المحفوظ لديك يسمى automation_script.py
COPY main.py .

# تحديد الأمر الذي سيتم تنفيذه عند تشغيل الحاوية
# استخدام 'python -u' يضمن أن يكون مخرج python غير مخزن مؤقتاً (unbuffered)، وهو أمر مفيد لـ Real-time logging في Zeabur
CMD ["python", "-u", "main.py"]

