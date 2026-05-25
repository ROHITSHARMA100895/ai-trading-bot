import config, requests, json

def call_openrouter(prompt):
    if not config.OPENROUTER_API_KEY: return None
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    models = [config.DEFAULT_MODEL] + config.BACKUP_MODELS
    for m in models:
        try:
            data = {"model": m, "messages": [{"role":"user","content":prompt}], "temperature":0.1, "max_tokens":80}
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content'].strip()
            if '```' in content: content = content.split('```')[1].split('```')[0].strip()
            if content.startswith('json'): content = content[4:].strip()
            print(f"✅ OpenRouter: {m}")
            return json.loads(content)
        except: continue
    return None

def call_groq(prompt):
    if not config.GROQ_API_KEY: return None
    try:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        chat = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=80)
        content = chat.choices[0].message.content
        if '```' in content: content = content.split('```')[1].split('```')[0].strip()
        print("✅ Groq")
        return json.loads(content)
    except: return None

def call_huggingface(text):
    if not config.HUGGINGFACE_API_KEY: return None
    try:
        headers = {"Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}"}
        payload = {"inputs": text[:512]}
        resp = requests.post("https://api-inference.huggingface.co/models/ProsusAI/finbert", headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if isinstance(result, list) and len(result) > 0:
                label = result[0].get('label','')
                score = result[0].get('score',0.7)
                sent = score if 'positive' in label.lower() else (-score if 'negative' in label.lower() else 0)
                return {"score": sent, "confidence": score}
    except: pass
    return None

def get_sentiment(symbol):
    prompt = f"Analyze latest financial news sentiment for {symbol}. Return ONLY JSON: {{'score':-1..1,'confidence':0..1}}. Example: {{'score':0.3,'confidence':0.8}}"
    res = call_openrouter(prompt)
    if res: return float(res['score']), float(res['confidence'])
    res = call_groq(prompt)
    if res: return float(res['score']), float(res['confidence'])
    # Use NewsAPI if key present
    news_text = f"{symbol} market outlook"
    if config.NEWSAPI_KEY:
        try:
            nr = requests.get(f"https://newsapi.org/v2/everything?q={symbol}&apiKey={config.NEWSAPI_KEY}&pageSize=1", timeout=5)
            if nr.status_code==200:
                arts = nr.json().get('articles',[])
                if arts: news_text = arts[0].get('title','') + ". " + arts[0].get('description','')
        except: pass
    res = call_huggingface(news_text)
    if res: return float(res['score']), float(res['confidence'])
    from data_feeds.technicals import get_technical_score
    tech = get_technical_score(symbol)
    if tech > 0.1: return 0.25, 0.7
    elif tech < -0.1: return -0.25, 0.7
    return 0.1, 0.6
