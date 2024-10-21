import dotenv, asyncio, quart, hypercorn, sqlite3, a2s, time
from quart import request, redirect, url_for, render_template, send_from_directory
from PIL import Image, ImageFont, ImageDraw

dotenv.load_dotenv()

app = quart.Quart(__name__)
db = sqlite3.connect("data.db")
cur = db.cursor()

is_up = True
banrand = 0

@app.before_serving
async def startup():
    app.add_background_task = asyncio.ensure_future(fetch_servers())

@app.after_serving
async def shutdown():
	global is_up
	is_up = False
	db.close()

@app.route('/')
async def index():
	cur.execute("UPDATE HITS SET hits = hits + 1")
	db.commit()
	cur.execute("SELECT hits FROM HITS")
	return await render_template('index.html', hits=cur.fetchone()[0])

@app.route('/about')
async def about():
	return await render_template('about.html')

@app.route('/eli')
async def sona():
	return await render_template('eli.html')

@app.route('/servers')
async def servers():
	return await render_template('servers.html', br=banrand)

@app.route('/gmod')
async def gmod():
	return await render_template('servers/gmod.html', br=banrand)

@app.route('/tf2')
async def tf2():
	return await render_template('servers/tf2.html', br=banrand)

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

@app.route('/credits')
async def credits():
	return await render_template('credits.html')

@app.route('/motd')
async def htmlmotd():
	return await render_template('etc/motd.html')

@app.route('/index.html')
@app.route('/home')
async def index_redirect():
	return redirect(url_for('index'), code=301)

@app.route('/trashbot')
@app.route('/sillybot')
@app.route('/elibot')
async def trashbot_redirect():
	return redirect(url_for('sillybot'), code=301)

@app.route('/sona')
@app.route('/fursona')
async def sona_redirect():
	return redirect(url_for('sona'), code=301)

@app.route('/homunculus')
async def homunculus():
	return await send_from_directory(app.static_folder, "img/homunculus.jpg")

@app.errorhandler(404)
@app.errorhandler(500)
async def error_handling(error):
	response = quart.Response(await render_template('etc/error.html', errors={
		404: ["[404] page not found", "the url youre trying to access does not exist! you likely followed a dead link or typed something wrong"],
		500: ["[500] internal server error", "somewhere along the way there was an error processing your request. if this keeps happening, please get in contact",],
	}, error=error,), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root():
	return await send_from_directory(app.static_folder, request.path[1:])

serverlist = {
	"gmod": {"game": "gmod", "name": "eli gmod server", "port": 27015},
	"sandbox": {"game": "gmod", "name": "eli sandbox server", "port": 27017},
	"tf2": {"game": "tf2", "name": "eli tf2 server", "port": 27016},
}

async def fetch_servers():
	global banrand
	while is_up:
		for server in serverlist:
			try:
				srv = a2s.info(("play.elisttm.space", serverlist[server]['port']))
				img = Image.open(f"static/img/servers/template-{serverlist[server]['game']}.png")
				draw = ImageDraw.Draw(img)
				draw.text((160, 1), f"{srv.player_count}/{srv.max_players}", "white", ImageFont.truetype("static/Verdana-Bold.ttf", 11))
				draw.text((160, 15.5), (srv.map_name[:16] + " ...") if len(srv.map_name) > 16 else srv.map_name, "white", ImageFont.truetype("static/Arial.ttf", 10))
			except Exception as e:
				print(server, e)
				img = Image.open("static/img/servers/template-offline.png")
				draw = ImageDraw.Draw(img)
			draw.text((34, 15.5), f"play.elisttm.space:{serverlist[server]['port']}", "white", ImageFont.truetype("static/Arial.ttf", 10))
			draw.text((34, 1), serverlist[server]['name'], "white", ImageFont.truetype("static/Verdana-Bold.ttf", 11))
			img.save(f"static/img/servers/banner-{server}.png")
		banrand = time.time_ns()
		print("server banners refreshed!")
		await asyncio.sleep(200)

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:7575"]
app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
