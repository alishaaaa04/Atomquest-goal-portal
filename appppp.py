from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "atomquest_hackathon_2025"

# ══════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════
USERS = {
    "emp1":   {"password":"emp123",   "name":"Arjun Sharma",  "role":"employee","manager":"mgr1","dept":"Sales"},
    "emp2":   {"password":"emp123",   "name":"Priya Mehta",   "role":"employee","manager":"mgr1","dept":"Sales"},
    "emp3":   {"password":"emp123",   "name":"Rohan Verma",   "role":"employee","manager":"mgr1","dept":"Sales"},
    "mgr1":   {"password":"mgr123",   "name":"Neha Kapoor",   "role":"manager", "manager":None,  "dept":"Sales"},
    "admin1": {"password":"admin123", "name":"Vikram Singh",  "role":"admin",   "manager":None,  "dept":"HR"},
}
THRUST_AREAS = ["Revenue Growth","Cost Optimisation","Customer Satisfaction","Process Efficiency","People Development","Innovation"]
GOALS = {
    "g1": {"id":"g1","owner":"emp1","sheet_status":"approved","submitted_at":"2025-04-10","goals":[
        {"id":"g1a","thrust":"Revenue Growth","title":"Increase Q-Sales Revenue","description":"Drive regional sales to hit Rs 50L quarterly target","uom":"min","target":5000000,"weightage":40,"status":"On Track","q1":2100000,"q2":2800000,"q3":0,"q4":0},
        {"id":"g1b","thrust":"Customer Satisfaction","title":"Improve NPS Score","description":"Raise Net Promoter Score from 42 to 60","uom":"min","target":60,"weightage":30,"status":"On Track","q1":48,"q2":55,"q3":0,"q4":0},
        {"id":"g1c","thrust":"Process Efficiency","title":"Reduce TAT on Proposals","description":"Cut proposal turnaround from 5 days to 2 days","uom":"max","target":2,"weightage":20,"status":"Completed","q1":3,"q2":2,"q3":0,"q4":0},
        {"id":"g1d","thrust":"People Development","title":"Complete Leadership Training","description":"Finish 3 leadership modules by Q3","uom":"min","target":3,"weightage":10,"status":"Not Started","q1":0,"q2":1,"q3":0,"q4":0},
    ]},
    "g2": {"id":"g2","owner":"emp2","sheet_status":"submitted","submitted_at":"2025-04-15","goals":[
        {"id":"g2a","thrust":"Revenue Growth","title":"New Client Acquisition","description":"Onboard 10 new enterprise clients","uom":"min","target":10,"weightage":50,"status":"On Track","q1":3,"q2":6,"q3":0,"q4":0},
        {"id":"g2b","thrust":"Customer Satisfaction","title":"Zero Safety Incidents","description":"Maintain zero workplace safety incidents","uom":"zero","target":0,"weightage":30,"status":"On Track","q1":0,"q2":0,"q3":0,"q4":0},
        {"id":"g2c","thrust":"Innovation","title":"Launch Digital Campaign","description":"Execute 2 digital marketing campaigns","uom":"min","target":2,"weightage":20,"status":"Not Started","q1":0,"q2":0,"q3":0,"q4":0},
    ]},
    "g3": {"id":"g3","owner":"emp3","sheet_status":"draft","submitted_at":None,"goals":[
        {"id":"g3a","thrust":"Cost Optimisation","title":"Reduce Operational Costs","description":"Cut dept operational costs by 15%","uom":"max","target":85,"weightage":60,"status":"Not Started","q1":0,"q2":0,"q3":0,"q4":0},
        {"id":"g3b","thrust":"Process Efficiency","title":"Automate Monthly Reporting","description":"Automate 3 manual reporting processes","uom":"min","target":3,"weightage":40,"status":"Not Started","q1":0,"q2":0,"q3":0,"q4":0},
    ]},
}
CHECKIN_COMMENTS = {
    "emp1":[
        {"quarter":"Q1","manager":"Neha Kapoor","comment":"Good start, sales pipeline looks healthy. Focus on NPS improvement.","date":"2025-07-15"},
        {"quarter":"Q2","manager":"Neha Kapoor","comment":"Excellent progress on TAT reduction. Keep the momentum on revenue targets.","date":"2025-10-12"},
    ],
    "emp2":[],"emp3":[],
}
AUDIT_LOG = [
    {"timestamp":"2025-06-01 10:23","user":"Neha Kapoor","action":"Approved","entity":"Arjun Sharma","detail":"All 4 goals approved and locked"},
    {"timestamp":"2025-07-16 09:45","user":"Neha Kapoor","action":"Check-in","entity":"Arjun Sharma","detail":"Q1 check-in comment added"},
    {"timestamp":"2025-10-13 11:00","user":"Neha Kapoor","action":"Check-in","entity":"Arjun Sharma","detail":"Q2 check-in comment added"},
    {"timestamp":"2025-09-10 14:30","user":"Vikram Singh","action":"Unlocked","entity":"Priya Mehta","detail":"Admin unlocked for revision"},
]
NOTIFICATIONS = {
    "emp1":[
        {"type":"success","icon":"check","title":"Goals Approved","msg":"Your goal sheet has been approved by Neha Kapoor. Goals are now locked.","time":"2025-06-01 10:23","read":True},
        {"type":"info","icon":"chat","title":"Q2 Check-in Done","msg":"Manager completed your Q2 check-in. View comments.","time":"2025-10-13 11:00","read":False},
    ],
    "emp2":[{"type":"warning","icon":"clock","title":"Awaiting Approval","msg":"Your goal sheet is pending manager review.","time":"2025-04-15 09:00","read":False}],
    "emp3":[{"type":"danger","icon":"alert","title":"Goals Overdue","msg":"Goal submission deadline passed 5 days ago. Submit immediately.","time":"2025-05-12 08:00","read":False}],
    "mgr1":[
        {"type":"warning","icon":"doc","title":"Review Pending","msg":"Priya Mehta has submitted goals for your review.","time":"2025-04-15 09:00","read":False},
        {"type":"danger","icon":"alert","title":"Escalation Alert","msg":"Rohan Verma has not submitted goals — 5 days overdue. HR notified.","time":"2025-05-12 08:00","read":False},
    ],
    "admin1":[
        {"type":"danger","icon":"alert","title":"Escalation: Rohan Verma","msg":"Employee has not submitted goals 5 days after cycle open. Escalated to HR.","time":"2025-05-12 08:00","read":False},
        {"type":"info","icon":"chart","title":"Q2 Window Closing","msg":"Q2 check-in window closes in 3 days. 1/3 employees pending.","time":"2025-10-27 08:00","read":False},
    ],
}
ESCALATION_LOG = [
    {"timestamp":"2025-05-12 08:00","employee":"Rohan Verma","type":"Goal Submission","days_overdue":5,"status":"Escalated","escalated_to":"Vikram Singh (HR)"},
    {"timestamp":"2025-04-20 08:00","employee":"Priya Mehta","type":"Manager Approval","days_overdue":5,"status":"Resolved","escalated_to":"Neha Kapoor"},
]
QOQ_DATA = {
    "emp1":{"name":"Arjun Sharma","Q1":62.5,"Q2":81.2,"Q3":0,"Q4":0},
    "emp2":{"name":"Priya Mehta","Q1":55.0,"Q2":70.0,"Q3":0,"Q4":0},
    "emp3":{"name":"Rohan Verma","Q1":0,"Q2":0,"Q3":0,"Q4":0},
}

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def compute_score(goal, quarter="q2"):
    actual = goal.get(quarter, 0)
    target = goal["target"]
    uom = goal["uom"]
    if uom == "zero": return 100 if actual == 0 else 0
    if target == 0: return 0
    if uom == "min": return round(min((actual / target) * 100, 100), 1)
    if uom == "max": return round(min((target / actual) * 100, 100), 1) if actual else 0
    return 0

def get_overall_score(sheet_id):
    sheet = GOALS.get(sheet_id)
    if not sheet: return 0
    total = weight = 0
    for g in sheet["goals"]:
        total += compute_score(g) * g["weightage"]; weight += g["weightage"]
    return round(total / weight, 1) if weight else 0

