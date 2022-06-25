#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import base64
import urllib3
import datetime
import requests

# plain text
BAHA_USERNAME = os.getenv('BAHA_USERNAME')
BAHA_PASSWORD = os.getenv('BAHA_PASSWORD')
BAHA_2FACODE = os.getenv('BAHA_2FACODE')

# base64 encoded string
BAHA_COOKIES = os.getenv('BAHA_COOKIES')

# telegram bot
TG_CHAT = os.getenv('TG_CHAT')
TG_TOKEN = os.getenv('TG_TOKEN')

GITHUB_ENV = os.getenv('GITHUB_ENV')

app_headers = {
    'User-Agent': 'Bahadroid (https://www.gamer.com.tw/)',
    'X-Bahamut-App-Android': 'tw.com.gamer.android.activecenter',
    'X-Bahamut-App-Version': '789',
    'OSVersion': '9.1.8'
}

csrfToken = '5d9f7240a225c09e'
bahamutCsrfToken = { 'bahamutCsrfToken': csrfToken }
ckBahamutCsrfToken = { 'ckBahamutCsrfToken': csrfToken }

session = requests.Session()
session.headers = app_headers
session.verify = False
urllib3.disable_warnings()

class Api():
    DEFAULT_URL = 'https://api.gamer.com.tw/'
    ANIMATE_URL = 'https://ani.gamer.com.tw/'
    APP_CREATE = f'{DEFAULT_URL}mobile_app/bahamut/v1/app_create.php'
    API_TWO_STEP_CHECK = f'{DEFAULT_URL}/user/v1/login_precheck.php'
    API_DO_LOGIN = f'{DEFAULT_URL}mobile_app/user/v4/do_login.php'
    PROFILE = f'{DEFAULT_URL}mobile_app/bahamut/v3/profile.php'
    SIGNIN = f'{DEFAULT_URL}mobile_app/bahamut/v4/sign_in.php'
    SIGNIN_AD_START = f'{DEFAULT_URL}mobile_app/bahamut/v1/sign_in_ad_start.php'
    SIGNIN_AD_FINISHED = f'{DEFAULT_URL}mobile_app/bahamut/v1/sign_in_ad_finished.php'
    HOME_INDEX = f'{DEFAULT_URL}mobile_app/bahamut/v1/home.php'
    HOME_CREATION_DETAIL = f'{DEFAULT_URL}mobile_app/bahamut/v1/home_creation_detail.php'
    ANI_GET_QUESTION = f'{ANIMATE_URL}/ajax/animeGetQuestion.php'
    ANI_ANS_QUESTION = f'{ANIMATE_URL}/ajax/animeAnsQuestion.php'
    GUILD_MY_GUILD = f'{DEFAULT_URL}guild/v2/guild_my.php'
    GUILD_SIGN = f'{DEFAULT_URL}guild/v1/guild_sign.php'


def CheckLogin():
    r = session.get(Api.APP_CREATE)
    if r.status_code != requests.codes.ok:
        return False
    try:
        return r.json()['login']
    except:
        return False


def Check2FA():
    r = session.post(
        Api.API_TWO_STEP_CHECK,
        data = { 'userid': BAHA_USERNAME },
        cookies = {}
    )
    if r.status_code != requests.codes.ok:
        return (False, 0)
    try:
        return (True, r.json()['data']['status'])
    except:
        return (False, 0)


def Login(need2FA):
    global text
    text += f'⚠ 巴哈登入\n帳號：{BAHA_USERNAME}\n密碼：{BAHA_PASSWORD}\n'
    data = { 'uid': BAHA_USERNAME, 'passwd': BAHA_PASSWORD }
    if need2FA == 1:
        text += f'2FA：{BAHA_2FACODE}\n'
        data.update({ 'twoStepAuth': BAHA_2FACODE })
    text += '\n'
    data.update(bahamutCsrfToken)
    session.cookies.clear()
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.API_DO_LOGIN, data = data)
    if r.status_code != requests.codes.ok:
        return (False, '')
    try:
        return (False, r.json()['error']['message'])
    except:
        return (True, r.json()['data']['userid'])


def UpdateCookie():
    try:
        cookie = json.dumps(session.cookies.get_dict())
        cookie = base64.b64encode(cookie.encode('UTF-8')).decode('UTF-8')
        with open('cookies.txt', 'w', encoding='UTF-8') as file:
            file.write(cookie)
        if GITHUB_ENV != None:
            with open(GITHUB_ENV, 'a') as file:
                file.write(f'BAHA_COOKIES={cookie}')
    except:
        return


