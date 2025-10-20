import time
import undetected_chromedriver as uc
import random
import string
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# --- الإعدادات العامة ---
FIXED_DOMAIN = "@mesemails.fr.nf"
LOG_FILE = "log.txt"

# --- تهيئة نظام التسجيل ---
def setup_logger():
    """تهيئة نظام تسجيل بسيط يسجل في ملف log.txt ويطبع في الكونسول."""
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a", encoding="utf-8")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    sys.stdout = Logger(LOG_FILE)
    print("\n" + "=" * 60)
    print(f"بدء تشغيل السكربت في {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

setup_logger()

# --- دوال مساعدة ---
def generate_random_username(length=10):
    """توليد اسم مستخدم عشوائي."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def setup_ad_blocking(driver):
    """حظر إعلانات Google AdSense."""
    ad_url_patterns = [
        "*pagead2.googlesyndication.com*",
        "*googleads.g.doubleclick.net*",
        "*adservice.google.com*",
    ]
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ad_url_patterns})
        print("✅ تم تفعيل حظر الإعلانات بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل إعداد حظر الإعلانات: {e}")


def open_github_in_new_tab(driver, github_url, wait):
    """فتح GitHub في تاب جديد بثلاث طرق."""
    print("🔗 محاولة فتح GitHub في تاب جديد...")
    orig_handles = driver.window_handles.copy()

    try:
        # الطريقة الأولى
        driver.execute_script("window.open(arguments[0], '_blank');", github_url)
        WebDriverWait(driver, 8).until(lambda d: len(d.window_handles) > len(orig_handles))
        new_handle = [h for h in driver.window_handles if h not in orig_handles][-1]
        driver.switch_to.window(new_handle)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url)
        print("✅ تم فتح GitHub بنجاح.")
        return True
    except Exception as e:
        print(f"⚠️ فشل فتح GitHub: {e}")
        return False


def run_automation():
    driver = None
    try:
# 1. إعداد المتصفح
        options = uc.ChromeOptions()
        
        # وسائط أساسية لتمكين Chrome من العمل في بيئة Docker/Headless
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        
        # استخدام الوضع الرأسي (headless)
        options.add_argument("headless-new")
        
        # وسائط سابقة
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        
        # تحديد مسار الـ ChromeDriver المثبت داخل Docker
        log_message("تم إعداد وسائط المتصفح بنجاح، جاري بدء تشغيل السيلينيوم.")
        driver = uc.Chrome(
            options=options, 
            driver_executable_path="/usr/bin/chromedriver"
        )
        setup_ad_blocking(driver)
        wait = WebDriverWait(driver, 30)

        # 2. فتح Yopmail واستخراج البريد
        yopmail_url = "https://yopmail.com/en/email-generator"
        driver.get(yopmail_url)
        print("🟢 تم فتح Yopmail.")

        email_display_element = wait.until(EC.visibility_of_element_located((By.ID, "egen")))
        full_generated_email = email_display_element.text
        generated_username = full_generated_email.split('@')[0]
        print(f"📧 اسم المستخدم المستخرج: {generated_username}")

        check_inbox_button = driver.find_element(By.CSS_SELECTOR, ".nw button:nth-child(3)")
        check_inbox_button.click()
        print("📥 تم النقر على 'Check Inbox'.")

        time.sleep(3)
        driver.switch_to.window(driver.window_handles[0])

        # 3. فتح GitHub في تاب جديد
        github_url = "https://github.com/signup"
        if not open_github_in_new_tab(driver, github_url, wait):
            print("❌ فشل في فتح GitHub. إنهاء العملية.")
            return

        print("🟢 تم فتح صفحة تسجيل GitHub.")

        # 4. إدخال البريد الثابت
        full_email = f"{generated_username}{FIXED_DOMAIN}"
        print(f"📧 البريد المستخدم: {full_email}")

        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.clear()
        email_input.send_keys(full_email)
        print("✅ تم إدخال البريد الإلكتروني.")

        # 5. إدخال باقي الحقول
        driver.find_element(By.ID, "password").send_keys("01205226167aA*qw")
        random_login = generate_random_username()
        driver.find_element(By.ID, "login").send_keys(random_login)
        print(f"👤 تم إدخال اسم المستخدم العشوائي: {random_login}")

        # 6. إنشاء الحساب
        create_button_selector = "div.js-octocaptcha-hide > button.signup-form-fields__button"
        create_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, create_button_selector)))
        create_button.click()
        print("🚀 تم النقر على زر إنشاء الحساب.")

        print("\n✅ السكربت أنهى المهام الأساسية بنجاح.")
        time.sleep(10)

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        if driver:
            driver.quit()
            print("🛑 تم إغلاق المتصفح.")

if __name__ == "__main__":
    run_automation()

