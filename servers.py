import os, a2s, mcstatus, time, asyncio
from PIL import Image, ImageFont, ImageDraw

servers = {
    "gmod": {
        "game": "gmod",
        "port": 27015,
        "name": "eli gmod server",
    },
    "sandbox": {
        "game": "gmod",
        "port": 27017,
        "name": "eli sandbox server",
    },
    "tf2": {
        "game": "tf2",
        "port": 27016,
        "name": "eli tf2 server",
    },
    "hldm": {
        "game": "hldm",
        "port": 27013,
        "name": "eli hldm server",
    },
    
    # extra
    "jazz": {
        "game": "gmod",
        "port": 27041,
        "name": "eli jazztronauts",
    },
    "sven": {
        "game": "sven",
        "port": 27040,
        "name": "eli sven server",
    },
    "mc": {
        "game": "minecraft",
        "name": "eli smp server",
        "port": 25565
    }
}

path = os.path.dirname(os.path.realpath(__file__))+'/' # still stupid
source_games = ("gmod", "tf2", "hldm", "sven", "l4d2")
timestamp = 0

def seconds(sec:int):
    min = hr = 0
    x = f"{sec}s"
    if sec >= 60:
        min, sec = divmod(sec, 60)
        x = f"{min}m {sec}s"
    if min >= 60:
        hr, min = divmod(min, 60)
        x = f"{hr}h {min}m {sec}s"
    return x

class server_info(object):
    max_players = 0
    player_count = 0
    player_list = []
    subtitle = ""
    map_name = ""
    def __init__(self, player_count, max_players, player_list, subtitle, map_name):
        self.player_count = player_count
        self.max_players = max_players
        self.player_list = player_list
        self.subtitle = subtitle
        self.map_name = map_name

def query_server(server):
    port = servers[server]["port"]
    game = servers[server]["game"]
    playerlist = []
    try:

        if game in source_games:
            q = a2s.info(("e.elisttm.space", port), 0.5)
            if q.player_count > 0:
                for player in a2s.players(("e.elisttm.space", port)):
                    playerlist.append({
                        "name": "unconnected" if not player.name else player.name,
                        "score": player.score,
                        "time": seconds(round(player.duration))
                    })
            map_name = (q.map_name[:16] + " ...") if len(q.map_name) > 16 else q.map_name
            subtitle = (q.game[:24] + "...") if len(q.game) > 24 else q.game
            return server_info(q.player_count, q.max_players, playerlist, subtitle, map_name)
        
        elif game == "minecraft":
            q = mcstatus.JavaServer.lookup(f"e.elisttm.space:{port}", 0.5).status()
            if q.players.sample:
                for player in q.players.sample:
                    playerlist.append({"name": player.name,})
            return server_info(q.players.online, q.players.max, playerlist, q.version.name, "")
    except (TimeoutError, ConnectionRefusedError):
        raise TimeoutError("server offline...")
    except Exception as e:
        print(f"EXCEPTION in query_server({server}): {e}")
        return None
    

async def fetch_servers():
    global timestamp
    while True:
        for server in servers:
            game = servers[server]["game"]
            try:
                query = query_server(server)
                img = Image.open(f"{path}static/img/servers/template-{game}.gif")
                draw = ImageDraw.Draw(img)
                draw.text((160, 1), f"{query.player_count}/{query.max_players}", "white", ImageFont.truetype(f"{path}static/Verdana-Bold.ttf", 11))
                draw.text((160, 15.5), query.map_name, "white", ImageFont.truetype(f"{path}static/Arial.ttf", 10))
                draw.text((34, 15.5), query.subtitle, "white", ImageFont.truetype(f"{path}static/Arial.ttf", 10))
            except TimeoutError:
                img = Image.open(f"{path}static/img/servers/template-offline.gif")
                draw = ImageDraw.Draw(img)
            except Exception as e:
                print(server, str(e))
                img = Image.open(f"{path}static/img/servers/template-error.gif")
                draw = ImageDraw.Draw(img)
            draw.text((34, 1), servers[server]['name'], "white", ImageFont.truetype(f"{path}static/Verdana-Bold.ttf", 11))
            img.save(f"{path}static/img/servers/banner-{server}.gif")
        timestamp = time.time_ns()
        await asyncio.sleep(60)
