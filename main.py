import time
import random
import string
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- النطاق الثابت (Fixed Domain) ---
FIXED_DOMAIN = "@webclub.infos.st"
# تم حذف DOMAINS_FILE و BLACKLIST_FILE
# وتم حذف الدوال load_domains و append_domain_to_blacklist

# --- دوال مساعدة ---
def generate_random_username(length=10):
    """توليد اسم مستخدم عشوائي يتكون من حروف وأرقام."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def setup_ad_blocking(context):
    """تكوين سياق المتصفح (Context) لحظر طلبات إعلانات أدسنس باستخدام context.route."""
    ad_url_patterns = [
        "**pagead2.googlesyndication.com**",
        "**googleads.g.doubleclick.net**",
        "**adservice.google.com**",
    ]
    
    try:
        for pattern in ad_url_patterns:
            # اعتراض وإلغاء طلبات الإعلانات
            context.route(pattern, lambda route: route.abort())
        print("تمت تهيئة المتصفح بنجاح لحظر إعلانات أدسنس (AdSense).")
    except Exception as e:
        print(f"فشل إعداد حظر الإعلانات عبر context.route: {e}")


def run_automation():
    # استخدام sync_playwright لضمان التنفيذ المتزامن
    with sync_playwright() as p:
        # تعريف المتغيرات قبل try/except لضمان إغلاقها في النهاية
        browser = None
        
        try:
            # 1. إعداد المتصفح
            browser = p.chromium.launch(headless=True, args=['--start-maximized'])
            
            # إنشاء سياق متصفح (Browser Context)
            context = browser.new_context(
                ignore_https_errors=True,
                viewport={"width": 1920, "height": 1080}
            )
            
            # إعداد حظر الإعلانات على مستوى السياق
            setup_ad_blocking(context)
            
            # 2. فتح Yopmail في التبويب الأول (page)
            yopmail_page = context.new_page()
            yopmail_url = "https://yopmail.com/en/email-generator"
            yopmail_page.goto(yopmail_url)
            print("التبويب 1: تم فتح Yopmail.")

            # استخدام locator.inner_text() للانتظار والحصول على النص
            email_display_locator = yopmail_page.locator("#egen")
            email_display_locator.wait_for(state="visible", timeout=30000)
            full_generated_email = email_display_locator.inner_text()
            generated_username = full_generated_email.split('@')[0]
            print(f"اسم المستخدم المستخرج من Yopmail: {generated_username}")

            # النقر على Check Inbox
            check_inbox_button_selector = ".nw button:nth-child(3)"
            yopmail_page.click(check_inbox_button_selector)
            print("تم النقر على 'Check Inbox'.")

            # 3. فتح تبويب جديد والتوجه إلى GitHub
            github_page = context.new_page()
            github_url = "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home"
            github_page.goto(github_url)
            
            # انتظار تحميل صفحة GitHub
            github_page.wait_for_selector("#email", timeout=30000)
            print("التبويب 2: تم فتح صفحة تسجيل GitHub في تاب جديد.")

            # 4. إدخال البريد الإلكتروني الثابت والتحقق منه
            
            chosen_domain = FIXED_DOMAIN
            full_email = f"{generated_username}{chosen_domain}"
            
            email_input_selector = "#email"
            github_page.fill(email_input_selector, full_email)
            print(f"تم إدخال البريد الإلكتروني الثابت: {full_email}")

            try:
                # تحفيز التحقق - النقر على عنوان H1 (أو يمكن استخدام page.press(selector, 'Tab'))
                github_page.click("h1")
                print("تم النقر على عنوان H1 لتحفيز التحقق.")
            except Exception as e:
                print(f"تحذير: فشل النقر على عنصر H1: {e}")
            
            time.sleep(2) # الانتظار قليلاً للتحقق من النص
            
            error_selector = "text=Email domain could not be verified"
            
            # التحقق مما إذا كان نص الخطأ مرئيًا
            if github_page.locator(error_selector).is_visible(timeout=5000):
                # إذا ظهر الخطأ، نتوقف لأنه لا توجد نطاقات بديلة
                print(f"فشل التحقق: النطاق {chosen_domain} غير مقبول من قبل GitHub. سأتوقف هنا.")
                return
            else:
                print(f"نجح التحقق: النطاق {chosen_domain} مقبول.")

            # 5. ملء باقي الحقول
            github_page.fill("#password", "01205226167aA*qw")
            print("تم إدخال كلمة المرور.")
            random_login = generate_random_username()
            github_page.fill("#login", random_login)
            print(f"تم إدخال اسم المستخدم العشوائي: {random_login}")
            
            # 6. النقر على زر "Create account"
            create_account_button_selector = "div.js-octocaptcha-hide > button.signup-form-fields__button"
            github_page.click(create_account_button_selector)
            print("تم النقر الأول على 'Create account'.")
            
            time.sleep(2)
            try:
                # محاولة النقر الثاني (كما في الكود الأصلي)
                github_page.click(create_account_button_selector, timeout=5000)
                print("تم النقر الثاني على 'Create account' (إذا لزم الأمر).")
            except PlaywrightTimeoutError:
                print("تحذير: ربما ظهر تحدي CAPTCHA أو تم الانتقال للصفحة التالية مباشرة.")


            # 7. التعامل مع تأكيد البريد الإلكتروني واستخراج الكود
            print("\n--- بدء خطوة تأكيد البريد الإلكتروني ---")
            
            # 7.1. انتظار صفحة "تأكيد البريد الإلكتروني" في GitHub
            try:
                github_page.wait_for_selector("text=Confirm your email address", timeout=30000)
                print("تم الوصول إلى صفحة 'Confirm your email address' في GitHub.")
                time.sleep(5) # انتظار إضافي لوصول البريد
            except PlaywrightTimeoutError:
                print("لم يتم الوصول لصفحة تأكيد البريد خلال 30 ثانية. (تحقق من CAPTCHA)")

            # 7.2. العودة إلى تبويب Yopmail
            yopmail_page.bring_to_front()
            print("تم العودة إلى تبويب Yopmail.")
            
            # 7.3. النقر على زر التحديث في Yopmail
            try:
                yopmail_page.click("#refresh", timeout=10000)
                print("تم النقر على زر التحديث في Yopmail.")
                time.sleep(3)
            except PlaywrightTimeoutError:
                print("فشل العثور على زر التحديث في Yopmail.")

            # 7.4. التبديل إلى iframe والنقر على رسالة GitHub
            try:
                # استخدام page.frame_locator للتعامل مع iframe صندوق الوارد
                inbox_frame = yopmail_page.frame_locator("#ifrinbox")
                # النقر على الرسالة
                github_email_locator = inbox_frame.locator("div:has-text('Your GitHub launch code')")
                github_email_locator.click(timeout=10000)
                print("تم النقر على رسالة GitHub.")
            except PlaywrightTimeoutError:
                print("فشل العثور على iframe أو رسالة GitHub.")

            # 7.5. استخراج الكود من iframe الرسالة
            verification_code = None
            try:
                # التبديل إلى iframe محتوى الرسالة
                mail_frame = yopmail_page.frame_locator("#ifmail")
                print("تم التبديل إلى iframe محتوى الرسالة (ifmail).")

                # المحدد الذي قدمته لاستخراج الكود
                code_selector = "#mail > div > table > tbody > tr > td > center > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > span:nth-child(5)"
                
                # استخدام inner_text للحصول على النص مباشرة
                code_locator = mail_frame.locator(code_selector)
                code_locator.wait_for(state="visible", timeout=15000)
                
                verification_code = code_locator.inner_text().strip()
                print(f"تم استخراج كود التحقق بنجاح: {verification_code}")

            except PlaywrightTimeoutError:
                print("فشل في استخراج كود التحقق من الرسالة.")

            # 7.6. إدخال الكود في صفحة GitHub
            if verification_code:
                github_page.bring_to_front()
                print("تم العودة إلى تبويب GitHub لإدخال الكود.")

                # إدخال الكود رقمًا برقم
                for i, digit in enumerate(verification_code):
                    try:
                        input_field_selector = f"#launch-code-{i}"
                        github_page.fill(input_field_selector, digit, timeout=5000)
                    except PlaywrightTimeoutError:
                        print(f"لم يتم العثور على حقل الإدخال رقم {i} أو انتهت المهلة.")
                        break
                print("تم إدخال الكود بالكامل.")

                # 7.7. النقر على زر التأكيد النهائي
                time.sleep(2)
                try:
                    submit_button_selector = "body > div.logged-out.env-production.page-responsive.height-full.d-flex.flex-column.header-overlay > div.application-main.d-flex.flex-auto.flex-column > div > main > div > div.signups-rebrand__container-form.position-relative > div.d-flex.flex-justify-center.signups-rebrand__container-inner > react-partial > div > div > div:nth-child(1) > form > div:nth-child(4) > button"
                    github_page.click(submit_button_selector, timeout=10000)
                    print("تم النقر على زر تأكيد الكود.")
                except PlaywrightTimeoutError:
                    print("فشل العثور على زر تأكيد الكود أو النقر عليه.")


            # 8. انتظار إضافي للمشاهدة
            print("\nالاسكربت أكمل الخطوات المطلوبة. سيتم إغلاق المتصفح بعد 20 ثانية...")
            time.sleep(20)


        except PlaywrightTimeoutError:
            print("فشل بسبب انتهاء مهلة الانتظار (Timeout).")
        except Exception as e:
            print(f"حدث خطأ غير متوقع: {e}")
        finally:
            if browser:
                browser.close()
                print("تم إغلاق المتصفح.")

if __name__ == "__main__":
    run_automation()