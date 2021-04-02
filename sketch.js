let button;
let curTurn;
let curStroke;
let aiTurn;
let txtDiv;
let prevCanvas;
let curCanvas;
let turnNum;
let prevCanvasBase64;
let curCanvasBase64;
let sessionId;

function setup() {
	let myCanvas = createCanvas(600, 600);
	myCanvas.parent("canvas");
	corner=myCanvas.position();

	button = createButton('CLEAR');
	button.center();
	button.style('margin-top', '45vh');
	button.mousePressed(() => {
		background(255);
	});

	background(255);

	currentSetting = {
		size: 5,
		col: color(0, 0, 0, 255)
	}

	agentSetting = {
		size: 5,
		col: color(150, 0, 0, 255)
	}

	turnNum = 0;
	curTurn = [];
	curStroke = [];
	aiTurn = [];
	sessionId = uuidv4();
	prevCanvas = document.getElementById("defaultCanvas0");
	prevCanvasBase64 = new Image();
	prevCanvasBase64 = prevCanvas.toDataURL();
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

		noFill();
		strokeWeight(currentSetting.size);

		if (transformation=='shadow'){
			stroke(currentSetting.col)
			drawingContext.shadowOffsetX = currentSetting.size + 5;
		  drawingContext.shadowOffsetY = currentSetting.size - 5;
		  drawingContext.shadowBlur = currentSetting.size + 10;
		  drawingContext.shadowColor = 'black';
		}
		else{
			stroke(agentSetting.col);
		}

		for (var i = 0; i < aiTurn.length; i++) {
			if (aiTurn[i].length > 1) {
				for (var j = 1; j < aiTurn[i].length; j++) {
					line(aiTurn[i][j-1][0], aiTurn[i][j-1][1], aiTurn[i][j][0], aiTurn[i][j][1])

					if (transformation == 'verthatch') {
						strokeWeight(2);
						stroke(currentSetting.col)
						line(aiTurn[i][j][0], aiTurn[i][j][1],aiTurn[i][j][0], aiTurn[i][j][1] + 20)
					}
				}
			}
		}

		prevCanvasBase64 = document.getElementById("defaultCanvas0").toDataURL();

		aiTurn = [];
		curTurn=[];
		textSize(24);
		fill(0);
		strokeWeight(0);
		console.log(transformation);
		txtIntroOptions=['How about if we ','What if I ','Let me take what you did and ',"I see what you did there. Let me "];
		txtIntro = txtIntroOptions[Math.floor(Math.random()*txtIntroOptions.length)];
		if (['rotate','shift','reflect','scale'].includes(transformation)) {
			txtStr=txtIntro + transformation + ' it.';
		}
		else if (transformation == 'shadow') {
			txtStr="Let's try adding a shadow.";
		}
		else if (transformation == 'verthatch') {
			txtStr="How about some vertical hatching?"
		}
		txtDiv = createDiv(txtStr);
		txtDiv.parent("canvas");
		txtDiv.position(corner.x + 10, corner.y - 30);
		txtDiv.style('font=size','24px');
		txtDiv.style('color','black');
	}
	drawingContext.shadowOffsetX = 0;
	drawingContext.shadowOffsetY = 0;
	drawingContext.shadowBlur = 0;
}

function mouseReleased() {
	if (curStroke.length > 0) {
		curTurn.push(curStroke);
		curStroke = [];
	}
	if (document.getElementById('txtDiv')) {
		txtDiv.remove();
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
	playerTurn = false;
	turnNum += 1;

	curCanvas = document.getElementById("defaultCanvas0");
	curCanvasBase64 = new Image();
	curCanvasBase64 = curCanvas.toDataURL();
	
	let postData = {
		"session_id" : sessionId,
		"current_turn_number" : turnNum,
		"width" : width,
		"height" : height,
		"stroke" : curTurn,
		"current_canvas" : curCanvasBase64,
		"previous_canvas" : prevCanvasBase64
	}

	// prevCanvasBase64 = curCanvasBase64;

	httpPost(
		"http://127.0.0.1:8000/draw",
		"json",
		postData,
		(response) => {
			aiTurn = response.data;
			transformation = response.transformation;
		});
  }

changeColor = newCol => {
	col = newCol;
}

function uuidv4() {
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
	  var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
	  return v.toString(16);
	});
  }
