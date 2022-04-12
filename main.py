import quart, asyncio, hypercorn
from quart import redirect, url_for

app = quart.Quart(__name__)

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
async def gmod_shortcut():
	return await quart.render_template('extra/gmod.html')

@app.route('/gmodload')
@app.route('/tf2motd')
@app.route('/srcmotd')
async def source_motd(): 
	return await quart.render_template('extra/sourcemotd.html')

@app.route('/sitemap.xml')
@app.route('/robots.txt')
async def static_from_root(): 
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

@app.route('/trashbot')
async def trashbot_redirect(): 
  return redirect(url_for('elibot'), code=301)

@app.route('/sona')
async def sona_redirect(): 
  return redirect(url_for('sona'), code=308)

@app.errorhandler(403)
async def forbidden(error): 
	return await quart.render_template('extra/error.html', e=["[403] access denied","you do not have the proper authorization to view this page"]), 403

@app.errorhandler(404)
async def page_not_found(error): 
	return await quart.render_template('extra/error.html', e=["[404] page not found",'the url youre trying to access does not exist, either i screwed something up or you got the wrong link']), 404

@app.errorhandler(500)
async def internal_server(error): 
	return await quart.render_template('extra/error.html', e=["[500] internal server error","somewhere along the way i screwed something up and there was an error in processing your request",]), 500

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
