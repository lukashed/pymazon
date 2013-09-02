import requests
from bs4 import BeautifulSoup
import getpass


class Order:
    def __init__(self, price):
        self.price = price


class Pymazon:
    def __init__(self, country):
        self.country = country
        self.session = requests.Session()
        self.session.headers.update({'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36'})

    def login(self, email, password):
        r = self.session.get('http://www.amazon.%s/gp/yourstore/home/' % self.country)
        soup = BeautifulSoup(r.text)
        form = soup.find('form', id='ap_signin_form')
        login_url = form.get('action')
        if 'http://' not in login_url and 'https://' not in login_url:
            login_url = 'https://www.amazon.%s%s' % (self.country, login_url)
        # print login_url
        fields = form.find_all('input')

        data = {f.get('name'): f.get('value') for f in fields if f.get('name')}

        data['email'] = email
        data['password'] = password
        data['create'] = '0'

        r = self.session.post(login_url, data=data)


    def get_orders(self, filter_='year-2013', start_index=0):
        url = 'https://www.amazon.%s/gp/css/order-history?digitalOrders=1&unifiedOrders=1&orderFilter=%s&startIndex=%d' % (
            self.country, filter_, start_index)

        r = self.session.get(url)

        soup = BeautifulSoup(r.text)
        prices = soup.find_all('span', {'class': 'price'})

        prices_ = []

        for price in prices:
            price = price.text
            price = price.replace('EUR ', '')
            price = price.replace(',', '.')
            price = float(price)
            prices_.append(Order(price=price))

        if prices:
            prices_.extend(self.get_orders(filter_=filter_, start_index=start_index + 10))

        return prices_


    def calculate_orders_total(self, filter_='year-2013'):
        return sum([p.price for p in self.get_orders(filter_=filter_)])
            


if __name__ == '__main__':
    pz = Pymazon('de')
    pz.login(raw_input('E-Mail: '), getpass.getpass('Password: '))
    print pz.calculate_orders_total()
