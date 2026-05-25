import os, requests, config, subprocess

def update_models():
    if not config.MODEL_UPDATE_URL: return
    print("🔄 Checking model updates...")
    for f in ["xgb_EURUSD.pkl","xgb_GBPUSD.pkl","xgb_USDJPY.pkl","xgb_BTC_USD.pkl","xgb_ETH_USD.pkl"]:
        url = config.MODEL_UPDATE_URL + "models/" + f
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                os.makedirs("models/saved", exist_ok=True)
                with open(f"models/saved/{f}", "wb") as file:
                    file.write(r.content)
                print(f"✅ {f} updated")
        except Exception as e:
            print(f"❌ {f}: {e}")

def update_code():
    if not config.CODE_UPDATE_REPO: return
    try:
        subprocess.run(["git", "-C", os.path.dirname(__file__), "pull", "origin", "main"], check=True)
        print("✅ Code updated")
    except Exception as e:
        print("Code update failed:", e)
