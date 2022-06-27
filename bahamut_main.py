#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import enum
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

# Discord Webhook
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

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

class Status(enum.IntEnum):
    error = 0
    yes = 1
    no = 2
    done = 3

class Result():
    Login = False
    Need_2FA = False
    Profile = {}
    Guild = {}
    Signin = Status.no
    Signin_Msg = ''
    Signin_AD = Status.no
    Signin_AD_Msg = ''
    Guild_Signin = Status.no
    Guild_Signin_Msg = ''
    Ani_Answer = Status.no
    Ani_Answer_Msg = ''

def CheckLogin():
    r = session.get(Api.APP_CREATE)
    if r.status_code != requests.codes.ok:
        return False
    return r.json().get('login')

def Check2FA():
    r = session.post(Api.API_TWO_STEP_CHECK, data = { 'userid': BAHA_USERNAME })
    if r.status_code != requests.codes.ok:
        return
    return r.json().get('data').get('status')

def Login():
    data = { 'uid': BAHA_USERNAME, 'passwd': BAHA_PASSWORD }
    if Result.Need_2FA:
        data.update({ 'twoStepAuth': BAHA_2FACODE })
    data.update(bahamutCsrfToken)
    session.cookies.clear()
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.API_DO_LOGIN, data = data)
    if r.status_code != requests.codes.ok:
        return (False, None)
    data = r.json().get('data')
    error = r.json().get('error')
    if data == None:
        return (False, error.get('message'))
    else:
        return (True, data.get('userid'))

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
    r = session.get(Api.PROFILE)
    if r.status_code != requests.codes.ok:
        return
    try:
        data = r.json()['data']
        Result.Profile = data
    except:
        pass

def Signin():
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        Result.Signin = Status.error
        return
    try:
        gift = r.json()['data']['result']['gift']
        signed = r.json()['data']['result']['signed']
        if signed:
            Result.Signin = Status.done
        else:
            Result.Signin = Status.yes
            Result.Signin_Msg = gift
    except:
        Result.Signin = Status.error
        pass

def Signin_AD():
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN_AD_START, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        Result.Signin_AD = Status.error
        return
    finish = r.json().get('data').get('finished')
    if finish == 1:
        Result.Signin_AD = Status.done
        return
    time.sleep(15)
    session.cookies.update(ckBahamutCsrfToken)
    r = session.post(Api.SIGNIN_AD_FINISHED, data = bahamutCsrfToken)
    if r.status_code != requests.codes.ok:
        Result.Signin_AD = Status.error
        return
    finish = r.json().get('data').get('finished')
    if finish != 1:
        Result.Signin_AD = Status.error
        return
    Status.Signin_AD = Status.yes

def GetAniAnswer():
    r = session.get(f'{Api.HOME_INDEX}?owner=blackXblue&page=1')
    if r.status_code != requests.codes.ok:
        return None
    try:
        sn = r.json()['creation'][0]['sn']
    except:
        return None
    r = session.get(f'{Api.HOME_CREATION_DETAIL}?sn=' + str(sn))
    if r.status_code != requests.codes.ok:
        return None
    try:
        content = r.json().get('content')
        m = re.search("[Aa][:;：](\d)", content)
        ans = m.group(1)
        return ans
    except:
        return None

def AniAnswer():
    ans = GetAniAnswer()
    r = session.get(Api.ANI_GET_QUESTION)
    if r.status_code != requests.codes.ok:
        Result.Ani_Answer = Status.error
        return
    token = r.json().get('token')
    error = r.json().get('error')
    message = r.json().get('msg')
    if error == 1:
        Result.Ani_Answer = Status.done
        Result.Ani_Answer_Msg = message
        return
    if token == None:
        Result.Ani_Answer = Status.error
        return
    data = { 'token': token, 'ans': ans }
    r = session.post(Api.ANI_ANS_QUESTION, data = data)
    if r.status_code != requests.codes.ok:
        Result.Ani_Answer = Status.error
        return
    ok = r.json().get('ok')
    gift = r.json().get('gift')
    if ok == 1:
        Result.Ani_Answer = Status.yes
        Result.Ani_Answer_Msg = gift
    else:
        Result.Ani_Answer = Status.error

