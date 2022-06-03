function addImage(canvasId, path, keypoints, bbox){
  var canvas = document.getElementById(canvasId);

  canvas.style["display"] = "inline";
  canvas.style["background"] = `url(static/images/test1.jpeg)`;
  canvas.style["background-position"] = "-" + bbox[0].toString() + "px -" + bbox[1].toString() + "px";
  canvas.style["width"] = bbox[2].toString() + 'px';
  canvas.style["height"] = bbox[3].toString() + 'px';
  canvas.style["background-repeat"] = 'no-repeat';

  var ctx = canvas.getContext("2d");

  ctx.moveTo(0, 0);
  ctx.lineTo(200, 100);
  ctx.stroke();

  ctx.moveTo(100, 0);
  ctx.lineTo(200, 100);
  ctx.stroke();
}

function addFrameGroup(frame_id, path, keypoints){
  id1 = frame_id.toString() + "1";
  id2 = frame_id.toString() + "2";
  id3 = frame_id.toString() + "3";
  carousel_id = "carousel" + frame_id.toString();
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
  document.getElementById('imageArea').innerHTML +=base_html;
}

function loadData(images, keypoints, bbox){
  document.getElementById('imageArea').innerHTML = "";
  for (let i = 0; i < images.length; i++) {
    addFrameGroup("frame" + i.toString(), images[i],keypoints[i]);
  }
  for (let i = 0; i < images.length; i++) {
    addImage("frame" + i.toString() + "1", images[i][0], keypoints[i][0], bbox[i][0]);
    addImage("frame" + i.toString() + "2", images[i][1], keypoints[i][1], bbox[i][1]);
    addImage("frame" + i.toString() + "3", images[i][2], keypoints[i][2], bbox[i][2]);
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

httpPost.onreadystatechange = function(err) {
    if (httpPost.readyState == 4 && httpPost.status == 200){
        const data = httpPost.response;
        loadData(data['images'],data['keypoints'], data['bbox']);
    } else {
        console.log(err);
    }
  };
};

function searchClicked(){
  var group = document.getElementsByClassName("form-check-input");
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