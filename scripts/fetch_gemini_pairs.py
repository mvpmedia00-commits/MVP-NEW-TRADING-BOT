import ccxt

gemini = ccxt.gemini()
pairs = list(gemini.load_markets().keys())
for pair in pairs:
    print(pair)