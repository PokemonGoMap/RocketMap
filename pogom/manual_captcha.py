import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

log = logging.getLogger(__name__)


def captcha_verifier(captcha_url, status):

    try:
        driver = webdriver.Chrome()
        driver.set_window_size(600, 600)
        driver.set_window_position(500, 300)
        driver.get("https://pgorelease.nianticlabs.com/")
        driver.get(captcha_url)
        ex_script = '''window.globalVariable = "Fail";
        var captchaPage = '<form action="?" method="POST"><div class="g-recaptcha" data-size="compact" data-sitekey="6LeeTScTAAAAADqvhqVMhPpr_vB9D364Ia-1dSgK" data-callback="captchaResponse"></form>';
        document.body.parentElement.innerHTML = captchaPage;
        var script = document.createElement('script');
        script.src = 'https://www.google.com/recaptcha/api.js?hl=en';
        script.type = 'text/javascript';
        document.getElementsByTagName('head')[0].appendChild(script);
        var script2 = document.createElement('script');
        script2.type = 'text/javascript';
        script2.text = 'function captchaResponse(str) {window.globalVariable = str;}'
        document.getElementsByTagName('head')[0].appendChild(script2);
        '''
        driver.execute_script(ex_script)
        try:
            WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element_value((By.ID, "g-recaptcha-response"), ""))
            captcha_token = driver.execute_script("return globalVariable;")
            driver.quit()
        except:
            try:
                driver.quit()
            except:
                status['message'] = 'Unable to close Chromedriver'
                log.warning(status['message'])
            status['message'] = 'ChromeDriver Has Timed Out'
            log.warning(status['message'])
            captcha_token = 'Fail'

        return captcha_token
    except:
        try:
            driver.quit()
        except:
            status['message'] = 'Unable to close Chromedriver'
            log.warning(status['message'])
        status['message'] = 'ChromeDriver was Closed, Retrying...'
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
