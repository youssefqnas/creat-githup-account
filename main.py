import time
import undetected_chromedriver as uc
import random
import string
import logging 
import re # مكتبة للتعامل مع التعبيرات النمطية (لاستخراج الكود)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# --- النطاق الثابت المطلوب ---
FIXED_DOMAIN = "@mymail.infos.st"

# تهيئة التسجيل (Log) ليظهر في السجلات
# هذا يضمن أن الرسائل ستظهر في سجلات Zeabur بشكل منظم
logging.basicConfig(
    level=logging.INFO, # ابدأ من مستوى INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

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
        logging.info("تمت تهيئة المتصفح بنجاح لحظر إعلانات أدسنس (AdSense).")
    except Exception as e:
        logging.warning(f"فشل إعداد حظر الإعلانات عبر CDP: {e}")


# --- دالة فتح GitHub في تاب جديد (طريقة مبسطة ومحسّنة) ---
def open_github_in_new_tab(driver, github_url, wait):
    """
    تحاول فتح GitHub في تاب جديد والانتقال إليه عبر JavaScript.
    ترجع True لو نجحت في فتح التاب والانتقال إليه، وإلا False.
    """
    logging.info("بدء محاولة فتح GitHub في تاب جديد عبر JavaScript.")
    original_window = driver.current_window_handle
    initial_handles = set(driver.window_handles)
    
    # الطريقة 1: استخدام window.open() لفتح تاب جديد
    try:
        logging.info("محاولة: window.open(url, '_blank')")
        driver.execute_script("window.open(arguments[0], '_blank');", github_url)
        
        # الانتظار حتى يظهر مقبض نافذة جديد
        wait.until(EC.number_of_windows_to_be(len(initial_handles) + 1))
        
        # تحديد المقبض الجديد والتبديل إليه
        new_handle = [h for h in driver.window_handles if h not in initial_handles][-1]
        driver.switch_to.window(new_handle)
        
        # التأكد من أن العنوان قد تم تحميله بنجاح
        wait.until(lambda d: "github.com" in d.current_url or d.title != "")
        logging.info("نجحت طريقة window.open(). تم التبديل إلى التاب الجديد.")
        return True
        
    except TimeoutException:
        logging.warning("فشل: انتهت مهلة الانتظار لظهور التاب الجديد أو تحميل GitHub.")
        # نحاول العودة إلى التاب الأصلي وتنظيف الوضع
        try:
            driver.switch_to.window(original_window)
        except:
            pass
        return False
    except Exception as e:
        logging.error(f"فشل غير متوقع أثناء فتح التاب الجديد: {repr(e)}")
        # نحاول العودة إلى التاب الأصلي وتنظيف الوضع
        try:
            driver.switch_to.window(original_window)
        except:
            pass
        return False


def run_automation():
    driver = None
    try:
        # 1. إعداد المتصفح
        options = uc.ChromeOptions()
        
        # وسائط تحسين الأداء في بيئات الحاوية
        options.add_argument("headless-new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")

        # مسار Chrome/Chromium الثابت داخل حاوية Docker (يتطلب Dockerfile معدل)
        chrome_binary_path = '/usr/bin/google-chrome' 
        
        logging.info("بدء تشغيل undetected_chromedriver...")
        # تأكد من استخدام browser_executable_path
        driver = uc.Chrome(options=options, browser_executable_path=chrome_binary_path)
        setup_ad_blocking(driver)
        wait = WebDriverWait(driver, 30)

        # 2. فتح Yopmail واستخراج اسم المستخدم والنقر على Check Inbox
        yopmail_url = "https://yopmail.com/en/email-generator"
        driver.get(yopmail_url)
        logging.info("التبويب 1: تم فتح Yopmail.")

        email_display_element = wait.until(EC.visibility_of_element_located((By.ID, "egen")))
        full_generated_email = email_display_element.text
        generated_username = full_generated_email.split('@')[0]
        logging.info(f"اسم المستخدم المستخرج من Yopmail: {generated_username}")

        check_inbox_button_selector = ".nw button:nth-child(3)"
        check_inbox_button = driver.find_element(By.CSS_SELECTOR, check_inbox_button_selector)
        check_inbox_button.click()
        logging.info("تم النقر على 'Check Inbox'.")

        time.sleep(3) 
        
        # يُفترض أن الصندوق الوارد هو الآن في التبويب الأول
        driver.switch_to.window(driver.window_handles[0])
        logging.info("تم التبديل إلى تبويب Yopmail (صندوق الوارد).")
        
        # 3. فتح تبويب جديد والتوجه إلى GitHub
        github_url = "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home"
        success = open_github_in_new_tab(driver, github_url, wait)
        if not success:
            logging.error("فشل فتح GitHub. سأنهي التنفيذ.")
            return
        logging.info("التبويب 2: تم فتح صفحة تسجيل GitHub في تاب جديد.")

        # 4. إدخال البريد الإلكتروني بالنطاق الثابت المطلوب
        
        chosen_domain = FIXED_DOMAIN
        full_email = f"{generated_username}{chosen_domain}"
        
        # العثور على حقل البريد الإلكتروني في تبويب GitHub (التبويب 2)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.clear()
        email_input.send_keys(full_email)
        logging.info(f"تم إدخال البريد الإلكتروني بالنطاق الثابت: {full_email}")

        try:
            # النقر لتحفيز التحقق من صحة النطاق
            driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[1]/div/h1").click()
            logging.info("تم النقر على عنوان H1 لتحفيز التحقق.")
        except Exception as e:
            logging.warning(f"تحذير: فشل النقر على عنصر H1: {e}")
        
        time.sleep(2)
        logging.info("تم استخدام النطاق الثابت. تم تخطي حلقة التحقق من النطاق الخارجي.")


        # 5. ملء باقي الحقول
        driver.find_element(By.ID, "password").send_keys("01205226167aA*qw")
        logging.info("تم إدخال كلمة المرور.")
        random_login = generate_random_username()
        driver.find_element(By.ID, "login").send_keys(random_login)
        logging.info(f"تم إدخال اسم المستخدم العشوائي: {random_login}")
        
        # 6. النقر على زر "Create account"
        create_account_button_selector = "div.js-octocaptcha-hide > button.signup-form-fields__button"
        create_account_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, create_account_button_selector)))
        create_account_button.click()
        logging.info("تم النقر الأول على 'Create account'.")
        time.sleep(2)
        try:
            # قد تكون هناك حاجة لنقرة ثانية أو أن النقرة الأولى تظهر حقل CAPTCHA
            driver.find_element(By.CSS_SELECTOR, create_account_button_selector).click()
            logging.info("تم النقر الثاني على 'Create account'.")
        except Exception:
            logging.warning("تحذير: ربما ظهر تحدي CAPTCHA بعد النقرة الأولى، أو أن النقرة الثانية لم تكن ضرورية.")

        # 7. التعامل مع تأكيد البريد الإلكتروني واستخراج الكود
        logging.info("\n--- بدء خطوة تأكيد البريد الإلكتروني ---")
        
        # 7.1. انتظار صفحة "تأكيد البريد الإلكتروني" في GitHub
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Confirm your email address')]")))
            logging.info("تم الوصول إلى صفحة 'Confirm your email address' في GitHub.")
            time.sleep(10) # انتظار لوصول البريد
        except TimeoutException:
            logging.error("لم يتم الوصول لصفحة تأكيد البريد خلال 30 ثانية.")

        # 7.2. العودة إلى تبويب Yopmail
        driver.switch_to.window(driver.window_handles[0])
        logging.info("تم العودة إلى تبويب Yopmail.")
        
        # 7.3. النقر على زر التحديث في Yopmail
        try:
            refresh_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#refresh")))
            actions = ActionChains(driver)
            actions.move_to_element(refresh_button).click_and_hold().release().perform()
            logging.info("تم النقر على زر التحديث في Yopmail.")
            time.sleep(3)
        except TimeoutException:
            logging.error("فشل العثور على زر التحديث في Yopmail.")

        # 7.4. التبديل إلى iframe صندوق الوارد والنقر على رسالة GitHub
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrinbox")))
            logging.info("تم التبديل إلى iframe صندوق الوارد (ifrinbox).")
            
            # محدد أكثر مرونة للرسالة
            github_email = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'GitHub') or contains(text(), 'launch code')]")))
            github_email.click()
            logging.info("تم النقر على رسالة GitHub.")
            driver.switch_to.default_content() # الخروج من iframe صندوق الوارد
            
        except TimeoutException:
            logging.error("فشل العثور على iframe صندوق الوارد أو رسالة GitHub بعد محاولة التحديث. إنهاء العملية.")
            driver.switch_to.default_content()
            return
        
        # 7.5. استخراج الكود من iframe الرسالة
        # 7.5. استخراج الكود من iframe الرسالة
        verification_code = None
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
            logging.info("تم التبديل إلى iframe محتوى الرسالة (ifmail).")

            # المحدد لاستخراج الكود (يجب أن يكون رقماً مكوناً من 6 خانات)
            code_selector = "#mail > div > table > tbody > tr > td > center > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > span:nth-child(5)"
            code_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, code_selector)))
            
            verification_code = code_element.text.strip()
            logging.info(f"تم استخراج كود التحقق بنجاح: {verification_code}")

            driver.switch_to.default_content() # الخروج من iframe الرسالة
        except TimeoutException:
            logging.error("فشل في استخراج كود التحقق من الرسالة.")

        # 7.6. إدخال الكود في صفحة GitHub
        if verification_code and verification_code.isdigit() and len(verification_code) == 8:
            driver.switch_to.window(driver.window_handles[1]) # تبديل لتبويب GitHub
            logging.info("تم العودة إلى تبويب GitHub لإدخال الكود.")

            # إدخال الكود رقمًا برقم في حقول الإدخال الستة
            for i, digit in enumerate(verification_code):
                try:
                    input_field = driver.find_element(By.ID, f"launch-code-{i}")
                    input_field.send_keys(digit)
                except NoSuchElementException:
                    logging.error(f"لم يتم العثور على حقل الإدخال رقم {i}")
                    break
            logging.info("تم إدخال الكود بالكامل.")

            # 7.7. انتظار والنقر على زر التأكيد النهائي
            time.sleep(2)
            try:
                # المحدد لزر التأكيد بعد إدخال الكود
                submit_button_selector = "body > div.logged-out.env-production.page-responsive.height-full.d-flex.flex-column.header-overlay > div.application-main.d-flex.flex-auto.flex-column > div > main > div > div.signups-rebrand__container-form.position-relative > div.d-flex.flex-justify-center.signups-rebrand__container-inner > react-partial > div > div > div:nth-child(1) > form > div:nth-child(4) > button"
                submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_selector)))
                submit_button.click()
                logging.info("تم النقر على زر تأكيد الكود.")
            except TimeoutException:
                logging.error("فشل العثور على زر تأكيد الكود أو النقر عليه.")

        else:
            logging.error("فشل عملية إدخال الكود: لم يتم استخراج كود صالح (ليس 6 أرقام).")


        # 8. انتظار إضافي للمشاهدة
        logging.info("\nالاسكربت أكمل الخطوات المطلوبة. سيتم إغلاق المتصفح بعد 20 ثانية...")
        time.sleep(20)


    except TimeoutException:
        logging.error("فشل بسبب انتهاء مهلة الانتظار (Timeout).")
    except Exception as e:
        logging.exception(f"حدث خطأ غير متوقع: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("تم إغلاق المتصفح.")

if __name__ == "__main__":
    run_automation()



