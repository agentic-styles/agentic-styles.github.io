const deck = document.querySelector('.deck');
const NS = 'http://www.w3.org/2000/svg';
const PALETTE = {ink:'#172331',paper:'#f4f0e7',paper2:'#fbf8f1',muted:'#5a6671',rule:'#c8c4bb',note:'#e9e4da',wash:'#e5dfd2',coral:'#b5472d',teal:'#1c6e67',blue:'#315ea8',gold:'#896b24',amber:'#d88b43'};

const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const accentFor = part => ({A:PALETTE.coral,B:PALETTE.blue,C:PALETTE.gold,D:PALETTE.teal,E:PALETTE.teal,F:PALETTE.blue,G:PALETTE.gold,H:PALETTE.coral}[part] || PALETTE.ink);
const wordTokens = value => {
  const tokens=[];
  let word='';
  const flush=()=>{if(word){tokens.push(word);word='';}};
  for(const char of [...value]){
    if(/[A-Za-z0-9_./:+%&@#\-–—]/.test(char)) word+=char;
    else {flush();tokens.push(char);}
  }
  flush();
  return tokens;
};
const wrap = (text, max=16) => String(text).split('\n').flatMap(part => {
  if(!part.length) return [''];
  const lines=[];
  let line='';
  let pendingSpace=false;
  for(const token of wordTokens(part)){
    if(/^\s+$/.test(token)){
      pendingSpace=Boolean(line);
      continue;
    }
    const spacer=pendingSpace?' ':'';
    const projected=[...line,...spacer,...token].length;
    const closingPunctuation=/^[,.;:!?，。；：！？、)%\]】》]+$/.test(token);
    if(line && projected>max && !closingPunctuation){
      lines.push(line);
      line=token;
    }else{
      line+=spacer+token;
    }
    pendingSpace=false;
  }
  if(line) lines.push(line);
  return lines.length?lines:[''];
});
const textBlock = (x,y,text,{size=22,fill=PALETTE.ink,weight=700,anchor='middle',max=18,line=1.25,family='sans'}={}) => {
  const lines=wrap(text,max); const dy=size*line;
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${fill}" font-family="${family==='serif'?'Iowan Old Style, Songti SC, serif':'Avenir Next, PingFang SC, sans-serif'}" font-size="${size}" font-weight="${weight}">${lines.map((l,i)=>`<tspan x="${x}" dy="${i?dy:0}">${esc(l)}</tspan>`).join('')}</text>`;
};
const marker = `<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="${PALETTE.rule}" stroke-width="2"/></pattern></defs>`;
const svg = (title,body,view='0 0 1000 520') => `<svg viewBox="${view}" role="img" aria-label="${esc(title)}" xmlns="${NS}">${marker}<title>${esc(title)}</title>${body}</svg>`;
const line = (x1,y1,x2,y2,{stroke=PALETTE.ink,width=3,dash='',arrow=true}={}) => `<path d="M${x1} ${y1} L${x2} ${y2}" fill="none" stroke="${stroke}" stroke-width="${width}" ${dash?`stroke-dasharray="${dash}"`:''} ${arrow?'marker-end="url(#arrow)"':''}/>`;
const box = (x,y,w,h,label,{sub='',fill=PALETTE.paper2,stroke=PALETTE.ink,accent='',size=22}={}) => `<g><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>${accent?`<rect x="${x}" y="${y}" width="10" height="${h}" fill="${accent}"/>`:''}${textBlock(x+w/2,y+h/2-(sub?9:0),label,{size,fill:stroke,max:Math.max(8,Math.floor(w/size*1.55))})}${sub?textBlock(x+w/2,y+h/2+25,sub,{size:14,fill:PALETTE.muted,weight:600,max:Math.max(10,Math.floor(w/12))}):''}</g>`;
const label = (x,y,value,color=PALETTE.muted,anchor='middle') => textBlock(x,y,value,{size:14,fill:color,weight:800,anchor,max:30});

function flow(labels, accent, opts={}) {
  const n=labels.length, gap=opts.gap ?? 22, width=(900-gap*(n-1))/n, y=opts.y ?? 200, h=opts.h ?? 120;
  const body=labels.map((item,i)=>{
    const x=50+i*(width+gap); const isObj=typeof item==='object'; const title=isObj?item.label:item; const sub=isObj?item.sub:'';
    const size=isObj&&item.size?item.size:(opts.size ?? (n>5?18:22));
    return box(x,y,width,h,title,{sub,accent:isObj&&item.color?item.color:accent,fill:i%2?PALETTE.paper2:PALETTE.note,size}) + (i<n-1?line(x+width,y+h/2,x+width+gap-5,y+h/2,{stroke:accent,width:3}):'');
  }).join('') + (opts.caption?textBlock(500,y+h+70,opts.caption,{size:22,fill:accent,max:42}):'');
  return svg(opts.title || labels.join(' → '),body,opts.view);
}

function branches(center, leaves, accent, opts={}) {
  const cx=500, cy=opts.cy??260, r=opts.r??185;
  let body=`<circle cx="${cx}" cy="${cy}" r="105" fill="${PALETTE.ink}"/>${textBlock(cx,cy-8,center,{size:23,fill:PALETTE.paper2,max:11})}`;
  leaves.forEach((item,i)=>{const angle=(-Math.PI/2)+(Math.PI*2*i/leaves.length);const x=cx+Math.cos(angle)*r,y=cy+Math.sin(angle)*r;body+=line(cx+Math.cos(angle)*105,cy+Math.sin(angle)*105,x-Math.cos(angle)*75,y-Math.sin(angle)*42,{stroke:accent,width:2,arrow:false});body+=box(x-82,y-42,164,84,typeof item==='string'?item:item.label,{sub:typeof item==='object'?item.sub:'',accent:typeof item==='object'&&item.color?item.color:accent,size:17});});
  return svg(opts.title||center,body);
}

function columns(items, accent, title='comparison') {
  const gap=18,w=(900-gap*(items.length-1))/items.length;
  return svg(title,items.map((it,i)=>{const x=50+i*(w+gap);const c=it.color||accent;return `<g><rect x="${x}" y="100" width="${w}" height="330" fill="${i%2?PALETTE.paper2:PALETTE.note}" stroke="${PALETTE.rule}"/><rect x="${x}" y="100" width="${w}" height="12" fill="${c}"/>${textBlock(x+w/2,165,it.title,{size:22,fill:c,max:14})}${textBlock(x+w/2,235,it.body||'',{size:17,fill:PALETTE.ink,weight:600,max:16,line:1.35})}${it.foot?textBlock(x+w/2,390,it.foot,{size:14,fill:PALETTE.muted,weight:700,max:18}):''}</g>`}).join(''));
}

