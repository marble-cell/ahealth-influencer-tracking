#!/usr/bin/env python3
"""data/data.json 을 읽어 index.html 을 만든다. 숫자를 새로 조회하면 data.json 만 고치고 다시 돌린다."""
import json, html
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "data/data.json").read_text(encoding="utf8"))
css = (HERE / "template.css").read_text(encoding="utf8")
WD = "월화수목금토일"
e = html.escape
DASH = '<span class="muted">-</span>'

def day(s):
    y, m, dd = map(int, s[:10].split("-"))
    return f"{m}월 {dd}일({WD[date(y, m, dd).weekday()]})"

def clock(s):
    t = datetime.strptime(s, "%Y-%m-%d %H:%M")
    return f'{"오전" if t.hour < 12 else "오후"} {t.hour % 12 or 12}시 {t.minute:02d}분'

def stamp(s): return f"{day(s)} {clock(s)}"
def man(n): return f"{n / 10000:,.0f}만 원"          # 비용은 만 원 단위
def won(n): return f"{round(n):,}원"                  # 단가는 원 단위
def won1(n): return f"{n:,.1f}원"
def pct(a, b): return f"{a / b * 100:.3f}%" if b else "-"   # 조회당 가입 비율

infl, sign, kr = d["influencers"], d["signups"], d["kr_paid"]
name_of = {i["user_id"]: i["name"] for i in infl}
# 가입 합계는 Mixpanel invite-regist-complete(초대 코드별 순 사용자)와 몽고 기록 중 큰 값.
# 링크 가입은 몽고 기록(event_meta random-point-referral)으로만 구분되므로 몽고 기록의 링크 수를 쓰고 나머지를 초대 코드로 센다.
mp = d.get("mixpanel", {}).get("by_code", {})
code_of = {i["user_id"]: i["code"] for i in infl}
def _mongo(uid, via=None): return sum(1 for s in sign if s["inviter"] == uid and via in (None, s["via"]))
def cnt(uid, via=None):
    link = _mongo(uid, "link"); tot = max(_mongo(uid), mp.get(code_of[uid], 0))
    return {"link": link, "code": tot - link, None: tot}[via]
mo, ma = d.get("mongo_as_of", ""), d.get("mixpanel", {}).get("as_of", "")
SRC = (f"가입은 앱 DB 조회({stamp(mo)} 기준)입니다." if mo >= ma else
       f"가입 합계는 Mixpanel 초대 코드 가입({stamp(ma)} 기준), 링크 가입은 앱 DB 조회({stamp(mo)} 기준)입니다.")
total = sum(cnt(i["user_id"]) for i in infl); n_link = sum(cnt(i["user_id"], "link") for i in infl); n_code = total - n_link
up = [i for i in infl if i["uploaded"]]
up_cost = sum(i["cost"] for i in up); up_views = sum(i["views"] for i in up)
all_cost = sum(i["cost"] for i in infl)
kr_cpm1 = kr["spend"] / kr["impressions"]; kr_cpa = kr["spend"] / kr["signups"]

def who(i):
    n = f'<a href="{e(i["post"])}"><b>{e(i["name"])}</b></a>' if i.get("post") else f'<b>{e(i["name"])}</b>'
    return f'{n}<br><span class="muted">{e(i["channel"])}</span>'

rows = ""
KEYS = ("views", "likes", "comments", "shares", "saves")
group = None
for i in infl:
    if i["campaign"] != group:
        group = i["campaign"]
        rows += f'<tr class="grp"><td colspan="15">{e(group)}</td></tr>'
    c, l = cnt(i["user_id"], "code"), cnt(i["user_id"], "link")
    note = f'<br><span class="muted">{e(i["cost_note"])}</span>' if i["cost_note"] else ""
    if i["uploaded"]:
        n = c + l
        when = f'{day(i["upload"])}<br>{clock(i["posted_at"])}<br><span class="idx good">업로드 완료</span>'
        m = "".join(f'<td class="n">{i[k]:,}</td>' for k in KEYS)
        m += f'<td class="n g"><b>{c}명</b></td><td class="n"><b>{l}명</b></td><td class="n"><b>{n}명</b></td><td class="n"><b>{pct(n, i["views"])}</b></td>'
        m += f'<td class="n g"><b>{won1(i["cost"] / i["views"])}</b></td><td class="n"><b>{won(i["cost"] / n) if n else "-"}</b></td>'
    else:
        when = f'{day(i["upload"])}<br><span class="idx mid">업로드 예정</span>'
        m = "".join(f'<td class="n{" g" if k in (5, 9) else ""}">{DASH}</td>' for k in range(11))
    rows += (f'<tr><td>{who(i)}</td><td>{when}</td><td class="n">{man(i["cost"])}{note}</td>{m}'
             f'<td><code>{e(i["code"])}</code><br><a href="{e(i["link"])}">{e(i["link"].replace("https://", ""))}</a></td></tr>')
rows += (f'<tr class="sum"><td><b>총합계</b><br><span class="muted">계약 {len(infl)}명 · 업로드 {len(up)}명</span></td><td></td><td class="n"><b>{man(all_cost)}</b><br><span class="muted">업로드분 {man(up_cost)}</span></td>'
         + "".join(f'<td class="n"><b>{sum(i[k] for i in up):,}</b></td>' for k in KEYS)
         + f'<td class="n g"><b>{n_code}명</b></td><td class="n"><b>{n_link}명</b></td><td class="n"><b>{total}명</b></td><td class="n"><b>{pct(total, up_views)}</b></td>'
         + f'<td class="n g"><b>{won1(up_cost / up_views)}</b></td><td class="n"><b>{won(up_cost / total)}</b></td><td><span class="muted">단가는 업로드분 비용 기준</span></td></tr>')

