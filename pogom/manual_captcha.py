import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

log = logging.getLogger(__name__)


def captcha_verifier(captcha_url, status):
    try:
        chrome_options = Options()
        chrome_options.add_argument("window-size=600,600")
        chrome_options.add_argument("window-position=500,300")

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get("https://pgorelease.nianticlabs.com/")
        driver.get(captcha_url)

        ex_script = '''
        window._pgm_captcharesponse = "Fail";

        var captchaPage = '<form action="?" method="POST"><div class="g-recaptcha" data-size="compact" data-sitekey="6LeeTScTAAAAADqvhqVMhPpr_vB9D364Ia-1dSgK" data-callback="_pgm_onCaptchaResponse"></form>';

        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://www.google.com/recaptcha/api.js?hl=en';

        var script2 = document.createElement('script');
        script2.type = 'text/javascript';
        script2.text = 'function _pgm_onCaptchaResponse(str) {window._pgm_captcharesponse = str;}'

        document.body.parentElement.innerHTML = captchaPage;
        document.getElementsByTagName('head')[0].appendChild(script);
        document.getElementsByTagName('head')[0].appendChild(script2);
        '''

        driver.execute_script(ex_script)

        try:
            WebDriverWait(driver, 60).until(
                EC.text_to_be_present_in_element_value((By.ID, 'g-recaptcha-response'), ''))
            captcha_token = driver.execute_script(
                'return window._pgm_captcharesponse;')
            driver.quit()
        except:
            try:
                driver.quit()
            except:
                status['message'] = 'Unable to close ChromeDriver.'
                log.warning(status['message'])

            status['message'] = 'ChromeDriver has timed out.'
            log.warning(status['message'])

            captcha_token = 'Fail'

        return captcha_token
    except:
        try:
            driver.quit()
        except:
            status['message'] = 'Unable to close ChromeDriver.'
            log.warning(status['message'])

        status['message'] = 'ChromeDriver was closed, retrying...'
        log.warning(status['message'])

        captcha_token = captcha_verifier(captcha_url, status)
        return captcha_token


def chrome_verifier():
    try:
        driver = webdriver.Chrome()
        driver.quit()

        return True
    except:
        return False
