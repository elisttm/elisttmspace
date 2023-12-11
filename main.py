import os, asyncio, quart, hypercorn
from quart import request, redirect, url_for, render_template, send_from_directory

app = quart.Quart(__name__)

@app.route('/')
async def index():
	return await render_template('index.html')

@app.route('/about')
async def about():
	return await render_template('about.html')

@app.route('/eli')
async def sona():
	return await render_template('eli.html')

@app.route('/servers')
async def servers():
	return await render_template('servers.html')

@app.route('/gmod')
async def gmod():
	return await render_template('servers/gmod.html')

@app.route('/tf2')
async def tf2():
	return await render_template('servers/tf2.html')

@app.route('/minecraft')
async def minecraft():
	return await render_template('servers/minecraft.html')

@app.route('/bot')
async def sillybot():
	return await render_template('bot.html')

@app.route('/pack')
async def pack():
	return await render_template('pack.html')

@app.route('/pages')
async def pagelist():
	return await render_template('pages.html')

@app.route('/motd')
async def htmlmotd():
	return await render_template('etc/motd.html')

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
	response = quart.Response(await render_template('etc/error.html', errors=errors, error=error), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root():
	return await send_from_directory(app.static_folder, request.path[1:])

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:7575"]
app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