def current_user():
    uid = session.get("user_id")
    if not uid or uid not in USERS: return None
    u = USERS[uid].copy(); u["id"] = uid; return u

def unread_count(uid):
    return sum(1 for n in NOTIFICATIONS.get(uid, []) if not n["read"])

def sc_color(s):
    return "#22c97a" if s >= 75 else "#f5c542" if s >= 50 else "#ff4d6a"

# ══════════════════════════════════════════════════════════════
# SHARED CSS + NAV (injected into every page)
# ══════════════════════════════════════════════════════════════
CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0f14;color:#e8ecf4;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;min-height:100vh}
a{text-decoration:none;color:inherit}
nav{background:#161a23;border-bottom:1px solid #2a3040;padding:0 1.5rem;display:flex;align-items:center;justify-content:space-between;height:56px;position:sticky;top:0;z-index:200}
.brand{font-weight:900;font-size:1.2rem;letter-spacing:-.5px}.brand b{color:#4f8eff}
.nav-links{display:flex;gap:2px}
.nav-links a{padding:.38rem .8rem;border-radius:6px;font-size:.82rem;font-weight:500;color:#6b7590;transition:all .15s}
.nav-links a:hover,.nav-links a.on{background:#1e2330;color:#e8ecf4}
.nav-r{display:flex;align-items:center;gap:.65rem}
.rbadge{padding:.18rem .6rem;border-radius:20px;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.rb-employee{background:rgba(79,142,255,.15);color:#4f8eff}
.rb-manager{background:rgba(0,212,170,.15);color:#00d4aa}
.rb-admin{background:rgba(255,123,71,.15);color:#ff7b47}
.sw{display:flex;gap:3px}
.sw a{padding:.2rem .55rem;border-radius:5px;font-size:.68rem;background:#1e2330;color:#6b7590;border:1px solid #2a3040;transition:all .15s}
.sw a:hover{border-color:#4f8eff;color:#4f8eff}
.nb{position:relative;padding:.28rem .48rem;border-radius:6px;cursor:pointer;color:#6b7590;font-size:1rem;background:none;border:none;transition:color .15s}
.nb:hover{color:#e8ecf4}
.nbd{position:absolute;top:2px;right:2px;background:#ff4d6a;color:#fff;font-size:.58rem;font-weight:700;min-width:15px;height:15px;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:0 2px}
.np{display:none;position:absolute;top:56px;right:1rem;width:340px;background:#161a23;border:1px solid #2a3040;border-radius:12px;z-index:300;box-shadow:0 8px 32px rgba(0,0,0,.45)}
.np.open{display:block}
.nh{padding:.9rem 1.1rem .65rem;border-bottom:1px solid #2a3040;display:flex;justify-content:space-between;align-items:center}
.ni{padding:.75rem 1.1rem;border-bottom:1px solid rgba(255,255,255,.04);display:flex;gap:.65rem;align-items:flex-start}
.ni.ur{background:rgba(79,142,255,.06)}
.ni-dot{width:8px;height:8px;border-radius:50%;margin-top:.35rem;flex-shrink:0}
.dot-success{background:#22c97a}.dot-warning{background:#f5c542}.dot-danger{background:#ff4d6a}.dot-info{background:#4f8eff}
.ni-title{font-size:.8rem;font-weight:600;margin-bottom:.18rem}
.ni-msg{font-size:.73rem;color:#6b7590}
.ni-time{font-size:.67rem;color:#6b7590;margin-top:.18rem}
.page{max-width:1200px;margin:0 auto;padding:1.75rem 1.5rem}
.pt{font-size:1.65rem;font-weight:800;margin-bottom:.22rem}
.ps{color:#6b7590;font-size:.85rem;margin-bottom:1.65rem}
.card{background:#1e2330;border:1px solid #2a3040;border-radius:12px;padding:1.4rem}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
@media(max-width:768px){.g2,.g3,.g4{grid-template-columns:1fr}}
.stat{background:#1e2330;border:1px solid #2a3040;border-radius:12px;padding:1.2rem}
.sl{font-size:.7rem;color:#6b7590;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.38rem}
.sv{font-size:1.9rem;font-weight:800}
.ss{font-size:.7rem;color:#6b7590;margin-top:.18rem}
.btn{display:inline-flex;align-items:center;gap:.32rem;padding:.46rem 1rem;border-radius:7px;border:none;font-size:.81rem;font-weight:600;cursor:pointer;transition:all .15s;font-family:inherit}
.btn-p{background:#4f8eff;color:#fff}.btn-p:hover{background:#3a7aee}
.btn-s{background:#22c97a;color:#fff}.btn-s:hover{filter:brightness(.9)}
.btn-w{background:#ff7b47;color:#fff}.btn-w:hover{filter:brightness(.9)}
.btn-d{background:#ff4d6a;color:#fff}.btn-d:hover{filter:brightness(.9)}
.btn-o{background:transparent;color:#6b7590;border:1px solid #2a3040}.btn-o:hover{border-color:#4f8eff;color:#4f8eff}
.btn-sm{padding:.28rem .65rem;font-size:.74rem}
table{width:100%;border-collapse:collapse;font-size:.81rem}
th{padding:.6rem 1rem;text-align:left;color:#6b7590;font-size:.68rem;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #2a3040;font-weight:600}
td{padding:.72rem 1rem;border-bottom:1px solid rgba(255,255,255,.04);vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.02)}
.pill{display:inline-block;padding:.16rem .56rem;border-radius:20px;font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.4px}
.p-approved{background:rgba(34,201,122,.15);color:#22c97a}
.p-submitted{background:rgba(245,197,66,.15);color:#f5c542}
.p-draft{background:rgba(107,117,144,.15);color:#6b7590}
.p-on-track{background:rgba(79,142,255,.15);color:#4f8eff}
.p-completed{background:rgba(34,201,122,.15);color:#22c97a}
.p-not-started{background:rgba(107,117,144,.15);color:#6b7590}
.p-danger{background:rgba(255,77,106,.15);color:#ff4d6a}
.p-resolved{background:rgba(34,201,122,.15);color:#22c97a}
.pbar{background:#2a3040;border-radius:20px;overflow:hidden}
.pf{border-radius:20px;transition:width .4s}
.pg{background:#22c97a}.py{background:#f5c542}.pr{background:#ff4d6a}.pb{background:#4f8eff}
.fg{margin-bottom:.9rem}
label{display:block;font-size:.72rem;color:#6b7590;margin-bottom:.28rem;text-transform:uppercase;letter-spacing:.4px}
input,select,textarea{width:100%;padding:.5rem .8rem;background:#0d0f14;border:1px solid #2a3040;border-radius:7px;color:#e8ecf4;font-family:inherit;font-size:.83rem;transition:border-color .2s}
input:focus,select:focus,textarea:focus{outline:none;border-color:#4f8eff}
textarea{min-height:72px;resize:vertical}
.flash{padding:.65rem 1rem;border-radius:8px;margin-bottom:1.1rem;font-size:.81rem}
.flash-success{background:rgba(34,201,122,.12);border:1px solid rgba(34,201,122,.3);color:#22c97a}
.flash-error{background:rgba(255,77,106,.12);border:1px solid rgba(255,77,106,.3);color:#ff4d6a}
.sh{display:flex;align-items:center;justify-content:space-between;margin-bottom:.9rem}
.sht{font-weight:700;font-size:.92rem}
.tag{font-size:.66rem;padding:.16rem .48rem;border-radius:4px;background:rgba(79,142,255,.12);color:#4f8eff;font-weight:600}
hr{border:none;border-top:1px solid #2a3040;margin:1.1rem 0}
details summary{cursor:pointer;list-style:none}
details summary::-webkit-details-marker{display:none}
.bar-wrap{display:flex;align-items:flex-end;gap:.4rem;height:110px;padding:.4rem 0}
.bar-col{display:flex;flex-direction:column;align-items:center;gap:.25rem;flex:1}
.bar{border-radius:4px 4px 0 0;width:100%;min-height:3px}
.bar-lbl{font-size:.66rem;color:#6b7590}
.bar-val{font-size:.7rem;font-weight:700}
.hm{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin-top:.65rem}
.hm-cell{padding:.5rem;border-radius:6px;text-align:center}
.hm-lbl{font-size:.66rem;color:#6b7590;margin-bottom:.18rem}
.hm-val{font-size:.88rem;font-weight:800}
.esc-i{padding:.8rem .95rem;border-radius:8px;margin-bottom:.55rem;display:flex;justify-content:space-between;align-items:center}
.esc-d{background:rgba(255,77,106,.08);border:1px solid rgba(255,77,106,.2)}
.esc-r{background:rgba(34,201,122,.08);border:1px solid rgba(34,201,122,.2)}
</style>
"""

def nav_html(uid, cu, notifs, unread):
    role = cu["role"] if cu else ""
    emp_links = '<a href="/goals" id="nl-goals">My Goals</a><a href="/checkin" id="nl-checkin">Check-in</a>' if role=="employee" else ""
    mgr_links = "" if role!="manager" else ""
    admin_links = '<a href="/analytics" id="nl-analytics">Analytics</a><a href="/escalations" id="nl-esc">Escalations</a><a href="/admin/report" id="nl-report">Reports</a>' if role=="admin" else ""
    notif_items = ""
    for n in notifs:
        ur = "ur" if not n["read"] else ""
        notif_items += f'<div class="ni {ur}"><div class="ni-dot dot-{n["type"]}"></div><div><div class="ni-title">{n["title"]}</div><div class="ni-msg">{n["msg"]}</div><div class="ni-time">{n["time"]}</div></div></div>'
    if not notifs: notif_items = '<div style="padding:1.4rem;text-align:center;color:#6b7590;font-size:.82rem">No notifications</div>'
    badge = f'<span class="nbd">{unread}</span>' if unread > 0 else ""
    name_short = cu["name"].split()[0] if cu else ""
    return f"""<nav>
<div class="brand">Atom<b>Quest</b></div>
<div class="nav-links">
  <a href="/dashboard" id="nl-dash">Dashboard</a>
  {emp_links}{admin_links}
</div>
<div class="nav-r">
  <div class="sw"><a href="/switch/employee">Emp</a><a href="/switch/manager">Mgr</a><a href="/switch/admin">Admin</a></div>
  <div style="position:relative">
    <button class="nb" onclick="toggleN()">&#128276;{badge}</button>
    <div class="np" id="np">
      <div class="nh"><span style="font-weight:700;font-size:.85rem">Notifications</span><span style="font-size:.7rem;color:#6b7590">{unread} unread</span></div>
      {notif_items}
    </div>
  </div>
  <span class="rbadge rb-{role}">{role}</span>
  <span style="font-size:.8rem;color:#6b7590">{name_short}</span>
  <a href="/logout" style="font-size:.73rem;color:#6b7590;padding:.28rem .55rem;border:1px solid #2a3040;border-radius:5px">Logout</a>
</div></nav>
<script>
function toggleN(){{document.getElementById('np').classList.toggle('open')}}
document.addEventListener('click',function(e){{var p=document.getElementById('np');if(p&&!p.contains(e.target)&&!e.target.closest('.nb'))p.classList.remove('open')}});
var path=window.location.pathname;
var map={{'/':[  ],'/dashboard':['nl-dash'],'/goals':['nl-dash','nl-goals'],'/checkin':['nl-dash','nl-checkin'],'/analytics':['nl-dash','nl-analytics'],'/escalations':['nl-dash','nl-esc'],'/admin/report':['nl-dash','nl-report']}};
var active=map[path]||['nl-dash'];
active.forEach(function(id){{var el=document.getElementById(id);if(el)el.classList.add('on')}});
</script>"""

def flash_html():
    from flask import get_flashed_messages
    msgs = get_flashed_messages(with_categories=True)
    return "".join(f'<div class="flash flash-{c}">{m}</div>' for c,m in msgs)

def page(content, uid=None):
    cu = current_user()
    uid = uid or session.get("user_id","")
    notifs = NOTIFICATIONS.get(uid,[])
    unread = unread_count(uid)
    nav = nav_html(uid, cu, notifs, unread) if cu else ""
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AtomQuest</title>{CSS}</head><body>
{nav}<div class="page">{flash_html()}{content}</div></body></html>"""

# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════
@app.route("/")
def index(): return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    error = ""
    if request.method == "POST":
        uid = request.form.get("username","").strip()
        pwd = request.form.get("password","").strip()
        if uid in USERS and USERS[uid]["password"] == pwd:
            session["user_id"] = uid; return redirect(url_for("dashboard"))
        error = '<div style="background:rgba(255,77,106,.12);border:1px solid rgba(255,77,106,.3);color:#ff4d6a;padding:.6rem 1rem;border-radius:8px;font-size:.82rem;margin-bottom:1rem">Invalid username or password.</div>'
    return render_template_string(f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AtomQuest Login</title>{CSS}
<style>body{{display:flex;align-items:center;justify-content:center}}.wrap{{width:100%;max-width:410px;padding:1rem}}.lcard{{background:#1e2330;border:1px solid #2a3040;border-radius:16px;padding:2rem}}</style>
</head><body>
<div class="wrap">
  <div style="text-align:center;margin-bottom:2rem">
    <div style="font-size:2.2rem;font-weight:900;letter-spacing:-1px">Atom<span style="color:#4f8eff">Quest</span></div>
    <div style="color:#6b7590;font-size:.83rem;margin-top:.35rem">Goal Setting and Tracking Portal &bull; FY 2025-26</div>
  </div>
  <div class="lcard">
    <div style="font-weight:700;font-size:1.1rem;margin-bottom:1.35rem">Sign In</div>
    {error}
    <form method="POST">
      <div class="fg"><label>Username</label><input name="username" placeholder="emp1 / mgr1 / admin1" autofocus required></div>
      <div class="fg"><label>Password</label><input type="password" name="password" placeholder="Password" required></div>
      <button class="btn btn-p" style="width:100%;padding:.65rem;font-size:.9rem;margin-top:.35rem">Sign In</button>
    </form>
    <div style="margin-top:1.4rem">
      <div style="font-size:.7rem;color:#6b7590;text-align:center;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.65rem">Quick Demo Access</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.45rem">
        <a href="/switch/employee" style="display:block;text-align:center;padding:.55rem .3rem;border-radius:8px;font-size:.75rem;font-weight:700;color:#4f8eff;border:1px solid rgba(79,142,255,.3);background:rgba(79,142,255,.08)">Employee<br><span style="font-size:.65rem;font-weight:400;color:#6b7590">emp1/emp123</span></a>
        <a href="/switch/manager"  style="display:block;text-align:center;padding:.55rem .3rem;border-radius:8px;font-size:.75rem;font-weight:700;color:#00d4aa;border:1px solid rgba(0,212,170,.3);background:rgba(0,212,170,.08)">Manager<br><span style="font-size:.65rem;font-weight:400;color:#6b7590">mgr1/mgr123</span></a>
        <a href="/switch/admin"    style="display:block;text-align:center;padding:.55rem .3rem;border-radius:8px;font-size:.75rem;font-weight:700;color:#ff7b47;border:1px solid rgba(255,123,71,.3);background:rgba(255,123,71,.08)">Admin<br><span style="font-size:.65rem;font-weight:400;color:#6b7590">admin1/admin123</span></a>
      </div>
    </div>
  </div>
</div></body></html>""")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/switch/<role>")
def switch_role(role):
    m={"employee":"emp1","manager":"mgr1","admin":"admin1"}
    if role in m: session["user_id"]=m[role]
    return redirect(url_for("dashboard"))

# ─── DASHBOARD ────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user: return redirect(url_for("login"))

    if user["role"] == "employee":
        sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
        score = get_overall_score(sheet["id"]) if sheet else 0
        comments = CHECKIN_COMMENTS.get(user["id"], [])
        color = sc_color(score)
        goals_rows = ""
        if sheet:
            for g in sheet["goals"]:
                sc = compute_score(g)
                cls = "pg" if sc>=75 else "py" if sc>=50 else "pr"
                st = f'<span class="pill p-on-track">On Track</span>' if g["status"]=="On Track" else f'<span class="pill p-completed">Done</span>' if g["status"]=="Completed" else f'<span class="pill p-not-started">Pending</span>'
                goals_rows += f"""<tr>
                  <td><div style="font-weight:600;font-size:.86rem">{g['title']}</div><div style="font-size:.72rem;color:#6b7590">{g['description'][:52]}...</div></td>
                  <td><span class="tag">{g['thrust']}</span></td>
                  <td style="font-family:monospace">{g['target']}</td>
                  <td style="font-family:monospace;color:#00d4aa">{g['q2']}</td>
                  <td><strong>{g['weightage']}%</strong></td>
                  <td style="min-width:110px"><div style="display:flex;align-items:center;gap:.38rem"><div class="pbar" style="flex:1;height:6px"><div class="pf {cls}" style="width:{min(sc,100)}%"></div></div><span style="font-size:.7rem;width:30px;text-align:right">{sc}%</span></div></td>
                  <td>{st}</td></tr>"""
        comment_html = ""
        for c in comments:
            comment_html += f'<div style="border-left:3px solid #00d4aa;padding:.65rem 1rem;margin-bottom:.6rem;background:rgba(0,212,170,.05);border-radius:0 8px 8px 0"><div style="display:flex;justify-content:space-between;margin-bottom:.2rem"><strong style="font-size:.81rem">{c["quarter"]} — {c["manager"]}</strong><span style="font-size:.7rem;color:#6b7590">{c["date"]}</span></div><div style="font-size:.81rem;color:#6b7590">{c["comment"]}</div></div>'
        sheet_status = sheet["sheet_status"] if sheet else "draft"
        sheet_count = len(sheet["goals"]) if sheet else 0
        comment_count = len(comments)
        body = f"""
<div class="pt">Good day, {user['name'].split()[0]} 👋</div>
<div class="ps">FY 2025–26 &bull; {user['dept']}</div>
<div class="g4" style="margin-bottom:1.4rem">
  <div class="stat"><div class="sl">Overall Score</div><div class="sv" style="color:{color}">{score}%</div><div class="ss">Weighted avg Q2</div></div>
  <div class="stat"><div class="sl">Goals</div><div class="sv">{sheet_count}<span style="font-size:.9rem;color:#6b7590">/8</span></div><div class="ss">Active this cycle</div></div>
  <div class="stat"><div class="sl">Sheet Status</div><div style="margin-top:.45rem"><span class="pill p-{sheet_status}">{sheet_status}</span></div><div class="ss" style="margin-top:.38rem">Goal sheet state</div></div>
  <div class="stat"><div class="sl">Check-ins</div><div class="sv">{comment_count}</div><div class="ss">Manager feedback</div></div>
</div>
{'<div class="card" style="margin-bottom:1.2rem"><div class="sh"><div class="sht">My Goals — Q2 Progress</div><div style="display:flex;gap:.45rem"><a href="/goals" class="btn btn-o btn-sm">Manage</a><a href="/checkin" class="btn btn-p btn-sm">Check-in</a></div></div><table><thead><tr><th>Goal</th><th>Thrust</th><th>Target</th><th>Q2 Actual</th><th>Weight</th><th>Progress</th><th>Status</th></tr></thead><tbody>' + goals_rows + '</tbody></table></div>' if sheet else '<div class="card" style="text-align:center;padding:3rem"><div style="font-size:2rem;margin-bottom:.85rem">🎯</div><div style="font-weight:700;font-size:1.05rem;margin-bottom:.45rem">No Goals Yet</div><div style="color:#6b7590;font-size:.83rem;margin-bottom:1.35rem">Start creating your goals for this cycle.</div><a href="/goals" class="btn btn-p">Create Goals</a></div>'}
{'<div class="card"><div class="sht" style="margin-bottom:.9rem">Manager Check-in Comments</div>' + comment_html + '</div>' if comments else ''}"""
        return render_template_string(page(body))

    elif user["role"] == "manager":
        team_html = ""
        submitted_count = approved_count = 0
        team_list = [(uid,u) for uid,u in USERS.items() if u.get("manager")==user["id"]]
        for uid,u in team_list:
            sheet = next((s for s in GOALS.values() if s["owner"]==uid), None)
            score = get_overall_score(sheet["id"]) if sheet else 0
            status = sheet["sheet_status"] if sheet else "no goals"
            if status=="submitted": submitted_count+=1
            if status=="approved": approved_count+=1
            overdue = '<span style="color:#ff4d6a;font-size:.72rem"> &bull; ⚠ 5d overdue</span>' if status=="draft" else ""
            review_btn = f'<a href="/manager/review/{uid}" class="btn btn-o btn-sm">{"Review ›" if status=="submitted" else "View ›"}</a>' if sheet else ""
            team_html += f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:.95rem;border:1px solid #2a3040;border-radius:10px;margin-bottom:.6rem;background:rgba(255,255,255,.01)">
              <div style="display:flex;align-items:center;gap:.9rem;flex:1">
                <div style="width:38px;height:38px;border-radius:50%;background:#4f8eff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.88rem;opacity:.85">{u['name'][0]}</div>
                <div><div style="font-weight:600;font-size:.9rem">{u['name']}</div>
                <div style="font-size:.73rem;color:#6b7590">{len(sheet['goals']) if sheet else 0} goals &bull; Q2: <strong style="color:#00d4aa">{score}%</strong>{overdue}</div></div>
              </div>
              <div style="display:flex;align-items:center;gap:.65rem"><span class="pill p-{status}">{status}</span>{review_btn}</div>
            </div>"""
        body = f"""<div class="pt">Team Overview</div><div class="ps">Review and approve your team's goals &bull; {user['name']}</div>
<div class="g3" style="margin-bottom:1.4rem">
  <div class="stat"><div class="sl">Team Size</div><div class="sv">{len(team_list)}</div><div class="ss">Direct reports</div></div>
  <div class="stat"><div class="sl">Pending Review</div><div class="sv" style="color:#f5c542">{submitted_count}</div><div class="ss">Awaiting approval</div></div>
  <div class="stat"><div class="sl">Approved</div><div class="sv" style="color:#22c97a">{approved_count}</div><div class="ss">Goals locked</div></div>
</div>
<div class="card"><div class="sht" style="margin-bottom:1.1rem">Team Members</div>{team_html}</div>"""
        return render_template_string(page(body))

    elif user["role"] == "admin":
        sheets_rows = ""
        for sid,sheet in GOALS.items():
            owner = USERS.get(sheet["owner"],{})
            sc = get_overall_score(sid)
            unlock_btn = f'<form method="POST" action="/admin/unlock/{sid}" style="display:inline"><button class="btn btn-w btn-sm">🔓 Unlock</button></form>' if sheet["sheet_status"]=="approved" else '<span style="font-size:.73rem;color:#6b7590">—</span>'
            sheets_rows += f'<tr><td><strong>{owner.get("name","")}</strong></td><td style="color:#6b7590;font-size:.78rem">{owner.get("dept","")}</td><td>{len(sheet["goals"])}</td><td><span class="pill p-{sheet["sheet_status"]}">{sheet["sheet_status"]}</span></td><td style="font-weight:700;color:{sc_color(sc)}">{sc}%</td><td>{unlock_btn}</td></tr>'
        audit_rows = "".join(f'<tr><td style="font-family:monospace;font-size:.72rem;color:#6b7590">{l["timestamp"]}</td><td style="font-size:.8rem;font-weight:500">{l["user"]}</td><td><span style="font-size:.7rem;padding:.16rem .48rem;border-radius:4px;background:rgba(79,142,255,.1);color:#4f8eff">{l["action"]}</span></td><td style="font-size:.8rem">{l["entity"]}</td><td style="font-size:.73rem;color:#6b7590">{l["detail"]}</td></tr>' for l in AUDIT_LOG)
        body = f"""<div class="pt">Admin Dashboard</div><div class="ps">Organisation-wide goal tracking &bull; FY 2025-26</div>
<div class="g4" style="margin-bottom:1.4rem">
  <div class="stat"><div class="sl">Goal Setting</div><div class="sv" style="color:#4f8eff">2/3</div><div class="ss">Submitted or approved</div></div>
  <div class="stat"><div class="sl">Q1 Check-ins</div><div class="sv" style="color:#22c97a">1/3</div><div class="ss">Completed</div></div>
  <div class="stat"><div class="sl">Q2 Check-ins</div><div class="sv" style="color:#22c97a">1/3</div><div class="ss">Completed</div></div>
  <div class="stat"><div class="sl">Escalations</div><div class="sv" style="color:#ff4d6a">1</div><div class="ss">Active alerts</div></div>
</div>
<div style="display:flex;gap:.85rem;margin-bottom:1.35rem;flex-wrap:wrap">
  <a href="/analytics" class="btn btn-p">📊 Analytics</a>
  <a href="/escalations" class="btn btn-w">🚨 Escalations</a>
  <a href="/admin/report" class="btn btn-o">📥 Reports</a>
</div>
<div class="card" style="margin-bottom:1.2rem">
  <div class="sh"><div class="sht">All Employee Goal Sheets</div></div>
  <table><thead><tr><th>Employee</th><th>Dept</th><th>Goals</th><th>Status</th><th>Q2 Score</th><th>Action</th></tr></thead>
  <tbody>{sheets_rows}</tbody></table>
</div>
<div class="card"><div class="sht" style="margin-bottom:.9rem">Audit Trail</div>
  <table><thead><tr><th>Timestamp</th><th>By</th><th>Action</th><th>Entity</th><th>Detail</th></tr></thead>
  <tbody>{audit_rows}</tbody></table>
</div>"""
        return render_template_string(page(body))
    return redirect(url_for("login"))

# ─── GOALS ────────────────────────────────────────────────────
@app.route("/goals")
def my_goals():
    user = current_user()
    if not user or user["role"]!="employee": return redirect(url_for("dashboard"))
    sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
    total_w = sum(g["weightage"] for g in sheet["goals"]) if sheet else 0
    wcolor = "#22c97a" if total_w==100 else "#ff4d6a" if total_w>100 else "#4f8eff"
    wcls = "pg" if total_w==100 else "pr" if total_w>100 else "pb"
    goal_cards = ""
    if sheet:
        for g in sheet["goals"]:
            lock = '<span class="pill" style="background:rgba(255,123,71,.1);color:#ff7b47">🔒 Locked</span>' if sheet["sheet_status"]=="approved" else ""
            st_html = f'<span class="pill p-on-track">On Track</span>' if g["status"]=="On Track" else f'<span class="pill p-completed">Completed</span>' if g["status"]=="Completed" else f'<span class="pill p-not-started">Not Started</span>'
            goal_cards += f"""<div class="card" style="margin-bottom:.8rem">
              <div style="display:flex;gap:.45rem;margin-bottom:.45rem"><span class="tag">{g['thrust']}</span>{st_html}{lock}</div>
              <div style="font-weight:700;font-size:.97rem;margin-bottom:.22rem">{g['title']}</div>
              <div style="font-size:.78rem;color:#6b7590;margin-bottom:.68rem">{g['description']}</div>
              <div style="display:flex;gap:1.75rem;font-size:.78rem;flex-wrap:wrap">
                <div><span style="color:#6b7590">Target: </span><strong>{g['target']}</strong></div>
                <div><span style="color:#6b7590">UoM: </span><strong>{g['uom'].upper()}</strong></div>
                <div><span style="color:#6b7590">Weight: </span><strong style="color:#4f8eff">{g['weightage']}%</strong></div>
                <div><span style="color:#6b7590">Q2 Actual: </span><strong style="color:#00d4aa">{g['q2']}</strong></div>
              </div></div>"""
    thrust_opts = "".join(f"<option>{t}</option>" for t in THRUST_AREAS)
    add_form = ""
    if sheet and sheet["sheet_status"]=="draft" and len(sheet["goals"])<8:
        add_form = f"""<details style="margin-top:1.4rem"><summary><span class="btn btn-p">+ Add New Goal</span></summary>
          <div class="card" style="margin-top:.8rem"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">Add Goal</div>
          <form method="POST" action="/goals/add">
            <div class="g2"><div class="fg"><label>Thrust Area</label><select name="thrust" required>{thrust_opts}</select></div>
            <div class="fg"><label>Unit of Measurement</label><select name="uom" required><option value="min">Min — Higher is better (Revenue)</option><option value="max">Max — Lower is better (TAT/Cost)</option><option value="zero">Zero-based (Incidents)</option></select></div></div>
            <div class="fg"><label>Goal Title</label><input name="title" placeholder="e.g. Increase Q3 Sales Revenue" required></div>
            <div class="fg"><label>Description</label><textarea name="description" placeholder="What you aim to achieve..."></textarea></div>
            <div class="g2"><div class="fg"><label>Target Value</label><input type="number" name="target" placeholder="e.g. 5000000" required min="0"></div>
            <div class="fg"><label>Weightage (%) — Min 10%, Remaining: {100-total_w}%</label>
              <input type="number" name="weightage" min="10" max="{100-total_w}" required oninput="updW(this.value)" placeholder="e.g. 20">
              <div style="background:#2a3040;border-radius:20px;height:6px;margin:.38rem 0;overflow:hidden"><div id="wb" style="height:100%;border-radius:20px;background:#4f8eff;width:{total_w}%;transition:all .3s"></div></div>
              <div style="font-size:.7rem;color:#6b7590">Total after: <span id="wp">{total_w}%</span></div>
            </div></div>
            <button type="submit" class="btn btn-s">Add Goal</button>
          </form></div></details>"""
    if sheet and sheet["sheet_status"]=="draft":
        submit_btn = f'<div style="margin-top:1.4rem;display:flex;align-items:center;gap:.9rem"><form method="POST" action="/goals/submit"><button class="btn btn-p">Submit for Approval</button></form>{"" if total_w==100 else f"<span style=\"color:#ff7b47;font-size:.78rem\">Weightage must equal 100% (currently {total_w}%)</span>"}</div>'
    elif sheet and sheet["sheet_status"]=="submitted":
        submit_btn = '<div class="card" style="margin-top:1.2rem;border-color:rgba(245,197,66,.3);background:rgba(245,197,66,.05)"><span style="color:#f5c542">Submitted — Awaiting manager approval.</span></div>'
    else:
        submit_btn = '<div class="card" style="margin-top:1.2rem;border-color:rgba(34,201,122,.3);background:rgba(34,201,122,.05)"><span style="color:#22c97a">Approved and Locked — Contact admin to make changes.</span></div>' if sheet else ""
    wbar = f'<div class="card" style="margin-bottom:1.2rem"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.6rem"><div><strong>Total Weightage</strong><span style="font-size:.76rem;color:#6b7590;margin-left:.45rem">(Must equal 100%)</span></div><div style="font-size:1.4rem;font-weight:800;color:{wcolor}">{total_w}% <span style="font-size:.85rem;color:#6b7590">/ 100%</span></div></div><div class="pbar" style="height:9px"><div class="pf {wcls}" style="width:{min(total_w,100)}%"></div></div><div style="display:flex;justify-content:space-between;margin-top:.38rem;font-size:.7rem;color:#6b7590"><span>Goals: {len(sheet["goals"]) if sheet else 0}/8</span><span>Remaining: {100-total_w}%</span></div></div>' if sheet else ""
    body = f"""<div class="pt">My Goal Sheet</div><div class="ps">FY 2025-26 &bull; Phase 1 Open</div>
{wbar}{goal_cards}{add_form}{submit_btn}
<script>var tw={total_w};function updW(v){{var t=tw+parseInt(v||0);document.getElementById('wp').textContent=t+'%';var b=document.getElementById('wb');b.style.width=Math.min(t,100)+'%';b.style.background=t>100?'#ff4d6a':t===100?'#22c97a':'#4f8eff';}}</script>"""
    return render_template_string(page(body))

@app.route("/goals/add", methods=["POST"])
def add_goal():
    user = current_user()
    if not user or user["role"]!="employee": return redirect(url_for("login"))
    sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
    if not sheet or sheet["sheet_status"]!="draft": flash("Goals are locked.","error"); return redirect(url_for("my_goals"))
    if len(sheet["goals"])>=8: flash("Maximum 8 goals allowed.","error"); return redirect(url_for("my_goals"))
    w = int(request.form.get("weightage",0))
    if w<10: flash("Minimum weightage is 10%.","error"); return redirect(url_for("my_goals"))
    if sum(g["weightage"] for g in sheet["goals"])+w>100: flash("Total weightage cannot exceed 100%.","error"); return redirect(url_for("my_goals"))
    sheet["goals"].append({"id":f"gn{len(sheet['goals'])+1}","thrust":request.form.get("thrust"),"title":request.form.get("title"),
        "description":request.form.get("description",""),"uom":request.form.get("uom"),
        "target":float(request.form.get("target",0)),"weightage":w,"status":"Not Started","q1":0,"q2":0,"q3":0,"q4":0})
    flash("Goal added!","success"); return redirect(url_for("my_goals"))

@app.route("/goals/submit", methods=["POST"])
def submit_goals():
    user = current_user()
    if not user or user["role"]!="employee": return redirect(url_for("login"))
    sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
    if not sheet: return redirect(url_for("my_goals"))
    tw = sum(g["weightage"] for g in sheet["goals"])
    if tw!=100: flash(f"Weightage must be 100% (currently {tw}%).","error"); return redirect(url_for("my_goals"))
    sheet["sheet_status"]="submitted"; sheet["submitted_at"]=datetime.now().strftime("%Y-%m-%d")
    NOTIFICATIONS.setdefault("mgr1",[]).insert(0,{"type":"warning","icon":"doc","title":"Goals Submitted",
        "msg":f"{user['name']} submitted goals for review.","time":datetime.now().strftime("%Y-%m-%d %H:%M"),"read":False})
    flash("Goals submitted for manager approval!","success"); return redirect(url_for("my_goals"))

# ─── CHECK-IN ─────────────────────────────────────────────────
@app.route("/checkin")
def checkin():
    user = current_user()
    if not user or user["role"]!="employee": return redirect(url_for("dashboard"))
    sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
    if not sheet or sheet["sheet_status"]!="approved":
        body = '<div class="pt">Q2 Check-in</div><div class="ps">Update achievements for Q2 (July - September 2025)</div><div class="card" style="text-align:center;padding:3rem;border-color:rgba(245,197,66,.3)"><div style="font-size:2rem;margin-bottom:.85rem">⏳</div><div style="font-weight:700;margin-bottom:.45rem">Goals Not Yet Approved</div><div style="color:#6b7590;font-size:.83rem">Manager needs to approve your goals first.</div></div>'
        return render_template_string(page(body))
    goal_blocks = ""
    for g in sheet["goals"]:
        sc = compute_score(g)
        color = "#22c97a" if sc>=75 else "#f5c542" if sc>=50 else "#ff4d6a"
        goal_blocks += f"""<div class="card" style="margin-bottom:.95rem">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:.75rem">
            <div style="flex:1"><div style="display:flex;gap:.38rem;margin-bottom:.38rem"><span class="tag">{g['thrust']}</span><span style="font-size:.66rem;color:#6b7590;background:#2a3040;padding:.16rem .48rem;border-radius:4px">{g['uom'].upper()}</span></div>
              <div style="font-weight:700;font-size:.95rem">{g['title']}</div><div style="font-size:.76rem;color:#6b7590;margin-top:.18rem">{g['description']}</div></div>
            <div style="text-align:right"><div style="font-size:.66rem;color:#6b7590;text-transform:uppercase;letter-spacing:.5px">Score</div><div style="font-size:1.6rem;font-weight:800;color:{color}">{sc}%</div><div style="font-size:.66rem;color:#6b7590">Wt: {g['weightage']}%</div></div>
          </div><hr>
          <div class="g2" style="margin-top:.7rem">
            <div><label>Planned Target</label><div style="font-size:1.2rem;font-weight:800">{g['target']}</div></div>
            <div><label>Q2 Actual Achievement</label><input type="number" name="actual_{g['id']}" value="{g['q2']}" step="any" style="font-size:.95rem;font-weight:600;color:#00d4aa" form="ci-form"></div>
          </div>
          <div class="fg" style="margin-top:.7rem;margin-bottom:0"><label>Goal Status</label>
            <select name="status_{g['id']}" form="ci-form">
              <option {'selected' if g['status']=='Not Started' else ''}>Not Started</option>
              <option {'selected' if g['status']=='On Track' else ''}>On Track</option>
              <option {'selected' if g['status']=='Completed' else ''}>Completed</option>
            </select></div>
          <div class="pbar" style="height:4px;margin-top:.6rem"><div class="pf {'pg' if sc>=75 else 'py' if sc>=50 else 'pr'}" style="width:{min(sc,100)}%"></div></div>
        </div>"""
    body = f'<div class="pt">Q2 Check-in</div><div class="ps">Update actual achievements for Q2 (July - September 2025)</div><form method="POST" action="/checkin/save" id="ci-form">{goal_blocks}<div style="display:flex;gap:.85rem;margin-top:1.2rem"><button type="submit" class="btn btn-p">Save Q2 Check-in</button><a href="/dashboard" class="btn btn-o">Cancel</a></div></form>'
    return render_template_string(page(body))

@app.route("/checkin/save", methods=["POST"])
def save_checkin():
    user = current_user()
    if not user: return redirect(url_for("login"))
    sheet = next((s for s in GOALS.values() if s["owner"]==user["id"]), None)
    if sheet:
        for g in sheet["goals"]:
            if f"actual_{g['id']}" in request.form: g["q2"]=float(request.form[f"actual_{g['id']}"])
            if f"status_{g['id']}" in request.form: g["status"]=request.form[f"status_{g['id']}"]
    flash("Q2 check-in saved!","success"); return redirect(url_for("checkin"))

# ─── MANAGER ──────────────────────────────────────────────────
@app.route("/manager/review/<uid>")
def review_employee(uid):
    user = current_user()
    if not user or user["role"]!="manager": return redirect(url_for("dashboard"))
    emp = USERS.get(uid)
    if not emp or emp.get("manager")!=user["id"]: return redirect(url_for("dashboard"))
    sheet = next((s for s in GOALS.values() if s["owner"]==uid), None)
    comments = CHECKIN_COMMENTS.get(uid,[])
    action_html = ""
    if sheet and sheet["sheet_status"]=="submitted":
        action_html = f"""<div class="card" style="margin-bottom:1.2rem;border-color:rgba(245,197,66,.3);background:rgba(245,197,66,.05)">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.85rem">
            <div><div style="font-weight:700;margin-bottom:.2rem">Awaiting Your Review</div><div style="font-size:.81rem;color:#6b7590">Submitted {sheet.get('submitted_at','')}. Approve or return for rework.</div></div>
            <div style="display:flex;gap:.6rem">
              <form method="POST" action="/manager/approve/{sheet['id']}"><button class="btn btn-s">Approve and Lock</button></form>
              <details><summary><span class="btn btn-d">Return</span></summary>
                <div class="card" style="margin-top:.6rem;border-color:rgba(255,77,106,.2)"><form method="POST" action="/manager/return/{sheet['id']}">
                  <div class="fg"><label>Reason</label><textarea name="reason" placeholder="What needs to change?" required></textarea></div>
                  <button type="submit" class="btn btn-d btn-sm">Return Goals</button>
                </form></div></details>
            </div></div></div>"""
    goal_rows = ""
    if sheet:
        for g in sheet["goals"]:
            sc = compute_score(g)
            goal_rows += f'<tr><td><div style="font-weight:500;font-size:.84rem">{g["title"]}</div><div style="font-size:.7rem;color:#6b7590">{g["description"][:48]}...</div></td><td><span class="tag" style="font-size:.65rem">{g["thrust"]}</span></td><td style="font-size:.73rem;color:#6b7590">{g["uom"].upper()}</td><td style="font-family:monospace">{g["target"]}</td><td style="font-family:monospace;color:#6b7590">{g["q1"]}</td><td style="font-family:monospace;color:#00d4aa">{g["q2"]}</td><td><strong>{g["weightage"]}%</strong></td><td style="font-weight:800;color:{"#22c97a" if sc>=75 else "#f5c542" if sc>=50 else "#ff4d6a"}">{sc}%</td><td>{"<span class=pill p-on-track>On Track</span>" if g["status"]=="On Track" else "<span class=pill p-completed>Done</span>" if g["status"]=="Completed" else "<span class=pill p-not-started>Pending</span>"}</td></tr>'
    comment_html = ""
    for c in comments:
        comment_html += f'<div style="border-left:3px solid #00d4aa;padding:.65rem 1rem;margin-bottom:.6rem;background:rgba(0,212,170,.05);border-radius:0 8px 8px 0"><div style="display:flex;justify-content:space-between;margin-bottom:.2rem"><strong style="font-size:.8rem">{c["quarter"]} — {c["manager"]}</strong><span style="font-size:.7rem;color:#6b7590">{c["date"]}</span></div><div style="font-size:.8rem;color:#6b7590">{c["comment"]}</div></div>'
    body = f"""<div style="margin-bottom:1.1rem"><a href="/dashboard" style="color:#6b7590;font-size:.8rem">Back to Team</a></div>
<div class="pt">{emp['name']}'s Goals</div>
<div class="ps">{emp['dept']} &bull; Status: <span class="pill p-{sheet['sheet_status'] if sheet else 'draft'}">{sheet['sheet_status'] if sheet else 'No Sheet'}</span></div>
{action_html}
{'<div class="card" style="margin-bottom:1.2rem"><div class="sht" style="margin-bottom:.9rem">Goal Details — Planned vs Actual</div><table><thead><tr><th>Goal</th><th>Thrust</th><th>UoM</th><th>Target</th><th>Q1</th><th>Q2</th><th>Wt</th><th>Score</th><th>Status</th></tr></thead><tbody>'+goal_rows+'</tbody></table></div>' if sheet else ''}
<div class="card"><div class="sht" style="margin-bottom:.9rem">Q2 Check-in Comments</div>
{comment_html if comments else '<div style="color:#6b7590;font-size:.82rem;margin-bottom:.85rem">No comments yet.</div>'}
<details style="margin-top:.45rem"><summary><span class="btn btn-p btn-sm">+ Add Q2 Comment</span></summary>
<div style="margin-top:.8rem"><form method="POST" action="/manager/checkin/{uid}">
  <div class="fg"><label>Comment / Feedback</label><textarea name="comment" placeholder="Document your discussion and guidance..." required></textarea></div>
  <button type="submit" class="btn btn-s btn-sm">Save Check-in</button>
</form></div></details></div>"""
    return render_template_string(page(body))

@app.route("/manager/approve/<sheet_id>", methods=["POST"])
def approve_sheet(sheet_id):
    user = current_user()
    if not user or user["role"]!="manager": return redirect(url_for("dashboard"))
    sheet = GOALS.get(sheet_id)
    if sheet:
        sheet["sheet_status"]="approved"
        AUDIT_LOG.insert(0,{"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),"user":user["name"],"action":"Approved","entity":USERS[sheet["owner"]]["name"],"detail":"Goals approved and locked"})
        NOTIFICATIONS.setdefault(sheet["owner"],[]).insert(0,{"type":"success","icon":"check","title":"Goals Approved","msg":f"Your goals were approved by {user['name']}.","time":datetime.now().strftime("%Y-%m-%d %H:%M"),"read":False})
    flash("Goal sheet approved and locked!","success"); return redirect(url_for("dashboard"))

@app.route("/manager/return/<sheet_id>", methods=["POST"])
def return_sheet(sheet_id):
    user = current_user()
    if not user or user["role"]!="manager": return redirect(url_for("dashboard"))
    sheet = GOALS.get(sheet_id)
    if sheet:
        sheet["sheet_status"]="draft"
        AUDIT_LOG.insert(0,{"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),"user":user["name"],"action":"Returned","entity":USERS[sheet["owner"]]["name"],"detail":request.form.get("reason","No reason")})
    flash("Goal sheet returned for rework.","success"); return redirect(url_for("dashboard"))

@app.route("/manager/checkin/<uid>", methods=["POST"])
def manager_checkin(uid):
    user = current_user()
    if not user or user["role"]!="manager": return redirect(url_for("dashboard"))
    comment = request.form.get("comment","").strip()
    if comment:
        CHECKIN_COMMENTS.setdefault(uid,[]).append({"quarter":"Q2","manager":user["name"],"comment":comment,"date":datetime.now().strftime("%Y-%m-%d")})
        flash("Check-in comment saved.","success")
    return redirect(url_for("review_employee",uid=uid))

# ─── ADMIN ────────────────────────────────────────────────────
@app.route("/admin/unlock/<sheet_id>", methods=["POST"])
def unlock_sheet(sheet_id):
    user = current_user()
    if not user or user["role"]!="admin": return redirect(url_for("dashboard"))
    sheet = GOALS.get(sheet_id)
    if sheet:
        sheet["sheet_status"]="draft"
        AUDIT_LOG.insert(0,{"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),"user":user["name"],"action":"Unlocked","entity":USERS[sheet["owner"]]["name"],"detail":"Admin unlocked goal sheet"})
    flash("Goal sheet unlocked.","success"); return redirect(url_for("dashboard"))

# ─── ANALYTICS ────────────────────────────────────────────────
@app.route("/analytics")
def analytics():
    user = current_user()
    if not user or user["role"]!="admin": return redirect(url_for("dashboard"))
    # QoQ bars
    qoq_html = ""
    for eid, qd in QOQ_DATA.items():
        bars = ""
        for q in ["Q1","Q2","Q3","Q4"]:
            v = qd[q]
            c = "#22c97a" if v>=75 else "#f5c542" if v>=50 else "#ff4d6a" if v>0 else "#2a3040"
            lbl = f"{v}%" if v>0 else "—"
            bars += f'<div class="bar-col"><div class="bar-val" style="color:{c}">{lbl}</div><div class="bar" style="height:{v}px;background:{c}"></div><div class="bar-lbl">{q}</div></div>'
        qoq_html += f'<div style="margin-bottom:1.1rem"><div style="font-size:.78rem;font-weight:600;margin-bottom:.45rem">{qd["name"]}</div><div class="bar-wrap">{bars}</div></div>'
    # Thrust distribution
    td = {}
    total_g = 0
    for sheet in GOALS.values():
        for g in sheet["goals"]: td[g["thrust"]]=td.get(g["thrust"],0)+1; total_g+=1
    thrust_html = ""
    for thrust,count in sorted(td.items(),key=lambda x:-x[1]):
        pct = int(count/total_g*100) if total_g else 0
        thrust_html += f'<div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.6rem"><div style="font-size:.78rem;width:155px">{thrust}</div><div class="pbar" style="flex:1;height:7px"><div class="pf pb" style="width:{pct}%"></div></div><div style="font-size:.76rem;font-weight:700;width:22px;text-align:right">{count}</div></div>'
    # Heatmap
    hm_html = ""
    for sheet in GOALS.values():
        sc = get_overall_score(sheet["id"])
        name = USERS[sheet["owner"]]["name"].split()[0]
        rgb = "34,201,122" if sc>=75 else "245,197,66" if sc>=50 else "255,77,106" if sc>0 else "107,117,144"
        hm_html += f'<div class="hm-cell" style="background:rgba({rgb},.18);border:1px solid rgba({rgb},.35)"><div class="hm-lbl">{name}</div><div class="hm-val" style="color:rgb({rgb})">{sc}%</div></div>'
    # UoM breakdown
    uom_counts = {"min":0,"max":0,"zero":0}
    for sheet in GOALS.values():
        for g in sheet["goals"]: uom_counts[g["uom"]]=uom_counts.get(g["uom"],0)+1
    uom_html = ""
    uom_labels = {"min":"Min (Higher is better)","max":"Max (Lower is better)","zero":"Zero-based"}
    uom_colors = {"min":"#4f8eff","max":"#00d4aa","zero":"#f5c542"}
    for uom,count in uom_counts.items():
        pct = int(count/total_g*100) if total_g else 0
        uom_html += f'<div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.55rem"><div style="font-size:.76rem;width:155px">{uom_labels[uom]}</div><div class="pbar" style="flex:1;height:7px"><div class="pf" style="width:{pct}%;background:{uom_colors[uom]}"></div></div><span style="font-size:.76rem;font-weight:700;width:22px;text-align:right">{count}</span></div>'
    # Manager effectiveness
    team_scores = [get_overall_score(sid) for sid in ["g1","g2","g3"]]
    avg_score = round(sum(team_scores)/len(team_scores),1)
    eff_bar = f'<div class="pbar" style="width:90px;height:5px;display:inline-block;vertical-align:middle;margin-left:.4rem"><div class="pf py" style="width:72%"></div></div>'
    mgr_row = f'<tr><td><strong>Neha Kapoor</strong></td><td>3</td><td><span class="pill p-submitted">1/3</span></td><td>1/3</td><td>1/3</td><td style="font-weight:700;color:{"#22c97a" if avg_score>=75 else "#f5c542"}">{avg_score}%</td><td>72%{eff_bar}</td></tr>'
    body = f"""<div class="pt">Analytics Dashboard</div><div class="ps">QoQ trends, heatmaps and goal distribution &bull; FY 2025-26</div>
<div class="g2" style="margin-bottom:1.2rem">
  <div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">📈 Quarter-on-Quarter Achievement</div>{qoq_html}</div>
  <div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">🎯 Goal Distribution by Thrust Area</div>{thrust_html}<hr><div style="font-size:.73rem;color:#6b7590">Total goals: <strong style="color:#e8ecf4">{total_g}</strong></div></div>
</div>
<div class="g2" style="margin-bottom:1.2rem">
  <div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">🔥 Completion Heatmap — Q2 Scores</div><div class="hm">{hm_html}</div></div>
  <div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">📐 Goal Distribution by UoM Type</div>{uom_html}<hr><div style="font-size:.73rem;color:#6b7590">Total goals: <strong style="color:#e8ecf4">{total_g}</strong></div></div>
</div>
<div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">👔 Manager Effectiveness Dashboard</div>
  <table><thead><tr><th>Manager</th><th>Team Size</th><th>Approvals</th><th>Q1 Check-ins</th><th>Q2 Check-ins</th><th>Avg Team Score</th><th>Effectiveness</th></tr></thead>
  <tbody>{mgr_row}</tbody></table>
</div>"""
    return render_template_string(page(body))

# ─── ESCALATIONS ──────────────────────────────────────────────
@app.route("/escalations")
def escalations():
    user = current_user()
    if not user or user["role"]!="admin": return redirect(url_for("dashboard"))
    active = sum(1 for e in ESCALATION_LOG if e["status"]!="Resolved")
    resolved = sum(1 for e in ESCALATION_LOG if e["status"]=="Resolved")
    esc_items = ""
    for e in ESCALATION_LOG:
        is_res = e["status"]=="Resolved"
        pill = f'<span class="pill p-resolved">Resolved</span>' if is_res else f'<span class="pill p-danger">Escalated</span>'
        esc_items += f'<div class="esc-i {"esc-r" if is_res else "esc-d"}"><div><div style="font-weight:600;font-size:.86rem">{e["employee"]} — {e["type"]}</div><div style="font-size:.76rem;color:#6b7590;margin-top:.18rem">Escalated to: {e["escalated_to"]} &bull; {e["days_overdue"]} days overdue</div><div style="font-size:.7rem;color:#6b7590;margin-top:.14rem">{e["timestamp"]}</div></div>{pill}</div>'
    body = f"""<div class="pt">Escalation Monitor</div><div class="ps">Rule-based alerts and escalation chain tracking</div>
<div class="g3" style="margin-bottom:1.4rem">
  <div class="stat"><div class="sl">Active</div><div class="sv" style="color:#ff4d6a">{active}</div><div class="ss">Require action</div></div>
  <div class="stat"><div class="sl">Resolved</div><div class="sv" style="color:#22c97a">{resolved}</div><div class="ss">This cycle</div></div>
  <div class="stat"><div class="sl">Rules Active</div><div class="sv">3</div><div class="ss">Configured</div></div>
</div>
<div class="card" style="margin-bottom:1.2rem">
  <div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">⚙ Configured Escalation Rules</div>
  <table><thead><tr><th>Rule</th><th>Trigger Condition</th><th>Escalation Chain</th><th>Status</th></tr></thead><tbody>
    <tr><td>Goal Submission Overdue</td><td>Not submitted within <strong>5 days</strong> of cycle open</td><td>Employee → Manager → HR</td><td><span class="pill p-approved">Active</span></td></tr>
    <tr><td>Manager Approval Overdue</td><td>Not approved within <strong>5 days</strong> of submission</td><td>Manager → HR</td><td><span class="pill p-approved">Active</span></td></tr>
    <tr><td>Check-in Overdue</td><td>Not completed within <strong>7 days</strong> of window close</td><td>Employee → Manager</td><td><span class="pill p-approved">Active</span></td></tr>
  </tbody></table>
</div>
<div class="card"><div style="font-weight:700;font-size:.9rem;margin-bottom:.9rem">📋 Escalation Log</div>{esc_items}</div>"""
    return render_template_string(page(body))

# ─── REPORT ───────────────────────────────────────────────────
@app.route("/admin/report")
def report():
    user = current_user()
    if not user or user["role"]!="admin": return redirect(url_for("dashboard"))
    rows = ""
    for sheet in GOALS.values():
        owner = USERS.get(sheet["owner"],{})
        for g in sheet["goals"]:
            sc = compute_score(g)
            c = sc_color(sc)
            st = '<span class="pill p-on-track">On Track</span>' if g["status"]=="On Track" else '<span class="pill p-completed">Done</span>' if g["status"]=="Completed" else '<span class="pill p-not-started">Pending</span>'
            rows += f'<tr><td style="font-weight:500">{owner.get("name","")}</td><td style="color:#6b7590;font-size:.78rem">{owner.get("dept","")}</td><td><span class="tag">{g["thrust"]}</span></td><td style="font-size:.81rem">{g["title"]}</td><td style="font-size:.73rem;color:#6b7590">{g["uom"].upper()}</td><td style="font-family:monospace">{g["target"]}</td><td style="font-family:monospace;color:#6b7590">{g["q1"]}</td><td style="font-family:monospace;color:#00d4aa">{g["q2"]}</td><td><strong>{g["weightage"]}%</strong></td><td style="font-weight:800;color:{c}">{sc}%<div class="pbar" style="height:3px;margin-top:3px"><div class="pf {"pg" if sc>=75 else "py" if sc>=50 else "pr"}" style="width:{min(sc,100)}%"></div></div></td><td>{st}</td></tr>'
    body = f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.4rem">
  <div><div class="pt">Achievement Report</div><div class="ps">Planned vs Actual &bull; All Employees &bull; Q2 2025</div></div>
  <button onclick="dlCSV()" class="btn btn-p">Download CSV</button>
</div>
<div class="card"><table id="rt"><thead><tr><th>Employee</th><th>Dept</th><th>Thrust</th><th>Goal</th><th>UoM</th><th>Target</th><th>Q1</th><th>Q2</th><th>Wt</th><th>Score</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<script>function dlCSV(){{var t=document.getElementById('rt');var csv=Array.from(t.querySelectorAll('tr')).map(function(r){{return Array.from(r.querySelectorAll('th,td')).map(function(c){{return'"'+c.innerText.replace(/\\n/g,' ').trim()+'"'}}).join(',')}}).join('\\n');var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{{type:'text/csv'}}));a.download='atomquest_report.csv';a.click();}}</script>"""
    return render_template_string(page(body))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
