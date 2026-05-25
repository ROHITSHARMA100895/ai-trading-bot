from pytrends.request import TrendReq
import config

def google_trend(symbol):
    try:
        pytrends = TrendReq()
        kw = symbol[:3] if len(symbol)>3 and symbol.isalpha() else symbol
        pytrends.build_payload([kw], timeframe='now 7-d')
        df = pytrends.interest_over_time()
        if not df.empty:
            change = (df[kw].iloc[-1] - df[kw].iloc[0]) / df[kw].iloc[0] if df[kw].iloc[0] else 0
            return max(-1, min(1, change))
    except: pass
    return 0

def reddit_score(symbol):
    if not config.REDDIT_CLIENT_ID: return 0
    try:
        import praw
        reddit = praw.Reddit(client_id=config.REDDIT_CLIENT_ID, client_secret=config.REDDIT_CLIENT_SECRET, user_agent=config.REDDIT_USER_AGENT)
        posts = reddit.subreddit('wallstreetbets+stocks+investing+trading').search(symbol, limit=15)
        ups = sum(p.ups - p.downs for p in posts)
        count = sum(1 for _ in posts)
        if count == 0: return 0
        avg = ups / count
        return max(-1, min(1, avg / 50))
    except: return 0

def satellite_score(symbol):
    """Use Sentinel Hub free tier to get NDVI for parking lot detection (simplified)."""
    if not config.SENTINEL_HUB_INSTANCE_ID: return 0
    # Placeholder: fetch true-color image and count cars (heavy, skip for now)
    return 0

def get_alternative_score(symbol):
    return google_trend(symbol) * 0.4 + reddit_score(symbol) * 0.4 + satellite_score(symbol) * 0.2
