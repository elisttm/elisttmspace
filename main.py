import os, asyncio, quart, hypercorn
from quart import request, redirect, url_for, render_template, send_from_directory

app = quart.Quart(__name__)
#db = pymongo.MongoClient(os.environ['mongo'])['elisttmspace']

#visitors = {}

#async def analytics():
#	try:
#		print("\n",request.path,"\n",request.headers)
#		if "elisttm.space" not in request.url or crawlerdetect.CrawlerDetect(request.headers).isCrawler() or "bot" in request.headers.get("User-Agent","").lower():
#			return
#		timestamp = int(time.time())
#		referer = request.headers.get("Referer")
#		ip = request.headers.get("X-Forwarded-For")
#		if referer and "elisttm.space" not in referer and "t.co" not in referer:
#			db["stats"].update_one({"_id":"referers"}, {"$addToSet":{"urls":referer}})	
#		if ip and ("static" not in request.path and "." not in request.path) and (ip not in visitors or visitors[ip]+3600 < timestamp):
#			visitors[ip] = timestamp
#			print(db['stats'].find_one_and_update({"_id":"hits"}, {"$inc":{"hits":1}})['hits'], visitors)
#	except Exception as e:
#		print(e)
			
#@app.after_request 
#async def after_request_callback(response):
#	app.add_background_task(analytics)
#	return response

@app.route('/')
async def index(): 
	return await render_template('index.html')#, hits=db['stats'].find_one({"_id":"hits"})['hits'])

@app.route('/about')
async def about():
	return await render_template('about.html')

@app.route('/eli')
async def sona():
	return await render_template('sona.html')	

@app.route('/pages')
async def pagelist():
	return await render_template('pages.html')

@app.route('/pack')
async def pack():
	return await render_template('pack.html')

@app.route('/bot')
async def sillybot():
	return await render_template('bot.html')

@app.route('/minecraft')
async def minecraft():
	return await render_template('extra/minecraft.html')

@app.route('/gmod')
async def gmod():
	return await render_template('extra/gmod.html')

@app.route('/gmodload')
@app.route('/tf2motd')
@app.route('/srcmotd')
async def source_motd(): 
	return await render_template('extra/sourcemotd.html')

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
	response = quart.Response(await render_template('extra/error.html', errors=errors, error=error), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root(): 
	return await send_from_directory(app.static_folder, request.path[1:])

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]
app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
