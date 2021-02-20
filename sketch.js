let button;
let curTurn;
let curStroke;
let aiTurn;

function setup() {
	let myCanvas = createCanvas(600, 600);
	myCanvas.parent("canvas");

	button = createButton('CLEAR');
	button.center();
	button.style('margin-top', '45vh');
	button.mousePressed(() => {
		background(255);
	});

	background(255);

	currentSetting = {
		size: 20,
		col: color(0, 0, 0, 150)
	}

	agentSetting = {
		size: 20,
		col: color(150, 0, 0, 150)
	}

	curTurn = [];
	curStroke = [];
	aiTurn = [];
}

function draw() {

	if (aiTurn.length == 0) {
		if (mouseIsPressed && isInsideCanvas(mouseX, mouseY)) {
			stroke(currentSetting.col);
			noFill();
			strokeWeight(currentSetting.size);
			line(pmouseX, pmouseY, mouseX, mouseY);
			curStroke.push([mouseX, mouseY]);
		}
	} else {
		stroke(agentSetting.col);
		noFill();
		strokeWeight(agentSetting.size);

		for (var i = 0; i < aiTurn.length; i++) {
			if (aiTurn[i].length > 1) {
				for (var j = 1; j < aiTurn[i].length; j++) {
					console.log(aiTurn[i][j-1][0].toString(), aiTurn[i][j-1][1].toString(), aiTurn[i][j][0].toString(), aiTurn[i][j][1].toString())
					line(aiTurn[i][j-1][0], aiTurn[i][j-1][1], aiTurn[i][j][0], aiTurn[i][j][1])
				}
			}
		}

		aiTurn = [];
	}
}

function mouseReleased() {
	if (curStroke.length > 0) {
		curTurn.push(curStroke);
		curStroke = [];
	}
}

function isInsideCanvas(x, y) {
	if (x >= 0 && x <= width && y >= 0 && y <= height) {
		return true;
	} else {
		return false;
	}
}

finishTurn = () => {

	console.log(curTurn);
	playerTurn = false;

	let postData = {
		"data" : curTurn,
		"width" : width,
		"height" : height
	}

	// httpPost(
	// 	"http://127.0.0.1:8000/draw", 
	// 	"json", 
	// 	postData,
	// 	(response) => {
	// 		aiTurn = response.data;
	// 	});
	

	//1.get canvas data: defaultCanvas0 is the actual Canvas id	
	let getCanvas=document.getElementById("defaultCanvas0");
	let canvasimg;
	if(getCanvas)
	{
		canvasimg=getCanvas.toDataURL("image/png");
	}

	//2.model request
	const model = new rw.HostedModel({
		url: "https://spade-coco-357d9ca4.hosted-models.runwayml.cloud/v1/",
		token: "nryMnMAdZutcSE91fgzo9w==",
	});
	const inputs = {
	     "semantic_map": canvasimg
	};
	model.query(inputs).then(outputs => {
	    const { output } = outputs;
		
		//3. print output to screen
		let image = new Image();
		image.src = output;
		let img_location=document.getElementById("img_output");
		img_location.innerHTML="";
		image.style.width="600px";
		image.style.height="600px";
		img_location.appendChild(image);

	});
	
  }

changeColor = newCol => {
	col = newCol;
}