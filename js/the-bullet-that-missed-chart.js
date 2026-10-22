(function () {
  const FACTIONS = [
    {
      id: "pensioners",
      label: "Pensioners",
      hint: "Co-op residents & amateur sleuths",
      accent: "#ffd56b",
    },
    {
      id: "police",
      label: "Police",
      hint: "Official investigation",
      accent: "#7eb8ff",
    },
    {
      id: "dealers",
      label: "Drug dealers",
      hint: "Heroin supply chain",
      accent: "#ff9f6b",
    },
    {
      id: "collectors",
      label: "Antique collectors",
      hint: "Kuldesh's circle & the box",
      accent: "#c89bff",
    },
  ];

  const PEOPLE = [
    {
      id: "joyce",
      name: "Joyce",
      faction: "pensioners",
      role: "Thursday Murder Club; digs into Kuldesh's death.",
    },
    {
      id: "elizabeth",
      name: "Elizabeth",
      faction: "pensioners",
      role: "Ex-union boss; sharp instincts on the case.",
    },
    {
      id: "stephen",
      name: "Stephen",
      faction: "pensioners",
      role: "Psychiatrist; Kuldesh trusts him with the box.",
    },
    {
      id: "ron",
      name: "Ron",
      faction: "pensioners",
      role: "Club member; along for the ride.",
    },
    {
      id: "ibrahim",
      name: "Ibrahim",
      faction: "pensioners",
      role: "Club member; chess and quiet observation.",
    },
    {
      id: "donna",
      name: "Donna",
      faction: "police",
      role: "Leads the heroin side of the investigation.",
    },
    {
      id: "jill",
      name: "Jill",
      faction: "police",
      role: "Works the drug trail with Donna.",
    },
    {
      id: "chris",
      name: "Chris",
      faction: "police",
      role: "On the official inquiry.",
    },
    {
      id: "mitch",
      name: "Mitch",
      faction: "dealers",
      role: "Intended recipient of the heroin shipment.",
    },
    {
      id: "luca",
      name: "Luca",
      faction: "dealers",
      role: "Part of the supply chain.",
    },
    {
      id: "connie",
      name: "Connie",
      faction: "dealers",
      role: "Connected to moving the box.",
    },
    {
      id: "kuldesh",
      name: "Kuldesh",
      faction: "collectors",
      role: "Antique dealer; friend of the pensioners; murdered.",
    },
    {
      id: "nina",
      name: "Nina",
      faction: "collectors",
      role: "Collector; kills Kuldesh after the handoff to Stephen.",
    },
    {
      id: "samantha",
      name: "Samantha",
      faction: "collectors",
      role: "Collector; wants the box back in play.",
    },
  ];

  /** @type {Array<{from:string,to:string,label:string}>} */
  const EDGES = [
    { from: "joyce", to: "kuldesh", label: "Friend; helps investigate his murder" },
    { from: "elizabeth", to: "kuldesh", label: "Friend; investigates his murder" },
    { from: "stephen", to: "kuldesh", label: "Friend; receives the heroin box from him" },
    { from: "ron", to: "kuldesh", label: "Friend (Thursday Murder Club)" },
    { from: "ibrahim", to: "kuldesh", label: "Friend (Thursday Murder Club)" },
    { from: "luca", to: "kuldesh", label: "Heroin box passes through dealers to Kuldesh" },
    { from: "connie", to: "kuldesh", label: "Linked to the box meant for Mitch" },
    { from: "kuldesh", to: "mitch", label: "Supposed to deliver the heroin box" },
    { from: "kuldesh", to: "stephen", label: "Brings the box to Stephen before he dies" },
    { from: "nina", to: "kuldesh", label: "Murders him after the box reaches Stephen" },
    { from: "donna", to: "mitch", label: "Traces the heroin toward Mitch" },
    { from: "jill", to: "mitch", label: "Follows the official drug investigation" },
    { from: "chris", to: "mitch", label: "Part of the heroin inquiry" },
    { from: "nina", to: "mitch", label: "Wants the box (collector side)" },
    { from: "samantha", to: "mitch", label: "Wants the box recovered" },
  ];

  const peopleById = Object.fromEntries(PEOPLE.map((p) => [p.id, p]));
  const factionById = Object.fromEntries(FACTIONS.map((f) => [f.id, f]));

  let selectedId = null;

  const el = {
    grid: document.getElementById("character-grid"),
    detail: document.getElementById("character-detail"),
    detailEmpty: document.getElementById("character-detail-empty"),
    detailContent: document.getElementById("character-detail-content"),
    detailName: document.getElementById("character-detail-name"),
    detailFaction: document.getElementById("character-detail-faction"),
    detailRole: document.getElementById("character-detail-role"),
    detailLinks: document.getElementById("character-detail-links"),
    revealBtn: document.getElementById("chart-reveal-btn"),
    chart: document.getElementById("character-chart"),
  };

  function edgesFor(personId) {
    return EDGES.filter((e) => e.from === personId || e.to === personId);
  }

  function connectedIds(personId) {
    const ids = new Set();
    for (const e of edgesFor(personId)) {
      ids.add(e.from === personId ? e.to : e.from);
    }
    return ids;
  }

  function formatLink(edge, viewerId) {
    const otherId = edge.from === viewerId ? edge.to : edge.from;
    const other = peopleById[otherId];
    const direction =
      edge.from === viewerId
        ? `→ ${other.name}`
        : `← ${other.name}`;
    return { direction, label: edge.label, otherId };
  }

  function renderGrid() {
    el.grid.innerHTML = FACTIONS.map((faction) => {
      const members = PEOPLE.filter((p) => p.faction === faction.id);
      const chips = members
        .map((p) => {
          const isSelected = p.id === selectedId;
          const isLinked =
            selectedId && connectedIds(selectedId).has(p.id) && p.id !== selectedId;
          let cls = "character-chip";
          if (isSelected) cls += " is-selected";
          else if (isLinked) cls += " is-linked";
          return `<button type="button" class="${cls}" data-id="${p.id}" aria-pressed="${isSelected}" style="--chip-accent:${faction.accent}">${p.name}</button>`;
        })
        .join("");
      return `
        <div class="faction-column" style="--faction-accent:${faction.accent}">
          <h3 class="faction-column__title">${faction.label}</h3>
          <p class="faction-column__hint">${faction.hint}</p>
          <div class="faction-column__chips">${chips}</div>
        </div>`;
    }).join("");
  }

  function renderDetail() {
    if (!selectedId) {
      el.detailEmpty.hidden = false;
      el.detailContent.hidden = true;
      return;
    }
    const person = peopleById[selectedId];
    const faction = factionById[person.faction];
    el.detailEmpty.hidden = true;
    el.detailContent.hidden = false;
    el.detailName.textContent = person.name;
    el.detailFaction.textContent = faction.label;
    el.detailRole.textContent = person.role;

    const links = edgesFor(selectedId).map((e) => formatLink(e, selectedId));
    el.detailLinks.innerHTML =
      links.length === 0
        ? "<li>No mapped links yet.</li>"
        : links
            .map(
              (l) =>
                `<li><span class="character-link__dir">${l.direction}</span> — ${l.label}</li>`
            )
            .join("");
  }

  function select(id) {
    selectedId = selectedId === id ? null : id;
    renderGrid();
    renderDetail();
  }

  function initChart() {
    renderGrid();
    renderDetail();

    el.grid.addEventListener("click", (e) => {
      const btn = e.target.closest(".character-chip");
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
