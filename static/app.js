async function go(){
  const sub=document.getElementById('sub').value.trim().replace(/^r\//,'');
  const limit=document.getElementById('limit').value||150;
  const maxw=document.getElementById('maxw').value||300;
  const sort=document.getElementById('sort').value;
  const timef=document.getElementById('timef').value;
  const cmap=document.getElementById('cmap').value;
  const bg=document.getElementById('bg').value;

  const list=document.getElementById('list');
  const img=document.getElementById('img');
  const dl=document.getElementById('dl');

  if(!sub){alert('Please enter a subreddit');return;}

  list.innerHTML='<li class="loading">Loading...</li>';
  img.src=''; dl.innerHTML='';

  try{
    img.src='/cloud?sub='+encodeURIComponent(sub)
           +'&limit='+limit+'&max_words='+maxw
           +'&sort='+sort+'&time_filter='+timef
           +'&colormap='+cmap+'&bg='+bg
           +'&_='+Date.now();

    dl.innerHTML='<a href="'+img.src+'" download="cloud_'+sub+'.png">⬇ Download PNG</a>';

    const r=await fetch('/top?sub='+encodeURIComponent(sub)
                        +'&limit='+limit
                        +'&sort='+sort
                        +'&time_filter='+timef);
    const data=await r.json();
    if(data.error){list.innerHTML='<li class="loading">'+data.error+'</li>';return;}
    list.innerHTML='';
    (data||[]).forEach(x=>{
      const li=document.createElement('li');
      li.textContent=x.term+" ("+x.count+")";
      list.appendChild(li);
    });
  }catch(err){
    list.innerHTML='<li class="loading">Failed to load.</li>';
  }
}
