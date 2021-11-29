import yfinance as yf
from airtable import Airtable

AIRTABLE_BASE_ID = ''
AIRTABLE_TABLE_NAME = ''
AIRTABLE_API_KEY = ''

table = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)
records = table.get_all()

def get_market_data(ticker):
    res = yf.Ticker(ticker)
    return res.info

# Ger Eur to USD
res = yf.Ticker('EURUSD=X')
eur2usd = res.info['regularMarketPrice']

for record in records:
    # handle special cases
    # EUR, Mintos
    if record['fields']['Type'] == 'Other':
        if record['fields']['Product'] in ['EUR', 'Mintos']:
            # Get usd value
            airtable_fields = {
              'Price USD': record['fields']['Price EUR'] * eur2usd,
            }
            table.update(record['id'], airtable_fields)
        continue

    ticker = record['fields']['Ticker']
    market_data = get_market_data(ticker)
    if not market_data.get('currency', None):
        print('missing currency',ticker, market_data)
        continue
    if market_data['currency'] == 'EUR':
        price_eur = market_data['regularMarketPrice']
        price_usd = price_eur * eur2usd
    elif market_data['currency'] == 'USD':
        price_usd = market_data['regularMarketPrice']
        price_eur = price_usd / eur2usd
    else:
        raise('ERROR: unknown currency')
    airtable_fields = {
        'Price USD': price_usd,
        'Price EUR': price_eur,
        'Currency': market_data['currency'],
        '200 days average': market_data.get('twoHundredDayAverage'),
        'Price to Book': market_data.get('priceToBook'),
        'Held by Insiders': market_data.get('heldPercentInsiders')
    }
    table.update(record['id'], airtable_fields)
    
    print(record['fields']['Ticker'] + ' - ' + str( market_data.get('regularMarketPrice', 'NORES')))

