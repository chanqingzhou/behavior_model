from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
import time
import lxml.html as LH
import lxml.html.clean as clean
import tldextract
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

ignore_tags = ('script', 'noscript', 'style')
error_words = ['incorrect', 'error', 'can\'t find','does not exist','dosen\'t exist',  'cannot find', 'not exist', 'try again' ,'not found','403 forbidden','404']
captcha_words = ['security challenge', 'enter words','type characters','enter the characters','not a robot']
class State:
    def __init__(self):
        self.password = 0
        self.username = 0
        self.captcha = 0
        self.error = None
        self.visible_text = []
        self.url = None
        self.link = False
        self.final = 0
    def __str__(self):
        return "user:{} , password:{}, captcha:{},error:{}, link:{}, url:{}, final:{}".format(str(self.username),str(self.password),str(self.captcha), str(self.error),str(self.link),self.url, str(self.final))

def clean_domain(domain, deletechars='\/:*?"<>|'):
    for c in deletechars:
        domain = domain.replace(c, '')
    return domain[:30]

def find_and_close_popup_window(driver):
    pass


def clean_str(string):
    return string.lower().replace(" ", "")


def test_site(url, driver, email ='casfmsa@hotmail.com',password='nonfdasf'):
    attributes = ['id','type','placeholder','name','value']
    driver.get(url)
    domain = tldextract.extract(url).domain
    print(domain)
    states = []
    time.sleep(6)
    visible_text =[]
    randomcount  = 0
    final_msg = ""
    for i in range(0,10):

        time.sleep(3)
        logs = driver.get_log("performance")

        print(logs)
        state = State()

        try:
            state.url = driver.current_url
        except exceptions.UnexpectedAlertPresentException as e:
            state.url = driver.current_url

        if '.php' in driver.current_url:
            print("sleeping:")
            time.sleep(5)

        paths = driver.find_elements_by_xpath('.//a')
        for path in paths:
            try:
                path_url = path.get_attribute('href')
                print(path_url)

                if path_url[:4] == 'http':
                    path_domain = tldextract.extract(path_url).domain
                    if path_domain == domain:
                        state.link = True
                        break
                else:
                    state.link = True
                    break
            except Exception as e:
                print("unable to find path")
        print(i)
        print(driver.current_url)

        current_domain = tldextract.extract(driver.current_url).domain
        if current_domain != domain:
            print(current_domain)
            print("hello")
            states.append(state)
            break

        page_text = driver.find_element_by_tag_name('body').text
        state.visible_text = page_text.split('\n')
        for i in state.visible_text:
            word = i.lower()
            for test in error_words:
                if test in word:
                    print(word)
                    state.error = word
                    break


        elem = driver.find_elements_by_xpath('.//input')
        print("finding elements")
        print(len(elem))
        element_counter = 0
        for ele in elem:
            if ele.get_attribute('type') != 'hidden' and ele.is_displayed():
                element_counter += 1
                id = ele.get_attribute('id')
                try:
                    label = driver.find_element_by_xpath('.//label[@for="{}"]'.format(id))
                    txt = label.text.lower()
                    print(txt)
                    if 'user' in txt or 'mail' in txt or 'login' in txt:
                        state.username = 1
                        if ele.get_attribute("value") == email:
                            continue
                        ele.send_keys(email)

                    if 'pass' in txt:
                        try:
                            ele.send_keys(password)
                            print("fill password")
                            state.password = 1
                            continue
                        except Exception as e:
                            print("failed_pass")
                            continue

                except Exception as e:
                    print("no label")

                for attribute in attributes:
                    print(ele.get_attribute(attribute))
                    if ('email' in ele.get_attribute(attribute).lower() or 'user' in  ele.get_attribute(attribute).lower()\
                            or 'login' in  ele.get_attribute(attribute).lower()) and state.username == 0:
                        state.username = 1
                        if ele.get_attribute("value") == email:
                            continue
                        ele.send_keys(email)
                        print("found email")

                    if 'pass' in ele.get_attribute(attribute):
                        try:
                            ele.send_keys(password)
                            print("fill password")
                            state.password = 1
                            continue
                        except Exception as e:
                            print("failed_pass")
                            continue
        print("1")
        '''
        #dk what this is for
        if element_counter > 4 and len(states) != 0:
            state.final = 1
            states.append(state)
            break
        '''

        if state.username == 0 and state.password == 0 and len(states) == 0:
            start = 0
            for ele in elem:
                if ele.is_displayed():
                    if start == 0:
                        start+=1
                        ele.send_keys(email)
                        state.username = 1
                        continue
                    if start == 1:
                        state.password = 1
                        ele.send_keys(password)
                        break

        if state.password == 0 and state.username == 0 and len(states)==0:
            try:
                iframe = driver.find_element_by_tag_name("iframe")
                print("going into iframe")
                if iframe:
                    driver.switch_to.frame(iframe)
                continue
            except Exception as e:
                print("no iframe")
        print("3")
        time.sleep(1)
        page_text = driver.find_element_by_tag_name('body').text
        print(page_text)
        state.visible_text = page_text.split('\n')

        for i in state.visible_text:
            word = i.lower()
            print(word)
            for test in captcha_words:
                if test in word:
                    state.captcha = 1
                    break

        if (state.password ==0 and state.username == 0) or state.captcha == 1:
                states.append(state)
                break
        print("hello")
        buttons = driver.find_elements_by_xpath('.//button|.//input')
        button_clicked = False
        print("start button")
        print(len(buttons))

        for i in range(len(buttons)):
            button = buttons[i]
            if (button.get_attribute('type') == 'submit' or button.get_attribute(
                    'type') == 'image') and button.is_displayed() and button.is_enabled():

                text = clean_str(button.get_attribute('outerHTML'))
                if 'login' in text or 'signin' in text:
                    button.click()
                    button_clicked = True
                    break
        logs = driver.get_log("performance")
        print(logs)
        if not button_clicked:
            for i in range(len(buttons)):
                button =  buttons[(i+randomcount) %len(buttons)]

                if (button.get_attribute('type') == 'submit' or button.get_attribute('type') == 'image')and button.is_displayed() and button.is_enabled():

                    try:
                        print("pressing button")
                        button_clicked = True
                        time.sleep(0.1)
                        button.click()
                        break
                    except Exception as e:
                        print("button exception")
                        continue

        if button_clicked == False:
            for button in buttons:
                print(button)
                if button.is_displayed():
                    print(button.get_attribute('value'))
                    try:
                        button_clicked = True
                        button.click()
                        time.sleep(0.1)
                        break
                    except Exception as e:
                        print("button exception")
                        continue

        if button_clicked == False:
            possible_clicks = driver.find_elements_by_xpath('.//*[@onclick!=""]')
            for click in possible_clicks:
                if click.is_displayed():
                    click.click()
                    time.sleep(0.1)
                    button_clicked = True
                    break

        print("end buttons")
        states.append(state)
        print(state)
        if button_clicked == False:
            final_msg  = "no buttons found"
            break
    with open('legit_sites_test/' + clean_domain(url),'w+') as f:
        for state in states:

            f.write(str(state) +'\n')
        f.write(final_msg)
if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    capabilities = DesiredCapabilities.CHROME
    # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

    options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

    driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities)
    with open('phish.txt') as f:
        for i in f.readlines():
            url = i.strip()
            url = 'https://www.paypal.com/sg/signin'

            test_site(url, driver)
            break
