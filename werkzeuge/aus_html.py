import sys, json, html, re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
IDS = {"Hannover & Region": "hannover", "Deutschland": "deutschland", "Die Welt": "welt",
       "Sport": "sport", "Was das Netz sucht": "netz"}
DEF_SUB = {"hannover": "Vor der Haustür", "deutschland": "Was das Land bewegt", "welt": "Was draußen passiert",
           "sport": "Hannover zuerst, dann der Rest", "netz": "Google Trends Deutschland"}
BEW = {"v3": "gesichert", "v2": "plausibel", "v1": "vorsicht"}

def t(el):
    return html.unescape(el.decode_contents()).strip()

data = {}
stand = soup.select("header.top .row .label")[1].get_text().strip()
data["stand"] = stand
data["kurz"] = [t(li) for li in soup.select(".core ol > li")]
data["ressorts"] = []
for sec in soup.select("section.res"):
    name = sec.select_one(".res-head h2").get_text()
    rid = IDS[name]
    r = {"id": rid}
    sub = sec.select_one(".res-head .sub").get_text()
    if sub != DEF_SUB[rid]:
        r["untertitel"] = sub
    hint = sec.select_one("p.hint")
    if hint:
        r["hinweis"] = t(hint)
    tr = sec.select(".trends .tr")
    if tr:
        r["trends"] = []
        for k in tr:
            span = k.find("span").get_text()
            vol, _, anlass = span.partition(" · ")
            e = {"begriff": k.find("b").get_text(), "volumen": vol}
            if anlass:
                e["anlass"] = anlass
            r["trends"].append(e)
    r["meldungen"] = []
    for a in sec.select("article"):
        m = {"titel": a.find("h3").get_text()}
        p = a.find("p", recursive=False)
        if p:
            m["kurz"] = t(p)
        ul = a.find("ul", class_="kurz", recursive=False)
        if ul:
            m["liste"] = [t(li) for li in ul.find_all("li")]
        val = a.select_one(".meta .val")
        m["bewertung"] = BEW[[c for c in val["class"] if c in BEW][0]]
        orte = []
        for g in a.select(".meta a.geo"):
            q = parse_qs(urlparse(html.unescape(g["href"])).query)["query"][0]
            lab = g.get_text()
            if lab.startswith("Karte: "):
                n = lab[len("Karte: "):]
                orte.append({"name": n, "suche": q} if n != q else {"name": n})
            else:
                orte.append(q)
        if orte:
            m["orte"] = orte
        lng = a.select_one(".long")
        if lng:
            ps = [x for x in lng.find_all("p", recursive=False) if not x.get("class")]
            m["lang"] = [t(x) for x in ps]
            why = lng.select_one("p.why")
            if why:
                why.find("b").extract()
                m["einschaetzung"] = t(why)
            m["quellen"] = [{"name": x.get_text(), "url": html.unescape(x["href"])} for x in lng.select("p.src a")]
        r["meldungen"].append(m)
    data["ressorts"].append(r)
data["faktencheck"] = [t(li) for li in soup.select(".warn ul > li")]
data["woche"] = [{"wann": s.select_one(".when").get_text(), "titel": s.find("b").get_text(),
                  "text": t(s.find_all("span", recursive=False)[-1])} for s in soup.select(".start .step")]
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