function docsVisual(accent) {
  const doc=(x,y,rot,kicker,title,rows,color)=>`<g transform="translate(${x} ${y}) rotate(${rot} 125 170)"><rect width="250" height="340" fill="${PALETTE.paper2}" stroke="${PALETTE.ink}" stroke-width="2"/><rect width="250" height="14" fill="${color}"/>${label(22,50,kicker,color,'start')}${textBlock(22,88,title,{size:23,anchor:'start',max:15})}${rows.map((r,i)=>`<line x1="22" y1="${130+i*50}" x2="228" y2="${130+i*50}" stroke="${PALETTE.rule}"/>${label(22,155+i*50,r,PALETTE.muted,'start')}`).join('')}<rect x="22" y="282" width="90" height="34" fill="${PALETTE.note}"/>${label(67,304,'PDF · SOURCE',PALETTE.ink)}</g>`;
  return svg('三份源单证',doc(70,80,-4,'BOOKING REQUEST','危险品订舱申请',['UN1263','10,000 kg','CNSHA → AEJEA'],PALETTE.coral)+doc(370,70,1,'PRELIMINARY DGD','DG Declaration',['UN1866','Class 3 / PG III','Signed'],PALETTE.blue)+doc(670,85,4,'SDS EXTRACT','Safety Data Sheet',['Section 9','Flash point 30°C','Section 14'],PALETTE.gold));
}

function scoreboard() {
  const data=[['TECHNICAL',100,PALETTE.teal],['STATUS',100,PALETTE.teal],['FIELD',97.9,PALETTE.blue],['EVIDENCE',66.7,PALETTE.coral]];
  return svg('Single-Agent baseline score board',data.map((d,i)=>{const y=95+i*80;return `${label(55,y+20,d[0],PALETTE.ink,'start')}<rect x="210" y="${y}" width="600" height="34" fill="${PALETTE.note}"/><rect x="210" y="${y}" width="${600*d[1]/100}" height="34" fill="${d[2]}"/>${textBlock(850,y+27,`${d[1]}%`,{size:24,fill:d[2],anchor:'start',max:8})}`}).join('')+`<line x1="50" y1="430" x2="950" y2="430" stroke="${PALETTE.ink}" stroke-width="2"/>${textBlock(280,480,'P95 · 25.8s',{size:28,fill:PALETTE.ink,max:15})}${textBlock(700,480,'AVG CALLS · 4.56',{size:28,fill:PALETTE.ink,max:18})}`);
}

function timerVisual() {
  return svg('90 秒讨论计时提示',`<circle cx="500" cy="260" r="185" fill="none" stroke="${PALETTE.rule}" stroke-width="26"/><path d="M500 75 A185 185 0 1 1 369 391" fill="none" stroke="${PALETTE.coral}" stroke-width="26"/><line x1="500" y1="260" x2="500" y2="125" stroke="${PALETTE.paper2}" stroke-width="8"/><line x1="500" y1="260" x2="610" y2="325" stroke="${PALETTE.paper2}" stroke-width="8"/>${textBlock(500,245,'90',{size:100,fill:PALETTE.paper2,family:'serif'})}${textBlock(500,315,'SECONDS',{size:20,fill:PALETTE.coral,max:12})}`);
}

