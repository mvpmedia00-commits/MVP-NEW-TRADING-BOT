import ccxt

gemini = ccxt.gemini({
    'apiKey': 'aaccount-12E3SLAaqfzQGf8cIHRa',
    'secret': 'DwLgoxej3WTqqsbErHobyzfFGv3',
    'test': True
})
try:
    balance = gemini.fetch_balance()
    print('Balance:', balance)
except Exception as e:
    print('Error:', e)
