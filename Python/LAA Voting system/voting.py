#!/usr/bin/env python3
"""General Assembly voting. Run: python3 voting.py [port] [admin_key]  (Python 3.8+, no installs)."""
import os, unicodedata, time, zlib, base64, re, json, sqlite3, sys, secrets, socket, threading, csv, io
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT") or (sys.argv[1] if len(sys.argv) > 1 else 8000))
ADMIN_KEY = os.environ.get("ADMIN_KEY") or (sys.argv[2] if len(sys.argv) > 2 else str(secrets.randbelow(900000) + 100000))
DB = sqlite3.connect(os.environ.get("DB_PATH", "voting.db"), check_same_thread=False)
LOCK = threading.Lock()
DB.executescript("""
CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY, licence TEXT UNIQUE COLLATE NOCASE, name TEXT, present INTEGER DEFAULT 1, pin TEXT);
CREATE TABLE IF NOT EXISTS ballots(id INTEGER PRIMARY KEY, member_id INTEGER, label TEXT, club TEXT);
CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY, title TEXT, secret INTEGER, options TEXT, status TEXT DEFAULT 'open', eligible INTEGER);
CREATE TABLE IF NOT EXISTS cast(vote_id INTEGER, ballot_id INTEGER, PRIMARY KEY(vote_id, ballot_id)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS tally(vote_id INTEGER, choice TEXT, n INTEGER, PRIMARY KEY(vote_id, choice));
CREATE TABLE IF NOT EXISTS open_choices(vote_id INTEGER, ballot_id INTEGER, choice TEXT);
CREATE TABLE IF NOT EXISTS roster(licence TEXT PRIMARY KEY COLLATE NOCASE, name TEXT, club TEXT, voting INTEGER DEFAULT 1);
""")
try: DB.execute("ALTER TABLE members ADD COLUMN pin TEXT")  # older databases
except sqlite3.OperationalError: pass

PUBLIC_URL = ""
# QR generator (qrcode-generator by Kazuhiko Arase, MIT license), embedded so it works without internet
QRJS = zlib.decompress(base64.b64decode("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")).decode()

FAILS = {}
class AuthError(ValueError): pass
def too_many(key, limit, window):
    now = time.time(); L = [t for t in FAILS.get(key, []) if now - t < window]; FAILS[key] = L
    return len(L) >= limit
def fail(key):
    if len(FAILS) > 5000: FAILS.clear()
    FAILS.setdefault(key, []).append(time.time())

def q(sql, a=()): return DB.execute(sql, a).fetchall()

def counts():
    return q("SELECT COUNT(DISTINCT m.id), COUNT(b.id) FROM members m JOIN ballots b ON b.member_id=m.id WHERE m.present=1")[0]

def votes():
    out = []
    for vid, title, secret, opts, status, elig in q("SELECT id,title,secret,options,status,eligible FROM votes ORDER BY id DESC"):
        opts = json.loads(opts); t = dict(q("SELECT choice,n FROM tally WHERE vote_id=?", (vid,)))
        out.append({"id": vid, "title": title, "secret": bool(secret), "options": opts,
                    "tally": {o: t.get(o, 0) for o in opts}, "status": status, "eligible": elig,
                    "cast": q("SELECT COUNT(*) FROM cast WHERE vote_id=?", (vid,))[0][0]})
    return out

def state():
    p, b = counts(); vs = votes()
    op = next((dict(v) for v in vs if v["status"] == "open"), None)
    if op: op.pop("tally")  # no live results for voters/screen
    return {"url": PUBLIC_URL, "people": p, "ballots": b, "open": op, "last": next((v for v in vs if v["status"] == "closed"), None), "closed": [v for v in vs if v["status"] == "closed"]}

def norm(s):
    m = re.fullmatch(r"(?:PL)?\s*(\d{5})", str(s).strip().upper())
    if not m: raise ValueError("Neplatné číslo licence. Formát: PL 12345")
    return "PL " + m.group(1)

