let ac,an,src;
function visStart(){if(ac)return;ac=new (window.AudioContext||window.webkitAudioContext)();an=ac.createAnalyser();an.fftSize=256;let a=document.getElementById("radioAudio");if(!a)a=document.getElementById("sunoAudio");src=ac.createMediaElementSource(a);src.connect(an);an.connect(ac.destination);}
function vis(){if(!an)return;let d=new Uint8Array(an.frequencyBinCount);an.getByteFrequencyData(d);let avg=d.reduce((x,y)=>x+y,0)/d.length;window.GEMIVAS_BEAT=avg/255;requestAnimationFrame(vis)}
document.addEventListener("click",()=>{visStart();vis();},{once:true});
