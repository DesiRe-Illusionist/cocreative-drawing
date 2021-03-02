let clearButton;
let sketchRNN;
let currentStroke;
let x, y;
let nextPen = 'down';
let seedPath = [];
let seedPoints = [];
let personDrawing = false;
let AiStroke;

let ctr =0;


function preload() {
  sketchRNN = ml5.sketchRNN('everything');
}


function setup() {
	let myCanvas = createCanvas(600, 600);
	myCanvas.parent("canvas");

	myCanvas.mousePressed(startDrawing);
  myCanvas.mouseReleased(sketchRNNStart);

	clearButton = createButton('CLEAR');
	clearButton.center();
	clearButton.style('margin-top', '45vh');
	clearButton.mousePressed(() => {
		background(255);
	});

	background(255);

	currentSetting = {
		size: 2,
		col: color(0, 0, 0)
	}

	agentSetting = {
		size: 2,
		col: color(150, 0, 0)
	}

}


function startDrawing() {
  personDrawing = true;
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
  background(255,5);
  //stroke(agentSetting.col);
  //strokeWeight(agentSetting.size);
  beginShape();
	let c = color(random(0,255),random(0,255),random(0,255));
	c.setAlpha(50);
	fill(c);
  //noFill();
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

function draw() {
	//stroke(0);
 	//strokeWeight(4);

	if (personDrawing) {
		stroke(currentSetting.col);
	  strokeWeight(currentSetting.size);
		line(mouseX, mouseY, pmouseX, pmouseY);
		seedPoints.push(createVector(mouseX, mouseY));
	 }

	if (currentStroke) {
		stroke(agentSetting.col);
	  strokeWeight(agentSetting.size);

		let noOfStroke = random (2,10);
		if (ctr < noOfStroke){
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

			ctr += 1;
		}
		else{
			//personDrawing = true;
			seedPoints = [];
			ctr = 0;
			AiStroke = currentStroke;
			currentStroke = null;
			sketchRNN.reset();
		}



	}

}

// function isInsideCanvas(x, y) {
// 	if (x >= 0 && x <= width && y >= 0 && y <= height) {
// 		return true;
// 	} else {
// 		return false;
// 	}
// }
//
// finishTurn = () => {
//
// 	console.log(curTurn);
// 	playerTurn = false;
//
// 	let postData = {
// 		"data" : curTurn,
// 		"width" : width,
// 		"height" : height
// 	}
//
// 	httpPost(
// 		"http://127.0.0.1:8000/draw",
// 		"json",
// 		postData,
// 		(response) => {
// 			aiTurn = response.data;
// 		});
//   }
//
// changeColor = newCol => {
// 	col = newCol;
// }