def me(lic, pin=""):
    lic = norm(lic); key = "L" + lic
    if too_many(key, 5, 120): raise AuthError("Příliš mnoho chybných pokusů. Zkuste to za 2 minuty nebo se obraťte na prezenční stůl.")
    r = q("SELECT id,name,present,pin FROM members WHERE licence=?", (lic,))
    if not r or not r[0][3] or not secrets.compare_digest(str(pin).encode(), r[0][3].encode()):
        fail(key); raise AuthError("Neplatné číslo licence nebo PIN.")
    if not r[0][2]: raise ValueError("Nejste zapsáni v prezenci. Obraťte se na prezenční stůl.")
    mid, name = r[0][0], r[0][1]; op = state()["open"]; bl = []
    for bid, label in q("SELECT id,label FROM ballots WHERE member_id=? ORDER BY id", (mid,)):
        voted = bool(op) and bool(q("SELECT 1 FROM cast WHERE vote_id=? AND ballot_id=?", (op["id"], bid)))
        bl.append({"id": bid, "label": label, "voted": voted})
    return {"name": name, "ballots": bl, "open": op}

def cast(lic, pin, bid, choice):
    m = me(lic, pin); op = m["open"]
    if not op: raise ValueError("Žádné hlasování právě neprobíhá.")
    if bid not in [b["id"] for b in m["ballots"]]: raise ValueError("Toto není váš hlas.")
    if choice not in op["options"]: raise ValueError("Neplatná volba.")
    try: DB.execute("INSERT INTO cast VALUES(?,?)", (op["id"], bid))
    except sqlite3.IntegrityError: raise ValueError("Již jste hlasovali.")
    DB.execute("INSERT INTO tally VALUES(?,?,1) ON CONFLICT(vote_id,choice) DO UPDATE SET n=n+1", (op["id"], choice))
    if not op["secret"]: DB.execute("INSERT INTO open_choices VALUES(?,?,?)", (op["id"], bid, choice))
    DB.commit()  # secret votes: only counts are stored, nothing links a choice to a ballot

def checkin(d):
    lic = norm(d.get("licence", "")); name = str(d.get("name", "")).strip(); club = str(d.get("club", "")).strip()
    if not lic or not name: raise ValueError("Číslo licence a jméno jsou povinné.")
    r = q("SELECT id,pin FROM members WHERE licence=?", (lic,))
    if r:
        mid = r[0][0]; DB.execute("UPDATE members SET present=1, name=? WHERE id=?", (name, mid))
        if not r[0][1]: DB.execute("UPDATE members SET pin=? WHERE id=?", ("%04d" % secrets.randbelow(10000), mid))
    else:
        mid = DB.execute("INSERT INTO members(licence,name,pin) VALUES(?,?,?)", (lic, name, "%04d" % secrets.randbelow(10000))).lastrowid
        DB.execute("INSERT INTO ballots(member_id,label) VALUES(?,?)", (mid, "Osobní hlas"))
    if club:
        c = q("SELECT b.id,b.member_id,m.present,m.name FROM ballots b JOIN members m ON m.id=b.member_id WHERE lower(b.club)=lower(?)", (club,))
        if not c: DB.execute("INSERT INTO ballots(member_id,label,club) VALUES(?,?,?)", (mid, "Klub: " + club, club))
        elif c[0][1] != mid:
            if c[0][2]: raise ValueError("Klub %s již zastupuje %s." % (club, c[0][3]))
            DB.execute("UPDATE ballots SET member_id=? WHERE id=?", (mid, c[0][0]))  # new representative takes over
    DB.commit(); FAILS.pop("L" + lic, None)
    return {"ok": 1, "pin": q("SELECT pin FROM members WHERE id=?", (mid,))[0][0]}