log = ""
for s in sorted(sign, key=lambda s: s["at"], reverse=True):
    via = '<span class="idx brand">링크</span>' if s["via"] == "link" else '<span class="idx mid">초대 코드</span>'
    log += f'<tr><td>{stamp(s["at"])}</td><td>{e(name_of[s["inviter"]])}</td><td>{via}</td><td>{e(s["os"])}</td></tr>'

media = "".join(f'<tr><td>{e(n)}</td><td class="n">{man(sp)}</td><td class="n">{im / 10000:,.0f}만 회</td><td class="n">{won1(sp / im)}</td></tr>' for n, sp, im in kr["media"])
media += f'<tr class="sum"><td><b>전체</b></td><td class="n"><b>{kr["spend"] / 1e8:.2f}억 원</b></td><td class="n"><b>{kr["impressions"] / 10000:,.0f}만 회</b></td><td class="n"><b>{won1(kr_cpm1)}</b></td></tr>'

GOAL = {"조회 캠페인": ("조회수", "목표 누적 500만 회", "조회 1회당 비용", "목표 1원 안팎"),
        "전환 캠페인": ("가입", "초대 코드와 링크 합계", "가입 1명당 비용", "목표 3,000원 이하")}
camp_cards = ""
for camp, (k1, s1, k2, s2) in GOAL.items():
    mem = [i for i in infl if i["campaign"] == camp]; done = [i for i in mem if i["uploaded"]]
    cost = sum(i["cost"] for i in done); views = sum(i["views"] for i in done); sg = sum(cnt(i["user_id"]) for i in done)
    if camp == "조회 캠페인":
        v1 = f"{views:,}회" if done else "-"; v2 = won1(cost / views) if views else "-"
    else:
        v1 = f"{sg}명" if done else "-"; v2 = won(cost / sg) if sg else "-"
    camp_cards += (f'<article><h3>{e(camp)}</h3><p class="muted">{e(" · ".join(i["name"] for i in mem))} · {len(mem)}명 중 {len(done)}명 업로드 · 업로드분 비용 {man(cost)}</p>'
                   f'<div class="pair"><div class="kpi"><div class="k">{k1}</div><div class="v brand">{v1}</div><div class="s">{s1}</div></div>'
                   f'<div class="kpi"><div class="k">{k2}</div><div class="v">{v2}</div><div class="s">{s2}</div></div></div></article>')

page = f"""<title>인플루언서 가입 트래킹</title><meta name="claude:viewport-fit-sides" content="cover"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap"><style>{css}
td.n,th.n{{text-align:right;white-space:nowrap}}
.idx.brand{{color:var(--brand-ink);background:var(--brand-soft)}}
code{{font:600 13.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--card);border-radius:6px;padding:2px 7px}}
table.all{{min-width:1380px;font-size:14px}}table.all th,table.all td{{padding:11px 10px}}th.c{{text-align:center}}.g{{border-left:1px solid var(--line)}}table.all td:first-child,table.all td:nth-child(2){{white-space:nowrap}}table.log{{min-width:520px}}table.kr{{min-width:480px}}
.camps{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.camps article{{background:transparent;padding:0}}.camps h3{{margin-bottom:2px}}.pair{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:12px}}@media(max-width:900px){{.camps{{grid-template-columns:1fr}}}}@media(max-width:480px){{.pair{{grid-template-columns:1fr}}}}
tr.sum td{{background:var(--head)}}tr.grp td{{background:var(--brand-soft);color:var(--brand-ink);font-weight:700;font-size:13.5px;padding:8px 10px}}
</style>
<main>
<header class="top"><span class="eyebrow">에이헬스 인플루언서 캠페인</span><h1>인플루언서 가입 트래킹</h1><p class="muted">{stamp(d["as_of"])} 기준 · 시각은 모두 한국 시간</p></header>
<section id="core"><h2>핵심</h2>
<div class="camps">{camp_cards}</div></section>
<section id="each"><h2>인플루언서별</h2><p class="muted">이름을 누르면 올라간 게시물이 열립니다. {SRC}</p>
<div class="scroll"><table class="all"><thead><tr><th rowspan="2">인플루언서</th><th rowspan="2">업로드</th><th rowspan="2" class="n">비용</th><th colspan="5" class="c">게시물 반응</th><th colspan="4" class="c g">가입</th><th colspan="2" class="c g">비용 효율</th><th rowspan="2">초대 코드 · 링크</th></tr>
<tr><th class="n">조회</th><th class="n">좋아요</th><th class="n">댓글</th><th class="n">공유</th><th class="n">저장</th><th class="n g">초대 코드</th><th class="n">링크</th><th class="n">합계</th><th class="n">조회당 가입</th><th class="n g">조회 1회당</th><th class="n">가입 1명당</th></tr></thead><tbody>{rows}</tbody></table></div></section>
</main>
"""
(HERE / "index.html").write_text(page, encoding="utf8")
print("ok", total, n_code, n_link, won1(up_cost / up_views), won(up_cost / total), won1(kr_cpm1), won(kr_cpa), man(all_cost))
