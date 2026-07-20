(() => {
  'use strict';

  const svg = document.getElementById('sketch');
  const lengthInput = document.getElementById('lengthInput');
  const approxBtn = document.getElementById('approxBtn');
  const undoBtn = document.getElementById('undoBtn');
  const finishBtn = document.getElementById('finishBtn');
  const toolsBtn = document.getElementById('toolsBtn');
  const toolsDialog = document.getElementById('toolsDialog');
  const classifyDialog = document.getElementById('classifyDialog');
  const classifyTitle = document.getElementById('classifyTitle');
  const classifyAreaText = document.getElementById('classifyAreaText');
  const classifyChoices = document.getElementById('classifyChoices');
  const backOutDialog = document.getElementById('backOutDialog');
  const backOutChoices = document.getElementById('backOutChoices');
  const modeBadge = document.getElementById('modeBadge');
  const closureText = document.getElementById('closureText');

  const SCALE = 12;
  const START = { x: 500, y: 350 };
  const STORAGE_KEY = 'clipboard-v5-0b-sketch';
  const AREA_TYPES = ['ANSI GLA','Garage','Covered Patio','Open Patio','Porch','Balcony','Storage','Guest Area','Utility','Other'];
  const BACKOUT_TYPES = ['Garage','Open to Below','Covered Patio','Open Patio','Porch','Storage','Breezeway','Courtyard','Other'];

  const state = load() || {
    structures: [{ id: crypto.randomUUID(), name: 'Structure 1', points: [START], walls: [], closed: false, classification: null }],
    activeStructure: 0,
    approximateMode: false,
    backOutMode: false,
    pendingBackOut: [],
    backOutAreas: []
  };

  function parseLength(value) {
    const v = String(value || '').trim();
    if (!v) return NaN;
    const feetInches = v.match(/^\s*(\d+(?:\.\d+)?)\s*'\s*(\d+(?:\.\d+)?)?\s*"?\s*$/);
    if (feetInches) return Number(feetInches[1]) + Number(feetInches[2] || 0) / 12;
    const mixed = v.match(/^\s*(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*$/);
    if (mixed) return Number(mixed[1]) + Number(mixed[2]) / 12;
    return Number(v.replace(/ft|feet|foot/gi, '').trim());
  }

  function active() { return state.structures[state.activeStructure]; }
  function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  function load() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch { return null; } }
  function fmt(n) { return Number(n).toFixed(1).replace(/\.0$/, ''); }

  function addWall(direction) {
    const structure = active();
    if (structure.closed) return notice('Start a new structure or undo the closure.');
    const feet = parseLength(lengthInput.value);
    if (!(feet > 0)) return notice('Enter a valid wall length.');
    const last = structure.points.at(-1);
    let dx = 0, dy = 0;
    if (direction === 'left') dx = -feet * SCALE;
    if (direction === 'right') dx = feet * SCALE;
    if (direction === 'up') dy = -feet * SCALE;
    if (direction === 'down') dy = feet * SCALE;
    const next = { x: last.x + dx, y: last.y + dy };
    structure.points.push(next);
    structure.walls.push({ length: feet, approximate: state.approximateMode });
    state.approximateMode = false;
    approxBtn.classList.remove('active-mode');
    lengthInput.value = '';
    save();
    render();
    lengthInput.focus();
  }

  function setApproximate() {
    state.approximateMode = !state.approximateMode;
    approxBtn.classList.toggle('active-mode', state.approximateMode);
    modeBadge.textContent = state.approximateMode ? 'Back-Out Later' : 'Sketch';
  }

  function undo() {
    const structure = active();
    if (state.pendingBackOut.length) {
      state.pendingBackOut.pop();
    } else if (structure.closed) {
      structure.closed = false;
      structure.points.pop();
      structure.walls.pop();
    } else if (structure.walls.length) {
      structure.walls.pop();
      structure.points.pop();
    }
    save(); render();
  }

  function finishStructure() {
    const structure = active();
    if (structure.points.length < 3) return notice('At least three walls are required.');
    const first = structure.points[0];
    const last = structure.points.at(-1);
    const gap = Math.hypot(first.x-last.x, first.y-last.y) / SCALE;
    if (gap > 0.05) {
      structure.points.push({ ...first });
      structure.walls.push({ length: gap, approximate: true, closureWall: true });
    }
    structure.closed = true;
    save(); render();
    notice(gap <= 0.25 ? 'Structure closed.' : `Closed with ${fmt(gap)} ft backed out. Review the dashed wall.`);
  }

  function polygonArea(points) {
    if (points.length < 3) return 0;
    let sum = 0;
    for (let i=0;i<points.length-1;i++) sum += points[i].x*points[i+1].y - points[i+1].x*points[i].y;
    return Math.abs(sum) / 2 / (SCALE*SCALE);
  }

  function netArea() {
    const gross = state.structures.reduce((t,s)=>t+(s.closed?polygonArea(s.points):0),0);
    const deductions = state.backOutAreas.reduce((t,a)=>t+polygonArea([...a.points,a.points[0]]),0);
    return { gross, deductions, net: Math.max(0,gross-deductions) };
  }

  function startBackOut() {
    toolsDialog.close();
    if (!active().closed) return notice('Finish the main footprint first.');
    state.backOutMode = true;
    state.pendingBackOut = [];
    modeBadge.textContent = 'Back-Out Area';
    closureText.textContent = 'Tap points around the area. Tap the first point to close.';
    render();
  }

  function svgPoint(evt) {
    const rect = svg.getBoundingClientRect();
    return { x: (evt.clientX-rect.left)*1000/rect.width, y: (evt.clientY-rect.top)*700/rect.height };
  }

  function handleCanvasTap(evt) {
    if (!state.backOutMode) return;
    const p = svgPoint(evt);
    if (state.pendingBackOut.length >= 3) {
      const first = state.pendingBackOut[0];
      if (Math.hypot(p.x-first.x,p.y-first.y) < 25) {
        backOutDialog.showModal();
        return;
      }
    }
    state.pendingBackOut.push(p);
    render();
  }

  function completeBackOut(type) {
    if (state.pendingBackOut.length < 3) return;
    state.backOutAreas.push({ id: crypto.randomUUID(), type, points: [...state.pendingBackOut] });
    state.pendingBackOut = [];
    state.backOutMode = false;
    backOutDialog.close();
    modeBadge.textContent = 'Sketch';
    save(); render();
  }

  function classifyAreas() {
    toolsDialog.close();
    const candidates = state.structures.filter(s=>s.closed);
    if (!candidates.length) return notice('Finish at least one structure first.');
    let i = 0;
    const next = () => {
      if (i >= candidates.length) { classifyDialog.close(); render(); return; }
      const s = candidates[i];
      classifyTitle.textContent = 'What area is this?';
      classifyAreaText.textContent = `${s.name}: ${fmt(polygonArea(s.points))} sf`;
      classifyChoices.innerHTML = '';
      AREA_TYPES.forEach(type => {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = type;
        b.onclick = () => { s.classification = type; i++; save(); next(); };
        classifyChoices.appendChild(b);
      });
      if (!classifyDialog.open) classifyDialog.showModal();
    };
    next();
  }

  function newStructure() {
    toolsDialog.close();
    state.structures.push({ id: crypto.randomUUID(), name:`Structure ${state.structures.length+1}`, points:[{x:500,y:350}], walls:[], closed:false, classification:null });
    state.activeStructure = state.structures.length-1;
    save(); render();
  }

  function resetSketch() {
    if (!confirm('Reset the entire sketch?')) return;
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
  }

  function render() {
    svg.innerHTML = '';
    const ns = 'http://www.w3.org/2000/svg';
    state.structures.forEach((s, structureIndex) => {
      if (s.closed && s.points.length>2) {
        const poly = document.createElementNS(ns,'polygon');
        poly.setAttribute('points', s.points.map(p=>`${p.x},${p.y}`).join(' '));
        poly.setAttribute('class','area-fill');
        svg.appendChild(poly);
      }
      for (let i=0;i<s.walls.length;i++) {
        const a=s.points[i], b=s.points[i+1];
        const line=document.createElementNS(ns,'line');
        line.setAttribute('x1',a.x); line.setAttribute('y1',a.y); line.setAttribute('x2',b.x); line.setAttribute('y2',b.y);
        line.setAttribute('class',`wall${s.walls[i].approximate?' approx':''}`);
        svg.appendChild(line);
        const label=document.createElementNS(ns,'text');
        label.setAttribute('x',(a.x+b.x)/2); label.setAttribute('y',(a.y+b.y)/2-10); label.setAttribute('class','measure-label');
        label.textContent=`${fmt(s.walls[i].length)}'${s.walls[i].approximate?' ~':''}`;
        svg.appendChild(label);
      }
      s.points.forEach((p,idx)=>{
        if (idx===s.points.length-1 && s.closed) return;
        const c=document.createElementNS(ns,'circle'); c.setAttribute('cx',p.x); c.setAttribute('cy',p.y); c.setAttribute('r',7); c.setAttribute('class','vertex'); svg.appendChild(c);
      });
      if (s.closed) {
        const pts=s.points.slice(0,-1); const cx=pts.reduce((t,p)=>t+p.x,0)/pts.length; const cy=pts.reduce((t,p)=>t+p.y,0)/pts.length;
        const txt=document.createElementNS(ns,'text'); txt.setAttribute('x',cx); txt.setAttribute('y',cy); txt.setAttribute('class','area-label');
        txt.textContent=s.classification||`Area ${structureIndex+1}`; svg.appendChild(txt);
      }
    });

    state.backOutAreas.forEach(a=>{
      const poly=document.createElementNS(ns,'polygon'); poly.setAttribute('points',a.points.map(p=>`${p.x},${p.y}`).join(' ')); poly.setAttribute('class','backout-fill'); svg.appendChild(poly);
      const cx=a.points.reduce((t,p)=>t+p.x,0)/a.points.length; const cy=a.points.reduce((t,p)=>t+p.y,0)/a.points.length;
      const txt=document.createElementNS(ns,'text'); txt.setAttribute('x',cx); txt.setAttribute('y',cy); txt.setAttribute('class','area-label'); txt.textContent=a.type; svg.appendChild(txt);
    });

    if (state.pendingBackOut.length) {
      const pl=document.createElementNS(ns,'polyline'); pl.setAttribute('points',state.pendingBackOut.map(p=>`${p.x},${p.y}`).join(' ')); pl.setAttribute('class','wall preview'); svg.appendChild(pl);
      state.pendingBackOut.forEach(p=>{const c=document.createElementNS(ns,'circle'); c.setAttribute('cx',p.x); c.setAttribute('cy',p.y); c.setAttribute('r',8); c.setAttribute('class','vertex'); svg.appendChild(c);});
    }

    const a=netArea();
    const current=active();
    if (state.backOutMode) {
      modeBadge.textContent='Back-Out Area';
    } else if (state.approximateMode) {
      modeBadge.textContent='Back-Out Later';
    } else {
      modeBadge.textContent='Sketch';
    }
    closureText.textContent = current.closed
      ? `Gross ${fmt(a.gross)} sf | Back-outs ${fmt(a.deductions)} sf | Net ${fmt(a.net)} sf`
      : `${current.name}: ${current.walls.length} wall${current.walls.length===1?'':'s'}`;
  }

  function notice(message) {
    closureText.textContent = message;
  }

  document.querySelectorAll('[data-direction]').forEach(b=>b.addEventListener('click',()=>addWall(b.dataset.direction)));
  approxBtn.addEventListener('click',setApproximate);
  undoBtn.addEventListener('click',undo);
  finishBtn.addEventListener('click',finishStructure);
  toolsBtn.addEventListener('click',()=>toolsDialog.showModal());
  document.getElementById('newStructureBtn').addEventListener('click',newStructure);
  document.getElementById('backOutAreaBtn').addEventListener('click',startBackOut);
  document.getElementById('classifyBtn').addEventListener('click',classifyAreas);
  document.getElementById('resetBtn').addEventListener('click',resetSketch);
  document.getElementById('cancelBackOut').addEventListener('click',()=>{state.backOutMode=false;state.pendingBackOut=[];backOutDialog.close();render();});
  svg.addEventListener('pointerdown',handleCanvasTap);
  lengthInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();notice('Tap a direction.');}});

  BACKOUT_TYPES.forEach(type=>{const b=document.createElement('button');b.type='button';b.textContent=type;b.onclick=()=>completeBackOut(type);backOutChoices.appendChild(b);});
  render();
})();