def checkout(d):
    DB.execute("UPDATE members SET present=0 WHERE licence=?", (str(d.get("licence", "")).strip(),)); DB.commit()

def open_vote(d):
    if q("SELECT 1 FROM votes WHERE status='open'"): raise ValueError("Nejprve ukončete probíhající hlasování.")
    title = str(d.get("title", "")).strip(); opts = [str(o).strip() for o in d.get("options", []) if str(o).strip()]
    if not title or len(opts) < 2 or len(set(opts)) < len(opts): raise ValueError("Zadejte otázku a alespoň 2 různé možnosti.")
    DB.execute("INSERT INTO votes(title,secret,options) VALUES(?,?,?)", (title, int(bool(d.get("secret"))), json.dumps(opts))); DB.commit()

def close_vote(d):
    DB.execute("UPDATE votes SET status='closed', eligible=(SELECT COUNT(*) FROM ballots b JOIN members m ON m.id=b.member_id WHERE m.present=1) WHERE status='open'"); DB.commit()

# ---- member list (roster): prepared list used for quick check-in ----
def fold(s): return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if not unicodedata.combining(c))

def parse_csv(text):
    text = text.lstrip("\ufeff"); first = text.split("\n", 1)[0]
    delim = ";" if first.count(";") > first.count(",") else ","
    out = []
    for r in csv.DictReader(io.StringIO(text), delimiter=delim):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        out.append((r.get("licence", ""), r.get("jmeno") or r.get("jméno") or r.get("name", ""), r.get("klub") or r.get("club", ""), r.get("hlasuje") or r.get("voting") or "ano"))
    return out

def roster_replace(rows):
    ok = bad = 0; DB.execute("DELETE FROM roster")
    for lic, name, club, vot in rows:
        try: lic = norm(lic)
        except ValueError: bad += 1; continue
        if not str(name).strip(): bad += 1; continue
        no = str(vot).strip().lower() in ("0", "ne", "no", "false", "n")
        DB.execute("INSERT OR REPLACE INTO roster VALUES(?,?,?,?)", (lic, str(name).strip(), str(club or "").strip(), 0 if no else 1)); ok += 1
    DB.commit(); return {"ok": 1, "imported": ok, "skipped": bad}

def load_roster_file(path):
    if path.endswith(".db"):  # SQLite file with table clenove(licence, jmeno, klub, hlasuje)
        c = sqlite3.connect(path); rows = c.execute("SELECT licence,jmeno,klub,hlasuje FROM clenove").fetchall(); c.close()
    else: rows = parse_csv(open(path, encoding="utf-8-sig").read())
    return roster_replace(rows)

def roster_search(text):
    toks = fold(text).split()
    if not toks: return []
    pres = {l for (l,) in q("SELECT licence FROM members WHERE present=1")}; out = []
    for lic, name, club, vot in q("SELECT licence,name,club,voting FROM roster ORDER BY name"):
        hay = fold(name + " " + lic + " " + club)
        if all(t in hay for t in toks): out.append({"licence": lic, "name": name, "club": club, "voting": bool(vot), "present": lic in pres})
        if len(out) >= 8: break
    return out

def admin_status():
    p, b = counts(); ms = []
    for mid, lic, name, pr, pin in q("SELECT id,licence,name,present,pin FROM members ORDER BY id DESC"):
        ms.append({"licence": lic, "name": name, "pin": pin, "present": bool(pr), "ballots": [x[0] for x in q("SELECT label FROM ballots WHERE member_id=? ORDER BY id", (mid,))]})
    return {"people": p, "ballots": b, "members": ms, "votes": votes(), "roster": q("SELECT COUNT(*) FROM roster")[0][0],
            "roster_present": q("SELECT COUNT(*) FROM roster r JOIN members m ON m.licence=r.licence WHERE m.present=1")[0][0]}

