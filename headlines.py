import feedparser
from flask import render_template
from flask import Flask

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'https://rss.cnn.com/rss/edition.rss',
			 'fox': 'https://feeds.foxnews.com/foxnews/latest',
			 'iol': 'https://www.iol.co.za/cmlink/1.640'}



@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
	feed = feedparser.parse(RSS_FEEDS[publication])
	if len(feed['entries']) > 0: 
		return render_template("home.html", articles = feed['entries'])
	else:
		return "There are no news today."

if __name__ == "__main__":
	app.run(port=5000, debug=True)
