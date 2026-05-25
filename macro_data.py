import config, requests

def get_macro_score(symbol):
    # Use FRED API for interest rate differential
    if not config.FRED_API_KEY: return 0
    try:
        # Get US interest rate (DFF)
        us_rate = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={config.FRED_API_KEY}&file_type=json&sort_order=desc&limit=1").json()['observations'][0]['value']
        us_rate = float(us_rate)
        # Placeholder: compare with EUR rate
        return 0
    except: return 0
