import json
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import os.path
try:
    from PIL import Image
except:
    pass


# 使用登录cookie信息
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")


AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'

HEADERS = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    'User-Agent':AGENT
}




def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/people/edit"
    login_code = session.get(url, headers=HEADERS, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False

def showSR():
    header={
        'Host': 'www.zhihu.com',
        'User-Agent':AGENT
    }

    try:
        #先请求cookie
        html = session.get("https://www.zhihu.com/signup?next=%2F",headers=header)
        html = session.get("https://www.zhihu.com/api/v3/oauth/captcha?lang=en", headers=HEADERS)
        #再请求cookie（udid什么的）
        html = session.post("https://www.zhihu.com/udid", headers=header)
        for item in session.cookies:
            if item.name=='d_c0':
                udid=item.value.split('|')[0]
                break
        header={
            'Host': 'www.zhihu.com',
            'Origin': 'https://www.zhihu.com',
            'Referer': 'https://www.zhihu.com/signup?next=%2F',
            'User-Agent':AGENT,
            'x-udid': udid,
        }
        #获取二维码保存的json
        html=session.post("https://www.zhihu.com/api/v3/account/api/login/qrcode",headers=header)
        token=json.loads(html.text).get('token')
        qr=session.get('https://www.zhihu.com/api/v3/account/api/login/qrcode/'+str(token)+'/image',headers=header)

        with open('QR.jpg', 'wb') as f:
            f.write(qr.content)
            f.close()

        try:
            im = Image.open(os.path.abspath('QR.jpg'))
            # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
            im = im.convert('L')
            # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
            threshold = 200

            table = []
            for i in range(256):
                if i < threshold:
                    table.append(0)
                else:
                    table.append(1)

            # 图片二值化
            im = im.point(table, '1')
            im.save(os.path.abspath('QR.jpg'))
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到QR.jpg 手动输入' % os.path.abspath('QR.jpg'))
            input('扫码完成后请输入回车继续')

        #还有一些小饼干（之前省略后就出错的地方）
        html = session.get('https://www.zhihu.com/api/v3/account/api/login/qrcode/'+str(token)+'/scan_info', headers=HEADERS)

        return True
    except Exception as e:
        print('二维码获取失败:',e)
        return False


def createLogin(reTryCount=2):
    while(True):
        if(not showSR()):
            if(reTryCount>=0):
                print('正在重试...')
                reTryCount-=1
            else:
                print('登录失败')
                return False
        else:
            print('正在测试是否登录...')
            if isLogin():
                print('登录成功')
                session.cookies.save()
                return True
            print('登录失败')
            reTryCount-=1


def login():
    if isLogin():
        print('目前为已登录状态')
        return True
    else:
        if createLogin():
            return True
        return False



