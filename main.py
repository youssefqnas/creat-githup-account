import time
import undetected_chromedriver as uc
import random
import string
import os
import sys
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# --- النطاق الثابت المطلوب استخدامه (بدلاً من الملفات الخارجية) ---
FIXED_DOMAIN = "@mesemails.fr.nf"
LOG_FILE = "automation_log.txt"

# --- دالة مخصصة للتسجيل في الملف والشاشة فوراً (Real-time Logging) ---
def log_message(message):
    """
    تسجيل الرسالة في ملف اللوغ وفي مخرجات الشاشة (stdout) فوراً.
    """
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    
    # الطباعة على الشاشة (Stdout) لـ Zeabur
    print(log_entry)
    sys.stdout.flush() 

    # الكتابة في ملف اللوغ
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        # إذا فشلت الكتابة في الملف، فقط نطبع الخطأ
        print(f"!! فشل كتابة اللوغ في الملف: {e}")
        sys.stdout.flush()


# --- دوال مساعدة ---

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
        log_message("تمت تهيئة المتصفح بنجاح لحظر إعلانات أدسنس (AdSense).")
    except Exception as e:
        log_message(f"فشل إعداد حظر الإعلانات عبر CDP: {e}")


# --- دالة فتح GitHub في تاب جديد (ثلاث طرق مع تشخيص) ---
def open_github_in_new_tab(driver, github_url, wait):
    """محاولة فتح GitHub في تاب جديد بثلاث طرق مع لوج تشخيصي."""
    log_message("محاولة فتح GitHub في تاب جديد — بدء سلسلة المحاولات.")
    try:
        orig_handles = driver.window_handles.copy()
    except Exception:
        orig_handles = []
    log_message(f"handles قبل الفتح: {orig_handles}")

    # طريقة 1: استخدام window.open(url, '_blank')
    try:
        driver.execute_script("window.open(arguments[0], '_blank');", github_url)
        WebDriverWait(driver, 8).until(lambda d: len(d.window_handles) > len(orig_handles))
        new_handle = [h for h in driver.window_handles if h not in orig_handles][-1]
        driver.switch_to.window(new_handle)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        log_message(f"نجح الفتح بالطريقة 1 (window.open). handles الآن: {driver.window_handles}")
        return True
    except Exception as e1:
        log_message(f"الطريقة 1 فشلت: {repr(e1)}")

    # طريقة 2: استخدام Selenium 4 new_window
    try:
        log_message("محاولة الفتح بالطريقة 2: driver.switch_to.new_window('tab') ...")
        try:
            driver.switch_to.new_window('tab')
        except Exception as e_sw:
            log_message(f"switch_to.new_window فشل: {repr(e_sw)}")
            raise

        driver.get(github_url)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        log_message(f"نجح الفتح بالطريقة 2 (new_window). handles الآن: {driver.window_handles}")
        return True
    except Exception as e2:
        log_message(f"الطريقة 2 فشلت: {repr(e2)}")

    # طريقة 3 (fallback): افتح في نفس التبويب كتشخيص
    try:
        log_message("محاولة الفتح بالطريقة 3 (فتح في نفس التبويب لأغراض تشخيصية)...")
        driver.get(github_url)
        WebDriverWait(driver, 15).until(lambda d: "github.com" in d.current_url or d.title != "")
        log_message(f"تم فتح GitHub في نفس التبويب (للتشخيص). current_url: {driver.current_url}")
        return True
    except Exception as e3:
        log_message(f"الطريقة 3 فشلت أيضاً: {repr(e3)}")
        return False