def export():
    o = io.StringIO(); w = csv.writer(o); w.writerow(["PREZENCE"]); w.writerow(["licence", "jméno", "přítomen", "hlasy"])
    for m in admin_status()["members"]: w.writerow([m["licence"], m["name"], "ano" if m["present"] else "ne", "; ".join(m["ballots"])])
    for v in reversed(votes()):
        w.writerow([]); w.writerow(["HLASOVÁNÍ", v["title"], "tajné" if v["secret"] else "veřejné", "probíhá" if v["status"] == "open" else "ukončeno", "odevzdáno", v["cast"], "oprávněno", v["eligible"]])
        for k, n in v["tally"].items(): w.writerow([k, n])
        if not v["secret"]:
            for row in q("SELECT b.label,m.name,c.choice FROM open_choices c JOIN ballots b ON b.id=c.ballot_id JOIN members m ON m.id=b.member_id WHERE c.vote_id=? ORDER BY m.name", (v["id"],)): w.writerow(row)
    return o.getvalue()

CSS = "<meta name=viewport content='width=device-width,initial-scale=1'><style>body{font:18px system-ui;max-width:560px;margin:auto;padding:16px}input,button{font:inherit;width:100%;padding:12px;margin:5px 0;border-radius:10px;border:1px solid #888;box-sizing:border-box}button{background:#1a5fb4;color:#fff;border:0}button.s{background:#666}.ok{color:#1a7f37}.err{color:#c01c28}.card{border:1px solid #888;border-radius:12px;padding:12px;margin:12px 0}.row{display:flex;justify-content:space-between;gap:8px;align-items:center}.row button{width:auto;padding:6px 10px}.bar{background:#1a5fb4;height:14px;border-radius:7px}</style>"

VOTER = CSS + r"""<title>Hlasování</title><div id=app></div><script>
const $=s=>document.querySelector(s),app=$("#app");let lic=sessionStorage.getItem("lic")||"",pin=sessionStorage.getItem("pin")||"",timer,last="";
const el=(t,p,...c)=>{const e=document.createElement(t);Object.assign(e,p||{});e.append(...c);return e};
async function api(p,b){const r=await fetch(p,{method:"POST",body:JSON.stringify(b)}),d=await r.json();if(!r.ok)throw new Error(d.error);return d}
async function refresh(){show(await api("/api/me",{licence:lic,pin:pin}))}
function start(){clearInterval(timer);timer=setInterval(()=>refresh().catch(()=>{}),3000)}
function login(msg){clearInterval(timer);last="";app.replaceChildren(el("h2",{},"Valná hromada – hlasování"),el("div",{style:"display:flex;align-items:center;gap:8px"},el("b",{},"PL"),el("input",{id:"l",placeholder:"12345",inputMode:"numeric",autocomplete:"off",oninput:e=>{e.target.value=e.target.value.replace(/\D/g,"").slice(0,5)},onkeydown:e=>{if(e.key=="Enter")$("#g").click()}})),el("input",{id:"p",placeholder:"PIN (dostanete při prezenci)",type:"password",inputMode:"numeric",autocomplete:"off",oninput:e=>{e.target.value=e.target.value.replace(/\D/g,"").slice(0,4)},onkeydown:e=>{if(e.key=="Enter")$("#g").click()}}),el("button",{id:"g",onclick:async()=>{lic="PL "+$("#l").value.trim();pin=$("#p").value.trim();try{await refresh();sessionStorage.setItem("lic",lic);sessionStorage.setItem("pin",pin);start()}catch(e){login(e.message)}}},"Přihlásit"),el("p",{className:"err"},msg||""))}
function show(d){const k=JSON.stringify(d);if(k===last)return;last=k;app.replaceChildren(el("h3",{},d.name));const o=d.open;
if(!o){app.append(el("p",{},"Čekejte na další hlasování…"));return}
app.append(el("h2",{},o.title),el("p",{},o.secret?"🔒 Tajné hlasování":"Veřejné hlasování (vaše jméno se zaznamená)"));
for(const b of d.ballots){const c=el("div",{className:"card"},el("b",{},b.label));
if(b.voted)c.append(el("p",{className:"ok"},"✓ Hlas odevzdán"));
else for(const x of o.options)c.append(el("button",{onclick:async()=>{if(!confirm(b.label+": "+x+"?"))return;try{await api("/api/cast",{licence:lic,pin:pin,ballot_id:b.id,choice:x});await refresh()}catch(e){alert(e.message);refresh()}}},x));
app.append(c)}}
if(lic&&pin)refresh().then(start).catch(e=>login(e.message));else login();
</script>"""

