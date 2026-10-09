(function () {
  const WRAPS = [
    {
      id: "thin-wheat",
      label: "Thin wheat dough",
      note: "Gyoza skins, jiaozi wrappers, pierogi dough",
    },
    {
      id: "yeast",
      label: "Fluffy yeast dough",
      note: "Bao buns, pan-fried bread pockets",
    },
    {
      id: "flaky",
      label: "Flaky pastry",
      note: "Samosa shells, empanada wrappers",
    },
    {
      id: "starch",
      label: "Rice & tapioca starch",
      note: "Har gow, shumai, crystal dumplings",
    },
  ];

  const FILLINGS = [
    { id: "beef", label: "Beef" },
    { id: "lamb", label: "Lamb" },
    { id: "pork", label: "Pork" },
    { id: "veg", label: "Vegetable" },
    { id: "cheese", label: "Cheese & potato" },
    { id: "ham", label: "Ham" },
    { id: "shrimp", label: "Shrimp" },
  ];

  const METHODS = [
    { id: "steam", label: "Steam" },
    { id: "boil", label: "Boil" },
    { id: "pan-fry", label: "Pan-fry" },
    { id: "deep-fry", label: "Deep-fry" },
  ];

  /** @type {Array<{id:string,name:string,region:string,blurb:string,wrap:string[],filling:string[],method:string[]}>} */
  const CATALOG = [
    {
      id: "gyoza",
      name: "Gyoza",
      region: "Japan · pan-fried heritage from Chinese jiaozi",
      blurb:
        "Thin skin, crisp lacey skirt from steam-fry technique, juicy pork-and-cabbage filling.",
      wrap: ["thin-wheat"],
      filling: ["pork", "veg", "beef", "shrimp"],
      method: ["pan-fry", "steam"],
    },
    {
      id: "jiaozi",
      name: "Jiaozi",
      region: "Northern China · New Year staple",
      blurb:
        "Plump crescent boiled or pan-fried — the archetype most dumplings are riffing on.",
      wrap: ["thin-wheat"],
      filling: ["pork", "beef", "lamb", "veg"],
      method: ["boil", "pan-fry", "steam"],
    },
    {
      id: "pierogi",
      name: "Pierogi",
      region: "Poland & Central Europe",
      blurb:
        "Soft half-moon, often potato-cheese inside, boiled then buttered or pan-crisped.",
      wrap: ["thin-wheat"],
      filling: ["cheese", "veg", "ham", "beef"],
      method: ["boil", "pan-fry", "steam"],
    },
    {
      id: "pelmeni",
      name: "Pelmeni",
      region: "Russia · Siberian freezer-friendly",
      blurb:
        "Tiny ear-shaped parcels, beef or mixed meat, boiled and served with sour cream.",
      wrap: ["thin-wheat"],
      filling: ["beef", "lamb", "pork", "ham"],
      method: ["boil"],
    },
    {
      id: "samosa",
      name: "Samosa",
      region: "South Asia · street-food icon",
      blurb:
        "Crisp triangular pastry, spiced potato or minced lamb, deep-fried until shattering.",
      wrap: ["flaky"],
      filling: ["veg", "lamb", "beef", "cheese"],
      method: ["deep-fry", "pan-fry"],
    },
    {
      id: "empanada",
      name: "Empanada",
      region: "Latin America · hand-held pie",
      blurb:
        "Half-moon pastry sealed with a rope crimp — ham and cheese to beef, baked or fried.",
      wrap: ["flaky"],
      filling: ["ham", "cheese", "beef", "veg"],
      method: ["deep-fry", "pan-fry", "steam"],
    },
    {
      id: "bao",
      name: "Bao (包子)",
      region: "China · fluffy steamed bun",
      blurb:
        "Pillowy yeast dough hugging BBQ pork or greens — cloud outside, savoury inside.",
      wrap: ["yeast"],
      filling: ["pork", "veg", "beef", "ham"],
      method: ["steam", "pan-fry"],
    },
    {
      id: "mandu",
      name: "Mandu",
      region: "Korea · dumpling for every season",
      blurb:
        "Plump crescents in soup or crisp on the bottom — kimchi pork is the classic flex.",
      wrap: ["thin-wheat"],
      filling: ["pork", "beef", "veg", "shrimp"],
      method: ["boil", "steam", "pan-fry"],
    },
    {
      id: "wonton",
      name: "Wonton",
      region: "Cantonese · soup companion",
      blurb:
        "Silky thin skin wrapped around shrimp or pork, boiled in broth or fried golden.",
      wrap: ["thin-wheat", "starch"],
      filling: ["shrimp", "pork", "ham", "veg"],
      method: ["boil", "deep-fry", "steam"],
    },
    {
      id: "shumai",
      name: "Shumai (siu mai)",
      region: "Guangdong · dim sum cart favourite",
      blurb:
        "Open-topped purse of pork and shrimp, steamed until the filling peeks out proudly.",
      wrap: ["starch", "thin-wheat"],
      filling: ["pork", "shrimp", "ham"],
      method: ["steam"],
    },
    {
      id: "har-gow",
      name: "Har gow",
      region: "Cantonese dim sum · shrimp jewel",
      blurb:
        "Translucent tapioca-wheat skin pleated around whole shrimp — steam only, no substitutes.",
      wrap: ["starch"],
      filling: ["shrimp"],
      method: ["steam"],
    },
    {
      id: "momo",
      name: "Momo",
      region: "Himalayas · Nepal & Tibet",
      blurb:
        "Round pleated top, buffalo or veg filling, steamed or fried with achaar on the side.",
      wrap: ["thin-wheat"],
      filling: ["veg", "lamb", "beef", "cheese"],
      method: ["steam", "pan-fry", "deep-fry"],
    },
    {
      id: "kreplach",
      name: "Kreplach",
      region: "Ashkenazi · Jewish dumpling",
      blurb:
        "Small triangles of dough in soup — beef or cheese, boiled like edible origami.",
      wrap: ["thin-wheat"],
      filling: ["beef", "cheese", "ham"],
      method: ["boil"],
    },
    {
      id: "soup-dumpling",
      name: "Xiao long bao",
      region: "Shanghai · soup inside magic",
      blurb:
        "Thin wheat pleats holding hot broth and pork — steam gently, bite carefully.",
      wrap: ["thin-wheat"],
      filling: ["pork", "beef", "shrimp"],
      method: ["steam"],
    },
    {
      id: "rangoon",
      name: "Crab rangoon",
      region: "American-Chinese · deep-fried curveball",
      blurb:
        "Crunchy wonton skin pockets of cream cheese — not authentic, extremely invited to parties.",
      wrap: ["thin-wheat", "starch"],
      filling: ["cheese", "shrimp", "ham"],
      method: ["deep-fry"],
    },
  ];

  const SVG = {
    gyoza: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="88" rx="72" ry="38" fill="#f4c896" stroke="#c9854a" stroke-width="3"/><path d="M35 88 Q100 35 165 88" fill="#e8b070" stroke="#c9854a" stroke-width="3"/><ellipse cx="100" cy="105" rx="68" ry="18" fill="#8b5a2b" opacity="0.85"/><circle cx="82" cy="78" r="5" fill="#2a2218"/><circle cx="118" cy="78" r="5" fill="#2a2218"/><path d="M88 92 Q100 98 112 92" fill="none" stroke="#2a2218" stroke-width="2" stroke-linecap="round"/></svg>`,
    jiaozi: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M40 85 Q100 25 160 85 Q100 115 40 85Z" fill="#f5d9a8" stroke="#c9925c" stroke-width="3"/><path d="M40 85 Q70 55 100 65 Q130 55 160 85" fill="none" stroke="#b87d45" stroke-width="2" opacity="0.6"/><circle cx="85" cy="72" r="5" fill="#2a2218"/><circle cx="115" cy="72" r="5" fill="#2a2218"/><path d="M92 82 Q100 88 108 82" fill="none" stroke="#2a2218" stroke-width="2" stroke-linecap="round"/></svg>`,
    pierogi: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M45 90 Q100 30 155 90 Q100 110 45 90Z" fill="#f8e4c4" stroke="#c49a6c" stroke-width="3"/><path d="M50 88 Q75 50 100 55 Q125 50 150 88" fill="none" stroke="#a67c52" stroke-width="2" stroke-dasharray="4 5"/><circle cx="88" cy="70" r="5" fill="#2a2218"/><circle cx="112" cy="70" r="5" fill="#2a2218"/><path d="M94 80 Q100 86 106 80" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    pelmeni: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="70" cy="85" rx="38" ry="28" fill="#f3dcb8" stroke="#c49a6c" stroke-width="2.5"/><ellipse cx="130" cy="85" rx="38" ry="28" fill="#f3dcb8" stroke="#c49a6c" stroke-width="2.5"/><path d="M32 85 Q70 55 108 85" fill="none" stroke="#a67c52" stroke-width="2"/><path d="M92 85 Q130 55 168 85" fill="none" stroke="#a67c52" stroke-width="2"/><circle cx="70" cy="78" r="4" fill="#2a2218"/><circle cx="130" cy="78" r="4" fill="#2a2218"/></svg>`,
    samosa: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><polygon points="100,25 170,110 30,110" fill="#e8a84a" stroke="#b87333" stroke-width="3"/><polygon points="100,40 150,105 50,105" fill="#f5c76b" opacity="0.5"/><circle cx="92" cy="78" r="5" fill="#2a2218"/><circle cx="108" cy="78" r="5" fill="#2a2218"/><path d="M94 92 Q100 98 106 92" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    empanada: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M50 95 Q100 20 150 95 Q100 120 50 95Z" fill="#d4a055" stroke="#9a6528" stroke-width="3"/><path d="M55 92 Q100 45 145 92" fill="none" stroke="#7a4f20" stroke-width="2"/><circle cx="88" cy="72" r="5" fill="#2a2218"/><circle cx="112" cy="72" r="5" fill="#2a2218"/></svg>`,
    bao: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="80" rx="65" ry="48" fill="#fff5e6" stroke="#e8c9a0" stroke-width="3"/><ellipse cx="100" cy="55" rx="22" ry="12" fill="#f5e6d3" stroke="#e8c9a0" stroke-width="2"/><circle cx="88" cy="78" r="5" fill="#2a2218"/><circle cx="112" cy="78" r="5" fill="#2a2218"/><path d="M92 90 Q100 96 108 90" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    mandu: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="82" rx="70" ry="42" fill="#f2d4a8" stroke="#c9925c" stroke-width="3"/><path d="M35 82 Q55 45 100 58 Q145 45 165 82" fill="none" stroke="#b87d45" stroke-width="2"/><ellipse cx="100" cy="100" rx="66" ry="14" fill="#7a4520" opacity="0.5"/><circle cx="85" cy="75" r="5" fill="#2a2218"/><circle cx="115" cy="75" r="5" fill="#2a2218"/></svg>`,
    wonton: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M100 30 L145 95 Q100 115 55 95 Z" fill="#f9d48a" stroke="#c9925c" stroke-width="3"/><circle cx="90" cy="72" r="5" fill="#2a2218"/><circle cx="110" cy="72" r="5" fill="#2a2218"/><path d="M94 82 Q100 88 106 82" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    shumai: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M55 95 Q100 40 145 95 Z" fill="#f5d9a8" stroke="#c9925c" stroke-width="3"/><ellipse cx="100" cy="70" rx="35" ry="22" fill="#e88a6a" stroke="#c96550" stroke-width="2"/><circle cx="92" cy="68" r="4" fill="#2a2218"/><circle cx="108" cy="68" r="4" fill="#2a2218"/></svg>`,
    "har-gow": `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="78" rx="58" ry="40" fill="#fff8f0" stroke="#e8d5c4" stroke-width="3" opacity="0.92"/><ellipse cx="100" cy="78" rx="38" ry="22" fill="#ffb4a2" opacity="0.55"/><path d="M45 78 Q70 50 100 55 Q130 50 155 78" fill="none" stroke="#d4b896" stroke-width="2"/><circle cx="88" cy="72" r="4" fill="#2a2218"/><circle cx="112" cy="72" r="4" fill="#2a2218"/></svg>`,
    momo: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><circle cx="100" cy="78" r="52" fill="#f0d4a8" stroke="#c9925c" stroke-width="3"/><path d="M55 78 Q75 35 100 42 Q125 35 145 78" fill="none" stroke="#b87d45" stroke-width="2"/><circle cx="88" cy="75" r="5" fill="#2a2218"/><circle cx="112" cy="75" r="5" fill="#2a2218"/><path d="M94 85 Q100 91 106 85" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    kreplach: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><polygon points="100,35 155,100 45,100" fill="#f5deb3" stroke="#c9925c" stroke-width="3"/><circle cx="92" cy="72" r="4" fill="#2a2218"/><circle cx="108" cy="72" r="4" fill="#2a2218"/></svg>`,
    "soup-dumpling": `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="82" rx="55" ry="42" fill="#f8eed8" stroke="#c9925c" stroke-width="3"/><path d="M50 82 Q70 48 100 52 Q130 48 150 82" fill="none" stroke="#b87d45" stroke-width="2"/><ellipse cx="100" cy="88" rx="12" ry="8" fill="#d4a574" opacity="0.4"/><circle cx="88" cy="74" r="5" fill="#2a2218"/><circle cx="112" cy="74" r="5" fill="#2a2218"/></svg>`,
    rangoon: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><path d="M60 90 Q100 35 140 90 Q100 115 60 90Z" fill="#e8b84a" stroke="#b8860b" stroke-width="3"/><circle cx="90" cy="72" r="5" fill="#2a2218"/><circle cx="110" cy="72" r="5" fill="#2a2218"/><path d="M94 82 Q100 90 106 82" fill="none" stroke="#2a2218" stroke-width="2"/></svg>`,
    fusion: `<svg viewBox="0 0 200 140" role="img" aria-hidden="true"><ellipse cx="100" cy="80" rx="60" ry="45" fill="#ffd4a8" stroke="#ff9f6b" stroke-width="3" stroke-dasharray="8 6"/><text x="100" y="88" text-anchor="middle" font-size="22" font-family="system-ui,sans-serif" fill="#2a2218">?</text><circle cx="85" cy="72" r="5" fill="#2a2218"/><circle cx="115" cy="72" r="5" fill="#2a2218"/></svg>`,
  };

  function scoreEntry(entry, wrap, filling, method) {
    let score = 0;
    if (entry.wrap.includes(wrap)) score += 3;
    else if (entry.wrap.length) score += 0;
    if (entry.filling.includes(filling)) score += 3;
    if (entry.method.includes(method)) score += 3;
    return score;
  }

  function matchDumpling(wrap, filling, method) {
    let best = null;
    let bestScore = -1;
    for (const entry of CATALOG) {
      const s = scoreEntry(entry, wrap, filling, method);
      if (s > bestScore) {
        bestScore = s;
        best = entry;
      }
    }
    const perfect = bestScore >= 9;
    return { entry: best, score: bestScore, perfect };
  }

  function labelFor(id, list) {
    return list.find((x) => x.id === id)?.label ?? id;
  }

  function renderOptions(container, items, groupName, selected) {
    container.innerHTML = items
      .map(
        (item) => `
      <button type="button" class="assembly-chip${
        selected === item.id ? " is-selected" : ""
      }" data-group="${groupName}" data-id="${item.id}" aria-pressed="${
          selected === item.id
        }">
        ${item.label}
      </button>`
      )
      .join("");
  }

  const state = { wrap: null, filling: null, method: null };

  const el = {
    wrap: document.getElementById("assembly-wrap"),
    filling: document.getElementById("assembly-filling"),
    method: document.getElementById("assembly-method"),
    path: document.getElementById("assembly-path"),
    output: document.getElementById("assembly-output"),
    art: document.getElementById("assembly-art"),
    name: document.getElementById("assembly-name"),
    region: document.getElementById("assembly-region"),
    blurb: document.getElementById("assembly-blurb"),
    hint: document.getElementById("assembly-hint"),
    map: document.getElementById("assembly-map"),
  };

  function renderMap() {
    const nodes = [
      { key: "wrap", label: "Wrap", value: state.wrap },
      { key: "filling", label: "Filling", value: state.filling },
      { key: "method", label: "Cook", value: state.method },
    ];
    el.map.innerHTML = nodes
      .map((n, i) => {
        const text = n.value
          ? labelFor(
              n.value,
              n.key === "wrap"
                ? WRAPS
                : n.key === "filling"
                  ? FILLINGS
                  : METHODS
            )
          : "…";
        const arrow =
          i < nodes.length - 1
            ? `<span class="assembly-map__arrow" aria-hidden="true">→</span>`
            : "";
        return `<div class="assembly-map__node${
          n.value ? " is-filled" : ""
        }"><span class="assembly-map__label">${n.label}</span><span class="assembly-map__value">${text}</span></div>${arrow}`;
      })
      .join("");
  }

  function renderResult() {
    const { wrap, filling, method } = state;
    renderMap();

    if (!wrap || !filling || !method) {
      el.path.textContent = "Complete all three stations to run the line.";
      el.output.classList.remove("is-ready");
      el.art.innerHTML = SVG.fusion;
      el.name.textContent = "Waiting on the line…";
      el.region.textContent = "";
      el.blurb.textContent =
        "Pick a wrap, filling, and cooking method. The conveyor will suggest a dumpling cousin from around the world.";
      el.hint.textContent = `${3 - [wrap, filling, method].filter(Boolean).length} step(s) left`;
      return;
    }

    const { entry, score, perfect } = matchDumpling(wrap, filling, method);
    const wrapL = labelFor(wrap, WRAPS);
    const fillL = labelFor(filling, FILLINGS);
    const methodL = labelFor(method, METHODS);

    el.path.textContent = `${wrapL} + ${fillL} + ${methodL}`;
    el.output.classList.add("is-ready");
    el.art.innerHTML = SVG[entry.id] ?? SVG.fusion;
    el.name.textContent = entry.name;
    el.region.textContent = entry.region;
    el.blurb.textContent = entry.blurb;
    el.hint.textContent = perfect
      ? "Classic match — this combo is canon."
      : score >= 6
        ? "Close match — real dumplings love to break rules."
        : "Wildcard build — call it fusion and serve with confidence.";
  }

  function init() {
    renderOptions(el.wrap, WRAPS, "wrap", state.wrap);
    renderOptions(el.filling, FILLINGS, "filling", state.filling);
    renderOptions(el.method, METHODS, "method", state.method);
    renderResult();

    document.querySelector(".assembly-line").addEventListener("click", (e) => {
      const btn = e.target.closest(".assembly-chip");
      if (!btn) return;
      const group = btn.dataset.group;
      const id = btn.dataset.id;
      state[group] = id;
      renderOptions(el.wrap, WRAPS, "wrap", state.wrap);
      renderOptions(el.filling, FILLINGS, "filling", state.filling);
      renderOptions(el.method, METHODS, "method", state.method);
      renderResult();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