def Profile():
    global text
    r = session.get(Api.PROFILE)
    if r.status_code != requests.codes.ok:
        return
    try:
        data = r.json()['data']
        userid = data.get('userid')
        gold = data.get('gold')
        gp = data.get('gp')
        signDays = data.get('signDays')
        lastSign = data.get('lastSign')
        text += f'ℹ 帳號資訊 ({userid})\n巴幣：{gold}\nGP：{gp}\n簽到天數：{signDays}\n上次簽到：{lastSign}\n\n'
    except:
        text += '❌ 帳號資訊\n'


def TodaySignin():
    global text
    if datetime.date.today().isoformat() in text:
        text += 'ℹ 今日已簽到\n\n'
        return True
    return False


def Signin():
    global text
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        return
    try:
        gift = r.json()['data']['result']['gift']
        text += f'✅ 主頁簽到\n{gift}\n\n'
    except:
        text += '❌ 主頁簽到\n'


def Signin_AD():
    global text
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN_AD_START, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        return
    finish = r.json().get('data').get('finished')
    if finish == 1:
        text += '✅ 雙倍巴幣 (今日已完成)\n\n'
        return
    time.sleep(15)
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN_AD_FINISHED, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        return
    finished = r.json().get('data').get('finished')
    if finish != 1:
        text += '❌ 雙倍巴幣\n\n'
        return
    text += '✅ 雙倍巴幣\n\n'


def GetAniAnswer():
    r = session.get(f'{Api.HOME_INDEX}?owner=blackXblue&page=1')
    if r.status_code != requests.codes.ok:
        return
    try:
        sn = r.json()['creation'][0]['sn']
    except:
        return None

    r = session.get(f'{Api.HOME_CREATION_DETAIL}?sn=' + str(sn))
    if r.status_code != requests.codes.ok:
        return
    try:
        content = r.json()['content']
        m = re.search("[Aa][:;：](\d)", content)
        ans = m.group(1)
        return ans
    except:
        return None


def AniAnswer():
    ans = GetAniAnswer()
    global text
    r = session.get(Api.ANI_GET_QUESTION)
    if r.status_code != requests.codes.ok:
        return

    token = r.json().get('token')
    error = r.json().get('error')
    if error == 1:
        text += '✅ 動畫瘋 (今日已答題)\n\n'
        return

    if token == None:
        text += '❌ 動畫瘋\n\n'
        return

    data = { 'token': token, 'ans': ans }
    r = session.post(Api.ANI_ANS_QUESTION, data = data)
    if r.status_code != requests.codes.ok:
        return

    ok = r.json().get('ok')
    gift = r.json().get('gift')
    if ok == 1:
        text += f'✅ 動畫瘋答題\n{gift}\n\n'
    else:
        text += f'❌ 動畫瘋\n\n'


def GuildSignin():
    global text
    r = session.get(Api.GUILD_MY_GUILD)
    if r.status_code != requests.codes.ok:
        text += f'❌ 公會簽到\n\n'
        return
    list = r.json().get('data').get('list')
    for guild in list:
        gsn = guild.get('sn')
        title = guild.get('title')
        data =  { 'gsn': gsn }
        data.update(bahamutCsrfToken)
        r = session.post(Api.GUILD_SIGN, data = data)
        if r.status_code != requests.codes.ok:
            text += f'❌ 公會簽到 ({title})\n'
            continue
        statusCode = r.json().get('data').get('statusCode')
        message = r.json().get('data').get('message')
        if statusCode != None:
            text += f'✅ 公會簽到 ({title})\n{message}\n\n'


def TG_SendMessage(text):
    try:
        r = requests.get(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT}&parse_mode=Markdown&text={text}')
    except:
        pass


if __name__ == "__main__":

    if BAHA_USERNAME == None or BAHA_PASSWORD == None:
        assert False, '請設定巴哈登入資訊\nBAHA_USERNAME=巴哈帳號\nBAHA_PASSWORD=巴哈密碼'

    if BAHA_COOKIES != None:
        try:
            cookie = base64.b64decode(BAHA_COOKIES).decode("UTF-8")
            requests.utils.add_dict_to_cookiejar(session.cookies, json.loads(cookie))
        except :
            pass

    text = ''

    if not CheckLogin():
        _, need2FA = Check2FA()
        _, message = Login(need2FA)
        assert _, message

    Profile()
    UpdateCookie()

    #if TodaySignin():
    #    print(text)
    #    sys.exit(0)

    Signin()
    Signin_AD()
    GuildSignin()
    AniAnswer()
    
    TG_SendMessage(text)
    
    print(text)
    sys.exit(0)
