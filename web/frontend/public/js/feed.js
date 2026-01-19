console.log("FEEDJS LOADED v=208");
(function () {
  let video = document.getElementById('video');
  const vTitle = document.getElementById('vTitle');
  const vTags = document.getElementById('vTags');

  let items = [];
  let idx = 0;
  let wheelLock = false;

  function dbg(m){ const d=document.getElementById("dbg"); if(d) d.textContent=m; }

  video.addEventListener("loadedmetadata", ()=>dbg("DBG: metadata "+video.videoWidth+"x"+video.videoHeight+" dur="+video.duration));
  video.addEventListener("canplay", ()=>dbg("DBG: canplay "+video.currentSrc+" paused="+video.paused));
  setInterval(()=>{dbg("DBG: t="+video.currentTime.toFixed(1)+" paused="+video.paused+" size="+video.videoWidth+"x"+video.videoHeight);}, 800);
  video.addEventListener("error", ()=>dbg("DBG: ERROR code="+(video.error?video.error.code:"?")+" src="+video.currentSrc));

  async function loadFeed() {
    const r = await fetch('/api/feed?_=' + Date.now());
    const j = await r.json();
    items = (j.items || []).filter(x => x && x.url);
    const dbg=document.getElementById("dbg"); if(dbg) dbg.textContent="DBG: items="+items.length;
  }

  function preloadNext(nextIndex) {
    if (!items.length) return;
    const it = items[nextIndex % items.length];
    if (!it || !it.url) return;
    const link = document.createElement("link");
    link.rel = "preload";
    link.as = "video";
    link.href = it.url;
    document.head.appendChild(link);
  }

  function render(i) {
    if (!items.length) return;
    const it = items[i];
    if (!it || !it.url) return;

    try { video.pause(); } catch(e) {}

      const old = video;
      const nv = old.cloneNode(false);
      nv.muted = true;
      nv.setAttribute("muted","");
      nv.playsInline = true;
      nv.setAttribute("playsinline","");
      nv.autoplay = true;
      nv.preload = "auto";

      const sep = it.url.includes("?") ? "&" : "?";
      const src = it.url + sep + "v=" + Date.now();
      nv.src = src; nv.load(); console.log("RENDER", i, it.id, src); dbg("DBG: render i="+i+" id="+it.id+" src="+src);

      old.replaceWith(nv);
      video = nv;

    try { video.currentTime = 0; } catch(e) {}
    if (vTitle) vTitle.textContent = it.title || "";
    if (vTags) vTags.textContent = (it.tags || []).map(t => "#"+t).join(" ");    const p = video.play();
    if (p && p.catch) p.catch((e)=>{console.log("PLAY FAIL", e); dbg("DBG: play fail "+e);});

      // preloadNext disabled for debug
    }


    function next() {
    if (!items.length) return;
    idx = (idx + 1) % items.length;
    render(idx);
  }

  function prev() {
    if (!items.length) return;
    idx = (idx - 1 + items.length) % items.length;
    render(idx);
  }

  function onWheel(e) {
    if (wheelLock) return;
    wheelLock = true;

    if (e.deltaY > 0) next();
    else prev();

    setTimeout(() => { wheelLock = false; }, 350);
  }

  window.addEventListener('wheel', onWheel, { passive: true });

  // Touch swipe
  let touchY = null;
  window.addEventListener('touchstart', (e) => {
    touchY = e.touches && e.touches[0] ? e.touches[0].clientY : null;
  }, { passive: true });

  window.addEventListener('touchend', (e) => {
    if (touchY === null) return;
    const y2 = e.changedTouches && e.changedTouches[0] ? e.changedTouches[0].clientY : null;
    if (y2 === null) return;

    const dy = y2 - touchY;
    if (Math.abs(dy) < 40) return;

    if (dy < 0) next();
    else prev();

    touchY = null;
  }, { passive: true });

  // Buttons
  const btnLike = document.getElementById('btnLike');
  const btnShare = document.getElementById('btnShare');
  const btnSave = document.getElementById('btnSave');

  if (btnLike) btnLike.onclick = () => console.log('LIKE', items[idx]?.id);
  if (btnSave) btnSave.onclick = () => console.log('SAVE', items[idx]?.id);
  if (btnShare) btnShare.onclick = async () => {
    const url = location.href;
    try {
      await navigator.clipboard.writeText(url);
      console.log('SHARE copied', url);
    } catch(e) {
      console.log('SHARE', url);
    }
  };
  'use strict';
(async function init() {
  const dbg=document.getElementById('dbg'); if(dbg) dbg.textContent='DBG: js loaded';
    await loadFeed();
    if (!items.length) {
      if (vTitle) vTitle.textContent = 'No videos in feed';
      return;
    }
    render(idx);
  })();
})();