def GuildSignin():
    r = session.get(Api.GUILD_MY_GUILD)
    if r.status_code != requests.codes.ok:
        Result.Guild_Signin = Status.error
        return
    try:
        guild = r.json().get('data').get('list')[0]
        Result.Guild = guild
    except:
        Result.Guild_Signin = Status.error
        return
    gsn = guild.get('sn')
    data =  { 'gsn': gsn }
    data.update(bahamutCsrfToken)
    r = session.post(Api.GUILD_SIGN, data = data)
    if r.status_code != requests.codes.ok:
        Result.Guild_Signin = Status.error
        return
    try:
        data = r.json().get('data')
        statusCode = data.get('statusCode')
        message = data.get('message')
        if statusCode != None:
            if statusCode:
                Result.Guild_Signin = Status.yes
            else:
                Result.Guild_Signin = Status.done
            Result.Guild_Signin_Msg = message
    except:
        Result.Guild_Signin = Status.error

def GetSummary():
    text = ''
    user = Result.Profile
    guild = Result.Guild
    if user.get('login'):
        text += 'ℹ 帳號資訊\n'
        text += f'🔹 巴幣：{user.get("gold")}\n'
        text += f'🔹 GP：{user.get("gp")}\n'
        text += f'🔹 LV{user.get("level")} / {user.get("race")} / {user.get("career")}\n'
        text += f'🔹 簽到天數：{user.get("signDays")}\n'
        text += f'🔹 上次簽到：{user.get("lastSign")}\n\n'

    if Result.Signin != Status.no:
        if Result.Signin == Status.error: text += '❌ 主頁簽到\n'
        if Result.Signin == Status.yes:   text += f'✅ 主頁簽到\n_{Result.Signin_Msg}_\n'
        if Result.Signin == Status.done:  text += '🔔 主頁簽到\n'
    if Result.Signin_AD != Status.no:
        if Result.Signin_AD == Status.error: text += '❌ 主頁加倍\n'
        if Result.Signin_AD == Status.yes:   text += f'✅ 主頁加倍\n_{Result.Signin_AD_Msg}_\n'
        if Result.Signin_AD == Status.done:  text += '🔔 主頁加倍\n'
    if Result.Guild_Signin != Status.no:
        if Result.Guild_Signin == Status.error: text += f'❌ 公會簽到 ({guild.get("title")})\n'
        if Result.Guild_Signin == Status.yes:   text += f'✅ 公會簽到 ({guild.get("title")})\n_{Result.Guild_Signin_Msg}_\n'
        if Result.Guild_Signin == Status.done:  text += f'🔔 公會簽到 ({guild.get("title")})\n'
    if Result.Ani_Answer != Status.no:
        if Result.Ani_Answer == Status.error: text += '❌ 動漫瘋答題\n'
        if Result.Ani_Answer == Status.yes:   text += f'✅ 動漫瘋答題\n_{Result.Ani_Answer_Msg}_\n'
        if Result.Ani_Answer == Status.done:  text += '🔔 動漫瘋答題\n'
    return text