function renderVisual(type, slide) {
  const a=accentFor(slide.part);
  switch(type){
    case 'title': return svg('源单证、证据路径与架构实验',`${docsVisual(a).match(/<svg[^>]*>([\s\S]*)<\/svg>/)?.[1]||''}<rect x="110" y="410" width="780" height="4" fill="${PALETTE.paper2}" opacity=".7"/>${['SOURCE','FACTS','RULE','DECISION'].map((t,i)=>`${textBlock(160+i*225,465,t,{size:18,fill:[PALETTE.coral,PALETTE.blue,PALETTE.gold,PALETTE.teal][i],max:12})}${i<3?line(220+i*225,458,300+i*225,458,{stroke:PALETTE.paper2,width:2}):''}`).join('')}`);
    case 'experiment': return columns([{title:'FIXED',body:'业务 · 9 DP · Policy · Rules · Model · Evaluator',color:PALETTE.ink,foot:'CONTROL VARIABLES'},{title:'VARIABLE',body:'职责 · Pattern · Context · 协作 · 失败策略',color:a,foot:'ARCHITECTURE'}],a,'实验控制变量');
    case 'journey': return flow(['Understand','Baseline','Design','Build','Compare','Decide'],a,{title:'Architecture learning journey',caption:'每个节点只产生一个可复用证据'});
    case 'boundary': return svg(
      'Booking Precheck boundary',
      flow(['PRECHECK','DG CLASSIFICATION','FINAL APPROVAL','BOOKING CONFIRM'],a,{y:55,h:110,size:18})
        .match(/<svg[^>]*>([\s\S]*)<\/svg>/)?.[1],
      '0 0 1000 220'
    );
    case 'documents': return docsVisual(a);
    case 'evidence-chain': return svg(
      '可回溯证据链',
      flow(['源单证','归一化事实','Policy Rule','全量原因','状态 / 行动'],a,{y:70,h:105})
        .match(/<svg[^>]*>([\s\S]*)<\/svg>/)?.[1]
        + line(860,45,165,45,{stroke:a,width:3,dash:'10 8'})
        + label(500,24,'TRACE BACK TO PAGE + TEXT',a),
      '0 0 1000 210'
    );
    case 'result-contract': return branches('PRECHECK RESULT',[{label:'Final Status',color:PALETTE.coral},{label:'Reasons / Rules',color:PALETTE.blue},{label:'Evidence',color:PALETTE.gold},{label:'Routing / Action',color:PALETTE.teal},{label:'Trace / Metrics',color:PALETTE.ink}],a);
    case 'information-abstraction': return svg('信息抽象与证据回溯',`
      ${label(42,70,'L2 · RULE FINDING',PALETTE.teal,'start')}
      ${label(42,248,'L1 · FACT',PALETTE.blue,'start')}
      ${label(42,426,'L0 · DOCUMENT',PALETTE.ink,'start')}
      <line x1="42" y1="86" x2="958" y2="86" stroke="${PALETTE.rule}" stroke-width="1"/>
      <line x1="42" y1="264" x2="958" y2="264" stroke="${PALETTE.rule}" stroke-width="1"/>
      <line x1="42" y1="442" x2="958" y2="442" stroke="${PALETTE.rule}" stroke-width="1"/>

      ${box(180,338,220,105,'DOCUMENT',{sub:'page + text',accent:PALETTE.ink,size:24})}
      ${box(390,178,220,105,'FACT',{sub:'normalized value',accent:PALETTE.blue,size:25})}
      ${box(625,18,220,105,'RULE FINDING',{sub:'Facts × Policy',accent:PALETTE.teal,size:21})}
      ${box(805,178,155,105,'POLICY',{sub:'policy rule',accent:PALETTE.gold,size:22})}
      ${box(625,338,220,105,'EVIDENCE',{sub:'path + page + text',accent:PALETTE.coral,size:23})}

      ${line(400,390,380,270,{stroke:PALETTE.blue,width:4})}
      ${line(610,210,615,110,{stroke:PALETTE.teal,width:4})}
      ${line(805,210,755,120,{stroke:PALETTE.gold,width:4})}
      ${textBlock(410,326,'向上抽象',{size:17,fill:PALETTE.blue,max:8})}
      ${textBlock(603,166,'确定性判断',{size:17,fill:PALETTE.teal,max:10})}

      ${line(735,123,735,328,{stroke:PALETTE.coral,width:3,dash:'9 7'})}
      <path d="M625 390 C550 485 385 485 300 448" fill="none" stroke="${PALETTE.coral}" stroke-width="3" stroke-dasharray="9 7" marker-end="url(#arrow)"/>
      ${textBlock(862,320,'向下回溯',{size:17,fill:PALETTE.coral,max:8})}
      ${textBlock(520,495,'RULE → FACT → DOCUMENT',{size:16,fill:PALETTE.coral,max:40})}
    `);
    case 'conflict': return flow([{label:'UN1263',sub:'BOOKING',color:PALETTE.coral},{label:'UN1866',sub:'DGD',color:PALETTE.blue},{label:'CONSISTENCY',sub:'RULE',color:PALETTE.gold},{label:'MANUAL_REVIEW',sub:'DG DESK',color:PALETTE.teal}],a,{title:'UN Number conflict across four responsibility boundaries'});
    case 'timer': return timerVisual();
    case 'baseline': return columns([{title:'SINGLE',body:'Quality\nLatency\nCost',color:PALETTE.blue,foot:'BASELINE'},{title:'MULTI',body:'—\n—\n—',color:PALETTE.rule,foot:'AFTER BUILD'}],a,'Baseline comparison table');
    case 'langfuse': return flow(['Dataset','Task','Trace','Evaluator','Scores','Run'],a,{title:'Langfuse experiment flow'});
    case 'dataset-item': return svg('Dataset Item structure',box(80,70,840,380,'DATASET ITEM',{accent:a,fill:PALETTE.paper2,size:28})+box(120,145,320,200,'input',{sub:'pack_id · stage_id',accent:PALETTE.blue,size:26})+box(560,145,320,200,'expected_output',{sub:'expected + ground_truth',accent:PALETTE.coral,size:26})+line(440,245,550,245,{stroke:a})+label(500,220,'ISOLATED',a));
    case 'answer-sources': return flow([{label:'TC / BA',sub:'expected.json',color:PALETTE.coral},{label:'expected_output',sub:'business answer',color:PALETTE.gold},{label:'DP',sub:'ground-truth.json',color:PALETTE.blue}],a,{title:'Two answer sources',caption:'Evaluator reads both · Agent reads neither'});
    case 'isolation': return svg('Expected output bypasses Agent',`${box(60,95,190,90,'item.input',{accent:PALETTE.blue})}${box(390,95,210,90,'Agent',{accent:a})}${box(745,95,190,90,'Actual',{accent:PALETTE.teal})}${line(250,140,380,140,{stroke:PALETTE.blue})}${line(600,140,735,140,{stroke:a})}${box(60,340,230,90,'expected_output',{accent:PALETTE.coral})}${box(420,340,210,90,'Evaluator',{accent:PALETTE.gold})}${box(760,340,175,90,'Score',{accent:PALETTE.teal})}${line(290,385,410,385,{stroke:PALETTE.coral})}${line(630,385,750,385,{stroke:PALETTE.gold})}${line(840,185,560,330,{stroke:PALETTE.teal,width:2})}${line(175,330,175,205,{stroke:PALETTE.coral,width:3,dash:'9 7',arrow:false})}${textBlock(235,270,'NO LEAKAGE',{size:18,fill:PALETTE.coral,max:14})}`);
    case 'manifest': return columns([{title:'MANIFEST',body:'protocol · transport\ncommand · cwd\nenv · capabilities',color:a},{title:'JSONL',body:'stdin request\nstdout response',color:PALETTE.ink},{title:'RESPONSE',body:'result\nfacts\ntelemetry',color:PALETTE.teal}],a,'Manifest driven adapter');
    case 'secret': return svg('Secrets stay local',`<rect x="110" y="90" width="780" height="340" fill="${PALETTE.ink}" stroke="${PALETTE.paper2}" stroke-width="2"/>${label(155,140,'.env.local',PALETTE.amber,'start')}${['LANGFUSE_BASE_URL=https://…','LANGFUSE_PUBLIC_KEY=pk-lf-…','LANGFUSE_SECRET_KEY=••••••••'].map((t,i)=>textBlock(155,205+i*65,t,{size:23,fill:i===2?PALETTE.coral:PALETTE.paper2,anchor:'start',max:45,family:'sans'})).join('')}<path d="M760 245 v-35 a55 55 0 0 0 -110 0 v35" fill="none" stroke="${PALETTE.amber}" stroke-width="12"/><rect x="625" y="245" width="160" height="120" fill="${PALETTE.amber}"/>${textBlock(705,318,'LOCAL ONLY',{size:18,fill:PALETTE.ink,max:12})}`);
    case 'runbook': return flow(['GET','TEST','DOCTOR','SYNC 9','BASELINE'],a,{title:'Baseline runbook',y:180,h:150,caption:'每一步只验证一个边界'});
    case 'terminal': return svg('Doctor command and success conditions',`<rect x="70" y="70" width="860" height="380" rx="0" fill="${PALETTE.ink}"/><circle cx="105" cy="105" r="8" fill="${PALETTE.coral}"/><circle cx="132" cy="105" r="8" fill="${PALETTE.gold}"/><circle cx="159" cy="105" r="8" fill="${PALETTE.teal}"/>${textBlock(105,180,'$ doctor --pack-id DP-001 --stage S1',{size:25,fill:PALETTE.paper2,anchor:'start',max:50})}${['✓ COMPLETED','✓ result','✓ facts','✓ telemetry'].map((t,i)=>textBlock(130+i%2*390,280+Math.floor(i/2)*80,t,{size:26,fill:PALETTE.teal,anchor:'start',max:16})).join('')}`);
    case 'sync': return flow(['9 LOCAL STAGES','STABLE ID','UPSERT','9 DATASET ITEMS'],a,{title:'Idempotent Dataset Sync',caption:'REPEAT → NO DUPLICATES'});
    case 'experiment-items': return svg('Nine items through one task',`${box(70,180,210,140,'ONE TASK',{sub:'same implementation',accent:a})}${box(720,180,210,140,'9 TRACES',{sub:'serial JSONL',accent:PALETTE.teal})}${line(280,250,710,250,{stroke:a,width:4})}${[0,1,2,3,4,5,6,7,8].map(i=>`<circle cx="${350+i*36}" cy="250" r="13" fill="${i%2?a:PALETTE.blue}"/>`).join('')}${label(500,360,'group-N-single-agent-baseline',a)}`);
    case 'diagnostic-ladder': {
      const levels=[
        {label:'OFFLINE TESTS',width:760,fill:PALETTE.note},
        {label:'DOCTOR',width:540,fill:PALETTE.wash},
        {label:'SYNC',width:320,fill:PALETTE.paper2},
        {label:'EXPERIMENT',width:190,fill:PALETTE.ink},
      ];
      return svg('Layered diagnostic ladder',levels.map((level,i)=>{
        const x=500-level.width/2;
        const y=370-i*85;
        return `<g><rect x="${x}" y="${y}" width="${level.width}" height="70" fill="${level.fill}" stroke="${PALETTE.ink}"/>${textBlock(500,y+44,level.label,{size:22,fill:i===3?PALETTE.paper2:PALETTE.ink,max:20})}</g>`;
      }).join(''));
    }
    case 'score-bands': return columns([{title:'QUALITY',body:'status · rule F1\nfield · evidence',color:PALETTE.blue},{title:'SAFETY',body:'technical success\ncritical false clear',color:PALETTE.coral},{title:'EFFICIENCY',body:'duration · calls\ntokens',color:PALETTE.gold}],a,'Score categories');
    case 'scoreboard': return scoreboard();
    case 'trace': return flow(['RUN','FAILED ITEM','SCORES','TRACE','ACTUAL'],a,{title:'Trace diagnostic path',caption:'DP-006 · FIELD 100% · EVIDENCE INCOMPLETE'});
    case 'two-tools': return columns([{title:'LANGSMITH',body:'Graph\nState\nTool Calls',color:PALETTE.gold,foot:'ONE RUN'},{title:'LANGFUSE',body:'Dataset\nExperiment\nComparison',color:PALETTE.blue,foot:'MANY RUNS'}],a,'LangSmith and Langfuse');
    case 'single-loop': return svg('Single-Agent graph',`${box(55,205,150,100,'PDFs',{accent:PALETTE.coral})}${box(290,205,210,100,'initialize_case',{accent:PALETTE.gold,size:19})}${box(585,120,260,100,'precheck_agent',{accent:PALETTE.blue})}${box(585,330,260,100,'precheck_tools',{accent:PALETTE.teal})}${line(205,255,280,255,{stroke:a})}${line(500,255,575,185,{stroke:a})}${line(715,220,715,320,{stroke:PALETTE.blue})}${line(680,330,680,230,{stroke:PALETTE.teal})}${box(850,205,130,100,'finalize',{accent:PALETTE.ink,size:18})}${line(845,170,910,200,{stroke:a})}`);
    case 'state-layers': return svg('Business state evolution',['Documents','Facts','Required Evidence','Matches','Aggregate','Final Result'].map((t,i)=>`<g><rect x="${120+i*42}" y="${70+i*62}" width="${760-i*84}" height="75" fill="${i===5?PALETTE.ink:i%2?PALETTE.paper2:PALETTE.note}" stroke="${PALETTE.rule}" stroke-width="2"/>${textBlock(500,116+i*62,t,{size:24,fill:i===5?PALETTE.paper2:PALETTE.ink,max:24})}</g>`).join('')+label(880,455,'MESSAGES = LOCAL COORDINATION',a,'end'));
    case 'tools': return branches('AGENT',['Submit Facts','Run Rules','Submit Evidence','Lookup Policy','Finalize Result'],a);
    case 'deterministic-boundary': return columns([{title:'LLM',body:'阅读\n归一化\n证据组织\n工具选择',color:PALETTE.blue,foot:'UNCERTAINTY'},{title:'TOOL / NODE',body:'Schema\n计算\n规则\n优先级\n审计',color:PALETTE.teal,foot:'DETERMINISTIC'},{title:'FINAL STATUS',body:'PRECHECK_*',color:PALETTE.ink,foot:'OWNED HERE'}],a,'Deterministic decision boundary');
    case 'tension': return svg('Single-Agent tension axis',`<line x1="120" y1="260" x2="880" y2="260" stroke="${PALETTE.ink}" stroke-width="8"/>${line(500,260,220,260,{stroke:PALETTE.teal,width:8})}${line(500,260,780,260,{stroke:PALETTE.coral,width:8})}${textBlock(220,190,'LOW COORDINATION',{size:26,fill:PALETTE.teal,max:18})}${textBlock(780,190,'HIGH COUPLING',{size:26,fill:PALETTE.coral,max:18})}${textBlock(500,355,'SINGLE-AGENT BASELINE',{size:32,fill:PALETTE.ink,max:24})}`);
    case 'decision-chain': return flow([
      'Scope','Drivers','Scenario','Pressure','Tactic',
      {label:'Roles',size:17},
      {label:'Experiment',size:16},
    ],a,{title:'ADD decision chain',gap:10,y:30,h:100,size:17,view:'0 0 1000 160'});
    case 'four-statements': return columns([{title:'FUNCTION',body:'读取单证\n给出结果',color:PALETTE.ink},{title:'QUALITY',body:'冲突 / 失败 / 变更 / 负载下怎样',color:PALETTE.teal},{title:'CONSTRAINT',body:'固定模型\n规则内核\n协议',color:PALETTE.coral},{title:'PREFERENCE',body:'想用某个 Pattern',color:PALETTE.gold}],a,'Four kinds of architecture statements');
    case 'quality-lenses': return svg('Three quality lenses',`<circle cx="500" cy="260" r="220" fill="${PALETTE.note}" stroke="${PALETTE.ink}"/><circle cx="500" cy="260" r="150" fill="${PALETTE.wash}" stroke="${PALETTE.blue}" stroke-width="3"/><circle cx="500" cy="260" r="80" fill="${PALETTE.teal}"/>${textBlock(500,78,'SOFTWARE PRODUCT QUALITY',{size:18,fill:PALETTE.ink,max:26})}${textBlock(500,160,'AI TRUSTWORTHINESS',{size:18,fill:PALETTE.blue,max:22})}${textBlock(500,250,'AGENTIC',{size:19,fill:PALETTE.paper2,max:10})}${textBlock(500,282,'EXECUTION',{size:19,fill:PALETTE.paper2,max:10})}${textBlock(500,500,'EXPLORE → PRIORITIZE → SCENARIOS',{size:20,fill:a,max:36})}`);
    case 'standards': return columns([{title:'ISO 25010',body:'Product Quality\n9 characteristics',color:PALETTE.teal,foot:'DIRECTION MAP'},{title:'ISO 25059',body:'AI System Quality\nSQuaRE extension',color:PALETTE.blue,foot:'AI EXTENSION'},{title:'NIST AI RMF',body:'Trustworthiness\ncharacteristics',color:PALETTE.coral,foot:'RISK LANGUAGE'}],a,'Quality models and trustworthiness framework');
    case 'agentic-lens': return branches('SHARED CASE STATE',[{label:'Outcome',color:PALETTE.coral},{label:'Tool / Action',color:PALETTE.gold},{label:'Context / State',color:PALETTE.blue},{label:'Handoff',color:PALETTE.teal},{label:'Control / Safety',color:PALETTE.coral},{label:'Efficiency / Diagnosis',color:PALETTE.ink}],a);
    case 'outcome': return branches('OUTCOME',['Architecture','Prompt / Model','Tools','Implementation'],a);
    case 'quality-realization': return svg('不合适的架构会阻碍质量属性达成，合适的架构也不能保证结果',`
      ${box(55,155,240,190,'ARCHITECTURE',{sub:'职责 · 边界 · 数据流 · 失败隔离',accent:a,fill:PALETTE.ink,stroke:PALETTE.paper2,size:25})}
      ${textBlock(175,115,'不合适 → 形成阻碍',{size:20,fill:PALETTE.coral,max:18})}
      ${box(380,80,230,90,'MODEL + PROMPT',{sub:'理解与生成',accent:PALETTE.blue,size:19})}
      ${box(380,215,230,90,'TOOLS + CODE',{sub:'确定性实现',accent:PALETTE.gold,size:20})}
      ${box(380,350,230,90,'RUNTIME + OPS',{sub:'部署与运行',accent:PALETTE.coral,size:19})}
      ${line(295,250,365,125,{stroke:a,width:3})}
      ${line(295,250,365,260,{stroke:a,width:3})}
      ${line(295,250,365,395,{stroke:a,width:3})}
      ${box(680,165,220,170,'质量结果',{sub:'用场景 + 指标验证',accent:PALETTE.teal,fill:PALETTE.note,size:24})}
      ${line(610,125,665,210,{stroke:PALETTE.blue,width:3})}
      ${line(610,260,665,250,{stroke:PALETTE.gold,width:3})}
      ${line(610,395,665,290,{stroke:PALETTE.coral,width:3})}
      ${textBlock(500,495,'不合适 → 阻碍 · 合适 ≠ 保证',{size:22,fill:PALETTE.coral,max:28})}
    `);
    case 'scenario': return branches('ARTIFACT',['Source','Stimulus','Environment','Response','Response Measure'],a);
    case 'scenario-example': return flow([{label:'INTAKE',sub:'source'},{label:'3 PDFs',sub:'stimulus'},{label:'WORKFLOW',sub:'artifact'},{label:'COMPLETE',sub:'response'},{label:'P95 ≤ BASELINE',sub:'measure'}],a,{title:'Latency scenario example'});
    case 'tradeoffs': return svg('Three architecture tradeoff axes',[['低延迟','复核准确率'],['职责隔离','协调复杂度'],['Trace 细度','Token / 存储成本']].map((d,i)=>{const y=125+i*145;return `${textBlock(110,y,d[0],{size:24,fill:PALETTE.teal,anchor:'start',max:15})}<line x1="300" y1="${y-8}" x2="700" y2="${y-8}" stroke="${PALETTE.ink}" stroke-width="4"/><circle cx="${[390,555,470][i]}" cy="${y-8}" r="18" fill="${a}"/>${textBlock(890,y,d[1],{size:24,fill:PALETTE.coral,anchor:'end',max:18})}`}).join(''));
    case 'top3': return svg('Prioritize top three quality attribute scenarios',`${[1,2,3].map((n,i)=>`<g><text x="${190+i*310}" y="310" text-anchor="middle" font-family="Iowan Old Style,serif" font-size="210" font-weight="700" fill="${i===0?a:i===1?PALETTE.blue:PALETTE.gold}" opacity="${1-i*.18}">${n}</text><line x1="${85+i*310}" y1="350" x2="${295+i*310}" y2="350" stroke="${PALETTE.paper2}"/><text x="${190+i*310}" y="395" text-anchor="middle" fill="${PALETTE.paper2}" font-family="Avenir Next,sans-serif" font-size="16" font-weight="800">SCENARIO + EVIDENCE</text></g>`).join('')}`);
    case 'worksheet': return svg('Quality attribute scenario worksheet',`<rect x="70" y="55" width="860" height="410" fill="${PALETTE.paper2}" stroke="${PALETTE.ink}" stroke-width="2"/><rect x="70" y="55" width="860" height="65" fill="${PALETTE.ink}"/>${textBlock(105,97,'QUALITY ATTRIBUTE SCENARIO',{size:19,fill:PALETTE.paper2,anchor:'start',max:30})}${['PRIORITY','SOURCE','STIMULUS','ARTIFACT','ENVIRONMENT','RESPONSE','MEASURE','BASELINE EVIDENCE'].map((t,i)=>{const col=i%4,row=Math.floor(i/4),x=70+col*215,y=120+row*172;return `<rect x="${x}" y="${y}" width="215" height="172" fill="${row?PALETTE.note:PALETTE.paper2}" stroke="${PALETTE.rule}"/>${label(x+18,y+32,t,a,'start')}<line x1="${x+18}" y1="${y+78}" x2="${x+197}" y2="${y+78}" stroke="${PALETTE.rule}"/><line x1="${x+18}" y1="${y+120}" x2="${x+197}" y2="${y+120}" stroke="${PALETTE.rule}"/>`}).join('')}`);
    case 'driver-chain': return flow(['Driver','Tactic','Boundary','Pattern Instance','Interface'],a,{title:'From driver to implementable interface'});
    case 'patterns-a': return columns([{title:'PIPELINE',body:'A → B → C',color:PALETTE.ink,foot:'SEQUENCE'},{title:'ORCHESTRATOR',body:'O → W₁ W₂ W₃',color:PALETTE.teal,foot:'SCHEDULING'},{title:'ROUTER',body:'R → ONE SPECIALIST',color:PALETTE.blue,foot:'SELECTION'}],a,'Pattern candidates one');
    case 'patterns-b': return columns([{title:'REVIEWERS',body:'W₁ ∥ W₂ → MERGE',color:PALETTE.blue,foot:'PARALLEL'},{title:'GEN / REVIEW',body:'G → R → G',color:PALETTE.coral,foot:'FEEDBACK'},{title:'BLACKBOARD',body:'W₁ W₂ ↔ STATE',color:PALETTE.gold,foot:'SHARED STATE'}],a,'Pattern candidates two');
    case 'responsibilities': return svg('Responsibility boundaries remain deterministic',`${box(80,110,240,250,'AGENTS',{sub:'understand\norganize evidence',accent:PALETTE.blue})}${box(680,110,240,250,'DETERMINISTIC',{sub:'schema · rules\naggregate · score',accent:PALETTE.teal})}${line(320,235,670,235,{stroke:a,width:4})}${box(410,190,180,90,'FACTS + EVIDENCE',{accent:PALETTE.gold,size:17})}${textBlock(500,445,'FINAL DECISION → DETERMINISTIC OWNER',{size:22,fill:PALETTE.teal,max:38})}`);
    case 'adr-interface': return columns([{title:'ELEMENT',body:'Responsibilities\nInput / Output\nCollaborations\nFailure Behaviour',color:PALETTE.blue,foot:'HOW TO COLLABORATE'},{title:'ADR',body:'Context / Decision\nAlternatives\nConsequences\nValidation / Reject',color:PALETTE.teal,foot:'WHY THIS DESIGN'}],a,'Interface and ADR');
    case 'adr': return svg('ADR validation skeleton',`<rect x="110" y="55" width="780" height="410" fill="${PALETTE.paper2}" stroke="${PALETTE.ink}" stroke-width="2"/>${['CONTEXT','DECISION','ALTERNATIVES','CONSEQUENCES','VALIDATION / REJECT CONDITIONS'].map((t,i)=>{const y=55+i*82;return `<rect x="110" y="${y}" width="780" height="82" fill="${i===4?PALETTE.wash:'transparent'}" stroke="${PALETTE.rule}"/>${label(145,y+32,t,i===4?a:PALETTE.ink,'start')}${i===4?`<rect x="690" y="${y+18}" width="165" height="46" fill="${a}"/>${textBlock(772,y+49,'DECIDE BEFORE CODE',{size:13,fill:PALETTE.paper2,max:18})}`:''}`}).join('')}`);
    case 'design-task': return flow(['COMPARE','BOUNDARIES','DIAGRAM','ADR','SHOWCASE'],a,{title:'Architecture design activity',y:170,h:160,caption:'OUTPUT · TWO OPTIONS + ONE DECISION'});
    case 'six-questions': return branches('DESIGN GATE',['Why Agent?','Which Driver?','Minimum Input?','State Owner?','Fail Safe?','Which Score?'],a);
    case 'adr-demo-code': return flow(['ADR','MICRO DEMO','CODE'],a,{title:'ADR to code transition',y:165,h:180,caption:'WHY → HOW → IMPLEMENT'});
    case 'scope': return svg('Data scope from local to shared',[{t:'MESSAGES',w:300,c:PALETTE.note},{t:'AGENT CONTEXT',w:460,c:PALETTE.paper2},{t:'AGENT RESULT',w:620,c:PALETTE.wash},{t:'SHARED CASE STATE',w:800,c:PALETTE.ink}].map((d,i)=>`<g><rect x="${500-d.w/2}" y="${80+i*95}" width="${d.w}" height="70" fill="${d.c}" stroke="${PALETTE.ink}"/>${textBlock(500,125+i*95,d.t,{size:22,fill:i===3?PALETTE.paper2:PALETTE.ink,max:24})}</g>`).join(''));
    case 'task-result-reducer': return svg('Task Result Reducer collaboration loop',`${box(60,205,180,110,'Coordinator',{accent:a})}${box(330,85,190,100,'Worker A',{accent:PALETTE.blue})}${box(330,330,190,100,'Worker B',{accent:PALETTE.blue})}${box(610,205,170,110,'Reducer',{accent:PALETTE.teal})}${box(850,205,120,110,'State',{accent:PALETTE.ink,size:20})}${line(240,235,320,135,{stroke:a})}${line(240,285,320,380,{stroke:a})}${line(520,135,600,235,{stroke:PALETTE.blue})}${line(520,380,600,285,{stroke:PALETTE.blue})}${line(780,260,840,260,{stroke:PALETTE.teal})}${label(270,80,'AgentTask',a)}${label(570,455,'AgentResult',PALETTE.blue)}`);
    case 'contracts': return columns([{title:'AgentTask',body:'task_id · case_id\nobjective\ndocument_refs\nrequired_outputs',color:PALETTE.blue,foot:'CONTEXT WHITELIST'},{title:'AgentResult',body:'status · facts\nevidence · error\ntelemetry',color:PALETTE.teal,foot:'IMMUTABLE OUTPUT'}],a,'Task and Result handoff contracts');
    case 'task-schema': return columns([{title:'RECEIVES',body:'task_id\ncase_id\nobjective\ndocument_refs\nrequired_outputs',color:PALETTE.teal},{title:'MUST NOT RECEIVE',body:'complete messages\nground truth\nunrelated state',color:PALETTE.coral}],a,'AgentTask context whitelist');
    case 'result-schema': return columns([{title:'SUCCESS',body:'status: completed\nfacts + evidence\ntelemetry',color:PALETTE.teal},{title:'FAILURE',body:'status: failed\nerror\ntelemetry',color:PALETTE.coral}],a,'Uniform AgentResult envelope');
    case 'reducer': return svg('Reducer is the only shared state writer',`${[105,255,405].map((y,i)=>box(65,y,210,90,`Result ${String.fromCharCode(65+i)}`,{accent:PALETTE.blue})).join('')}${box(410,175,230,180,'REDUCER',{sub:'validate · dedupe\nnamespace · merge',accent:PALETTE.teal,size:28})}${box(790,205,160,120,'SHARED STATE',{accent:PALETTE.ink,size:18})}${[150,300,450].map(y=>line(275,y,400,260,{stroke:PALETTE.blue})).join('')}${line(640,265,780,265,{stroke:PALETTE.teal,width:5})}`);
    case 'fail-safe': return svg('Fail safe branch',`${box(70,205,180,110,'Worker',{accent:PALETTE.blue})}${box(365,80,220,110,'Completed',{accent:PALETTE.teal})}${box(365,330,220,110,'Timeout / Failed',{accent:PALETTE.coral})}${box(740,80,200,110,'Reducer → State',{accent:PALETTE.teal})}${box(740,330,200,110,'Retry / Escalate',{accent:PALETTE.coral})}${line(250,240,355,135,{stroke:PALETTE.teal})}${line(250,280,355,385,{stroke:PALETTE.coral})}${line(585,135,730,135,{stroke:PALETTE.teal})}${line(585,385,730,385,{stroke:PALETTE.coral})}${line(835,330,835,205,{stroke:PALETTE.coral,width:5,dash:'10 8',arrow:false})}${textBlock(700,275,'NO PRECHECK_PASS',{size:22,fill:PALETTE.coral,max:20})}`);
    case 'context-table': return svg('Context contract mapping table',`<rect x="45" y="70" width="910" height="365" fill="${PALETTE.paper2}" stroke="${PALETTE.ink}" stroke-width="2"/>${['AGENT / NODE','RECEIVES','MUST NOT RECEIVE','PRODUCES','STATE OWNER','FAILURE'].map((t,i)=>{const x=45+i*151.67;return `<rect x="${x}" y="70" width="151.67" height="365" fill="${i%2?PALETTE.note:'transparent'}" stroke="${PALETTE.rule}"/>${textBlock(x+75.8,120,t,{size:14,fill:a,max:16})}${[190,255,320,385].map(y=>`<line x1="${x+16}" y1="${y}" x2="${x+136}" y2="${y}" stroke="${PALETTE.rule}"/>`).join('')}`}).join('')}`);
    case 'ai-boundary': return columns([{title:'AI CODING',body:'骨架 · 类型\n节点 · Reducer\nAdapter · Tests',color:PALETTE.gold,foot:'ACCELERATE'},{title:'TEAM',body:'边界 · Context\nOwnership · Failure\nTradeoff · Acceptance',color:PALETTE.ink,foot:'OWN THE DECISION'}],a,'AI and team responsibility boundary');
    case 'three-prompts': return flow([{label:'PLAN',sub:'ADR + Contract'},{label:'IMPLEMENT',sub:'Thin Slice'},{label:'FIX',sub:'Tests + Doctor'}],a,{title:'Three prompt coding loop',y:160,h:180,caption:'SMALL CHANGE → REAL ERROR → NEXT CHANGE'});
    case 'redlines': return svg('Four AI coding red lines',`<rect x="80" y="80" width="840" height="360" fill="none" stroke="${PALETTE.coral}" stroke-width="6"/>${line(140,380,860,140,{stroke:PALETTE.coral,width:12,arrow:false})}${textBlock(500,245,'DO NOT MOVE THE RULER',{size:42,fill:PALETTE.paper2,max:28})}${textBlock(500,310,'NO GROUND TRUTH LEAKAGE',{size:24,fill:PALETTE.coral,max:30})}`);
    case 'gates': return svg('Three coding gates',`<line x1="120" y1="260" x2="880" y2="260" stroke="${PALETTE.paper2}" stroke-width="5"/>${[{x:220,t:'GATE 1',l:'CONTRACT'},{x:500,t:'GATE 2',l:'THIN SLICE'},{x:780,t:'GATE 3',l:'EVALUATION'}].map((g,i)=>`<g><circle cx="${g.x}" cy="260" r="34" fill="${i===2?PALETTE.coral:a}" stroke="${PALETTE.paper2}" stroke-width="4"/>${textBlock(g.x,170,g.t,{size:28,fill:PALETTE.paper2,max:8})}${textBlock(g.x,345,g.l,{size:19,fill:i===2?PALETTE.coral:a,max:14})}</g>`).join('')}`);
    case 'same-dataset': return svg('Single and Multi evaluated against same Dataset',`${box(55,205,190,110,'SAME DATASET',{accent:PALETTE.ink})}${box(365,80,200,100,'Single Task',{accent:PALETTE.blue})}${box(365,330,200,100,'Multi Task',{accent:PALETTE.teal})}${box(750,205,190,110,'SAME SCORES',{accent:PALETTE.coral})}${line(245,235,355,130,{stroke:PALETTE.blue})}${line(245,285,355,380,{stroke:PALETTE.teal})}${line(565,130,740,235,{stroke:PALETTE.blue})}${line(565,380,740,285,{stroke:PALETTE.teal})}`);
    case 'comparison': return svg('Single Multi Delta comparison table',`<rect x="60" y="70" width="880" height="390" fill="${PALETTE.paper2}" stroke="${PALETTE.ink}" stroke-width="2"/>${['METRIC','SINGLE','MULTI','DELTA','DRIVER','CONCLUSION'].map((t,i)=>`<rect x="${60+i*146.67}" y="70" width="146.67" height="390" fill="${i===3?PALETTE.wash:'transparent'}" stroke="${PALETTE.rule}"/>${label(133+i*146.67,112,t,i===3?a:PALETTE.ink)}${[165,220,275,330,385,440].map(y=>`<line x1="${74+i*146.67}" y1="${y}" x2="${192+i*146.67}" y2="${y}" stroke="${PALETTE.rule}"/>`).join('')}`).join('')}`);
    case 'bad-case': return flow(['ITEM','EXPECTED','ACTUAL','SCORES','TRACE','OWNER','ROOT CAUSE'],a,{title:'Bad case diagnostic path'});
    case 'showcase': return flow(['DRIVERS','BOUNDARIES','DELTA','BAD CASE','DECISION'],a,{title:'Five minute architecture defense',y:180,h:150,caption:'5 MINUTES · EVIDENCE BEFORE DIAGRAM DETAIL'});
    case 'three-exits': return columns([{title:'ADOPT',body:'收益成立\n代价可接受',color:PALETTE.teal,foot:'KEEP'},{title:'ADAPT',body:'方向有效\n边界需调整',color:PALETTE.gold,foot:'CHANGE'},{title:'REJECT',body:'收益不足\n代价过高',color:PALETTE.coral,foot:'RETURN TO BASELINE'}],a,'Three equal architecture decisions');
    case 'dod': return flow(['BASELINE','TOP 3','ADR','CONTRACT','ADAPTER','SAME RUN','BAD CASE','DECISION'],a,{title:'Definition of done evidence chain',gap:10,h:130,y:190});
    case 'final': return svg('Evidence decides whether architecture changes',`${box(70,205,210,110,'SINGLE',{sub:'baseline',accent:PALETTE.blue})}${box(395,205,210,110,'MULTI',{sub:'hypothesis',accent:PALETTE.teal})}${line(280,260,385,260,{stroke:PALETTE.paper2,width:4})}${line(605,260,710,140,{stroke:PALETTE.teal,width:4})}${line(605,260,710,260,{stroke:PALETTE.gold,width:4})}${line(605,260,710,380,{stroke:PALETTE.coral,width:4})}${box(720,85,210,90,'ADOPT',{accent:PALETTE.teal})}${box(720,215,210,90,'ADAPT',{accent:PALETTE.gold})}${box(720,345,210,90,'REJECT',{accent:PALETTE.coral})}`);
    default: return flow(slide.items?.slice(0,6) || ['EVIDENCE','DESIGN','DECIDE'],a,{title:slide.title});
  }
}

