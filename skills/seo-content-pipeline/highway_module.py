#!/usr/bin/env python3
"""Highway (interstate) data module for WareMatch location pages. PROTOTYPE.

Source: U.S. Census Bureau TIGERweb Transportation MapServer (keyless):
  layer 0 = Primary Roads Interstates 5M scale (generalized)
  layer 3 = Secondary Roads Interstates and US Highways (more detailed; we filter RTTYP='I')
State boundary: TIGERweb State_County MapServer layer 0 (States, full detail).
City coordinates: GeoNames cities15000 dump (keyless).

Public API
  interstates_in_state(state_fips, mode="polygon") -> dict
  interstates_near(lat, lon, km) -> dict   (exact min distance to centerline, not just envelope)
  geonames_city(name, state_abbr) -> (lat, lon, record)

All HTTP responses are cached as JSON under runs/highway_cache/.
No API key is needed (the Census key in .env is NOT used here).
CLI: python3 highway_module.py state 13 | near 33.749 -84.388 15 | city Atlanta GA 15 30
"""
import hashlib, io, json, math, os, re, sys, time, zipfile
import urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "runs", "highway_cache")
TRANSPORT = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer"
STATES = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0"
GEONAMES_URL = "https://download.geonames.org/export/dump/cities15000.zip"
LAYERS = (0, 3)
UA = {"User-Agent": "WareMatch-highway-module/0.1 (contact: your-email)"}

CITATION = "U.S. Census Bureau, TIGERweb Transportation (Primary Roads Interstates 5M scale; Secondary Roads Interstates and US Highways), vintage January 1, 2026"


# ---------------------------------------------------------------- cache / http
def _cache_path(key):
    return os.path.join(CACHE_DIR, hashlib.sha1(key.encode()).hexdigest()[:16] + ".json")


def _cached(key, fetch):
    os.makedirs(CACHE_DIR, exist_ok=True)
    p = _cache_path(key)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)["data"]
    data = fetch()
    with open(p, "w") as f:
        json.dump({"key": key, "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"), "data": data}, f)
    return data


def _http(url, params=None, post=False, retries=3):
    body = None
    if params is not None:
        enc = urllib.parse.urlencode(params).encode()
        if post:
            body = enc
        else:
            url += "?" + enc.decode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"HTTP failed: {url}: {last}")


def _query(layer, geometry, geom_type, extra=None):
    """ArcGIS query with POST (polygons are big). Returns list of features."""
    p = {"f": "json", "where": "RTTYP='I'", "outFields": "NAME,RTTYP,MTFCC",
         "geometry": geometry if isinstance(geometry, str) else json.dumps(geometry),
         "geometryType": geom_type, "inSR": 4326, "outSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "returnGeometry": "true"}
    p.update(extra or {})
    key = f"q|{layer}|{json.dumps(p, sort_keys=True)}"

    def fetch():
        d = json.loads(_http(f"{TRANSPORT}/{layer}/query", p, post=True))
        if "error" in d:
            raise RuntimeError(d["error"])
        if d.get("exceededTransferLimit"):
            raise RuntimeError("exceededTransferLimit: need paging")
        return d["features"]
    return _cached(key, fetch)


# ---------------------------------------------------------------- route names
_RT = re.compile(r"\bI-\s*-?\s*(\d{1,3})([A-Z]?)\b")


def normalize_route(name):
    """'I- 75' -> ('I-75', None); 'I- 85 Bus' -> ('I-85', 'Bus'); 'E I- 10' -> ('I-10', None).
    Returns (None, None) if not parseable (e.g. 'I- Rte 35', 'I- H-1')."""
    m = _RT.search(name or "")
    if not m:
        return None, None
    num = m.group(1) + m.group(2)
    rest = name[m.end():].strip().lower()
    variant = None
    if "bus" in rest:
        variant = "Bus"
    elif "hov" in rest or "express" in rest or "toll" in rest:
        variant = "HOV/Express"
    elif "lp" in rest or "byp" in rest or "spr" in rest or "scn" in rest:
        variant = "Loop/Spur/Scenic"
    return f"I-{num}", variant


def _summarize(features_by_layer):
    """-> {route: {features:int, layers:[..], variants:{}}} ; excludes Bus routes from 'routes'."""
    routes, bus, unparsed = {}, {}, {}
    for layer, feats in features_by_layer.items():
        for ft in feats:
            nm = ft["attributes"]["NAME"]
            r, var = normalize_route(nm)
            if r is None:
                unparsed[nm] = unparsed.get(nm, 0) + 1
                continue
            tgt = bus if var == "Bus" else routes
            e = tgt.setdefault(r, {"features": 0, "layers": set()})
            e["features"] += 1
            e["layers"].add(layer)
    fix = lambda d: {k: {"features": v["features"], "layers": sorted(v["layers"])}
                     for k, v in sorted(d.items(), key=lambda kv: (len(kv[0]), kv[0]))}
    return fix(routes), fix(bus), unparsed


# ---------------------------------------------------------------- state
def state_polygon(fips, offset_deg=0.001):
    """Esri polygon (WGS84) for the state, lightly generalised (~100 m) to keep the POST small."""
    p = {"f": "json", "where": f"STATE='{fips}'", "outFields": "NAME,STATE", "returnGeometry": "true",
         "outSR": 4326, "maxAllowableOffset": offset_deg}
    key = "statepoly|" + json.dumps(p, sort_keys=True)
    d = _cached(key, lambda: json.loads(_http(STATES + "/query", p)))
    if not d.get("features"):
        raise RuntimeError(f"no state with FIPS {fips}")
    f = d["features"][0]
    return f["attributes"]["NAME"], {"rings": f["geometry"]["rings"], "spatialReference": {"wkid": 4326}}


def interstates_in_state(state_fips, mode="polygon"):
    """Interstates whose centerline intersects the state.
    mode='polygon' : server-side intersect with the Census state polygon (default; exact to ~100 m)
    mode='bbox'    : state polygon's bounding box only (includes neighbour-state false positives)
    """
    name, poly = state_polygon(state_fips)
    xs = [x for ring in poly["rings"] for x, _ in ring]
    ys = [y for ring in poly["rings"] for _, y in ring]
    bbox = {"xmin": min(xs), "ymin": min(ys), "xmax": max(xs), "ymax": max(ys), "spatialReference": {"wkid": 4326}}
    geom, gt = (poly, "esriGeometryPolygon") if mode == "polygon" else (bbox, "esriGeometryEnvelope")
    by_layer = {l: _query(l, geom, gt, {"returnGeometry": "false"}) for l in LAYERS}
    routes, bus, unparsed = _summarize(by_layer)
    return {"state": name, "fips": state_fips, "mode": mode, "bbox": bbox,
            "routes": routes, "bus_routes_excluded": bus, "unparsed_names": unparsed,
            "raw_feature_counts": {str(l): len(v) for l, v in by_layer.items()},
            "citation": CITATION}


# ---------------------------------------------------------------- proximity
def _km_to_deg(lat, km):
    dlat = km / 110.574                       # km per degree latitude (~110.57-111.69; mid-lat value is fine)
    dlon = km / (111.320 * math.cos(math.radians(lat)))
    return dlat, dlon


def _seg_dist_km(lat0, lon0, a, b):
    """Distance (km) from point to segment a-b (lon,lat pairs) using a local equirectangular plane
    centred on the point. Error is negligible (<0.1%) at the <=50 km scales used here."""
    kx = 111.320 * math.cos(math.radians(lat0))
    ky = 110.574
    ax, ay = (a[0] - lon0) * kx, (a[1] - lat0) * ky
    bx, by = (b[0] - lon0) * kx, (b[1] - lat0) * ky
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, -(ax * dx + ay * dy) / L2))
    return math.hypot(ax + t * dx, ay + t * dy)


