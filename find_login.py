from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import lxml.html as LH
import lxml.html.clean as clean
import tldextract
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
TEXT = ['login', 'signin']
import random
from multiprocessing import Pool
import logging
logging.basicConfig(filename='log.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


def convert_str_to_xpath(string):
    ele = BeautifulSoup(string, 'html.parser')
    ele = ele.find_all()[0]
    name = ele.name
    str_to_ret = ''
    for key in ele.attrs:
        print(ele.attrs[key])
        print(ele.attrs)
        value = ele.attrs[key]
        if type(value) == list:
            value_temp = ''
            for i in value:
                value_temp += i + ' '
            value = value_temp.strip()
        str_to_ret += "[@{}='{}']".format(key, value)
    return './/' + name + str_to_ret

def clean_str(string):
    return string.lower().replace(" ", "")

def compare_link(url,url2):
    if url == url2:
        return True
    elif url.split('?')[0] == url2.split('?')[0]:
        return True

def get_clickable(driver):
    pass

def ctrl_click(driver, element):
    print("clicking")
    time.sleep(1)
    return ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

def check_element(driver, code):
    xpath = convert_str_to_xpath(code)
    print(xpath)
    elements = driver.find_elements_by_xpath(xpath)
    print(elements)
    if len(elements) == 0:
        return False

    for i in elements:
        if i.is_displayed() and i.is_enabled():
            return True
    return False
def test_two_click(driver):
    expand_items = driver.find_elements_by_xpath(".//a[@aria-expanded='false'] | .//button[@aria-expanded='false']")
    original_items = driver.find_elements_by_xpath('.//a | .//button')
    displayed_items = []
    for i in original_items:
        if i.is_displayed() and i.is_enabled():
            displayed_items.append(i)
    print(len(displayed_items))

    for item in expand_items:
        if item.is_enabled() and item.is_displayed():
            print(item.get_attribute('outerHTML'))
            item.click()
            print(len(original_items))
            time.sleep(0.5)
            new_items = driver.find_elements_by_xpath('.//a | .//button')

            to_test = list(filter(lambda x: x not in original_items,new_items))
            possible_log_in = dom_tree_search(driver, to_test,3)
            print(possible_log_in)
            click_possible_links(driver, possible_log_in)
            time.sleep(0.5)
            time.sleep(0.5)

def dom_tree_search(driver, elements, max):
    elements_storage = []
    new_tags = []
    for tag in elements:

        #if tag.is_displayed() and tag.is_enabled():
        elements_storage.append(tag)
        new_tags.append(tag)
    possible_log_in = []
    start_time = time.time()

    for count in range(0,max):
        for i in range(len(elements_storage)):
            tag = elements_storage[i]
            try:
                text_data = tag.get_attribute('outerHTML')
            except Exception as e:
                continue
            for text in TEXT:
                if text in clean_str(text_data):
                    possible_log_in.append([new_tags[i], text_data,count])
                    break
        final_time = time.time()
        print(final_time-start_time)
        print(count)
        if possible_log_in or count == max-1:
            break
        for i in range(len(elements_storage)):
            try:
                elements_storage[i] = tag.find_element_by_xpath('./..')
            except Exception as e:
                elements_storage[i] = tag
        final_time = time.time()

    return possible_log_in

def click_possible_links(driver, possible_log_in):
    for possible in possible_log_in:
        print("starting")
        try:
            if possible[0].is_displayed() and possible[0].is_enabled():
                    result = ctrl_click(driver, possible[0])
                    print(result)

                    time.sleep(1)
            else:
                print("item not enabled")
                expand_items = driver.find_elements_by_xpath(".//a[@aria-expanded='false'] | .//button[@aria-expanded='false']")
                clicked = False
                for item in expand_items:
                    if item.is_enabled() and item.is_displayed():
                        item.click()
                        time.sleep(2)
                        if possible.is_displayed() and possible.is_enabled():
                            try:
                                clicked = True
                                ctrl_click(driver, possible[0])
                            except Exception as e:
                                print('unable to find')
                            finally:
                                item.click()
                                break
                        time.sleep(0.5)
                if not clicked:
                    up = possible[0].find_element_by_xpath('./..')
                    for i in range(0,4):
                        if up.is_enabled() and up.is_displayed():
                            up.click()
                            time.sleep(0.5)
                            ctrl_click(driver, possible[0])
                            break
                        else:
                            up = up.find_element_by_xpath('./..')

        except Exception as e:
            print('unable to find')

def click_popup_links(driver, possible_log_in, code):
    for possible in possible_log_in:
        print("starting")
        try:
            if possible[0].is_displayed() and possible[0].is_enabled():
                    result = ctrl_click(driver, possible[0])
                    print(result)
                    time.sleep(3)
                    if check_element(driver, code):
                        return True
                    time.sleep(1)
            else:
                print("item not enabled")
                expand_items = driver.find_elements_by_xpath(".//a[@aria-expanded='false'] | .//button[@aria-expanded='false']")
                clicked = False
                for item in expand_items:
                    if item.is_enabled() and item.is_displayed():
                        item.click()
                        time.sleep(2)
                        if possible.is_displayed() and possible.is_enabled():
                            try:
                                clicked = True
                                ctrl_click(driver, possible[0])
                                time.sleep(3)
                                if check_element(driver, code):
                                    return True
                                break
                            except Exception as e:
                                print('unable to find')
                            finally:
                                item.click()
                if not clicked:
                    print("testing")
                    up = possible[0].find_element_by_xpath('./..')
                    for i in range(0, 4):
                        if up.is_enabled() and up.is_displayed():
                            up.click()
                            time.sleep(0.5)
                            ctrl_click(driver, possible[0])
                            time.sleep(3)
                            if check_element(driver, code):
                                return True
                            break
                        else:
                            up = up.find_element_by_xpath('./..')

        except Exception as e:
            print('unable to find')
    return False

def click_randomly(driver, working_tags):
    for tag in working_tags:
        text_data = tag.get_attribute('outerHTML')
        if 'enter' in text_data or 'close' in text_data:
            tag.click()
            time.sleep(1)
            try:
                if tag.is_enabled() and tag.is_displayed():
                    continue
                else:
                    return tag
            except Exception as e:
                return
    while len(working_tags) > 0:
        to_click = random.randint(0,len(working_tags) - 1)
        working_tags[to_click].click()
        time.sleep(1)
        try:
            if working_tags[to_click].is_enabled() and working_tags[to_click].is_displayed():
                working_tags.remove(working_tags[to_click])
                continue
            else:
                return
        except Exception as e:
            return


def run_normal_test(url, driver, popup):
    if popup:
        if check_element(driver, popup):
            raise Exception("login already exists")

    href_tags = driver.find_elements_by_xpath('.//a | .//button')

    print(len(href_tags))
    possible_log_in = dom_tree_search(driver, href_tags, 1)
    print("hello")
    print(possible_log_in)
    if not possible_log_in:
        regex_str = re.findall('(?i)<[^>]*?log.{0,2}in[^<]*?>', driver.page_source)
        regex_str.extend(re.findall('(?i)<[^>]*?sign.{0,2}in[^<]*?>', driver.page_source))
        for i in regex_str:
            xpath = convert_str_to_xpath(i)
            print(xpath)
            eles = driver.find_elements_by_xpath(xpath)
            print(eles)
            for ele in eles:
                possible_log_in.append([ele, '', ''])

    to_ret = []
    if not popup:
        if possible_log_in:
            click_possible_links(driver, possible_log_in)

        else:
            test_two_click(driver)
        time.sleep(5)

        print(driver.window_handles)

        for window in driver.window_handles:
            driver.switch_to.window(window)

            to_ret.append(driver.current_url)
        if len(driver.window_handles) < 2:
            for possible in possible_log_in:

                try:
                    link = possible[0].get_attribute('href')
                    to_ret.append(link)
                except Exception as e:
                    continue
    else:
        result = click_popup_links(driver, possible_log_in, popup)
        if result:
            to_ret = ['Found']
        else:
            to_ret = ['Not Found']
    return to_ret

def test_site(args):
    try:
        url, options, popup = args[0], args[1], args[2]
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        driver.get(url)
        #test_two_click(driver)

        #get_clickable(driver)

        '''
        eles = driver.find_elements_by_xpath('.//*')
        print(eles)
        for i in eles:
            if i.is_displayed() and i.is_enabled():
                print(i.get_attribute('outerHTML'))
                try:
                    i.click()
                except Exception as e:
                    print(str(e))
                break
        '''
        time.sleep(6)
        current_url = driver.current_url
        print("searching")
        to_ret = run_normal_test(url, driver, popup)
        print(to_ret)
        if not popup and len(to_ret) == 1 and driver.current_url == current_url:
            print("clicking randomly")
            href_tags = driver.find_elements_by_xpath('.//a | .//button')
            working_tags = []
            for i in href_tags:
                if i.is_displayed() and i.is_enabled():
                    working_tags.append(i)
            try:
                click_randomly(driver, working_tags)
            except Exception as e:
                print("erorr")
            to_ret.extend(run_normal_test(url, driver, popup))
    except Exception as e:
        logging.exception(url)
        return [url, str(e)]
    finally:
        driver.quit()
    return [url, to_ret]

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
    popup = True
    to_do = []
    with open('test_popup.txt') as f:
        for url in f.readlines():
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")

            options.add_experimental_option("prefs", prefs)

            url = url.strip()

            if popup:
                url, popup = url.split('\t')

            to_do.append([url, options, popup])
    pool = Pool(processes=4)
    results = pool.map(test_site, to_do)
    print(results)
    for result in results:
        with open('test_popupresults.txt','a+') as f2:
            f2.write("{},{}\n".format(str(result[0]),str(result[1])))