PIE = r"""function pie(v,size){const C=["#1a5fb4","#c01c28","#e5a50a","#1a7f37","#9141ac","#865e3c"],T=v.options.reduce((s,o)=>s+v.tally[o],0),w=el("div",{style:"display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin:8px 0"});if(!T)return w;
const NS="http://www.w3.org/2000/svg",svg=document.createElementNS(NS,"svg");svg.setAttribute("viewBox","-1 -1 2 2");svg.style.width=size+"px";svg.style.transform="rotate(-90deg)";
let a=0;const lg=el("div");
v.options.forEach((o,i)=>{const n=v.tally[o],f=n/T,c=C[i%C.length];
if(f>0){let p;if(f>=1){p=document.createElementNS(NS,"circle");p.setAttribute("r","1")}else{const a2=a+f*2*Math.PI;p=document.createElementNS(NS,"path");p.setAttribute("d","M0 0L"+Math.cos(a)+" "+Math.sin(a)+"A1 1 0 "+(f>.5?1:0)+" 1 "+Math.cos(a2)+" "+Math.sin(a2)+"Z");a=a2}p.setAttribute("fill",c);svg.append(p)}
lg.append(el("div",{},el("span",{style:"display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:6px;background:"+c}),o+": "+n+" ("+Math.round(100*f)+"%)"))});
w.append(svg,lg);return w}"""

SCREEN = CSS + r"""<title>Promítání</title><style>body{max-width:900px;font-size:28px}</style><div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap"><h1>Hlasujte na <span id=u></span></h1><div id=q style="width:260px;background:#fff;padding:6px;border-radius:8px"></div></div><div id=s></div><script src=/qr.js></script><script>
//PIE
const $=s=>document.querySelector(s);
const el=(t,p,...c)=>{const e=document.createElement(t);Object.assign(e,p||{});e.append(...c);return e};
async function tick(){const d=await (await fetch("/api/state")).json(),s=$("#s");if(!window.qd){window.qd=1;const U=/^(localhost|127\.)/.test(location.hostname)&&d.url?d.url:location.origin+"/";$("#u").textContent=U.replace(/^https?:\/\//,"");const qr=qrcode(0,"M");qr.addData(U);qr.make();$("#q").innerHTML=qr.createSvgTag({scalable:true,margin:0});$("#q").firstChild.style.width="100%"}s.replaceChildren(el("p",{},"Přítomno: "+d.people+" osob · "+d.ballots+" hlasů (pro usnášeníschopnost)"));
if(d.open)s.append(el("h2",{},d.open.title),el("p",{},"Hlasování probíhá — odevzdáno "+d.open.cast+" z "+d.ballots+" hlasů"));
else if(d.last){const v=d.last;s.append(el("h2",{},v.title),el("p",{},"Odevzdáno "+v.cast+" z "+v.eligible+" hlasů"));
s.append(pie(v,300))}
else s.append(el("p",{},"Zatím žádné hlasování."))}
tick();setInterval(()=>tick().catch(()=>{}),2000);
</script>"""

