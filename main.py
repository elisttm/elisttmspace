import os, asyncio, quart, hypercorn, sqlite3, a2s, time
from quart import request, redirect, url_for, render_template, send_from_directory
from PIL import Image, ImageFont, ImageDraw

path = os.path.dirname(os.path.realpath(__file__))+'/' # this is really stupid
is_up = True
banrand = 0

db = sqlite3.connect(f"{path}/data.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS HITS (hits)")

app = quart.Quart(__name__)

@app.before_serving
async def startup():
    app.add_background_task = asyncio.ensure_future(fetch_servers())

@app.after_serving
async def shutdown():
	global is_up
	is_up = False
	db.close()

@app.route('/')
async def _index():
	try:
		cur.execute("UPDATE HITS SET hits = hits + 1")
		cur.execute("SELECT hits FROM HITS")
		db.commit()
		hits = cur.fetchone()[0]
	except:
		hits = None
	return await render_template('index.html', hits=hits)

@app.route('/about')
async def _about():
	return await render_template('about.html')

@app.route('/eli')
async def _sona():
	return await render_template('eli.html')

@app.route('/servers')
async def _servers():
	return await render_template('servers.html', time=server_data["time"])

@app.route('/gmod')
async def _gmod():
	return await render_template('servers/gmod.html', time=server_data["time"])

@app.route('/tf2')
async def _tf2():
	return await render_template('servers/tf2.html', time=server_data["time"])

@app.route('/bot')
async def _sillybot():
	return await render_template('bot.html')

@app.route('/pack')
async def _pack():
	return await render_template('pack.html')

@app.route('/pages')
async def _pages():
	return await render_template('pages.html')

@app.route('/motd')
async def _motd():
	return await render_template('etc/motd.html')

@app.route('/connect/<game>')
async def _connect(game):
	if game not in servers:
		return quart.abort(404)
	return redirect(f"steam://connect/{server_data['ip']}:{servers[game]['port']}/chungus", code=302)

@app.route('/index.html')
@app.route('/home')
async def redirect_index():
	return redirect(url_for('_index'), code=301)

@app.route('/trashbot')
@app.route('/sillybot')
@app.route('/elibot')
async def redirect_sillybot():
	return redirect(url_for('_sillybot'), code=301)

@app.route('/sona')
@app.route('/fursona')
async def redirect_sona():
	return redirect(url_for('_sona'), code=301)

@app.route('/minecraft')
async def redirect_server():
	return redirect(url_for('_servers'), code=301)

@app.route('/homunculus')
async def homunculus():
	return await send_from_directory(app.static_folder, "img/homunculus.png")

@app.route('/sitemap.xml')
@app.route('/robots.txt')
@app.route('/favicon.ico')
async def static_from_root():
	return await send_from_directory(app.static_folder, request.path[1:])

@app.errorhandler(404)
@app.errorhandler(500)
async def error_handler(error):
	response = quart.Response(await render_template('etc/error.html', errors={
		404: ["[404] page not found", "the url youre trying to access does not exist! you likely followed a dead link or typed something wrong"],
		500: ["[500] internal server error", "somewhere along the way there was an error processing your request. if this keeps happening, please get in contact",],
	}, error=error,), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response


server_data = {"ip": "73.207.108.187", "time": 0}
servers = {
	"gmod": {"game": "gmod", "name": "eli gmod server", "port": 27015},
	"sandbox": {"game": "gmod", "name": "eli sandbox server", "port": 27017},
	"tf2": {"game": "tf2", "name": "eli tf2 server", "port": 27016},
	"hl1": {"game": "hl1", "name": "eli hldm server", "port": 27013},
}

async def fetch_servers():
	global banrand
	while is_up:
		for server in servers:
			try:
				srv = a2s.info((server_data["ip"], servers[server]['port']), 3)
				img = Image.open(f"{path}static/img/servers/template-{servers[server]['game']}.png")
				draw = ImageDraw.Draw(img)
				draw.text((160, 1), f"{srv.player_count}/{srv.max_players}", "white", ImageFont.truetype(f"{path}static/Verdana-Bold.ttf", 11))
				draw.text((160, 15.5), (srv.map_name[:16] + " ...") if len(srv.map_name) > 16 else srv.map_name, "white", ImageFont.truetype(f"{path}static/Arial.ttf", 10))
			except Exception as e:
				print(server, str(e))
				img = Image.open(f"{path}static/img/servers/template-offline.png")
				draw = ImageDraw.Draw(img)
			draw.text((34, 15.5), f"play.elisttm.space:{servers[server]['port']}", "white", ImageFont.truetype(f"{path}static/Arial.ttf", 10))
			draw.text((34, 1), servers[server]['name'], "white", ImageFont.truetype(f"{path}static/Verdana-Bold.ttf", 11))
			img.save(f"{path}static/img/servers/banner-{server}.png")
		server_data["time"] = time.time_ns()
		await asyncio.sleep(60)


hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:7575"]
app.jinja_env.cache = {}

if __name__ == '__main__':
	asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
