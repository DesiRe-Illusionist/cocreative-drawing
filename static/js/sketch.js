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

//################################################
//################################################
//SketchRNN-
let sketchRNN;
let currentStroke;
let x, y;
let nextPen = 'down';
let seedPath = [];
let seedPoints = [];
let personDrawing = false;
let RNN_AiStroke;
let RNN_ctr =0;


function preload() {
  sketchRNN = ml5.sketchRNN('everything');
}
//################################################
//################################################

function setup() {
	let myCanvas = createCanvas(600, 600);
	myCanvas.parent("canvas");
	corner=myCanvas.position();

	//################################################
	//################################################
	//SketchRNN-
	myCanvas.mousePressed(startDrawing);
  //myCanvas.mouseReleased(sketchRNNStart);
  myCanvas.mouseReleased(stopDrawing);
	//################################################
	//################################################

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
			// stroke(currentSetting.col)
			// drawingContext.shadowOffsetX = currentSetting.size + 5;
		  // drawingContext.shadowOffsetY = currentSetting.size - 5;
		  // drawingContext.shadowBlur = currentSetting.size + 10;
		  // drawingContext.shadowColor = 'black';
		}
		else{
			stroke(agentSetting.col);
		}

		for (var i = 0; i < aiTurn.length; i++) {
			if (aiTurn[i].length > 1) {
				for (var j = 1; j < aiTurn[i].length; j++) {
					line(aiTurn[i][j-1][0], aiTurn[i][j-1][1], aiTurn[i][j][0], aiTurn[i][j][1])

					// if (transformation == 'verthatch') {
					// 	strokeWeight(2);
					// 	stroke(currentSetting.col)
					// 	line(aiTurn[i][j][0], aiTurn[i][j][1],aiTurn[i][j][0], aiTurn[i][j][1] + 20)
					// }
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
		// txtIntroOptions=['How about if we ','What if I ','Let me take what you did and ',"I see what you did there. Let me "];
		// txtIntro = txtIntroOptions[Math.floor(Math.random()*txtIntroOptions.length)];
		if (['rotate','shift','reflect','scale'].includes(transformation)) {
			// txtStr=txtIntro + transformation + ' it.';
		}
		else if (transformation == 'shadow') {
			// txtStr="Let's try adding a shadow.";
		}
		else if (transformation == 'verthatch') {
			// txtStr="How about some vertical hatching?"
		} else {
			txtStr = transformation + " " + usrAction
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

	//################################################
	//################################################
	//SketchRNN-
	if (personDrawing) {
		stroke(currentSetting.col);
	  strokeWeight(currentSetting.size);
    noFill();
		line(mouseX, mouseY, pmouseX, pmouseY);
		seedPoints.push(createVector(mouseX, mouseY));
	 }

	if (currentStroke) {
		stroke(agentSetting.col);
	  strokeWeight(agentSetting.size);
    noFill();

		let noOfStroke = random (10,25);
		if (RNN_ctr <noOfStroke){
			if (nextPen == 'end') {
	 		 //sketchRNN.reset();
	 		 //sketchRNNStart();
	 		 currentStroke = null;
	 		 noLoop();
	 		 nextPen = 'down';
	 		 return;
	 	 }

	 	if (nextPen == 'down') {
			line(x, y, x + currentStroke.dx, y + currentStroke.dy);
	 	}
	 		x += currentStroke.dx;
	 		y += currentStroke.dy;
	 		nextPen = currentStroke.pen;
	 		currentStroke = null;
	 		sketchRNN.generate(gotStrokePath);

			RNN_ctr += 1;
		}
		else{
			//personDrawing = true;
			seedPoints = [];
			RNN_ctr = 0;
			RNN_AiStroke = currentStroke;
			currentStroke = null;
			sketchRNN.reset();
		}
	}
	//################################################
	//################################################
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

//Triggered by finish button on the interface!
finishTurn = () => {
	const radiobtns = document.querySelectorAll('input[name="AgentChoice"]');
  let selectedAgent;
  for (const rb of radiobtns) {
      if (rb.checked) {
          selectedAgent = rb.value;
          break;
      }
  }
	if (selectedAgent == "Rule") {
		console.log("you selected - ",selectedAgent);

		playerTurn = false;
		turnNum += 1;
		if (txtDiv) {
			txtDiv.remove();
		}

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

		console.log("postData",postData);

		// http://127.0.0.1:5000/draw
		// "https://artifex-backend.herokuapp.com/draw"

		httpPost(
			"http://127.0.0.1:5000/draw",
			"json",
			postData,
			(response) => {
				console.log(response)
				aiTurn = response.data;
				transformation = response.transformation;
				usrAction = response.usr_action
			});

	}
	else if (selectedAgent == "SketchRNN-QD") {
		console.log("you selected - ",selectedAgent);
		sketchRNNStart();
	}
	else {
		console.log("you selected - ",selectedAgent);
    let postData2 = {
			"stroke" : curTurn
		}
    httpPost(
			"http://127.0.0.1:5000/drawRNN",
			"json",
			postData2,
			(response) => {
				console.log(response)
				aiTurn = response.data;
				transformation = response.transformation;
				usrAction = response.usr_action
			});
	}
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

//################################################
//################################################
//SketchRNN-Functions
function startDrawing() {
  personDrawing = true;
  x = mouseX;
  y = mouseY;
}

function stopDrawing() {
  personDrawing = false;
  x = mouseX;
  y = mouseY;
}

function sketchRNNStart() {
  personDrawing = false;

  // Perform RDP Line Simplication
  const rdpPoints = [];
  const total = seedPoints.length;
  const start = seedPoints[0];
  const end = seedPoints[total - 1];
  rdpPoints.push(start);
  rdp(0, total - 1, seedPoints, rdpPoints);
  rdpPoints.push(end);

  // Drawing simplified path
  //background(255);
  stroke(currentSetting.col);
  strokeWeight(currentSetting.size);
  beginShape();
	//let c = color(random(0,255),random(0,255),random(0,255));
	//c.setAlpha(50);
	//fill(c);
  noFill();
  for (let v of rdpPoints) {
    vertex(v.x, v.y);
  }
  endShape();

  x = rdpPoints[rdpPoints.length - 1].x;
  y = rdpPoints[rdpPoints.length - 1].y;

  seedPath = [];
  // Converting to SketchRNN states
  for (let i = 1; i < rdpPoints.length; i++) {
    let strokePath = {
      dx: rdpPoints[i].x - rdpPoints[i - 1].x,
      dy: rdpPoints[i].y - rdpPoints[i - 1].y,
      pen: 'down'
    };
    seedPath.push(strokePath);
  }

  sketchRNN.generate(seedPath, gotStrokePath);
}


function gotStrokePath(error, strokePath) {
  currentStroke = strokePath;
}
//################################################
//################################################