ADMIN = CSS + r"""<title>Správa</title><h2>Správa valné hromady</h2>
<div id=gate><input id=key type=password placeholder="Klíč správce"><button id=go>Vstoupit</button><p class=err id=ge></p></div>
<div id=main hidden>
<div class=card><h3>Prezence</h3><input id=sr placeholder="🔍 Hledat v seznamu (jméno, licence, klub)" autocomplete=off><div id=sres></div><p style="margin:8px 0 0;opacity:.7">Nebo ručně (mimo seznam):</p><div style="display:flex;align-items:center;gap:8px"><b>PL</b><input id=lic placeholder="12345" inputmode=numeric autocomplete=off oninput="this.value=this.value.replace(/\D/g,'').slice(0,5)"></div><input id=nm placeholder="Jméno a příjmení"><input id=cl placeholder="Zastupuje klub (nepovinné)"><button id=ci>Zapsat</button><p id=cm style="font-size:26px;font-weight:bold"></p></div>
<div class=card><h3 id=att></h3><div id=mem></div></div>
<div class=card><h3>Seznam členů</h3><input type=file id=rf accept=".csv"><p id=rm></p></div>
<div class=card><h3>Nové hlasování</h3><input id=ti placeholder="Otázka"><input id=op value="Ano,Ne,Zdržel se"><label><input type=checkbox id=se style="width:auto"> Tajné hlasování</label><button id=ov>Zahájit hlasování</button><p id=vm class=err></p></div>
<div class=card id=cur></div><div id=hist></div><p><a id=ex>Stáhnout CSV (prezence + výsledky)</a></p></div>
<script>
const $=s=>document.querySelector(s);let K="";
const el=(t,p,...c)=>{const e=document.createElement(t);Object.assign(e,p||{});e.append(...c);return e};
async function api(p,b){const r=await fetch(p,{method:b?"POST":"GET",headers:{"X-Admin":K},body:b?JSON.stringify(b):undefined}),d=await r.json();if(!r.ok)throw new Error(d.error);return d}
//PIE
const tl=v=>v.options.map(o=>el("div",{},o+": "+v.tally[o]));
async function tick(){const d=await api("/api/admin/status");$("#att").textContent="Přítomno: "+d.people+" osob · "+d.ballots+" hlasů"+(d.roster?" · ze seznamu "+d.roster_present+"/"+d.roster:"");
$("#mem").replaceChildren(...d.members.map(m=>el("div",{className:"row"},el("span",{style:m.present?"":"opacity:.5"},m.name+" ("+m.licence+") PIN "+m.pin+" · "+m.ballots.length+"×"),
el("button",{className:"s",onclick:()=>act(m.present?"checkout":"checkin",{licence:m.licence,name:m.name})},m.present?"Odejít":"Zpět"))));
const cur=d.votes.find(v=>v.status=="open");$("#cur").hidden=!cur;
if(cur)$("#cur").replaceChildren(el("h3",{},"Probíhá: "+cur.title),el("p",{},(cur.secret?"🔒 tajné · ":"veřejné · ")+"odevzdáno "+cur.cast+" z "+d.ballots),...tl(cur),el("button",{onclick:()=>act("close",{})},"Ukončit hlasování"));
$("#hist").replaceChildren(...d.votes.filter(v=>v.status=="closed").map(v=>el("div",{className:"card"},el("b",{},v.title+(v.secret?" 🔒":"")),el("div",{},"Odevzdáno "+v.cast+" z "+v.eligible),...tl(v),pie(v,160))))}
async function act(a,b){try{await api("/api/admin/"+a,b);tick()}catch(e){alert(e.message)}}
$("#go").onclick=async()=>{K=$("#key").value;try{await tick();$("#gate").hidden=true;$("#main").hidden=false;$("#ex").href="/api/admin/export?key="+encodeURIComponent(K);setInterval(()=>tick().catch(()=>{}),2000)}catch(e){$("#ge").textContent=e.message}};
$("#ci").onclick=async()=>{try{const r=await api("/api/admin/checkin",{licence:"PL "+$("#lic").value,name:$("#nm").value,club:$("#cl").value});$("#cm").textContent="✓ "+$("#nm").value+" — PIN: "+r.pin;for(const i of["lic","nm","cl"])$("#"+i).value="";$("#cm").className="ok";tick()}catch(e){$("#cm").textContent=e.message;$("#cm").className="err"}};
async function srch(){const v=$("#sr").value.trim();if(!v){$("#sres").replaceChildren();return}
const r=await api("/api/admin/roster?q="+encodeURIComponent(v));
$("#sres").replaceChildren(...r.map(m=>el("button",{className:m.present?"s":"",disabled:m.present,onclick:()=>pick(m)},m.name+" ("+m.licence+")"+(m.club?" · "+m.club:"")+(m.present?" ✓ přítomen":"")+(m.voting?"":" ⚠ bez hlasovacího práva"))))}
function pick(m){if(!m.voting&&!confirm(m.name+" nemá hlasovací právo. Přesto zapsat?"))return;$("#lic").value=m.licence.replace("PL ","");$("#nm").value=m.name;$("#cl").value=m.club;$("#sr").value="";$("#sres").replaceChildren();$("#ci").focus()}
$("#sr").oninput=()=>srch().catch(()=>{});
$("#sr").onkeydown=e=>{if(e.key=="Enter"){const b=$("#sres").querySelector("button:not(:disabled)");if(b)b.click()}};
$("#rf").onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const r=await api("/api/admin/roster",{csv:await f.text()});$("#rm").textContent="Načteno: "+r.imported+", přeskočeno: "+r.skipped;tick()}catch(x){$("#rm").textContent=x.message}};
$("#ov").onclick=async()=>{try{await api("/api/admin/open",{title:$("#ti").value,options:$("#op").value.split(","),secret:$("#se").checked});$("#vm").textContent="";$("#ti").value="";tick()}catch(e){$("#vm").textContent=e.message}};
for(const[i,b]of[["key","go"],["lic","ci"],["nm","ci"],["cl","ci"],["ti","ov"],["op","ov"]])$("#"+i).onkeydown=e=>{if(e.key=="Enter")$("#"+b).click()};
</script>"""

