import time
import undetected_chromedriver as uc
import random
import string
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# --- أسماء الملفات ---
DOMAINS_FILE = "yopmail domain.txt"
BLACKLIST_FILE = "Email domain could not be verified.txt"

# --- دوال مساعدة لإدارة الملفات ---
def load_domains(filepath):
    """تحميل قائمة النطاقات من ملف، مع إنشاء الملف إذا لم يكن موجودًا."""
    if not os.path.exists(filepath):
        print(f"إنشاء ملف {filepath} حيث أنه غير موجود.")
        with open(filepath, 'w', encoding='utf-8') as f:
            pass 
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"خطأ أثناء قراءة الملف {filepath}: {e}")
        return []

def append_domain_to_blacklist(domain):
    """إضافة نطاق غير صالح إلى قائمة الحظر."""
    try:
        with open(BLACKLIST_FILE, 'a', encoding='utf-8') as f:
            f.write(domain + '\n')
        print(f"تم تسجيل النطاق غير الصالح: {domain} في ملف الحظر.")
    except Exception as e:
        print(f"خطأ أثناء كتابة النطاق في ملف الحظر: {e}")

def generate_random_username(length=10):
    """توليد اسم مستخدم عشوائي يتكون من حروف وأرقام."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def setup_ad_blocking(driver):
    """تكوين المتصفح لحظر طلبات إعلانات أدسنس باستخدام Chrome DevTools Protocol."""
    ad_url_patterns = [
        "*pagead2.googlesyndication.com*",
        "*googleads.g.doubleclick.net*",
        "*adservice.google.com*",
    ]
    
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ad_url_patterns})
        print("تمت تهيئة المتصفح بنجاح لحظر إعلانات أدسنس (AdSense).")
    except Exception as e:
        print(f"فشل إعداد حظر الإعلانات عبر CDP: {e}")


# --- دالة فتح GitHub في تاب جديد (ثلاث طرق مع تشخيص) ---
def open_github_in_new_tab(driver, github_url, wait):
    """محاولة فتح GitHub في تاب جديد بثلاث طرق مع لوج تشخيصي.
    ترجع True لو نجحت في فتح التاب والانتقال إليه، وإلا False."""
    print("محاولة فتح GitHub في تاب جديد — بدء سلسلة المحاولات.")
    try:
        orig_handles = driver.window_handles.copy()
    except Exception:
        orig_handles = []
    print("handles قبل الفتح:", orig_handles)

    # طريقة 1: استخدام window.open(url, '_blank')
    try:
        driver.execute_script("window.open(arguments[0], '_blank');", github_url)
        WebDriverWait(driver, 8).until(lambda d: len(d.window_handles) > len(orig_handles))
        new_handle = [h for h in driver.window_handles if h not in orig_handles][-1]
        driver.switch_to.window(new_handle)
        # ننتظر حتى تتغير URL أو يظهر عنوان الصفحة
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        print("نجح الفتح بالطريقة 1 (window.open). handles الآن:", driver.window_handles)
        return True
    except Exception as e1:
        print("الطريقة 1 فشلت:", repr(e1))
        try:
            print("handles بعد محاولة 1:", driver.window_handles)
        except Exception:
            pass

    # طريقة 2: استخدام Selenium 4 new_window (موثوقة أكثر)
    try:
        print("محاولة الفتح بالطريقة 2: driver.switch_to.new_window('tab') ...")
        # هذا الصيط يفتح تبويب جديد ويبدل إليه
        try:
            driver.switch_to.new_window('tab')
        except Exception as e_sw:
            # بعض إصدارات undetected_chromedriver قد لا تدعم هذه الطريقة؛ نطبع السبب
            print("switch_to.new_window فشل:", repr(e_sw))
            raise

        driver.get(github_url)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        print("نجح الفتح بالطريقة 2 (new_window). handles الآن:", driver.window_handles)
        return True
    except Exception as e2:
        print("الطريقة 2 فشلت:", repr(e2))
        try:
            print("handles بعد محاولة 2:", driver.window_handles)
        except Exception:
            pass

    # طريقة 3 (fallback): افتح في نفس التبويب كتشخيص — لنفهم إذا كان المشكلة في الفتح الفعلي للتبويب أو في الوصول للصفحة
    try:
        print("محاولة الفتح بالطريقة 3 (فتح في نفس التبويب لأغراض تشخيصية)...")
        driver.get(github_url)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        print("تم فتح GitHub في نفس التبويب (للتشخيص). current_url:", driver.current_url)
        return True
    except Exception as e3:
        print("الطريقة 3 فشلت أيضاً:", repr(e3))
        # اطبع مقتطف من مصدر الصفحة للمساعدة في التشخيص
        try:
            print("current_url:", driver.current_url)
            page_snippet = driver.page_source[:1000]
            print("Page source snippet (first 1000 chars):")
            print(page_snippet)
        except Exception as eprint:
            print("فشل في طباعة مصدر الصفحة:", repr(eprint))
        return False


def run_automation():
    driver = None
    try:
        # 1. إعداد المتصفح
        options = uc.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        driver = uc.Chrome(options=options)
        setup_ad_blocking(driver)
        wait = WebDriverWait(driver, 30)

        # 2. فتح Yopmail واستخراج اسم المستخدم والنقر على Check Inbox
        yopmail_url = "https://yopmail.com/en/email-generator"
        driver.get(yopmail_url)
        print("التبويب 1: تم فتح Yopmail.")

        email_display_element = wait.until(EC.visibility_of_element_located((By.ID, "egen")))
        full_generated_email = email_display_element.text
        generated_username = full_generated_email.split('@')[0]
        print(f"اسم المستخدم المستخرج من Yopmail: {generated_username}")

        check_inbox_button_selector = ".nw button:nth-child(3)"
        check_inbox_button = driver.find_element(By.CSS_SELECTOR, check_inbox_button_selector)
        check_inbox_button.click()
        print("تم النقر على 'Check Inbox'.")

        time.sleep(3) 
        
        driver.switch_to.window(driver.window_handles[0])
        print("تم التبديل إلى تبويب Yopmail (صندوق الوارد).")
        
        # 3. فتح تبويب جديد والتوجه إلى GitHub
        github_url = "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home"
        success = open_github_in_new_tab(driver, github_url, wait)
        if not success:
            print("فشل فتح GitHub. سأنهي التنفيذ.")
            return
        print("التبويب 2: تم فتح صفحة تسجيل GitHub في تاب جديد.")

        # 4. تحميل النطاقات وحلقة التحقق
        all_domains = load_domains(DOMAINS_FILE)
        if not all_domains:
            print("تحذير: قائمة النطاقات فارغة. لا يمكن المتابعة.")
            return

        chosen_domain = None
        while True:
            blacklist_domains = load_domains(BLACKLIST_FILE)
            candidate_domain = random.choice(all_domains)
            
            if candidate_domain in blacklist_domains:
                print(f"تخطي النطاق المحظور: {candidate_domain}")
                continue
            
            full_email = f"{generated_username}{candidate_domain}"
            
            email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_input.clear()
            email_input.send_keys(full_email)
            print(f"تم إدخال البريد الإلكتروني: {full_email}")

            try:
                driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[1]/div/h1").click()
                print("تم النقر على عنوان H1 لتحفيز التحقق.")
            except Exception as e:
                print(f"تحذير: فشل النقر على عنصر H1: {e}")
            
            time.sleep(2)
            
            error_selector = "//p[contains(text(), 'Email domain could not be verified')]"
            try:
                driver.find_element(By.XPATH, error_selector)
                append_domain_to_blacklist(candidate_domain)
                print(f"فشل التحقق: النطاق {candidate_domain} غير مقبول. إعادة المحاولة...")
            except NoSuchElementException:
                chosen_domain = candidate_domain
                print(f"نجح التحقق: النطاق {chosen_domain} مقبول.")
                break

        # 5. ملء باقي الحقول
        driver.find_element(By.ID, "password").send_keys("01205226167aA*qw")
        print("تم إدخال كلمة المرور.")
        random_login = generate_random_username()
        driver.find_element(By.ID, "login").send_keys(random_login)
        print(f"تم إدخال اسم المستخدم العشوائي: {random_login}")
        
        # 6. النقر على زر "Create account"
        create_account_button_selector = "div.js-octocaptcha-hide > button.signup-form-fields__button"
        create_account_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, create_account_button_selector)))
        create_account_button.click()
        print("تم النقر الأول على 'Create account'.")
        time.sleep(2)
        try:
            driver.find_element(By.CSS_SELECTOR, create_account_button_selector).click()
            print("تم النقر الثاني على 'Create account'.")
        except Exception:
            print("تحذير: ربما ظهر تحدي CAPTCHA.")

        # 7. التعامل مع تأكيد البريد الإلكتروني واستخراج الكود
        print("\n--- بدء خطوة تأكيد البريد الإلكتروني ---")
        
        # 7.1. انتظار صفحة "تأكيد البريد الإلكتروني" في GitHub
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Confirm your email address')]")))
            print("تم الوصول إلى صفحة 'Confirm your email address' في GitHub.")
        except TimeoutException:
            print("لم يتم الوصول لصفحة تأكيد البريد خلال 30 ثانية.")

        # 7.2. العودة إلى تبويب Yopmail
        driver.switch_to.window(driver.window_handles[0])
        print("تم العودة إلى تبويب Yopmail.")
        
        # 7.3. النقر على زر التحديث في Yopmail
        try:
            refresh_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#refresh")))
            actions = ActionChains(driver)
            actions.move_to_element(refresh_button).click_and_hold().release().perform()
            print("تم النقر على زر التحديث في Yopmail.")
            time.sleep(3)
        except TimeoutException:
            print("فشل العثور على زر التحديث في Yopmail.")

        # 7.4. التبديل إلى iframe والنقر على رسالة GitHub
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrinbox")))
            print("تم التبديل إلى iframe صندوق الوارد (ifrinbox).")
            github_email = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Your GitHub launch code')]")))
            github_email.click()
            print("تم النقر على رسالة GitHub.")
            driver.switch_to.default_content() # الخروج من iframe صندوق الوارد للتحضير للدخول إلى iframe الرسالة
        except TimeoutException:
            print("فشل العثور على iframe أو رسالة GitHub.")

        # 7.5. *** الجزء الجديد: استخراج الكود من iframe الرسالة ***
        verification_code = None
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
            print("تم التبديل إلى iframe محتوى الرسالة (ifmail).")

            # المحدد الذي قدمته لاستخراج الكود
            code_selector = "#mail > div > table > tbody > tr > td > center > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > span:nth-child(5)"
            code_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, code_selector)))
            
            verification_code = code_element.text.strip()
            print(f"تم استخراج كود التحقق بنجاح: {verification_code}")

            driver.switch_to.default_content() # الخروج من iframe الرسالة
        except TimeoutException:
            print("فشل في استخراج كود التحقق من الرسالة.")

        # 7.6. إدخال الكود في صفحة GitHub
        if verification_code:
            driver.switch_to.window(driver.window_handles[1])
            print("تم العودة إلى تبويب GitHub لإدخال الكود.")

            # إدخال الكود رقمًا برقم
            for i, digit in enumerate(verification_code):
                try:
                    input_field = driver.find_element(By.ID, f"launch-code-{i}")
                    input_field.send_keys(digit)
                except NoSuchElementException:
                    print(f"لم يتم العثور على حقل الإدخال رقم {i}")
                    break
            print("تم إدخال الكود بالكامل.")

            # 7.7. انتظار والنقر على زر التأكيد النهائي
            time.sleep(2)
            try:
                # المحدد الطويل الذي قدمته لزر التأكيد
                submit_button_selector = "body > div.logged-out.env-production.page-responsive.height-full.d-flex.flex-column.header-overlay > div.application-main.d-flex.flex-auto.flex-column > div > main > div > div.signups-rebrand__container-form.position-relative > div.d-flex.flex-justify-center.signups-rebrand__container-inner > react-partial > div > div > div:nth-child(1) > form > div:nth-child(4) > button"
                submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_selector)))
                submit_button.click()
                print("تم النقر على زر تأكيد الكود.")
            except TimeoutException:
                print("فشل العثور على زر تأكيد الكود أو النقر عليه.")


        # 8. انتظار إضافي للمشاهدة
        print("\nالاسكربت أكمل الخطوات المطلوبة. سيتم إغلاق المتصفح بعد 20 ثانية...")
        time.sleep(20)


    except TimeoutException:
        print("فشل بسبب انتهاء مهلة الانتظار (Timeout).")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
    finally:
        if driver:
            driver.quit()
            print("تم إغلاق المتصفح.")

if __name__ == "__main__":
    if not os.path.exists(DOMAINS_FILE):
        print(f"!! تنبيه: ملف {DOMAINS_FILE} غير موجود. جاري إنشاء ملف افتراضي.")
        with open(DOMAINS_FILE, 'w', encoding='utf-8') as f:
            f.write("@yopmail.com\n")
            
    run_automation()
