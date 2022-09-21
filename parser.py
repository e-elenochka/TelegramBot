import logging
# import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from price_parser import Price
import requests
from urllib.parse import urlparse
import random
import enum


# logg = logging.getLogger()
# logger.init_logger('app')

# log = logger.getLogger(app.parser)

option = webdriver.FirefoxOptions()        #переменная которая отвечает за настройки браузера (в этом браузере все настройки под себя)
option.set_preference('dom.webdriver.enabled', False)
option.set_preference('dom.webnotification.enabled', False) #откл/ уведомления в браузере
option.set_preference('media.volume_scale', '0,0') #отключили звук
user_agent = str(random.random()*10000)
option.set_preference('general.useragent.override', user_agent)
option.headless = True #работа раузера в фоне, без интерфеса


class Country(enum.Enum):
    ua = "Ukraine"
    pl = "Poland"
    uk = "United Kindom"
    es = "Spain"
    pt = "Portugal"
    de = "Germany"
    fr = "France"
    us = "USA"
    it = "Italy"
    at = "Austria"
    gb = "Great Britain"


class PriceParser:

    def __init__(self):
        # logging.warning('Watch out!')  # will print a message to the console
        # logging.info('I told you so')  # will not print anything

        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=option)
        self.currency = self.get_currency()

    def is_valid(self, url_input):
        print('is_valid...')
        '''Функция проверяет валидность ссылки'''
        u_pars = urlparse(url_input)
        if u_pars.scheme == 'https' and u_pars.netloc in ['www.zara.com', 'www.oysho.com']:
            return True
        else:
            return False

    def get_shops_urls(self, url_input):
        print('get_shops_urls...')
        '''Функция которая принимает ссылку и создает список ссылок на магазины разных стран'''
        url_list = []
        if 'www.oysho.com' in url_input:
            url_split_pars = url_input.split('/')
            for i in Country:
                if i == 'uk':
                    continue
                url = f"{url_split_pars[0]}//{url_split_pars[1]}{url_split_pars[2]}/{i.name}/"
                url = url + '/'.join(url_split_pars[4:])
                url_list.append({'url': url, 'country': i.value})
        if 'www.zara.com' in url_input:
            url_split_pars = url_input.split('/')
            for i in Country:
                if i == 'gb':
                    continue
                url = f"{url_split_pars[0]}//{url_split_pars[1]}{url_split_pars[2]}/{i.name}/"
                url = url + '/'.join(url_split_pars[4:])
                url_list.append({'url': url, 'country': i.value})
        return url_list

    def get_goods_list(self, url_input):
        print('get_goods_list...')
        '''Функция принимает строку-ссылку, и возвращает список состоящий из словаря'''
        if 'www.zara.com' in url_input:
            url_list = self.get_shops_urls(url_input)
            return self.get_url_list(url_list, 'price-current__amount')

        if 'www.oysho.com' in url_input:
            url_list = self.get_shops_urls(url_input)
            return self.get_url_list(url_list, 'price-wrapper__price')

    def get_url_list(self, url_list, search_class):
        print('get_url_list...')
        '''Функция принимает спиоск ссылок на магазины, название класса, по которому идет поиск цен на сайтах
         и возвращает отсортированный список состоящий из словаря'''
        item_list = []
        # print(url_list)
        for url in url_list:  # подготовленньій список которьій сразу в драйвер
            try:
                self.driver.get(url['url'])
                if 'www.zara.com' or 'www.oysho.com' in url['url']:
                    raw_price = self.driver.find_element(By.CLASS_NAME, value=search_class)
                    print('raw_price', raw_price.text)
                    item = self.dict_price(raw_price.text)
                    print('item', item)
                    item['url'] = url['url']
                    print('url', url['url'])

                    item['country'] = url['country']
                    print('country', url['country'])

                    item['price_uah'] = self.currency_exchange(self.currency, item['price'], item['currency'])
                    item_list.append(item)
            except BaseException as a:
                print('Товара нет на сайте', a)
        return self.sort_min_price(item_list)

    def dict_price(self, val):
        '''принимает цены и валюту строкой, разбивате на число цены и валюту в международном коде'''
        # print('dict_price...')
        dict_value = {}
        split_price = val.split(' ')
        dict_value['currency'] = split_price.pop()
        price = Price.fromstring(val)
        dict_value['currency'] = price.currency
        dict_value['price'] = float(price.amount)
        if price.currency == '€':
            dict_value['currency'] = 'EUR'
        if price.currency == '£':
            dict_value['currency'] = 'GBP'
        if price.currency == '₴':
            dict_value['currency'] = 'UAH'
        if price.currency == '$':
            dict_value['currency'] = 'USD'
        if price.currency == 'zł':
            dict_value['currency'] = 'PLN'
        return dict_value

    def get_currency(self):
        print('get_currency...')
        '''Функция вытягивает курс валют в формате json'''
        res = requests.get('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json')
        dict_currency = (res.json())
        return dict_currency

    def currency_exchange(self, currency_list, price, currency):
        print('currency_exchange...')
        '''Функция округляет цену до 2х знаков после запятой'''
        for c in currency_list:
            if currency == 'UAH':
                return price
            if c["cc"] == currency:
                return round((float(c["rate"]) * price), 2)

    def sort_min_price(self, list_dict):
        print('sort_min_price...')
        '''сортирует готовый список по гривневой, конвертированой цене от наименьшего к большему'''
        sorted_dict = sorted(list_dict, key=lambda x: x['price_uah'])
        print('sort_min_price', sorted_dict)
        return sorted_dict

    def quit(self):
        print('quit.')
        self.driver.quit()

# if __name__ == '__main__':
#     print('Start parsing ...')
#     parser = PriceParser()
    #
    # result = parser.get_goods_list('https://www.zara.com/de/de/t-shirt-mit-stickerei-und-tunnelzug-p05643703.html?v1=184470556&v2=2112292')
    # # print('Zara', len(result))
    # print('Zara', result)

    # result = parser.get_goods_list('https://www.oysho.com/es/sujetador-cl%C3%A1sico-multiposici%C3%B3n-poliamida-c0p114224160.html')
    # print('oysho', len(result))

    # result = parser.get_goods_list('https://www.pullandbear.com/pl/spodnie-chinosy-carpenter-l04674320?cS=614&pelement=511917268')
    # print('PullandBear', len(result))

    # result = parser.get_goods_list('https://shop.mango.com/es/nina/pijamas/pijama-algodon-estampado-jirafa_27017112.html')
    # print('Mango', len(result))

    # result = parser.get_goods_list('https://www.massimodutti.com/ua/широкі-штани-палаццо%C2%A0—-limited%C2%A0edition-l05075555')
    # print('massimodutti', len(result))
    #
    # ???result = parser.get_goods_list('https://www.calzedonia.com/ua/product/сумка_пляжна_з_ефектом_«кроше»-CZM102.html?dwvar_CZM102_Z_COL_MARE=541C')
    # print('calzedonia', len(result))

    # result = parser.get_goods_list('https://www.stradivarius.com/es/camiseta-rayas/camiseta-rayas-c1020428826p320363651.html?colorId=001')
    # print('stradivarius', len(result))

    # parser.quit()
    # print('Quit parser.')
