# استخدام آخر نسخة مستقرة من بايثون 3.12 (slim)
FROM python:3.12-slim-bullseye

# تعيين متغير البيئة لجعل تثبيت الحزم غير تفاعلي
ENV DEBIAN_FRONTEND=noninteractive

# تثبيت متصفح Chrome وتبعياته (Xvfb)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        unzip \
        xvfb \
        xauth \
        # تثبيت حزم أساسية لحل تبعيات Chrome
        # يجب أن تكون هذه الحزم كافية للتشغيل في بيئة headless
        libnss3 \
        libxss1 \
        libappindicator1 \
        libindicator7 \
        fonts-liberation \
        xdg-utils \
        libgbm-dev \
        libu2f-udev \
        libcups2 \
        libgtk-3-0 \
    # 1. تحميل حزمة Google Chrome .deb مباشرةً
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    \
    # 2. تثبيت الحزمة (dpkg قد يفشل بسبب التبعيات)
    && dpkg -i /tmp/chrome.deb || true \
    \
    # 3. تثبيت التبعيات المفقودة وحل أي فشل في dpkg
    && apt-get install -fy \
    \
    # 4. تنظيف الملفات المؤقتة لتصغير حجم الصورة
    && rm /tmp/chrome.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# إعداد دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت مكتبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات الكود
# نستخدم اسم الملف كما هو 'creat githup.py'
COPY creat\ githup.py .

# إنشاء ملف النطاقات الافتراضي لتجنب خطأ إذا لم يكن موجوداً
RUN echo "@yopmail.com" > "yopmail domain.txt"

# تعيين نقطة الدخول (ENTRYPOINT) لتشغيل السكريبت باستخدام Xvfb
# يستخدم Zeabur هذا الأمر كعملية رئيسية للحاوية.
ENTRYPOINT ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24"]

# الأمر الذي سيتم تنفيذه ضمن بيئة Xvfb
CMD ["python", "main.py"]