function createSlide(slide, index) {
  const section=document.createElement('section');
  const titleLength=[...slide.title].length;
  const classNames=['slide'];
  if(slide.kind==='title') classNames.push('title-slide');
  else if(slide.kind==='statement') classNames.push('statement-slide');
  else if(slide.kind==='statement-split') classNames.push('statement-slide','split-statement-slide');
  else if(slide.kind==='activity') classNames.push('activity-slide');
  else if(slide.kind==='optional') classNames.push('optional');
  else if(slide.kind==='insert') classNames.push('insert');
  if(slide.visual==='decision-chain') classNames.push('compact-flow-slide');
  if(titleLength>28) classNames.push('xlong-title'); else if(titleLength>21) classNames.push('long-title');
  section.className=classNames.join(' ');
  section.dataset.part=slide.part; section.dataset.id=slide.id; section.dataset.title=slide.title; section.dataset.index=String(index+1).padStart(2,'0');
  const optional=slide.kind==='optional', insert=slide.kind==='insert';
  if(optional) section.dataset.optional='true';
  const tag=optional?'OPTIONAL DETAIL':insert?'CORE INSERT':`PART ${slide.part}`;
  const bullets=slide.items?.length?`<ul class="bullets">${slide.items.map(item=>`<li>${esc(item).replace(/ · /g,' <strong>·</strong> ')}</li>`).join('')}</ul>`:'';
  const visual=`<figure class="visual">${renderVisual(slide.visual,slide)}</figure>`;
  if(slide.kind==='title'){
    const agendaColumn=(label,items)=>`<div class="agenda-column"><p class="agenda-period">${label}</p>${items.map(([time,name])=>`<div class="agenda-row"><time>${esc(time)}</time><span>${esc(name)}</span></div>`).join('')}</div>`;
    const agenda=`<div class="day-agenda"><div class="agenda-head"><span>LEARNING PATH</span><b>DESIGN → VALIDATE</b></div><div class="agenda-columns">${agendaColumn('理解与基线',slide.agenda.morning)}${agendaColumn('设计与验证',slide.agenda.afternoon)}</div></div>`;
    section.innerHTML=`<div class="hero"><div class="hero-copy"><p class="kicker">AGENTIC ARCHITECTURE LAB</p><h1>先看证据，<br>再决定要不要<br>多 Agent</h1><p class="hero-lead">${esc(slide.claim)}</p></div>${agenda}</div><footer class="slide-footer"><span class="logical-id">LAB</span><span class="part-name">用同一套数据做架构实验</span><span>${String(index+1).padStart(2,'0')} / ${SLIDES.length}</span></footer>`;
  } else {
    const bodyClass=slide.kind==='visual-first'?'slide-body visual-first':(slide.kind==='statement'?'slide-body full':'slide-body');
    section.innerHTML=`<header class="slide-header"><div><p class="kicker">${esc(PARTS[slide.part])}</p><h2>${esc(slide.title)}</h2></div><span class="slide-tag">${tag}</span></header><div class="${bodyClass}">${slide.kind==='visual-first'?`${visual}<div class="copy"><p class="claim">${esc(slide.claim)}</p>${bullets}</div>`:`<div class="copy"><p class="claim">${esc(slide.claim)}</p>${bullets}</div>${visual}`}</div><footer class="slide-footer"><span class="logical-id">${esc(slide.id)}</span><span class="part-name">${esc(PARTS[slide.part])}</span><span>${String(index+1).padStart(2,'0')} / ${SLIDES.length}</span></footer>`;
  }
  section.setAttribute('aria-label',`Slide ${index+1}: ${slide.title}`); section.setAttribute('aria-hidden','true');
  return section;
}

