# oura-omi-plugin
Access oura data from your Omi/Friend device https://www.omi.me/


## connet and deploy on heroku

```
heroku login
heroku create oura-omi-plugin

```

Set env variables in heroku
```
heroku config:set OURA_PERSONAL_TOKEN=your_token_here
heroku config:set OPENAI_API_KEY=your_key_here
```

Deploy
```
git push heroku main
```

Open app
```
heroku open
```