def GetSummary_Dict():
    account_info = {}
    singin_result = {}
    user = Result.Profile
    guild = Result.Guild
    if user.get('login'):
        account_info['gold'] = user.get('gold')
        account_info['gp'] = user.get('gp')
        account_info['level'] = user.get('level')
        account_info['race'] = user.get('race')
        account_info['career'] = user.get('career')
        account_info['signDays'] = user.get('signDays')
        account_info['lastSign'] = user.get('lastSign')
    
    if Result.Signin != Status.no:
        if Result.Signin == Status.error: singin_result['signin'] = ':x: 錯誤'
        if Result.Signin == Status.yes:
            singin_result['signin'] = ':white_check_mark: 成功' + '\n' + Result.Signin_Msg
        if Result.Signin == Status.done:  singin_result['signin'] = ':bell: 已完成'
    if Result.Signin_AD != Status.no:
        singin_result['guild_title'] = guild.get('title')
        if Result.Signin_AD == Status.error:
            singin_result['signin_ad'] = ':x: 錯誤'
        if Result.Signin_AD == Status.yes:
            singin_result['signin_ad'] = ':white_check_mark: 成功' + '\n' + Result.Signin_AD_Msg
        if Result.Signin_AD == Status.done:  singin_result['signin_ad'] = ':bell: 已完成'
    if Result.Guild_Signin != Status.no:
        if Result.Guild_Signin == Status.error: singin_result['guild_signin'] = ':x: 錯誤'
        if Result.Guild_Signin == Status.yes:
            singin_result['guild_signin'] = ':white_check_mark: 成功' + '\n' + Result.Guild_Signin_Msg
        if Result.Guild_Signin == Status.done:  singin_result['guild_signin'] = ':bell: 已完成'
    if Result.Ani_Answer != Status.no:
        if Result.Ani_Answer == Status.error: singin_result['ani_answer'] = ':x: 錯誤'
        if Result.Ani_Answer == Status.yes:
            singin_result['ani_answer'] = ':white_check_mark: 成功' + '\n' + Result.Ani_Answer_Msg
            singin_result['ani_answer_msg'] = Result.Ani_Answer_Msg
        if Result.Ani_Answer == Status.done:  singin_result['ani_answer'] = ':bell: 已完成'
    return account_info, singin_result
 
def TG_SendMessage(text):
    try:
        r = requests.get(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT}&parse_mode=Markdown&text={text}')
    except:
        pass

def Discord_SendEmbed(account_info: dict, singin_result: dict):
    try:
        payload = {
            'username': '巴哈姆特自動簽到機器人',
            'avatar_url': 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
            'content': '',
            'embeds': [{
                'title': '帳號資訊',
                'description': '',
                'color': 0x0099AF,
                'fields': [
                    {'name': '巴幣', 'value': account_info['gold'], 'inline': True},
                    {'name': 'GP', 'value': account_info['gp'], 'inline': True},
                    {'name': 'LV', 'value': account_info['level'], 'inline': True},
                    {'name': '種族', 'value': account_info['race'], 'inline': True},
                    {'name': '簽到天數', 'value': account_info['signDays'], 'inline': True},
                    {'name': '上次簽到', 'value': account_info['lastSign'], 'inline': True}
                    ],
                'footer': {'text': '更新時間'},
                'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'thumbnail': {'url': Result.Profile.get('avatar')},
                'author': {'name': Result.Profile.get('userid'), 'url': Result.Profile.get('avatar_s'), 'icon_url': Result.Profile.get('avatar_s')} },
                {'title': '簽到資訊',
                'description': '',
                'color': 0x0099AF,
                'fields': [
                    {'name': '主頁簽到', 'value': singin_result['signin'], 'inline': True},
                    {'name': '公會簽到', 'value': singin_result['guild_signin'], 'inline': True},
                    {'name': '動漫瘋答題', 'value': singin_result['ani_answer'], 'inline': True}
                    ],
                'footer': {'text': '更新時間'},
                'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
            ]
        }
        r = requests.post(f'{DISCORD_WEBHOOK}', json=payload)
    except:
        pass

if __name__ == "__main__":

    if BAHA_USERNAME == None or BAHA_PASSWORD == None:
        assert False, '請設定巴哈登入資訊'

    if BAHA_COOKIES != None:
        try:
            cookie = base64.b64decode(BAHA_COOKIES).decode("UTF-8")
            requests.utils.add_dict_to_cookiejar(session.cookies, json.loads(cookie))
        except :
            pass

    Result.Login = CheckLogin()
    Result.Need_2FA = (Check2FA() == 1)
    if not Result.Login:
        Result.Login, message = Login()
        assert Result.Login, message

    Profile()
    UpdateCookie()

    Signin()
    Signin_AD()
    AniAnswer()
    GuildSignin()

    text = GetSummary()
    account_info, singin_result = GetSummary_Dict()
    Discord_SendEmbed(account_info, singin_result)
    if datetime.datetime.now().hour < 3:
        TG_SendMessage(text)
        # Discord_SendEmbed(account_info, singin_result)
    print(text) 
    sys.exit(0)
