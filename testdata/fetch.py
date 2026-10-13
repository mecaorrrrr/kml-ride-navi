import json, gzip, time, urllib.request, urllib.parse, subprocess
EPS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
HW = "^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|track|road|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"
A = json.load(open("testdata/areas.json"))
log = []
def q(query, name):
    for ep in EPS:
        for t in range(2):
            try:
                req = urllib.request.Request(ep, data=urllib.parse.urlencode({"data": query}).encode(), headers={"User-Agent": "kml-ride-navi-test"})
                body = urllib.request.urlopen(req, timeout=300).read()
                json.loads(body)
                gzip.open(f"testdata/{name}.json.gz", "wb").write(body)
                log.append(f"{name}: {len(body)} bytes from {ep}")
                return
            except Exception as e:
                log.append(f"{name}: {ep} try{t} failed {e}")
                time.sleep(10)
for a in A["detail"]:
    s, w, n, e = a["bbox"]
    q(f'[out:json][timeout:180][bbox:{s},{w},{n},{e}];way[highway~"{HW}"];out body geom;node[highway~"^(traffic_signals|motorway_junction|stop)$"];out body;node[barrier=toll_booth];out body;', a["id"])
s, w, n, e = A["motorway_bbox"]
q(f'[out:json][timeout:300][bbox:{s},{w},{n},{e}];way[highway~"^(motorway|motorway_link|trunk_link)$"];out body geom;node[highway=motorway_junction];out body;node[barrier=toll_booth];out body;', "motorways")
pl = ",".join(str(x) for x in A["around_test"])
q(f'[out:json][timeout:60];way(around:30,{pl})[highway~"{HW}"];out body geom;node(around:30,{pl})[highway~"^(traffic_signals|motorway_junction)$"];out body;', "around_test")
for ep in EPS:
    r = subprocess.run(["curl", "-sSI", "--max-time", "30", "-H", "Origin: https://mecaorrrrr.github.io", ep + "?data=" + urllib.parse.quote("[out:json];node(1);out;")], capture_output=True, text=True)
    log.append("CORS " + ep + "\n" + "\n".join(l for l in r.stdout.splitlines() if l.lower().startswith(("http", "access-control"))))
open("testdata/log.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
