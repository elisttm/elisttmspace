import os, quart, asyncio, hypercorn, pymongo
my_secret = os.environ['secret']
from quart import redirect, url_for, request

app = quart.Quart(__name__)
#db = pymongo.MongoClient(os.environ['mongo'])['elisttmspace']

@app.route('/')
async def index(): 
	return await quart.render_template('index.html')

@app.route('/about')
async def about(): 
	return await quart.render_template('about.html')

@app.route('/eli')
async def sona(): 
	return await quart.render_template('sona.html')
	
@app.route('/bot')
async def elibot(): 
	return await quart.render_template('elibot.html')

@app.route('/pages')
async def pagelist(): 
	return await quart.render_template('pages.html')

@app.route('/pack')
async def pack():
	return await quart.render_template('pack.html')

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
  return redirect(url_for('elibot'), code=301)

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
	return await quart.render_template('extra/error.html', errors=errors, error=error), error.code

@app.route('/sitemap.xml')
@app.route('/robots.txt')
async def static_from_root(): 
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]

app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
