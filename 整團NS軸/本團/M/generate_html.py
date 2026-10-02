"""Build the self-contained Mythic NSRT viewer from the sibling TXT files."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
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


def build() -> None:
    files = list(ROOT.glob("*.txt"))
    expected = {f"{name}.txt" for name in LABELS}
    if {path.name for path in files} != expected:
        raise RuntimeError("TXT 清單與頁面設定不一致；請檢查新增或移除的王。")
    data = []
    for name, label in LABELS.items():
        filename = f"{name}.txt"
        raw = (ROOT / filename).read_bytes().decode("utf-8-sig")
        rows = [line for line in raw.splitlines() if line.startswith("time:")]
        if not raw.startswith("EncounterID:") or not rows:
            raise RuntimeError(f"{filename} 不是預期的 NSRT 格式")
        data.append({"file": filename, "label": label, "raw": raw, "rows": len(rows)})

    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.replace("__DATA__", payload)
    (ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"Built {ROOT / 'index.html'} from {len(data)} TXT files, {sum(item['rows'] for item in data)} rows")


TEMPLATE = r'''<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>本團傳奇 NS 軸｜團隊補招</title>
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
    @media(max-width:780px){.layout{display:block}nav{position:static;display:flex;overflow:auto;gap:5px;margin-bottom:16px}nav button{white-space:nowrap;width:auto;flex:none}.content{padding:17px}}
  </style>
</head>
<body><div class="wrap">
  <header><div><div class="eyebrow">MYTHIC · 本團 NSRT</div><h1>團隊補招時間軸</h1><p>選王查看角色、階段與提醒；原始字串可完整複製匯入 NSRT。</p></div><a href="README.md">文字說明與版本註記 ↗</a></header>
  <div class="layout"><nav class="card" id="bosses" aria-label="選擇首領"></nav>
    <main class="card content"><div class="topline"><div><h2 id="title"></h2><p id="subtitle"></p></div><span class="badge" id="count"></span></div>
      <p class="caution">時間為 NSRT 階段相對秒數；不同階段的 0:00 不代表開戰後 0:00。草稿與實戰校正狀態請以原檔及說明為準。</p>
      <div class="actions"><button class="action" id="copy" type="button">複製完整 NSRT</button><a class="action" id="download" download>下載原始 TXT</a></div>
      <div class="filters"><label for="phase">階段</label><select id="phase"></select><label for="player">角色</label><select id="player"></select><input id="search" type="search" placeholder="搜尋技能、角色或文字" aria-label="搜尋技能、角色或文字"></div>
      <div class="tablewrap"><table><thead><tr><th>階段</th><th>階段時間</th><th>角色</th><th>技能／提醒</th></tr></thead><tbody id="rows"></tbody></table></div><p id="shown" aria-live="polite"></p>
      <details><summary>展開原始 NSRT 字串</summary><textarea id="raw" readonly spellcheck="false" aria-label="原始 NSRT 字串"></textarea></details>
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
  function renderRows(){const item=data[selected],phase=$('phase').value,player=$('player').value,query=$('search').value.trim().toLocaleLowerCase();const rows=item.raw.split(/\r?\n/).filter(line=>line.startsWith('time:')).map(fields);const filtered=rows.filter(row=>(!phase||row.ph===phase)&&(!player||row.tag===player)&&(!query||[row.ph,row.time,row.tag,row.text,row.spellid].join(' ').toLocaleLowerCase().includes(query)));const body=$('rows');body.replaceChildren();for(const row of filtered){const tr=document.createElement('tr');for(const [value,klass] of [[row.ph||'','phase'],[formatTime(row.time),'time'],[row.tag||'',''],[row.text||'','']]){const td=document.createElement('td');td.textContent=value;td.className=klass;tr.append(td)}body.append(tr)}$('shown').textContent=`顯示 ${filtered.length}／${rows.length} 筆提醒`}
  function selectBoss(index){selected=index;const item=data[index];$('title').textContent=item.label;$('subtitle').textContent=item.raw.split(/\r?\n/)[0];$('count').textContent=`${item.rows} 筆提醒`;$('raw').value=item.raw;$('download').href=item.file;$('download').setAttribute('download',item.file);const rows=item.raw.split(/\r?\n/).filter(line=>line.startsWith('time:')).map(fields);fillSelect($('phase'),[...new Set(rows.map(row=>row.ph).filter(Boolean))],'全部階段');fillSelect($('player'),[...new Set(rows.map(row=>row.tag).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'zh-Hant')),'全部角色');$('search').value='';for(const [i,button] of [...$('bosses').children].entries())button.setAttribute('aria-current',String(i===index));renderRows();history.replaceState(null,'',`#${encodeURIComponent(item.file.replace(/\.txt$/,''))}`)}
  for(const [index,item] of data.entries()){const button=document.createElement('button');button.type='button';button.textContent=item.label;button.addEventListener('click',()=>selectBoss(index));$('bosses').append(button)}
  for(const id of ['phase','player','search'])$(id).addEventListener(id==='search'?'input':'change',renderRows);
  $('copy').addEventListener('click',async()=>{const button=$('copy');try{if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(data[selected].raw);else{$('raw').focus();$('raw').select();if(!document.execCommand('copy'))throw Error('copy failed')}button.textContent='已複製完整 NSRT';setTimeout(()=>button.textContent='複製完整 NSRT',1800)}catch{button.textContent='請展開下方文字手動複製';setTimeout(()=>button.textContent='複製完整 NSRT',2500)}});
  const slug=decodeURIComponent(location.hash.slice(1));const start=data.findIndex(item=>item.file.replace(/\.txt$/,'')===slug);selectBoss(start<0?data.findIndex(item=>item.file==='劇毒7王.txt'):start);
</script></body></html>
'''


if __name__ == "__main__":
    build()
