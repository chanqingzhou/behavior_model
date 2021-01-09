from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
import time
import lxml.html as LH
import lxml.html.clean as clean
import tldextract
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys


def clean_domain(domain, deletechars='\/:*?"<>|'):
    for c in deletechars:
        domain = domain.replace(c, '')
    return domain[:30]

class State:
    def __init__(self, driver, start_url):
        self.password = None
        self.username = None
        self.captcha = None
        self.error = None
        self.visible_text = []
        self.current_url = None
        self.link = 0 # 0 - no link, 1 - link, 2- unsure, either javasript or #
        self.final = None
        self.driver = driver
        self.start_url = start_url
        self.redirect = None


    def update_link(self):
        domain = tldextract.extract(self.start_url).domain
        paths = self.driver.find_elements_by_xpath('.//a')
        for path in paths:
            try:
                path_url = path.get_attribute('href')
                if path_url[:4] == 'http':
                    path_domain = tldextract.extract(path_url).domain
                    if path_domain == domain:
                        self.link = 1
                        break
                else:
                    if path_url.startswith('javascript') or path_url == '#':
                        self.link = 2

            except Exception as e:
                print("unable to find path")

    def update_password(self, password):
        self.password = password

    def update_username(self, username):
        self.username = username

    def update_captcha(self):
        pass

    def update_url(self):
        self.current_url = self.driver.current_url
        start_domain = tldextract.extract(self.start_url).domain
        domain = tldextract.extract(self.current_url).domain
        if start_domain != domain:
            self.redirect = 1

    def update_error(self):
        error_words = ['incorrect', 'error', 'can\'t find', 'does not exist', 'dosen\'t exist', 'cannot find',
                       'not exist', 'try again', 'not found', '403 forbidden', '404']

        page_text = self.driver.find_element_by_tag_name('body').text
        self.visible_text = page_text.split('\n')
        for i in self.visible_text:
            word = i.lower()
            for test in error_words:
                if test in word:
                    print(word)
                    self.error = word
                    break

    def update_all(self, username, password):
        self.update_captcha()
        self.update_error()
        self.update_link()
        self.update_username(username)
        self.update_password(password)
        self.update_url()

        if (not self.username and not self.password) or self.captcha or self.redirect:
            self.final = 1

    def is_final(self):
        return self.final

    def __str__(self):
        return "user:{} , password:{}, captcha:{},error:{}, link:{}, url:{}, final:{}".format(str(self.username), str(self.password), str(self.captcha), str(self.error), str(self.link), self.current_url, str(self.final))


class WebsiteTester:
    def __init__(self, url, prefs):
        options = webdriver.ChromeOptions()
        capabilities = DesiredCapabilities.CHROME
        # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
        options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities, chrome_options=options)

        self.driver = driver
        self.url = url
        self.email = 'test123123@gmail.com'
        self.password = 'arekrewa'

    def find_username_password(self):
        elements = self.driver.find_elements_by_xpath('.//input')

        possible_users = []
        possible_passwords = []
        other_inputs = []
        # we first look at labels
        username_keywords = ['user','mail', 'login', 'id', 'account', 'number']
        password_keywords = ['pass', 'pin']

        for ele in elements:
            id = ele.get_attribute('id')
            try:
                label = self.driver.find_element_by_xpath('.//label[@for="{}"]'.format(id))
            except Exception:
                continue
            if label:
                done = False
                txt = label.text.lower()
                for keyword in username_keywords:
                    if keyword in txt:
                        possible_users.append(ele)
                        done = True
                        break
                if done:
                    continue

                for keyword in password_keywords:
                    if keyword in txt:
                        possible_passwords.append(ele)
                        break

        # match htrl
        print(possible_passwords)
        print(possible_users)
        if not possible_passwords or not possible_users:
            for ele in elements:
                done = False
                txt = ele.get_attribute('outerHTML').lower()
                for keyword in username_keywords:
                    if keyword in txt:
                        possible_users.append(ele)
                        done = True
                        break
                if done:
                    continue
                for keyword in password_keywords:
                    if keyword in txt:
                        possible_passwords.append(ele)
                        break
        for i in elements:
            if i not in possible_passwords and i not in possible_users:
                other_inputs.append(i)
        return possible_users, possible_passwords, other_inputs

    def try_submit(self):
        logs = self.driver.get_log("performance")
        logs = self.driver.get_log("performance")
        assert(len(logs) == 0)
        buttons = self.driver.find_elements_by_xpath('.//button|.//input')
        #maybe can use dom tree to find cloest element or smth
        for button in buttons:
            if (button.get_attribute('type') == 'submit' or button.get_attribute('type') =='image') and \
                button.is_displayed() and button.is_enabled():
                try:
                    button.click()
                    time.sleep(2)
                    if len(self.driver.get_log("performance")) > 0:
                        return True
                except Exception as e:
                    continue

    def test_site(self):
        self.driver.get(self.url)
        time.sleep(3)
        first_url = self.driver.current_url
        states = []
        for i in range(0,5):
            print(i)
            state = State(self.driver, first_url)
            usernames, passwords, other_inputs = self.find_username_password()
            print(usernames)
            print(passwords)
            user_state, pass_state = 0, 0

            for ele in usernames:
                if ele.is_displayed and ele.is_enabled() and ele.get_attribute('type') != 'hidden':
                    try:
                        ele.send_keys(self.email)
                    except Exception as e:
                        continue
                    user_state = 1

            for ele in passwords:
                if  ele.is_displayed and ele.is_enabled() and ele.get_attribute('type') != 'hidden' :
                    try:
                        print("filling in passwords")
                        ele.send_keys(self.password)
                    except Exception as e:
                        continue
                    pass_state = 1

            for ele in other_inputs:
                if ele.is_displayed() and ele.is_enabled() and ele.get_attribute('type') != 'hidden':
                    try:
                        ele.send_keys('random')
                    except Exception as e:
                        continue
            state.update_all(user_state, pass_state)
            states.append(state)
            if state.is_final():
                break


            submitted = self.try_submit()

            if not submitted:
                print("unable to submit")
                break

        return states

if __name__ == "__main__":
    white_lists = {}

    with open('lang.txt') as langf:
        for i in langf.readlines():
            i = i.strip()
            text = i.split(' ')
            print(text)
            white_lists[text[1]] = 'en'
    print(white_lists)
    prefs = {
        "translate": {"enabled": "true"},

        "translate_whitelists": white_lists
    }

    url = 'localhost:8051'
    if len(sys.argv) == 1:
        file_name = clean_domain(url)
    else:
        file_name = sys.argv[1]
    tester = WebsiteTester(url,prefs)
    states = tester.test_site()
    print(file_name)
    with open('legit_sites_test/' + file_name, 'w+') as f:
        for state in states:
            f.write(str(state) + '\n')