def run_automation():
    driver = None
    try:
        # 1. إعداد المتصفح (تعديلات Docker/Zeabur)
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
        
        # إعداد المتصفح: السماح لـ undetected_chromedriver بتحديد مكان متصفح Chromium
        log_message("تم إعداد وسائط المتصفح بنجاح، جاري بدء تشغيل السيلينيوم.")
        
        chrome_exec_path = uc.find_chrome_executable()
        if not chrome_exec_path:
             # إذا لم يجده uc، نحدد المسار الشائع لـ Chromium يدوياً
            chrome_exec_path = '/usr/bin/chromium' 
        
        log_message(f"مسار متصفح كروم المحدد: {chrome_exec_path}")
        
        driver = uc.Chrome(
            options=options, 
            browser_executable_path=chrome_exec_path # توجيه uc إلى المتصفح نفسه
        )
        
        setup_ad_blocking(driver)
        wait = WebDriverWait(driver, 30)

        # 2. فتح Yopmail واستخراج اسم المستخدم والنقر على Check Inbox
        yopmail_url = "https://yopmail.com/en/email-generator"
        driver.get(yopmail_url)
        log_message("التبويب 1: تم فتح Yopmail.")

        email_display_element = wait.until(EC.visibility_of_element_located((By.ID, "egen")))
        full_generated_email = email_display_element.text
        generated_username = full_generated_email.split('@')[0]
        log_message(f"اسم المستخدم المستخرج من Yopmail: {generated_username}")

        check_inbox_button_selector = ".nw button:nth-child(3)"
        check_inbox_button = driver.find_element(By.CSS_SELECTOR, check_inbox_button_selector)
        check_inbox_button.click()
        log_message("تم النقر على 'Check Inbox'.")

        time.sleep(3) 
        
        driver.switch_to.window(driver.window_handles[0])
        log_message("تم التبديل إلى تبويب Yopmail (صندوق الوارد).")
        
        # 3. فتح تبويب جديد والتوجه إلى GitHub
        github_url = "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home"
        success = open_github_in_new_tab(driver, github_url, wait)
        if not success:
            log_message("فشل فتح GitHub. سأنهي التنفيذ.")
            return
        log_message("التبويب 2: تم فتح صفحة تسجيل GitHub في تاب جديد.")

        # 4. استخدام النطاق الثابت والتحقق منه لمرة واحدة
        chosen_domain = FIXED_DOMAIN
        full_email = f"{generated_username}{chosen_domain}"
        log_message(f"سيتم استخدام البريد الإلكتروني الثابت: {full_email}")

        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.clear()
        email_input.send_keys(full_email)
        log_message(f"تم إدخال البريد الإلكتروني: {full_email}")

        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[1]/div/h1").click()
            log_message("تم النقر على عنوان H1 لتحفيز التحقق.")
        except Exception as e:
            log_message(f"تحذير: فشل النقر على عنصر H1: {e}")
        
        time.sleep(2)
        
        error_selector = "//p[contains(text(), 'Email domain could not be verified')]"
        try:
            driver.find_element(By.XPATH, error_selector)
            log_message(f"فشل التحقق: النطاق الثابت {chosen_domain} غير مقبول من GitHub. سأنهي التنفيذ.")
            return
        except NoSuchElementException:
            log_message(f"نجح التحقق: النطاق الثابت {chosen_domain} مقبول.")


        # 5. ملء باقي الحقول
        driver.find_element(By.ID, "password").send_keys("01205226167aA*qw")
        log_message("تم إدخال كلمة المرور.")
        random_login = generate_random_username()
        driver.find_element(By.ID, "login").send_keys(random_login)
        log_message(f"تم إدخال اسم المستخدم العشوائي: {random_login}")
        
        # 6. النقر على زر "Create account"
        create_account_button_selector = "div.js-octocaptcha-hide > button.signup-form-fields__button"
        create_account_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, create_account_button_selector)))
        create_account_button.click()
        log_message("تم النقر الأول على 'Create account'.")
        time.sleep(2)
        try:
            driver.find_element(By.CSS_SELECTOR, create_account_button_selector).click()
            log_message("تم النقر الثاني على 'Create account'.")
        except Exception:
            log_message("تحذير: ربما ظهر تحدي CAPTCHA بعد النقرة الأولى، أو أن النقرة الثانية لم تكن ضرورية.")

        # 7. التعامل مع تأكيد البريد الإلكتروني واستخراج الكود
        log_message("\n--- بدء خطوة تأكيد البريد الإلكتروني ---")
        
        # 7.1. انتظار صفحة "تأكيد البريد الإلكتروني" في GitHub
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Confirm your email address')]")))
            log_message("تم الوصول إلى صفحة 'Confirm your email address' في GitHub.")
            time.sleep(10)
        except TimeoutException:
            log_message("لم يتم الوصول لصفحة تأكيد البريد خلال 30 ثانية.")

        # 7.2. العودة إلى تبويب Yopmail
        driver.switch_to.window(driver.window_handles[0])
        log_message("تم العودة إلى تبويب Yopmail.")
        
        # 7.3. النقر على زر التحديث في Yopmail
        try:
            refresh_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#refresh")))
            actions = ActionChains(driver)
            actions.move_to_element(refresh_button).click_and_hold().release().perform()
            log_message("تم النقر على زر التحديث في Yopmail.")
            time.sleep(3)
        except TimeoutException:
            log_message("فشل العثور على زر التحديث في Yopmail.")

        # 7.4. التبديل إلى iframe صندوق الوارد والنقر على رسالة GitHub
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrinbox")))
            log_message("تم التبديل إلى iframe صندوق الوارد (ifrinbox).")
            github_email = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Your GitHub launch code')]")))
            github_email.click()
            log_message("تم النقر على رسالة GitHub.")
            driver.switch_to.default_content()
        except TimeoutException:
            log_message("فشل العثور على iframe أو رسالة GitHub.")

        # 7.5. استخراج الكود من iframe الرسالة
        verification_code = None
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
            log_message("تم التبديل إلى iframe محتوى الرسالة (ifmail).")

            code_selector = "#mail > div > table > tbody > tr > td > center > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > span:nth-child(5)"
            code_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, code_selector)))
            
            verification_code = code_element.text.strip()
            log_message(f"تم استخراج كود التحقق بنجاح: {verification_code}")

            driver.switch_to.default_content()
        except TimeoutException:
            log_message("فشل في استخراج كود التحقق من الرسالة.")

        # 7.6. إدخال الكود في صفحة GitHub
        if verification_code and verification_code.isdigit() and len(verification_code) == 6:
            driver.switch_to.window(driver.window_handles[1])
            log_message("تم العودة إلى تبويب GitHub لإدخال الكود.")

            for i, digit in enumerate(verification_code):
                try:
                    input_field = driver.find_element(By.ID, f"launch-code-{i}")
                    input_field.send_keys(digit)
                except NoSuchElementException:
                    log_message(f"لم يتم العثور على حقل الإدخال رقم {i}")
                    break
            log_message("تم إدخال الكود بالكامل.")

            # 7.7. انتظار والنقر على زر التأكيد النهائي
            time.sleep(2)
            try:
                submit_button_selector = "body > div.logged-out.env-production.page-responsive.height-full.d-flex.flex-column.header-overlay > div.application-main.d-flex.flex-auto.flex-column > div > main > div > div.signups-rebrand__container-form.position-relative > div.d-flex.flex-justify-center.signups-rebrand__container-inner > react-partial > div > div > div:nth-child(1) > form > div:nth-child(4) > button"
                submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_selector)))
                submit_button.click()
                log_message("تم النقر على زر تأكيد الكود.")
            except TimeoutException:
                log_message("فشل العثور على زر تأكيد الكود أو النقر عليه.")

        else:
            log_message("فشل عملية إدخال الكود: لم يتم استخراج كود صالح (ليس 6 أرقام).")


        # 8. انتظار إضافي للمشاهدة
        log_message("\nالاسكربت أكمل الخطوات المطلوبة. سيتم إغلاق المتصفح بعد 20 ثانية...")
        time.sleep(20)


    except TimeoutException:
        log_message("فشل بسبب انتهاء مهلة الانتظار (Timeout).")
    except Exception as e:
        log_message(f"حدث خطأ غير متوقع: {e}")
    finally:
        if driver:
            driver.quit()
            log_message("تم إغلاق المتصفح.")

if __name__ == "__main__":
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*50 + "\n")
            f.write(f"بدء تشغيل السكربت في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n")
    except Exception:
        pass
    
    run_automation()
