(function () {
  const NODE_W = 118;
  const NODE_H = 36;

  /** @type {Array<{id:string,name:string,x:number,y:number,color:string,group:string,note?:string}>} */
  const NODES = [
    { id: "dom", name: "Dom Holt", x: 62, y: 28, color: "#c5d4ef", group: "other" },
    { id: "mitch", name: "Mitch", x: 210, y: 28, color: "#c5d4ef", group: "dealers" },
    { id: "luca", name: "Luca", x: 358, y: 28, color: "#c5d4ef", group: "dealers" },
    { id: "police", name: "Police", x: 62, y: 468, color: "#c5d4ef", group: "police" },
    { id: "caroline", name: "Caroline", x: 448, y: 72, color: "#9ec5f5", group: "other" },
    { id: "samantha", name: "Samantha", x: 448, y: 148, color: "#d4c5e8", group: "collectors" },
    { id: "garth", name: "Garth", x: 448, y: 224, color: "#d4c5e8", group: "collectors" },
    {
      id: "kuldesh",
      name: "Kuldesh",
      x: 448,
      y: 308,
      color: "#9fd4d4",
      group: "collectors",
      note: "1 received a box of heroin",
    },
    { id: "nina", name: "Nina", x: 448, y: 392, color: "#d4c5e8", group: "collectors" },
    { id: "connie", name: "Connie", x: 788, y: 108, color: "#bfe8bf", group: "pensioners" },
    { id: "ibrahim", name: "Ibrahim", x: 788, y: 204, color: "#bfe8bf", group: "pensioners" },
    { id: "stephen", name: "Stephen", x: 788, y: 300, color: "#bfe8bf", group: "pensioners" },
    { id: "elizabeth", name: "Elizabeth", x: 788, y: 396, color: "#bfe8bf", group: "pensioners" },
  ];

  /** @type {Array<{from:string,to:string,label?:string,dashed?:boolean,step?:number}>} */
  const EDGES = [
    { from: "kuldesh", to: "nina", label: "2 called Nina to inspect the box", step: 2 },
    { from: "kuldesh", to: "stephen", label: "3 brought the box to Stephen", step: 3 },
    { from: "nina", to: "kuldesh", label: "4 kill", step: 4 },
    { from: "ibrahim", to: "connie", label: "6 told Connie about it", step: 6 },
    { from: "elizabeth", to: "nina", label: "8 got cam footage of stealing", step: 8 },
    { from: "garth", to: "nina", label: "9 pretend to buy the box", step: 9 },
    { from: "caroline", to: "mitch", label: "9 searching for the box in a pile of garbage", step: 9 },
    { from: "nina", to: "police", label: "10 arrested for killing Kuldesh", step: 10 },
    { from: "caroline", to: "dom", label: "kill" },
    { from: "caroline", to: "samantha" },
    { from: "caroline", to: "connie", label: "hitwoman" },
    { from: "luca", to: "police", label: "spy" },
    { from: "connie", to: "ibrahim", dashed: true },
    { from: "ibrahim", to: "stephen", dashed: true },
    { from: "stephen", to: "elizabeth", dashed: true },
  ];

  const GROUP_LABELS = {
    pensioners: "Pensioners (club)",
    collectors: "Antique collectors",
    dealers: "Drug dealers",
    police: "Police",
    other: "Others",
  };

  const nodesById = Object.fromEntries(NODES.map((n) => [n.id, n]));

  let selectedId = null;

  const el = {
    revealBtn: document.getElementById("chart-reveal-btn"),
    chart: document.getElementById("character-chart"),
    stage: document.getElementById("plot-graph-stage"),
    svg: document.getElementById("plot-edges"),
    nodes: document.getElementById("plot-nodes"),
    detailEmpty: document.getElementById("character-detail-empty"),
    detailContent: document.getElementById("character-detail-content"),
    detailName: document.getElementById("character-detail-name"),
    detailFaction: document.getElementById("character-detail-faction"),
    detailRole: document.getElementById("character-detail-role"),
    detailLinks: document.getElementById("character-detail-links"),
  };

  function center(node) {
    return { x: node.x + NODE_W / 2, y: node.y + NODE_H / 2 };
  }

  function connectedIds(personId) {
    const ids = new Set();
    for (const e of EDGES) {
      if (e.from === personId) ids.add(e.to);
      if (e.to === personId) ids.add(e.from);
    }
    return ids;
  }

  function edgesFor(personId) {
    return EDGES.filter((e) => e.from === personId || e.to === personId);
  }

  function edgeActive(edge) {
    if (!selectedId) return false;
    return edge.from === selectedId || edge.to === selectedId;
  }

  function pathD(from, to) {
    const a = center(nodesById[from]);
    const b = center(nodesById[to]);
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const cx = (a.x + b.x) / 2 + dy * 0.12;
    const cy = (a.y + b.y) / 2 - dx * 0.12;
    return `M ${a.x} ${a.y} Q ${cx} ${cy} ${b.x} ${b.y}`;
  }

  function labelPoint(from, to) {
    const a = center(nodesById[from]);
    const b = center(nodesById[to]);
    const t = 0.5;
    const cx = (a.x + b.x) / 2 + (b.y - a.y) * 0.12;
    const cy = (a.y + b.y) / 2 - (b.x - a.x) * 0.12;
    const x = (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * cx + t * t * b.x;
    const y = (1 - t) * (1 - t) * a.y + 2 * (1 - t) * t * cy + t * t * b.y;
    return { x, y };
  }

  function renderGraph() {
    const w = 960;
    const h = 540;
    el.svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    const defs = `<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path>
      </marker>
    </defs>`;

    const edgeMarkup = EDGES.map((edge, i) => {
      const active = edgeActive(edge);
      const dim = selectedId && !active;
      const d = pathD(edge.from, edge.to);
      const cls = [
        "plot-edge",
        edge.dashed ? "plot-edge--dashed" : "",
        active ? "is-active" : "",
        dim ? "is-dim" : "",
      ]
        .filter(Boolean)
        .join(" ");
      let label = "";
      if (edge.label) {
        const p = labelPoint(edge.from, edge.to);
        label = `<text class="plot-edge__label${dim ? " is-dim" : ""}${active ? " is-active" : ""}" x="${p.x}" y="${p.y}" text-anchor="middle">${escapeHtml(edge.label)}</text>`;
      }
      return `<path class="${cls}" d="${d}" marker-end="url(#arrow)" aria-hidden="true"></path>${label}`;
    }).join("");

    el.svg.innerHTML = defs + edgeMarkup;

    el.nodes.innerHTML = NODES.map((node) => {
      const isSelected = node.id === selectedId;
      const isLinked =
        selectedId && connectedIds(selectedId).has(node.id) && node.id !== selectedId;
      const cls = [
        "plot-node",
        isSelected ? "is-selected" : "",
        isLinked ? "is-linked" : "",
        selectedId && !isSelected && !isLinked ? "is-dim" : "",
      ]
        .filter(Boolean)
        .join(" ");
      const note = node.note
        ? `<span class="plot-node__note">${escapeHtml(node.note)}</span>`
        : "";
      return `<button type="button" class="${cls}" data-id="${node.id}" aria-pressed="${isSelected}" style="left:${node.x}px;top:${node.y}px;width:${NODE_W}px;background:${node.color}">${note}<span class="plot-node__name">${escapeHtml(node.name)}</span></button>`;
    }).join("");
  }

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderDetail() {
    if (!selectedId) {
      el.detailEmpty.hidden = false;
      el.detailContent.hidden = true;
      return;
    }
    const node = nodesById[selectedId];
    el.detailEmpty.hidden = true;
    el.detailContent.hidden = false;
    el.detailName.textContent = node.name;
    el.detailFaction.textContent = GROUP_LABELS[node.group] || node.group;
    el.detailRole.textContent = node.note || "Click another name to trace the plot threads.";

    const links = edgesFor(selectedId)
      .filter((e) => e.label)
      .map((e) => {
        const out = e.from === selectedId;
        const other = nodesById[out ? e.to : e.from];
        const dir = out ? `→ ${other.name}` : `← ${other.name}`;
        return `<li><span class="character-link__dir">${dir}</span> — ${e.label}</li>`;
      });
    el.detailLinks.innerHTML =
      links.length > 0
        ? links.join("")
        : "<li>Dashed lines: pensioner club stack (no label on chart).</li>";
  }

  function select(id) {
    selectedId = selectedId === id ? null : id;
    renderGraph();
    renderDetail();
  }

  function initChart() {
    renderGraph();
    renderDetail();
    el.nodes.addEventListener("click", (e) => {
      const btn = e.target.closest(".plot-node");
      if (!btn) return;
      select(btn.dataset.id);
    });
  }

  function initReveal() {
    if (!el.revealBtn || !el.chart) return;
    el.revealBtn.addEventListener("click", () => {
      el.chart.hidden = false;
      el.revealBtn.closest(".spoiler-gate")?.remove();
      initChart();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initReveal);
  } else {
    initReveal();
  }
})();
