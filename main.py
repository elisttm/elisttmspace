import quart, asyncio, hypercorn
from markupsafe import Markup

app = quart.Quart(__name__)

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]

#		main routes

@app.route('/')
async def index(): 
	return await quart.render_template('index.html')

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

#		extra routes

@app.route('/gmodload')
@app.route('/tf2motd')
async def source_motd(): 
	return await quart.render_template('extra/sourcemotd.html')

@app.route('/gmod')
async def gmod_shortcut():
	return await quart.render_template('extra/gmod.html')

#		utility routes

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root(): 
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

@app.errorhandler(403)
async def forbidden(): 
	return await quart.render_template('extra/error.html', e=["[403] access denied","you do not have the proper authorization to view this page"]), 403

@app.errorhandler(404)
async def page_not_found(): 
	return await quart.render_template('extra/error.html', e=["[404] page not found",Markup('the url youre trying to access does not exist, either i screwed something up or you got a dead link')]), 404

@app.errorhandler(500)
async def internal_server(): 
	return await quart.render_template('extra/error.html', e=["[500] internal server error","somewhere along the way one of us (probably me) screwed something up and the server could not handle your request",]), 500

if __name__ == '__main__':
	#app.run(host="0.0.0.0", port=8080, use_reloader=True)
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))