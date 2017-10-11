import feedparser
import json
import urllib2
import urllib

from flask import render_template
from flask import Flask
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'https://rss.cnn.com/rss/edition.rss',
			 'fox': 'https://feeds.foxnews.com/foxnews/latest',
			 'iol': 'https://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication': 'bbc',
			'city': 'London, UK',
			'currency_from': 'GBP',
			'currency_to': 'USD'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=1bce807ab2a172f4da8a4811f814223e"

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=9b494778413c471e8cb8644d1e7e1e94"

@app.route("/")
def home():
	#get castomized headlines, based on user input or default
	publication = get_val_from_request_or_default('publication')
	articles = get_news(publication)

	#get castomized weather
	city = get_val_from_request_or_default('city')
	weather = get_weather(city)

	#get castomized currency
	currency_from = get_val_from_request_or_default('currency_from')
	currency_to = get_val_from_request_or_default('currency_to')
	rate, currencies = get_rate(currency_from, currency_to)

	return render_template("home.html", 
		articles = articles, 
		weather = weather, 
		rate = rate,
		currency_from = currency_from,
		currency_to = currency_to,
		currencies = sorted(currencies))

def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS['publication']
	else:
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']

def get_weather(query):
	api_url = WEATHER_URL
	query = urllib.quote(query)
	url = api_url.format(query)
	data = urllib2.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather =   {"description": parsed["weather"][0]["description"],
					"temperature": parsed["main"]["temp"],
					"city": parsed["name"],
					"country": parsed['sys']['country']
					}
	return weather

def get_rate(frm, to):
	all_currency = urllib2.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())

def get_val_from_request_or_default(val_name):
	val = get_val_from_request(val_name)
	if not val:
		val = DEFAULTS[val_name]
	return val

def get_val_from_request(val_name):
	return request.args.get(val_name)

if __name__ == "__main__":
	app.run(port=5000, debug=True)
