from __main__ import app, quart, a

class pack:
	version = ''


@app.route('/')
@app.route('/extra')
async def index(): 
	return await quart.render_template('index.html', a=a)

@app.route('/eli')
async def sona(): 
	return await quart.render_template('sona.html', a=a)
	
@app.route('/bot')
async def elibot(): 
	return await quart.render_template('elibot.html', a=a)

@app.route('/pages')
async def pagelist(): 
	return await quart.render_template('pages.html', a=a)

@app.route('/pack')
async def pack():
	return await quart.render_template('pack.html', a=a)