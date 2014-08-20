from flask import Flask
from flask.ext.mongoengine import MongoEngine
# If you'd rather use Creole for markup, import Creole instead
from flaskext.markdown import Markdown
# from flaskext.creole import Creole

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': "CareerLog"}
app.config["SECRET_KEY"] = "YourSecretKey"

db = MongoEngine(app)

# Use markdown extension to parse the body of posts, comment out if using
# Creole:
Markdown(app)
# To use creole instead, uncomment the following and set parser_method:
# creole = Creole(app, parser_method='xml')
# NOTE:  possible values for parser_method: xhtml, html, xml, text
#   (from creoleparser.core)


# this filter gives us html up to the first paragraph close tag
@app.template_filter('excerpt')
def excerpt(s):
    return s.split("</p>")[0]

import CareerLog.admin
import CareerLog.views


if __name__ == '__main__':
    app.run()
