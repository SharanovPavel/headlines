import feedparser

from flask import Flask

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'https://rss.cnn.com/rss/edition.rss',
			 'fox': 'https://feeds.foxnews.com/foxnews/latest',
			 'iol': 'https://www.iol.co.za/cmlink/1.640'}



@app.route("/")
def bbc():
	return get_news(publication = "bbc")

@app.route("/<publication>")
def get_news(publication):
	feed = feedparser.parse(RSS_FEEDS[publication])
	if len(feed['entries']) > 0: 
		first_article = feed['entries'][0] 
		return """<html>
			<body>
			<h1>Headlines </h1>
			<b>{0}</b> </ br>
			<i>{1}</i> </ br>
			<p>{2}</p> </ br>
			</body>
			</html>""".format(first_article.get("title"), first_article.
			get("published"), first_article.get("summary"))
	else:
		return "There are no news today."

if __name__ == "__main__":
	app.run(port=5000, debug=True)