RESULTS = CSS + r"""<title>Výsledky</title><h2>Výsledky hlasování</h2><div id=s></div><script>
const $=s=>document.querySelector(s);
const el=(t,p,...c)=>{const e=document.createElement(t);Object.assign(e,p||{});e.append(...c);return e};
//PIE
async function tick(){const d=await (await fetch("/api/state")).json(),s=$("#s");
s.replaceChildren(el("p",{},"Přítomno: "+d.people+" osob · "+d.ballots+" hlasů"));
if(d.open)s.append(el("p",{},"Právě probíhá hlasování: "+d.open.title+" (odevzdáno "+d.open.cast+" z "+d.ballots+")"));
if(!d.closed.length)s.append(el("p",{},"Zatím žádné ukončené hlasování."));
for(const v of d.closed)s.append(el("div",{className:"card"},el("b",{},v.title+(v.secret?" 🔒":"")),el("div",{},"Odevzdáno "+v.cast+" z "+v.eligible+" hlasů"),pie(v,180)))}
tick();setInterval(()=>tick().catch(()=>{}),5000);
</script>"""
RESULTS = RESULTS.replace("//PIE", PIE)
SCREEN = SCREEN.replace("//PIE", PIE); ADMIN = ADMIN.replace("//PIE", PIE)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, body, ctype="application/json", code=200):
        b = body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def js(self, obj, code=200): self.send(json.dumps(obj), code=code)
    def ip(self): return self.headers.get("X-Forwarded-For", "").split(",")[-1].strip() or self.client_address[0]
    def is_admin(self):
        k = self.headers.get("X-Admin") or parse_qs(urlparse(self.path).query).get("key", [""])[0]
        return secrets.compare_digest(k, ADMIN_KEY)
    def do_GET(self):
        p = urlparse(self.path).path
        try:
            pages = {"/": VOTER, "/admin": ADMIN, "/screen": SCREEN, "/vysledky": RESULTS}
            if p == "/qr.js": return self.send(QRJS, "application/javascript")
            if p in pages: return self.send(pages[p], "text/html")
            if p == "/api/state":
                with LOCK: return self.js(state())
            if p in ("/api/admin/status", "/api/admin/export", "/api/admin/roster"):
                if too_many("A" + self.ip(), 10, 60): return self.js({"error": "Příliš mnoho pokusů. Zkuste to za minutu."}, 429)
                if not self.is_admin(): fail("A" + self.ip()); return self.js({"error": "Nesprávný klíč správce."}, 403)
                with LOCK:
                    if p.endswith("status"): return self.js(admin_status())
                    if p.endswith("roster"): return self.js(roster_search(parse_qs(urlparse(self.path).query).get("q", [""])[0]))
                    return self.send("\ufeff" + export(), "text/csv")
            self.js({"error": "Nenalezeno"}, 404)
        except Exception: self.js({"error": "Chyba serveru"}, 500)
    def do_POST(self):
        p = urlparse(self.path).path; ip = self.ip(); adm = p.startswith("/api/admin/")
        try:
            if too_many(("A" if adm else "I") + ip, 10 if adm else 60, 60): return self.js({"error": "Příliš mnoho pokusů. Zkuste to za minutu."}, 429)
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            admin = {"checkin": checkin, "checkout": checkout, "open": open_vote, "close": close_vote, "roster": lambda d: roster_replace(parse_csv(str(d.get("csv", ""))))}
            with LOCK:
                try:
                    if p == "/api/me": out = me(str(d.get("licence", "")).strip(), d.get("pin", ""))
                    elif p == "/api/cast":
                        cast(str(d.get("licence", "")).strip(), d.get("pin", ""), d.get("ballot_id"), d.get("choice")); out = {"ok": 1}
                    elif p.startswith("/api/admin/") and p[11:] in admin:
                        if not self.is_admin(): raise PermissionError("Nesprávný klíč správce.")
                        out = admin[p[11:]](d) or {"ok": 1}
                    else: raise ValueError("Nenalezeno")
                except Exception: DB.rollback(); raise
            self.js(out)
        except PermissionError as e: fail("A" + ip); self.js({"error": str(e)}, 403)
        except AuthError as e: fail("I" + ip); self.js({"error": str(e)}, 403)
        except ValueError as e: self.js({"error": str(e)}, 400)
        except Exception: self.js({"error": "Chyba serveru"}, 500)

def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(("10.255.255.255", 1)); return s.getsockname()[0]
    except Exception: return "localhost"

if __name__ == "__main__":
    ip = lan_ip()
    PUBLIC_URL = os.environ.get("PUBLIC_URL") or "http://%s:%d/" % (ip, PORT)
    print("Hlasující (do QR kódu): http://%s:%d/\nPromítání:                   http://%s:%d/screen\nSpráva / prezence:           http://%s:%d/admin   klíč: %s" % (ip, PORT, ip, PORT, ip, PORT, ADMIN_KEY if not os.environ.get("ADMIN_KEY") else "(z proměnné ADMIN_KEY)"))
    rp = os.environ.get("ROSTER") or next((f for f in ("clenove.db", "roster.csv") if os.path.exists(f)), None)
    if rp:
        try: r = load_roster_file(rp); print("Seznam členů: %s — načteno %d, přeskočeno %d" % (rp, r["imported"], r["skipped"]))
        except Exception as e: print("Seznam členů se nepodařilo načíst:", e)
    class Srv(ThreadingHTTPServer):
        request_queue_size = 256  # many phones connecting at once
        daemon_threads = True
    Srv(("0.0.0.0", PORT), H).serve_forever()
