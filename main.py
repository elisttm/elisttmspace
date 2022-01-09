import quart, os, re, asyncio, hypercorn
from markupsafe import Markup, escape

app = quart.Quart(__name__)
#app.secret_key=os.environ['secret']

# constant vars for all pages
class a():
	dsfjksda = 'a'


	# silly formatting
	def md(text, urls=False):
		if urls:
			for x in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
				text = text.replace(x, f'<a href="{x}">{x}</a>')
		for x in re.findall(r'\[(img|video|audio|iframe):(.*?)\]', text):
			if x[0] == 'video' or x[0] == 'audio':
				replacement = f'<{x[0]} controls><source src="{x[1]}" type="{(x[1].rsplit(".", 1))[1]}"></{x[0]}>'
			elif x[0] == 'img':
				replacement = f'<img src="{x[1]}"/>'
			elif x[0] == 'iframe':
				replacement = f'<iframe src="{x[1]}" frameborder="0"></iframe>'
			text = text.replace(f'[{x[0]}:{x[1]}]', replacement)
		for x in re.findall(r'\[(a|c|style):(.*?):(.*?)\]', text):
			if x[0] == 'a':
				replacement = f'<a href="{x[1]}">{x[2]}</a>'
			elif x[0] == 'c':
				replacement = f'<span style="color:{x[1]}">{x[2]}</span>'
			elif x[0] == 'style':
				replacement = f'<span style="{x[1]}">{x[2]}</span>'
			text = text.replace(f'[{x[0]}:{x[1]}:{x[2]}]', replacement)
		for x in re.findall(r'\[(h2|h3|b|i|u|s|sup|sub):(.*?)\]', text):
			text = text.replace(f'[{x[0]}:{x[1]}]', f'<{x[0]}>{x[1]}</{x[0]}>')
		for x in re.findall(r'\[(br|h1)\]', text):
			text = text.replace(f'[{x[0]}]', f'<{x[0]}>')
		return Markup(text)

sitemap_timeformat = '%Y-%m-%d'
sitemap_stuff = (
	['', 1.0],
	['eli', 0.9, ''],
)

urlset = ''
for page in sitemap_stuff:
	lastmod = f'		<lastmod>{page[2]}</lastmod>\n' if len(page) >= 3 else ''
	urlset += f"""	<url>\n		<loc>https://elisttm.space/{page[0]}</loc>\n		<priority>{page[1]}</priority>\n		<changefreq>daily</changefreq>\n{lastmod}</url>\n"""
sitemap = f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n{urlset}</urlset>'

@app.route('/sitemap.xml')
async def sitemap_xml(): 
	return await quart.Response(sitemap, mimetype='text/xml')

@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root(): 
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:8080"]

if __name__ == '__main__':
	import routes
	#app.run(host="0.0.0.0", port=8080, use_reloader=True) # testing
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig)) # hypercorn