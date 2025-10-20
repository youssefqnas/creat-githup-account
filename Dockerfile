# Dockerfile

# -----------------
# 1. مرحلة البناء (Build Stage)
# -----------------

# ابدأ من صورة بايثون رسمية. نسخة "slim" تكون أصغر حجماً وأكثر كفاءة.
FROM python:3.9-slim-bullseye

# عيّن مجلد العمل داخل الحاوية. جميع الأوامر التالية ستنفذ من هذا المسار.
WORKDIR /app

# ----------------------------------------------------
# 2. تثبيت Google Chrome Stable والاعتماديات الهامة
# هذا يحل مشكلة عدم تطابق إصدار المتصفح (Version Mismatch)
# ----------------------------------------------------

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    --no-install-recommends \
# تنزيل مفتاح GPG لإضافة مستودع Google Chrome
&& wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
# إضافة مستودع Google Chrome إلى قائمة المصادر
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
# التحديث وتثبيت المتصفح الفعلي (Google Chrome Stable)
&& apt-get update && apt-get install -y google-chrome-stable \
# تثبيت حزم مساعدة ضرورية لـ Headless Mode (على الرغم من أن Chrome Stable قد يثبت معظمها)
# libnss3 و libgconf-2-4 لم تعد ضرورية مع الإصدارات الحديثة، ولكن لن نضر بإبقائها
# الحزمة الأساسية هي google-chrome-stable
# حذف ملفات الحزم المؤقتة لتقليل حجم الصورة
&& rm -rf /var/lib/apt/lists/*


# -----------------
# 3. تثبيت الاعتماديات (Dependencies)
# -----------------

COPY requirements.txt .

# قم بتثبيت جميع المكتبات المذكورة في الملف.
RUN pip install --no-cache-dir -r requirements.txt

# -----------------
# 4. نسخ الكود وتشغيل التطبيق
# -----------------

COPY . .

# الأمر الذي سيتم تنفيذه عند بدء تشغيل الحاوية.
# لا يتغير
CMD ["python", "main.py"]