def interstates_near(lat, lon, km):
    """Interstates with any centerline within `km` of (lat, lon).
    Step 1: envelope query (half-side km converted to degrees at this latitude) on layers 0 and 3.
    Step 2: exact min distance from point to returned polylines; keep <= km (envelope corners are dropped).
    Returns {routes: {I-75: {min_km, features, layers}}, ...}. Bus routes listed separately."""
    dlat, dlon = _km_to_deg(lat, km)
    env = {"xmin": lon - dlon, "ymin": lat - dlat, "xmax": lon + dlon, "ymax": lat + dlat,
           "spatialReference": {"wkid": 4326}}
    best, bus_best, in_env = {}, {}, {}
    for l in LAYERS:
        for ft in _query(l, env, "esriGeometryEnvelope"):
            r, var = normalize_route(ft["attributes"]["NAME"])
            if r is None:
                continue
            in_env.setdefault(r, set()).add(l)
            dmin = min((_seg_dist_km(lat, lon, p[i], p[i + 1])
                        for p in ft["geometry"]["paths"] for i in range(len(p) - 1)), default=1e9)
            tgt = bus_best if var == "Bus" else best
            e = tgt.setdefault(r, {"min_km": 1e9, "features": 0, "layers": set()})
            e["min_km"] = min(e["min_km"], dmin)
            if dmin <= km:
                e["features"] += 1
                e["layers"].add(l)
    fin = lambda d: {r: {"min_km": round(e["min_km"], 1), "features": e["features"], "layers": sorted(e["layers"])}
                     for r, e in sorted(d.items(), key=lambda kv: kv[1]["min_km"]) if e["min_km"] <= km}
    return {"lat": lat, "lon": lon, "km": km, "routes": fin(best), "bus_routes_excluded": fin(bus_best),
            "envelope_only_false_positives": sorted(set(best) - set(fin(best))),
            "citation": CITATION}


# ---------------------------------------------------------------- GeoNames
def _geonames_rows():
    def fetch():
        z = zipfile.ZipFile(io.BytesIO(_http(GEONAMES_URL)))
        rows = []
        for line in z.read("cities15000.txt").decode("utf8").splitlines():
            c = line.split("\t")
            if c[8] == "US":
                rows.append({"name": c[1], "ascii": c[2], "lat": float(c[4]), "lon": float(c[5]),
                             "fcode": c[7], "admin1": c[10], "pop": int(c[14] or 0), "geonameid": c[0]})
        return rows
    return _cached("geonames_cities15000_US", fetch)


def geonames_city(name, state_abbr):
    c = [r for r in _geonames_rows() if r["ascii"].lower() == name.lower() and r["admin1"] == state_abbr]
    if not c:
        raise KeyError(f"{name}, {state_abbr} not in cities15000")
    r = max(c, key=lambda x: x["pop"])
    return r["lat"], r["lon"], r


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["state"]:
        print(json.dumps(interstates_in_state(a[1], a[2] if len(a) > 2 else "polygon"), indent=1))
    elif a[:1] == ["near"]:
        print(json.dumps(interstates_near(float(a[1]), float(a[2]), float(a[3])), indent=1))
    elif a[:1] == ["city"]:
        la, lo, rec = geonames_city(a[1], a[2])
        for k in a[3:]:
            print(json.dumps(interstates_near(la, lo, float(k)), indent=1))
    else:
        print(__doc__)