SLIDES.forEach((slide,index)=>deck.appendChild(createSlide(slide,index)));
const allSlides=[...document.querySelectorAll('.slide')];
const counter=document.querySelector('#slide-counter'); const progress=document.querySelector('.progress'); const notesCopy=document.querySelector('#notes-copy');
let current=0, showOptional=true;
const visibleSlides=()=>allSlides.filter(s=>showOptional || s.dataset.optional!=='true');
function show(index,updateHash=true){
  const visible=visibleSlides(); if(!visible.length)return;
  current=Math.min(Math.max(index,0),visible.length-1);
  allSlides.forEach(s=>{s.classList.remove('active');s.setAttribute('aria-hidden','true')});
  const active=visible[current]; active.classList.add('active'); active.setAttribute('aria-hidden','false');
  const rawIndex=allSlides.indexOf(active); const data=SLIDES[rawIndex];
  counter.value=`${String(current+1).padStart(2,'0')} / ${String(visible.length).padStart(2,'0')}`;
  progress.style.width=`${(current+1)/visible.length*100}%`; notesCopy.innerHTML=`<p><b>${esc(data.id)} · ${esc(data.title)}</b></p><p>${esc(data.notes||'')}</p>${data.sources?`<p>[Sources]<br>${data.sources.map(esc).join('<br>')}</p>`:''}`;
  document.title=`${data.title} · ${current+1}/${visible.length}`;
  if(updateHash) history.replaceState(null,'',`#${encodeURIComponent(data.id)}`);
}
function move(delta){show(current+delta)}
document.querySelector('#prev').addEventListener('click',()=>move(-1)); document.querySelector('#next').addEventListener('click',()=>move(1));
document.querySelector('#fullscreen').addEventListener('click',()=>document.fullscreenElement?document.exitFullscreen?.():document.documentElement.requestFullscreen?.());
document.querySelector('#optional').addEventListener('click',event=>{const activeId=visibleSlides()[current]?.dataset.id;showOptional=!showOptional;event.currentTarget.setAttribute('aria-pressed',String(showOptional));event.currentTarget.textContent=showOptional?'DETAIL ON':'CORE ONLY';allSlides.forEach(s=>s.classList.toggle('hidden-optional',!showOptional&&s.dataset.optional==='true'));const idx=visibleSlides().findIndex(s=>s.dataset.id===activeId);show(idx>=0?idx:Math.min(current,visibleSlides().length-1));});
const toggleNotes=force=>{const open=force??!document.body.classList.contains('notes-open');document.body.classList.toggle('notes-open',open);document.querySelector('#notes').setAttribute('aria-pressed',String(open));};
document.querySelector('#notes').addEventListener('click',()=>toggleNotes()); document.querySelector('#close-notes').addEventListener('click',()=>toggleNotes(false));
const toggleOverview=force=>{const open=force??!document.body.classList.contains('overview');document.body.classList.toggle('overview',open);document.querySelector('#overview').setAttribute('aria-pressed',String(open));if(!open)show(current,false);};
document.querySelector('#overview').addEventListener('click',()=>toggleOverview());
deck.addEventListener('click',event=>{if(!document.body.classList.contains('overview'))return;const slide=event.target.closest('.slide');if(!slide)return;const idx=visibleSlides().indexOf(slide);toggleOverview(false);show(idx);});
document.addEventListener('keydown',event=>{
  if(document.body.classList.contains('overview')){if(event.key==='Escape'||event.key.toLowerCase()==='o')toggleOverview(false);return;}
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(event.key)){event.preventDefault();move(1)}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(event.key)){event.preventDefault();move(-1)}
  else if(event.key==='Home'){event.preventDefault();show(0)} else if(event.key==='End'){event.preventDefault();show(visibleSlides().length-1)}
  else if(event.key.toLowerCase()==='f')document.querySelector('#fullscreen').click(); else if(event.key.toLowerCase()==='o')toggleOverview(true); else if(event.key.toLowerCase()==='n')toggleNotes();
});
window.addEventListener('hashchange',()=>{const id=decodeURIComponent(location.hash.slice(1));const idx=visibleSlides().findIndex(s=>s.dataset.id===id);if(idx>=0)show(idx,false)});
const initialId=decodeURIComponent(location.hash.slice(1));const initialIndex=visibleSlides().findIndex(s=>s.dataset.id===initialId);show(initialIndex>=0?initialIndex:0,false);
