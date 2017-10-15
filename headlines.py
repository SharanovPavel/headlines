import datetime
import feedparser
import json
import urllib2
import urllib

from flask import make_response
from flask import render_template
from flask import Flask
from flask import request

app = Flask(__name__)

#Available RSS channels
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'http://rss.cnn.com/rss/edition.rss',
			 'fox': 'http://feeds.foxnews.com/foxnews/latest',
			 'iol': 'http://www.iol.co.za/cmlink/1.640'}

#Default values of data
DEFAULTS = {'publication': 'bbc',
			'city': 'London, UK',
			'currency_from': 'GBP',
			'currency_to': 'USD'}

#Weather API's URL
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=1bce807ab2a172f4da8a4811f814223e"

#Currency API's URL
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=9b494778413c471e8cb8644d1e7e1e94"

#Main method, that service home page of that app
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

	response = make_response(render_template("home.html", 
		articles = articles, 
		weather = weather, 
		rate = rate,
		currency_from = currency_from,
		currency_to = currency_to,
		currencies = sorted(currencies)))

	add_many_vals_to_cookies(response, {
		"publication": publication,
		"city": city,
		"currency_from": currency_from,
		"currency_to": currency_to
		})
	return response

#Get RSS data
def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS['publication']
	else:
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']

#Get weather data
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

#Get currency data
def get_rate(frm, to):
	all_currency = urllib2.urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())

#Get value from request(including cookies) or DEFAULTS
def get_val_from_request_or_default(val_name):
	return get_val_from_request(val_name) or DEFAULTS[val_name]

#Get value from request(including cookies)
def get_val_from_request(val_name):
	return request.args.get(val_name) or get_val_from_cookies(val_name)

#Get value from request's cookies
def get_val_from_cookies(val_name):
	return request.cookies.get(val_name)

#Add values from dictionary to request's cookies
def add_many_vals_to_cookies(response, dict, expires = None):
	expires = expires or get_cookies_expires_date()
	for item in dict.items():
		add_val_to_cookies(response, item[0], item[1], expires)

#Add values to request's cookies
def add_val_to_cookies(response, val_name, val, expires = None):
	response.set_cookie(
		val_name, 
		val, 
		expires = expires or get_cookies_expires_date())

def get_cookies_expires_date():
	return datetime.datetime.now() + datetime.timedelta(days = 365)

#App entry point
if __name__ == "__main__":
	app.run(port=5000, debug=True)
