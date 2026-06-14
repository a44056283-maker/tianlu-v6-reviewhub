#!/usr/bin/env python3
"""Generate lightweight CardDuel UI blueprint HTML from design/page-catalog.json.

This repository stores the compact generator. The full generated SVG/PNG package
is delivered separately as tianlu-frequi-cardduel-full-ui-pack.zip.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "design" / "page-catalog.json"
OUT = ROOT / "design" / "responsive_full_pages.generated.html"

CSS = """
:root{--bg:#050810;--panel:#08111f;--gold:#f0cf7a;--line:rgba(201,150,61,.5);--muted:#9aa7b7;--green:#40d878;--red:#ff5b5b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 10%,#2d1659 0,#050810 40%,#02050d 100%);font-family:Inter,'Microsoft YaHei',sans-serif;color:#f3e6c1}main{padding:24px}h1,h2,h3{color:var(--gold)}.page{margin:0 0 28px}.head{display:flex;justify-content:space-between;gap:12px}.head span{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{border:1px solid var(--line);border-radius:18px;padding:16px;background:linear-gradient(135deg,rgba(15,29,48,.95),rgba(5,10,18,.95));box-shadow:0 14px 30px #0008}.card p{color:var(--muted)}.ok{color:var(--green)}@media(max-width:767px){main{padding:12px 12px 84px}.head{display:block}.grid{grid-template-columns:1fr}.card{border-radius:15px}}
"""

DEFAULT_MODULES = ["指标卡", "图表", "状态", "表格", "筛选", "操作", "详情", "保存"]


def render() -> str:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    pages = data["pages"]
    body = ["<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>CardDuel UI Blueprints</title><style>", CSS, "</style></head><body><main>"]
    body.append("<h1>天禄 Freqtrade CardDuel UI Blueprints</h1>")
    for p in pages:
        body.append(f"<section class='page'><div class='head'><h2>{p['name']}</h2><span>{p['route']} · {p['category']} · mobile={p['mobile']}</span></div><div class='grid'>")
        for idx, module in enumerate(DEFAULT_MODULES):
            sign = "+" if idx % 4 != 2 else "-"
            body.append(f"<article class='card'><h3>{module}</h3><p>{p['category']} card-duel module. Business logic remains unchanged.</p><strong class='ok'>{sign}{1+idx*0.73:.2f}%</strong></article>")
        body.append("</div></section>")
    body.append("</main></body></html>")
    return "".join(body)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT}")
