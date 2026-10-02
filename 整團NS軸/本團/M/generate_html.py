"""Build the self-contained Mythic raid timeline and NSRT viewer."""

from __future__ import annotations

import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
TIMELINES = ROOT.parents[2] / "整團時間軸" / "M"
LABELS = {
    "浪縛單王": "浪縛單王 · 妮莉莎",
    "劇毒1王": "劇毒 1 王 · 纏魂者尼札利",
    "劇毒2王": "劇毒 2 王 · 墓封哨兵",
    "劇毒3王": "劇毒 3 王 · 迷路的探險者",
    "劇毒4王": "劇毒 4 王 · 伐許尼克",
    "劇毒5王": "劇毒 5 王 · 司佐拉",
    "劇毒6王": "劇毒 6 王 · 雙生毒牙",
    "劇毒7王": "劇毒 7 王 · 盤蛇祭壇",
}


def render_inline(source: str) -> str:
    """Render the inline syntax used by these source timeline documents."""
    tokens: list[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens) - 1}@@"

    def code(match: re.Match[str]) -> str:
        return stash(f"<code>{html.escape(match.group(1))}</code>")

    source = re.sub(r"`([^`]+)`", code, source)

    def link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        target = match.group(2)
        if not re.match(r"^https?://", target):
            relative = posixpath.normpath(posixpath.join("整團時間軸/M", target))
            target = "https://github.com/AppleCE/wow-raid-guides/blob/main/" + quote(relative)
        return stash(f'<a href="{html.escape(target, quote=True)}" target="_blank" rel="noopener">{label}</a>')

    source = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, source)
    source = html.escape(source)
    source = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", source)
    for index, value in enumerate(tokens):
        source = source.replace(f"@@TOKEN{index}@@", value)
    return source


