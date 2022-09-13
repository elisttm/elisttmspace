import os, quart, asyncio, hypercorn, pymongo, json, datetime
from pprint import pprint
from markupsafe import Markup, escape
from quart import redirect, url_for, request

app = quart.Quart(__name__)
db = pymongo.MongoClient(os.environ['mongo'])['elisttmspace']
dba = db['analytics']

print(db['hitcount'].find_one({})['hits'])

def is_crawler(headers):
	return "elisttm.space" not in str(headers.get("Host")) or "bot" in str(headers.get("User-Agent")).lower() or "crawl" in str(headers.get("User-Agent")).lower() or headers.get("Accept") == None

@app.after_request 
async def after_request_callback(response):
	try:
		time = datetime.datetime.utcnow()
		print(time.strftime("%m-%d-%y %I:%M:%S %p"))
		if not is_crawler(request.headers) and "static" not in request.path and "." not in request.path:
			headers = {x:request.headers[x] for x in ["Date","Referer","User-Agent","Sec-Ch-Ua","Sec-Ch-Ua-Platform","X-Forwarded-For"] if x in request.headers}
			headers['date'] = time
			headers['path'] = request.path
			dba.insert_one(headers)
			print(headers)
		else:
			print("the following request was blocked")
		print(request.path,"\n",request.headers)
		print('')
	except Exception as e:
		print(e)
	return response

@app.route('/')
async def index(): 
	hits = db['hitcount'].find_one_and_update({}, {"$inc":{"hits":1}})['hits']+1 if not is_crawler(request.headers) else db['hitcount'].find_one({})['hits']
	return await quart.render_template('index.html', hits=hits)

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
