import requests
import hashlib
import execjs
import json
import time
import pymongo


class AnswerSpider():
    print('start')
    User_Agent = 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'
    cookie = ''
    # cookie中d_c0的值
    d_c0 = ''
    main_url = 'https://www.zhihu.com'

    def __init__(self, offset):
        self.offset = offset
        # 用户 people
        self.hash_url = '/api/v4/members/people/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Cexcerpt%2Cis_labeled%2Clabel_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B*%5D.vessay_info%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B*%5D.question.has_publishing_draft%2Crelationship&offset={}&limit=20&sort_by=created'.format(
            offset)

        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['zhihu']
        self.col = self.db['answer']

        self.write_database()

    # api地址以及未加密文本
    def address(self):
        hash_url = self.hash_url.format(self.offset)
        url = ''.join([self.main_url, hash_url])
        self.d = '+'.join(['3_2.0', hash_url, self.d_c0])
        return url, self.d

    # 加密
    def encrypt(self, d):
        d_md5 = hashlib.new('md5', d.encode()).hexdigest()
        # 调用知乎的加密函数,运行js文件
        with open('zhihu1.js', 'r') as f:
            ctx = execjs.compile(f.read(), 'C:/Users/hasee/node_modules')
        encrypt_d = ctx.call('b', d_md5)
        return encrypt_d

    # 获取内容
    def get(self):
        url, d = self.address()
        encrypt_d = self.encrypt(d)
        headers = {
            'user-agent': self.User_Agent,
            'cookie': self.cookie,
            'x-zse-83': '3_2.0',
            'x-zse-86': '2.0_%s' % encrypt_d
        }

        r = requests.get(url=url, headers=headers)
        answer = json.loads(r.text)
        return answer

    # save answer
    def write_database(self):
        answer = self.get()
        answer_data = answer['data']
        # 将每一个回答 json 存入数据库
        for i in range(len(answer_data)):
            data = {
                "name": "zhihu_a",
                "content": answer_data[i]
            }
            self.col.insert_one(data)
        print('--save--')


if __name__ == '__main__':
    offset = 0
    i = 1
    while True:
        content = AnswerSpider(offset)
        items = content.get()
        if items['paging']['is_end'] == True:
            print('最后一页')
            break
        print('{}页,已保存,offset={}'.format(i, content.offset))
        i += 1
        offset += 20