def render_timeline(source: str) -> str:
    """Render the headings, prose, lists and four-column tables in M timelines."""
    lines = source.splitlines()
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            table: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    table.append(cells)
                i += 1
            if table:
                columns = len(table[0])
                if any(len(row) != columns for row in table):
                    raise RuntimeError("整團時間軸表格欄數不一致")
                result.append('<div class="tablewrap"><table class="timeline-table"><thead><tr>')
                result.extend(f"<th>{render_inline(cell)}</th>" for cell in table[0])
                result.append("</tr></thead><tbody>")
                for row in table[1:]:
                    result.append("<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>")
                result.append("</tbody></table></div>")
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 4)
            result.append(f"<h{level + 1}>{render_inline(line[level:].strip())}</h{level + 1}>")
            i += 1
            continue
        if line.startswith(">"):
            quoted: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quoted.append(lines[i].lstrip()[1:].strip())
                i += 1
            result.append("<blockquote>" + "<br>".join(render_inline(part) for part in quoted if part) + "</blockquote>")
            continue
        if line.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append("<li>" + render_inline(lines[i].strip()[2:]) + "</li>")
                i += 1
            result.append("<ul>" + "".join(items) + "</ul>")
            continue
        paragraph: list[str] = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^[#>|]", lines[i].strip()) and not lines[i].strip().startswith("- "):
            paragraph.append(lines[i].strip())
            i += 1
        result.append("<p>" + render_inline(" ".join(paragraph)) + "</p>")
    return "\n".join(result)


def build() -> None:
    files = list(ROOT.glob("*.txt"))
    expected = {f"{name}.txt" for name in LABELS}
    if {path.name for path in files} != expected:
        raise RuntimeError("TXT 清單與頁面設定不一致；請檢查新增或移除的王。")
    timeline_files = {path.name for path in TIMELINES.glob("*.md")}
    if timeline_files != {f"{name}.md" for name in LABELS}:
        raise RuntimeError("M 整團時間軸清單與 NSRT 清單不一致")
    data = []
    for name, label in LABELS.items():
        filename = f"{name}.txt"
        raw = (ROOT / filename).read_bytes().decode("utf-8-sig")
        rows = [line for line in raw.splitlines() if line.startswith("time:")]
        if not raw.startswith("EncounterID:") or not rows:
            raise RuntimeError(f"{filename} 不是預期的 NSRT 格式")
        timeline = (TIMELINES / f"{name}.md").read_text(encoding="utf-8-sig")
        data.append({"file": filename, "label": label, "raw": raw, "rows": len(rows),
                     "timeline": timeline, "timelineHtml": render_timeline(timeline)})

    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.replace("__DATA__", payload)
    (ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"Built {ROOT / 'index.html'} from {len(data)} TXT files, {sum(item['rows'] for item in data)} rows")


TEMPLATE = r'''<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>本團傳奇整團時間軸與 NSRT</title>
  <style>
    :root{color-scheme:dark;--bg:#0b1020;--panel:#151c30;--panel2:#1d2840;--line:#33415c;--text:#edf4ff;--muted:#a7b6d0;--accent:#72e0cb;--warn:#ffd28d}
    *{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#263b55 0,transparent 33%),var(--bg);color:var(--text);font:16px/1.55 system-ui,"Microsoft JhengHei",sans-serif}
    .wrap{max-width:1180px;margin:auto;padding:28px 20px 70px}header{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:16px;margin-bottom:24px}
    .eyebrow{color:var(--accent);font-weight:700;letter-spacing:.12em;font-size:.8rem}h1{margin:.1em 0;font-size:clamp(1.7rem,4vw,2.7rem)}p{margin:.4em 0;color:var(--muted)}a{color:var(--accent)}
    .layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:18px}.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 12px 30px #0002}
    nav{padding:14px;align-self:start;position:sticky;top:16px}nav button{display:block;width:100%;text-align:left;margin:3px 0;padding:11px 12px;border:1px solid transparent;border-radius:10px;background:transparent;color:var(--text);font:inherit;cursor:pointer}
    nav button:hover,nav button[aria-current="true"]{background:var(--panel2);border-color:var(--accent)}.content{padding:22px;min-width:0}
    .topline{display:flex;justify-content:space-between;gap:12px;align-items:start;flex-wrap:wrap}h2{margin:0;font-size:1.5rem}.badge{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:3px 9px;color:var(--muted);font-size:.84rem}
    .caution{color:var(--warn);margin:12px 0 18px}.actions{display:flex;flex-wrap:wrap;gap:9px;margin:16px 0}button.action,a.action{display:inline-block;border:1px solid var(--line);border-radius:9px;padding:9px 13px;background:var(--panel2);color:var(--text);font:inherit;text-decoration:none;cursor:pointer}
    button.action:hover,a.action:hover{border-color:var(--accent)}.filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:16px 0}.filters label{color:var(--muted)}select,input{background:#10182a;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:9px;font:inherit}input{min-width:190px;flex:1}
    .tablewrap{overflow:auto;border:1px solid var(--line);border-radius:10px}table{border-collapse:collapse;width:100%;min-width:620px}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #33415c80;white-space:nowrap}th{position:sticky;top:0;background:var(--panel2);color:var(--muted)}tr:last-child td{border-bottom:0}tbody tr:hover{background:#ffffff0a}.phase{color:var(--accent);font-weight:700}.time{font-variant-numeric:tabular-nums;font-weight:700}details{margin-top:20px}summary{cursor:pointer;color:var(--accent);font-weight:700}textarea{display:block;width:100%;height:280px;margin-top:12px;padding:14px;background:#0a1220;border:1px solid var(--line);border-radius:9px;color:var(--text);font:13px/1.5 Consolas,monospace;resize:vertical}footer{margin-top:25px;font-size:.9rem}
    .tabs{display:flex;gap:8px;border-bottom:1px solid var(--line);margin:18px 0}.tabs button{border:0;border-bottom:3px solid transparent;background:transparent;color:var(--muted);padding:11px 15px;font:inherit;cursor:pointer}.tabs button[aria-selected="true"]{color:var(--accent);border-bottom-color:var(--accent);font-weight:700}.timeline h2,.timeline h3,.timeline h4{margin:20px 0 9px}.timeline h2{font-size:1.3rem}.timeline p{color:var(--text);margin:12px 0}.timeline blockquote{border-left:3px solid var(--accent);background:#ffffff08;margin:14px 0;padding:9px 15px;color:var(--muted)}.timeline ul{padding-left:24px}.timeline li{margin:5px 0}.timeline code{color:var(--accent);background:#ffffff12;padding:1px 4px;border-radius:4px}.timeline .tablewrap{margin:18px 0}.timeline-table{min-width:850px}.timeline-table th,.timeline-table td{white-space:normal;vertical-align:top;min-width:150px}.timeline-table th:first-child,.timeline-table td:first-child{min-width:165px;max-width:240px;font-variant-numeric:tabular-nums}.timeline-table td:nth-child(3){min-width:250px}
    @media(max-width:780px){.layout{display:block}nav{position:static;display:flex;overflow:auto;gap:5px;margin-bottom:16px}nav button{white-space:nowrap;width:auto;flex:none}.content{padding:17px}}
  </style>
</head>
<body><div class="wrap">
  <header><div><div class="eyebrow">MYTHIC · 本團</div><h1>整團時間軸與 NSRT</h1><p>選王看完整團技能、減傷與補招；再切換 NSRT 複製匯入字串。</p></div><a href="README.md">文字說明與版本註記 ↗</a></header>
  <div class="layout"><nav class="card" id="bosses" aria-label="選擇首領"></nav>
    <main class="card content"><div class="topline"><div><h2 id="title"></h2><p id="subtitle"></p></div><span class="badge" id="count"></span></div>
      <div class="tabs" role="tablist" aria-label="檢視內容"><button id="timeline-tab" role="tab" type="button" aria-selected="true" aria-controls="timeline-panel">整團時間軸</button><button id="nsrt-tab" role="tab" type="button" aria-selected="false" aria-controls="nsrt-panel">NSRT 匯入軸</button></div>
      <section id="timeline-panel" role="tabpanel" aria-labelledby="timeline-tab"><div class="timeline" id="timeline"></div></section>
      <section id="nsrt-panel" role="tabpanel" aria-labelledby="nsrt-tab" hidden>
      <p class="caution">NSRT 的時間是階段相對秒數；不同階段的 0:00 不代表開戰後 0:00。草稿與實戰校正狀態請以原檔及整團時間軸說明為準。</p>
      <div class="actions"><button class="action" id="copy" type="button">複製完整 NSRT</button><a class="action" id="download" download>下載原始 TXT</a></div>
      <div class="filters"><label for="phase">階段</label><select id="phase"></select><label for="player">角色</label><select id="player"></select><input id="search" type="search" placeholder="搜尋技能、角色或文字" aria-label="搜尋技能、角色或文字"></div>
      <div class="tablewrap"><table><thead><tr><th>階段</th><th>階段時間</th><th>角色</th><th>技能／提醒</th></tr></thead><tbody id="rows"></tbody></table></div><p id="shown" aria-live="polite"></p>
      <details><summary>展開原始 NSRT 字串</summary><textarea id="raw" readonly spellcheck="false" aria-label="原始 NSRT 字串"></textarea></details>
      </section>
    </main></div><footer>本頁包含全部文字資料，可離線開啟；網頁只負責展示，不會修改遊戲設定。</footer>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
  const data=JSON.parse(document.getElementById('data').textContent);
  const $=id=>document.getElementById(id);
  let selected=0;
  function fields(line){const result={};for(const part of line.split(';')){const split=part.indexOf(':');if(split>0)result[part.slice(0,split)]=part.slice(split+1)}return result}
  function option(value,label){const el=document.createElement('option');el.value=value;el.textContent=label;return el}
  function fillSelect(el,values,label){el.replaceChildren(option('',label),...values.map(value=>option(value,value)))}
  function formatTime(seconds){const n=Number(seconds);return Number.isFinite(n)?`${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`:seconds}
  function showTab(name){const timeline=name==='timeline';$('timeline-panel').hidden=!timeline;$('nsrt-panel').hidden=timeline;$('timeline-tab').setAttribute('aria-selected',String(timeline));$('nsrt-tab').setAttribute('aria-selected',String(!timeline))}
  function renderRows(){const item=data[selected],phase=$('phase').value,player=$('player').value,query=$('search').value.trim().toLocaleLowerCase();const rows=item.raw.split(/\r?\n/).filter(line=>line.startsWith('time:')).map(fields);const filtered=rows.filter(row=>(!phase||row.ph===phase)&&(!player||row.tag===player)&&(!query||[row.ph,row.time,row.tag,row.text,row.spellid].join(' ').toLocaleLowerCase().includes(query)));const body=$('rows');body.replaceChildren();for(const row of filtered){const tr=document.createElement('tr');for(const [value,klass] of [[row.ph||'','phase'],[formatTime(row.time),'time'],[row.tag||'',''],[row.text||'','']]){const td=document.createElement('td');td.textContent=value;td.className=klass;tr.append(td)}body.append(tr)}$('shown').textContent=`顯示 ${filtered.length}／${rows.length} 筆提醒`}
  function selectBoss(index){selected=index;const item=data[index];$('title').textContent=item.label;$('subtitle').textContent=item.raw.split(/\r?\n/)[0];$('count').textContent=`${item.rows} 筆 NSRT 提醒`;$('timeline').innerHTML=item.timelineHtml;$('raw').value=item.raw;$('download').href=item.file;$('download').setAttribute('download',item.file);const rows=item.raw.split(/\r?\n/).filter(line=>line.startsWith('time:')).map(fields);fillSelect($('phase'),[...new Set(rows.map(row=>row.ph).filter(Boolean))],'全部階段');fillSelect($('player'),[...new Set(rows.map(row=>row.tag).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'zh-Hant')),'全部角色');$('search').value='';for(const [i,button] of [...$('bosses').children].entries())button.setAttribute('aria-current',String(i===index));renderRows();history.replaceState(null,'',`#${encodeURIComponent(item.file.replace(/\.txt$/,''))}`)}
  for(const [index,item] of data.entries()){const button=document.createElement('button');button.type='button';button.textContent=item.label;button.addEventListener('click',()=>selectBoss(index));$('bosses').append(button)}
  for(const id of ['phase','player','search'])$(id).addEventListener(id==='search'?'input':'change',renderRows);
  $('timeline-tab').addEventListener('click',()=>showTab('timeline'));$('nsrt-tab').addEventListener('click',()=>showTab('nsrt'));
  $('copy').addEventListener('click',async()=>{const button=$('copy');try{if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(data[selected].raw);else{$('raw').focus();$('raw').select();if(!document.execCommand('copy'))throw Error('copy failed')}button.textContent='已複製完整 NSRT';setTimeout(()=>button.textContent='複製完整 NSRT',1800)}catch{button.textContent='請展開下方文字手動複製';setTimeout(()=>button.textContent='複製完整 NSRT',2500)}});
  const slug=decodeURIComponent(location.hash.slice(1));const start=data.findIndex(item=>item.file.replace(/\.txt$/,'')===slug);selectBoss(start<0?data.findIndex(item=>item.file==='劇毒7王.txt'):start);
</script></body></html>
'''


if __name__ == "__main__":
    build()
