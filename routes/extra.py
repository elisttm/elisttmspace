from __main__ import app, quart, a, Markup

@app.errorhandler(403)
async def forbidden(error): 
	return await quart.render_template('extra/errors.html', e=["[403] access denied","you do not have the proper authorization to view this page"], no_analytics=True, a=a), 403

@app.errorhandler(404)
async def page_not_found(error): 
	return await quart.render_template('extra/errors.html', e=["[404] page not found",Markup('the url youre trying to access does not exist, either i screwed something up or you got a dead link')], no_analytics=True, a=a), 404

@app.errorhandler(500)
async def internal_server(error): 
	return await quart.render_template('extra/errors.html', e=["[500] internal server error","somewhere along the way one of us (probably me) screwed something up and the server could not handle your request",], no_analytics=True, a=a), 500


@app.route('/gmodload')
@app.route('/tf2motd')
async def source_motd(): 
	return await quart.render_template('extra/sourcemotd.html')