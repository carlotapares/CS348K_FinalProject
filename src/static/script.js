function addImage(canvasId, path, keypoints, bbox){
  var canvas = document.getElementById(canvasId);
  var ctx = canvas.getContext("2d");

  canvas.setAttribute("width", 200);
  canvas.setAttribute("height",300);

  canvas.style["display"] = "inline";
  const image = new Image();
  image.src = "./static/dataset/frames/thumb" + path + ".png";
  image.style.width = 'auto';
  image.style.height = '300px';
  image.addEventListener('load', render);

  function render() {
    const newx = (200 - bbox[2])/2;
    const newy = (300 - bbox[3])/2;

    ctx.drawImage(image,bbox[0]-newx,bbox[1]-newy,canvas.width,canvas.height,0,0,canvas.width,canvas.height);

    for (let i = 0; i < keypoints.length; i++){
      if (i > 0) ctx.beginPath();
      k = keypoints[i];
      ctx.moveTo(k[0]+newx, k[1]+newy);
      ctx.lineTo(k[2]+newx, k[3]+newy);
      ctx.lineWidth = 2;
      ctx.strokeStyle = `rgb(${Math.floor(255 * k[4][0])},${Math.floor(255 * k[4][1])},${Math.floor(255 * k[4][2])})`
      ctx.stroke();
    }
    ctx.font = '12px sans-serif';
    ctx.fillText('Frame: ' + path, 10, 20);
  }
}

function addFrameGroup(frame_id, areaId){
  id1 = frame_id.toString() + "1_" + areaId;
  id2 = frame_id.toString() + "2_" + areaId;
  id3 = frame_id.toString() + "3_" + areaId;
  carousel_id = "carousel" + frame_id.toString() + "_" + areaId;
  carousel_href = "#" + carousel_id;

  const exists = document.getElementById(id1);
  if (exists != null) return;

  const base_html = `
  <div class="col">
      <div class="card mb-3" style="border: 0px; width=auto !important">
          <div id=${carousel_id} class="carousel" data-ride="carousel" data-interval="false">
              <div class="carousel-inner">
                  <div class="carousel-item">
                      <canvas id=${id1} style="display: none;"></canvas>
                  </div>
                  <div class="carousel-item active">
                      <canvas id=${id2} style="display: none;"></canvas>
                  </div>
                  <div class="carousel-item">
                      <canvas id=${id3} style="display: none;"></canvas>
                  </div>
              </div>
              <a class="carousel-control-prev" href=${carousel_href} role="button" data-slide="prev">
                  <span class="carousel-control-prev-icon" aria-hidden="true"></span>
              </a>
              <a class="carousel-control-next" href=${carousel_href} role="button" data-slide="next">
                  <span class="carousel-control-next-icon" aria-hidden="true"></span>
              </a>
          </div>
      </div>
  </div>
  `;
  document.getElementById(areaId).innerHTML +=base_html;
}

function loadData(images, keypoints, bbox, areaId){
  for (let i = 0; i < images.length; i++) {
    addFrameGroup("frame" + i.toString(), areaId);
  }
  for (let i = 0; i < images.length; i++) {
    addImage("frame" + i.toString() + "1_" + areaId, images[i][0], keypoints[i][0], bbox[i][0]);
    addImage("frame" + i.toString() + "2_" + areaId, images[i][1], keypoints[i][1], bbox[i][1]);
    addImage("frame" + i.toString() + "3_" + areaId, images[i][2], keypoints[i][2], bbox[i][2]);
  }
}

function decode(html) {
  var txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

function sendSelectionToServer(checkbox, batches, frames){
var httpPost = new XMLHttpRequest(),
path = "http://localhost:5000/search",
data = JSON.stringify({checkbox: checkbox, batches: batches, frames: frames});
httpPost.responseType = 'json';
httpPost.open("POST", path, true);
httpPost.setRequestHeader('Content-Type', 'application/json');
httpPost.send(data);
document.getElementById("imageArea").innerHTML = "";

httpPost.onreadystatechange = function(err) {
    if (httpPost.readyState == 4 && httpPost.status == 200){
        const data = httpPost.response;
        loadData(data['images'],data['keypoints'], data['bbox'], "imageArea");
    } else {
        console.log(err);
    }
  };
};

function searchClicked(){
  var group = document.getElementsByClassName("check_exp");
  var checkbox = []
  for (let i = 0; i < group.length; i++){
    if (group[i].checked == true){
      checkbox.push(group[i].value);
    }
  }
  var batches = document.getElementById('batchRange').value;
  var frames = document.getElementById('frameRange').value;
  sendSelectionToServer(checkbox, batches, frames);
}

function change_tab(tab){
  if (tab == "exploration"){
    document.getElementById("exploration").className = "nav-link active";
    document.getElementById("assertions").className = "nav-link";
    document.getElementById("exploration_content").className = "container-fluid" 
    document.getElementById("assertions_content").className = "container-fluid hidden_content" 
  } 
  else {
    document.getElementById("assertions").className = "nav-link active";
    document.getElementById("exploration").className = "nav-link";
    document.getElementById("exploration_content").className = "container-fluid hidden_content" 
    document.getElementById("assertions_content").className = "container-fluid" 
  }
}

const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: {
        name: "python",
        version: 3,
        singleLineStringErrors: false
    },
    lineNumbers: true,
    indentUnit: 4,
    matchBrackets: true
});

editor.setSize(null,150);

function checkClicked(){
  var assertions = editor.getValue();
  var group = document.getElementsByClassName("check_asst");
  var checkbox = []
  for (let i = 0; i < group.length; i++){
    if (group[i].checked == true){
      checkbox.push(group[i].value);
    }
  }
  sendAssertionsToServer(assertions, checkbox);
}

function sendAssertionsToServer(assertions, checkbox){
  var httpPost = new XMLHttpRequest(),
  path = "http://localhost:5000/check",
  data = JSON.stringify({assertions: assertions, checkbox: checkbox});
  httpPost.responseType = 'json';
  httpPost.open("POST", path, true);
  httpPost.setRequestHeader('Content-Type', 'application/json');
  httpPost.send(data);

  document.getElementById("imageAreaAssertions").innerHTML = "";
  document.getElementById("loadSpinner").className = "spinner-border"
  
  httpPost.onreadystatechange = function(err) {
    if (httpPost.readyState == 4 && httpPost.status == 200){
      document.getElementById("loadSpinner").className = "spinner-border hidden_content"
      const data = httpPost.response;
      console.log(data);
      const err = data['error']
      if (err == true){
        document.getElementById('asst_syntax').className = "alert alert-warning alert-dismissible fade show";
        return;
      }
      if (data["images"].length == 0){
        document.getElementById('asst_empty').className = "alert alert-warning alert-dismissible fade show";
        return;
      }

      loadData(data['images'],data['keypoints'], data['bbox'], "imageAreaAssertions");
    } else {
        console.log(err);
    }
  };
};

function hideAlert(){
  document.getElementById('asst_syntax').className = "alert alert-warning alert-dismissible fade show hidden_content";
  document.getElementById('asst_empty').className = "alert alert-warning alert-dismissible fade show hidden_content";
}



  