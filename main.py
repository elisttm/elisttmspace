import os, quart, asyncio, hypercorn, pymongo, time
#from markupsafe import Markup, escape
from quart import redirect, url_for, request

app = quart.Quart(__name__)
db = pymongo.MongoClient(os.environ['mongo'])['elisttmspace']

visitors = {}

print(db['hitcount'].find_one({})['hits'])

def is_crawler(request):
	return "elisttm.space" not in request.url or request.headers.get("X-Is-Bot","true") == "true"

async def analytics():
	print(request.path,"\n",request.headers)
	if "elisttm.space" in request.url and request.headers.get("X-Is-Bot","true") == "false":
		if "elisttm.space" not in request.headers.get("Referer","elisttm.space"):
			db['referers'].insert_one({"referer":request.headers.get("Referer"),"path":request.path})
		ip = request.headers.get("X-Forwarded-For",None); ts = int(time.time())
		if ip and (ip not in visitors or (ip in visitors and visitors[ip]+3600 < ts)):
			print(db['hitcount'].find_one_and_update({}, {"$inc":{"hits":1}})['hits'])
			visitors[ip] = ts
			print(visitors)
			
@app.after_request 
async def after_request_callback(response):
	app.add_background_task(analytics)
	return response

@app.route('/')
async def index(): 
	return await quart.render_template('index.html', hits=db['hitcount'].find_one({})['hits'])

@app.route('/about')
async def about():
	return await quart.render_template('about.html')

@app.route('/eli')
async def sona():
	return await quart.render_template('sona.html')	

@app.route('/pages')
async def pagelist():
	return await quart.render_template('pages.html')

@app.route('/pack')
async def pack():
	return await quart.render_template('pack.html')

@app.route('/bot')
async def sillybot():
	return await quart.render_template('bot.html')

@app.route('/minecraft')
async def minecraft():
	return await quart.render_template('extra/minecraft.html')

@app.route('/gmod')
async def gmod():
	return await quart.render_template('extra/gmod.html')

@app.route('/gmodload')
@app.route('/tf2motd')
@app.route('/srcmotd')
async def source_motd(): 
	return await quart.render_template('extra/sourcemotd.html')

@app.route('/trashbot')
async def trashbot_redirect(): 
  return redirect(url_for('sillybot'), code=301)

@app.route('/sona')
async def sona_redirect(): 
  return redirect(url_for('sona'), code=308)

@app.route('/error')
async def force_error():
	return 0/0

errors = {
	404: ["[404] page not found",'the url youre trying to access does not exist, you probably put the link in wrong or i just messed something up'],
	500: ["[500] internal server error","somewhere along the way there was an error processing your request; if this keeps happening, please get in contact",],
}

@app.errorhandler(404)
@app.errorhandler(500)
async def error_handling(error):
	response = quart.Response(await quart.render_template('extra/error.html', errors=errors, error=error), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root(): 
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]
app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
