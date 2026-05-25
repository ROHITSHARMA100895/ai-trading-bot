from data_feeds.news_sentiment import get_sentiment
from data_feeds.fundamentals_deep import get_fundamental_score
from data_feeds.technicals import get_technical_score
from data_feeds.alternative_data import get_alternative_score
from data_feeds.order_flow import get_order_flow
from data_feeds.macro_data import get_macro_score
import numpy as np, json, os

WEIGHTS_FILE = "models/saved/ensemble_weights.json"
default_weights = np.array([0.25,0.20,0.25,0.10,0.10,0.10])  # sent,fund,tech,alt,order,macro

def load_weights():
    if os.path.exists(WEIGHTS_FILE):
        try:
            with open(WEIGHTS_FILE, 'r') as f:
                return np.array(json.load(f)['weights'])
        except: pass
    return default_weights

weights = load_weights()

def get_final_signal(symbol):
    sent_score, sent_conf = get_sentiment(symbol)
    fund_score = get_fundamental_score(symbol)
    tech_score = get_technical_score(symbol)
    alt_score = get_alternative_score(symbol)
    order_score = get_order_flow(symbol)
    macro_score = get_macro_score(symbol)
    scores = [sent_score, fund_score, tech_score, alt_score, order_score, macro_score]
    confs = [sent_conf, 0.7, 0.8, 0.5, 0.5, 0.5]
    final_score = np.dot(weights, scores)
    final_conf = np.average(confs, weights=weights)
    return final_score, final_conf

# Optional: LangChain AGI debate (lightweight)
def agi_debate(symbol):
    """Runs a simple debate using free LLM, returns BUY/SELL/HOLD."""
    # This would be more complex; for now we rely on ensemble
    return None

def should_trade(symbol):
    score, conf = get_final_signal(symbol)
    if conf > 0.25 and abs(score) > 0.05:
        return "BUY" if score > 0 else "SELL"
    return "HOLD"
