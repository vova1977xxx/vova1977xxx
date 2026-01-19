async function lifeTick(){try{let j=await fetch("/data/life.json?"+Date.now()).then(r=>r.json());window.GEMIVAS_LIFE=j;let e=document.getElementById("lifeText");if(e)e.textContent=j.text||"";}catch(e){}}
setInterval(lifeTick,10000);document.addEventListener("DOMContentLoaded",lifeTick);
