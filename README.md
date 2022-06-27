# 巴哈姆特 每日簽到
請先 Fork 該專案到您自己的 Github 帳號

該專案需要加入以下的 Actions secrets
* ```BAHA_PASSWORD``` _巴哈姆特帳號_
* ```BAHA_USERNAME``` _巴哈姆特密碼_
* ```GH_TOKEN``` _Github API Token_
* ```TG_CHAT``` _Telegram Chat_Id_ *非必要*
* ```TG_TOKEN``` _Telegram Bot Token_ *非必要*
* ```DISCORD_WEBHOOK``` _Discord Webhook URL_ *非必要*

> ![sshot-4](https://user-images.githubusercontent.com/7044575/175803790-74da35ac-4a33-48c6-b103-0b9169977752.png)

### Github API Token
請到以下網址申請一組 API Token (https://github.com/settings/tokens)

申請後請馬上紀錄 API Token，跳到其他頁面後就不可看到了

> ![sshot-3](https://user-images.githubusercontent.com/7044575/175803719-4d521d2c-8124-4e56-b090-f526acda911c.png)

### Telegram Bot
需要 Telegram 傳送通知訊息請自行申請 Telegram Bot，本文檔不解釋如何操作

> ```TG_TOKEN``` 從 Telegram Bot Father 取得 API Token
>
> ```TG_CHAT``` 可從以下網址取得 ID，請自行帶入 Bot Token
>
> https://api.telegram.org/bot<TG_TOKEN>/getUpdates

### Discord Webhook
需要 Discord 傳送通知訊息請自行建立 Discord Webhook 網址，本文檔不解釋如何操作

> ```DISCORD_WEBHOOK``` Discord Channel -> 頻道設定 -> 整合 -> 建立webhook -> 複製 Webhook 網址

# 開始使用
請到自己的 BahamutDailySignin 專案 -> Actions -> Signin

> ![sshot-5](https://user-images.githubusercontent.com/7044575/175804124-830fd1e4-e356-43cd-a586-74996e660381.png)

如果有設定兩階段驗證登入，請在 2FA Code 填入驗證碼 (注意時效性)

輸入後即可點選 Run Workflow 開始第一次手動執行

等待 Workflow 成功執行後會顯示執行紀錄並儲存 Cookies

往後的排程執行就會自動登入並實時更新 Cookies

> ![sshot-6](https://user-images.githubusercontent.com/7044575/175804266-012c3480-9627-4767-a0fb-b2fc9aac2385.png)

若有其他問題歡迎提交 Issues 並在底下討論
