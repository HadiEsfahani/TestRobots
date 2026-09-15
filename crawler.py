import argparse,csv,re,sys,time,requests,xml.etree.ElementTree as ET
from collections import deque
from urllib.parse import urljoin,urlparse,urldefrag
from bs4 import BeautifulSoup

UA="GitHubActions-CompleteWebsiteMapper/1.0"
TIMEOUT=20

def norm(u):
    if not u:return None
    u=urldefrag(u)[0].strip()
    p=urlparse(u)
    if p.scheme not in ("http","https") or not p.netloc:return None
    path=re.sub(r"/+","/",p.path or "/")
    if path!="/" and path.endswith("/"):path=path[:-1]
    return p._replace(path=path).geturl()

def same(a,b):
    x,y=urlparse(a),urlparse(b)
    return x.netloc.lower().removeprefix("www.")==y.netloc.lower().removeprefix("www.")

class Mapper:
    def __init__(self,start,max_pages):
        self.start=norm(start); self.max_pages=max_pages
        self.s=requests.Session(); self.s.headers["User-Agent"]=UA
        self.seen=set(); self.rows={}; self.sitemaps=set()

    def get(self,u):
        try:return self.s.get(u,timeout=TIMEOUT,allow_redirects=True)
        except:return None

    def sitemap(self,u,found):
        u=norm(u)
        if not u or u in self.sitemaps:return
        self.sitemaps.add(u)
        r=self.get(u)
        if not r or r.status_code>=400:return
        try:
            root=ET.fromstring(r.content)
            for e in root.iter():
                if e.tag.split("}")[-1]=="loc" and e.text:
                    x=norm(e.text)
                    if x:
                        if x.lower().endswith(".xml"):self.sitemap(x,found)
                        elif same(x,self.start):found.add(x)
        except:pass

    def discover(self):
        sms=set()
        r=self.get(urljoin(self.start,"/robots.txt"))
        if r:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):sms.add(line.split(":",1)[1].strip())
        sms.update([urljoin(self.start,"/sitemap.xml"),
                    urljoin(self.start,"/sitemap_index.xml"),
                    urljoin(self.start,"/wp-sitemap.xml")])
        found=set()
        for x in sms:self.sitemap(x,found)
        return found

    def run(self):
        sm=self.discover(); q=deque([self.start]+sorted(sm))
        while q and len(self.seen)<self.max_pages:
            u=norm(q.popleft())
            if not u or u in self.seen or not same(u,self.start):continue
            self.seen.add(u); r=self.get(u)
            row={"url":u,"status":"ERROR","title":"","content_type":"","source":"sitemap" if u in sm else "link","final_url":u}
            if r:
                row["status"]=r.status_code; row["final_url"]=norm(r.url) or u
                row["content_type"]=r.headers.get("content-type","").split(";")[0]
                if "text/html" in row["content_type"]:
                    try:
                        soup=BeautifulSoup(r.text,"html.parser")
                        row["title"]=soup.title.get_text(" ",strip=True) if soup.title else ""
                        for a in soup.find_all("a",href=True):
                            x=norm(urljoin(row["final_url"],a["href"]))
                            if x and same(x,self.start) and x not in self.seen:q.append(x)
                    except:pass
            self.rows[u]=row
            if len(self.seen)%25==0:print(f"Scanned {len(self.seen)} | queue {len(q)}",flush=True)
        return sm

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--max-pages",type=int,default=50000)
    a=ap.parse_args(); m=Mapper(a.url,a.max_pages)
    sms=m.run()
    rows=list(m.rows.values())
    with open("site-map.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=["url","title","status","content_type","source","final_url"]);w.writeheader();w.writerows(rows)
    with open("site-map.txt","w",encoding="utf-8") as f:
        for r in sorted(rows,key=lambda x:x["url"]):f.write(r["url"]+"\n")
    with open("summary.txt","w",encoding="utf-8") as f:
        f.write(f"Start URL: {m.start}\nPages found: {len(rows)}\nSitemaps found: {len(sms)}\n")
    print(f"DONE: {len(rows)} URLs")
if __name__=="__main__":main()
