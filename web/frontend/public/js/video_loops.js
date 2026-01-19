function setLoopVideo(name){
  var el = document.getElementById("gemivasPlayer");
  if(!el) return;

  var url = "/video_8k/loops/" + name + ".mp4";

  try{
    if(window.videojs){
      var pl = videojs("gemivasPlayer");
      pl.loop(true);
      pl.src({src:url, type:"video/mp4"});
      pl.play();
      return;
    }
  }catch(e){}

  el.loop = true;
  el.src = url;
  el.load();
  el.play();
}
