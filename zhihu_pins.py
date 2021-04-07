import requests
import hashlib
import execjs
import json
import pymongo


class PinsSpider():
    print('start')
    User_Agent = 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'
    cookie = '_xsrf=IDPOXjwEYD3cXjLWo2P9VowWZ5F1tdzz; d_c0="ALAd3ohjFRKPTjNZeG5_W8KUwFVpuCzndOk=|1603453023"; _zap=2364d58b-ed20-4520-ac9a-a7bdb0f8de71; __guid=74140564.3978841882797056000.1603453059214.0905; captcha_session_v2="2|1:0|10:1617085582|18:captcha_session_v2|88:L3pzd0JMRmkrMDJyOGwxM3J6M1ExVkp0YlNVOHJYaStxWWVzeXFLSTI3QXFYcGdxUW9yOGYxdTFiOHZVM2g4eQ==|13d44c108f8f03020b5cf2644887117157fb11d0e2f7c86c6a8f2ad6f5da10d4"; __snaker__id=U97F5GpVAdD8SZTj; gdxidpyhxdE=RJkMnsBqeLdqK%2B6qxkNOcXtIz%5ChytciqPiUaI8ys4QKq2nAz68xwaaUpbHoIPX3Oc0xpK5lcOQvpmzgzI7ANXyQro%2BjAyuRK6qEsntAKOGiNRszX0XZ9KlmjGJzaPss5E2gAkl3Eq3ToBcw%2FKtQjDEP3K43SMXO%2FxJGNGCeP8mtXV6AW%3A1617086483971; _9755xjdesxxd_=32; YD00517437729195%3AWM_NI=aGHXaii47H%2BoOwM6hXKRk4lfZzt2ExNKkUYrVhDJyQrGZimoqXnrQ1%2BUldYztWJzq2%2Fbr7NpKfZ%2BqPPFrM%2FAC%2FImkLp6rV3xG6eyE%2FCkTJu3PvZ5z7n%2FV9vZ736X9j%2FtR1g%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eed4ea4e908f85bab352afac8fa3d45f838b9eaff47da18e9891ce7ef197869aef2af0fea7c3b92aa39988b9e463abecf9a9aa658da983d7eb54898ea5d5ef6e9aa6bcd3c8748e95a5b6dc7a96b88cabfc5bb299968af065b388a293d43be98ba485dc72b889869bf43aedbebed8cd7c89ba96ccf45c949abeaeae4b81f1878eea48b4eabeb7b27485eaab9ac82581b59cabf83994aa96d6f93daef19adaf552f5edfab9bc62edac9ed2e637e2a3; YD00517437729195%3AWM_TID=NxhSIJQG0v5BVUUQAQZqkcEG5L%2BjcZnx; z_c0="2|1:0|10:1617085604|4:z_c0|92:Mi4xSVRnekFBQUFBQUFBc0IzZWlHTVZFaWNBQUFDRUFsVk5wRkdLWUFDT09NaU03ZWd0TlpraG8ycFlnQVdWZDJIZF93|8097667c5b212394b07af69cfc30ec1161d7ab0d2a8ab83dd098740147291584"; tst=r; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1615687620,1616055104,1617080880,1617105016; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1617105041; KLBRSID=fb3eda1aa35a9ed9f88f346a7a3ebe83|1617166139|1617166124'
    d_c0 = '"ALAd3ohjFRKPTjNZeG5_W8KUwFVpuCzndOk=|1603453023"'
    main_url = 'https://www.zhihu.com'

    def __init__(self, offset):
        self.offset = offset
        self.hash_pins_url = '/api/v4/members/cao-feng-ze-37/pins?offset={}&limit=20&includes=data%5B*%5D.upvoted_followees%2Cadmin_closed_comment'.format(
            offset)

        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['zhihu']
        self.col = self.db['pins']

        self.write_database()

    # api地址以及未加密文本
    def address(self):
        hash_url = self.hash_pins_url.format(self.offset)
        pins_url = ''.join([self.main_url, hash_url])
        d = '+'.join(['3_2.0', hash_url, self.d_c0])
        return pins_url, d

    # 加密
    def encrypt(self, d):
        d_md5 = hashlib.new('md5', d.encode()).hexdigest()
        with open('zhihu1.js', 'r') as f:
            ctx = execjs.compile(f.read(), 'C:/Users/hasee/node_modules')
        encrypt_d = ctx.call('b', d_md5)
        return encrypt_d

    # 获取内容
    def get(self):
        pins_url, d = self.address()
        encrypt_d = self.encrypt(d)
        headers = {
            'user-agent': self.User_Agent,
            'cookie': self.cookie,
            'x-zse-83': '3_2.0',
            'x-zse-86': '2.0_%s' % encrypt_d
        }

        r = requests.get(url=pins_url, headers=headers)
        pins = json.loads(r.text)
        return pins

    # save pins
    def write_database(self):
        pins = self.get()
        pins_data = pins['data']
        for i in range(len(pins_data)):
            data = {
                "name": "zhihu_pins",
                "content": pins_data[i]
            }
            self.col.insert_one(data)
        print('--save--')


if __name__ == '__main__':
    offset = 20
    i = 2
    while True:
        content = PinsSpider(offset)
        items = content.get()
        if items['paging']['is_end'] == True:
            print('最后一页')
            break
        print('{}页,已保存,offset={}'.format(i, content.offset))
        i += 1
        offset += 20
