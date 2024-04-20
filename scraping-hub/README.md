# Yahooアクセスランキング

## ローカルでのYahooアクセスランキングデータ取得・集計

### 前提条件

- `scraping-hub/.env.example`をコピーして`scraping-hub/.env`を作成

- `.env`にSlack情報を記載

```
YAHOO_ACCESS_RANKING_OAUTH_TOKEN=
YAHOO_ACCESS_RANKING_CHANNEL_ID=
```

### 手順

1. **Dockerの起動**  
   `$ docker-compose up -d`

2. **Yahooアクセスランキングデータの取得**  
   `$ python -m scraping_hub.yahoo_access_ranking.get_yahoo_ranking`

3. **データの集計とSlackへの通知**  
   `$ python -m scraping_hub.yahoo_access_ranking.aggregate_yahoo_ranking`