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

let transformation;
let usrAction;

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
let displayMsg = false;


function preload() {
  sketchRNN = ml5.sketchRNN('everything');
}
//################################################
//################################################

function setup() {
	let myCanvas = createCanvas(600, 600);
	myCanvas.parent("canvas");
	corner=myCanvas.position();

	pencilPicked = false;

	//################################################
	//################################################
	//SketchRNN-
	myCanvas.mousePressed(startDrawing);
  //myCanvas.mouseReleased(sketchRNNStart);
  myCanvas.mouseReleased(stopDrawing);
	//################################################
	//################################################

	button = createButton('CLEAR');
	button.parent('#clearButtonDiv');
	button.mousePressed(() => {
		$('#dialogue').css('display', 'none');
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
		if (mouseIsPressed && isInsideCanvas(mouseX, mouseY) && pencilPicked) {
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
		console.log('transformation=',transformation);
    console.log('usrAction=',usrAction);

    //***code shifted to line 254 to 280
    // //sketch RNN based on quick draw-
    // if (usrAction == "sketchRNN-QD Selected") {
    //   options = ["Let me just add something to what you just drew.",
    //           "I love that! Let me just extend what you did.",
    //           "We're totally sympatico. I like this whole drawing together thing.",
    //           "I'm basically the best octopus artist I know",
    //           "That looks awesome! How about if I add this?",
    //           "I've seen some doodles that used shapes kind of like this",
    //           "If you're not loving the doodly style I'm using, just choose a different option on your next turn!",
    //           "My training tells me this would fit well with what you drew.",
    //           "I got this idea from all the sketches and doodles I've been looking at lately."];
    //   txtStr = options[Math.floor(Math.random()*options.length)];
    // }

    //sketch RNN based on abstract art
  	if (usrAction == "sketchRNN-Artist Selected"){
  			//if (agent returns something){
  				options = ["Based on what I've learned about shapes and lines in abstract art, I thought this would look good.",
  				"The contours of some paintings I've seen looked something like this.",
  				"OK so it doesn't look EXACTLY like an abstract painting, but these are sorts of shapes and lines I've seen in those paintings.",
  				"I'm just gonna go crazy and try something here.",
  				"I thought this would look AMAZING.",
  				"Here's something I decided to add based on my training in abstract art.",
  				"After looking at sooo many abstract paintings, I think I'm getting the hang of this whole art thing.",
  				"Do you like the abstract drawing style I'm using? If not, just try another option! It won't hurt my feelings."];
  			//}
  			//else {
  			//	options=["I like what you drew so much, I'm not going to add anything to it. Why don't you take another turn?",
  			//						"I'm not really sure what to do next. I think you should take another turn"];
  			//}
  			txtStr = options[Math.floor(Math.random()*options.length)];
  	}


    //text responses for the rule based agent
		else {
  		txt1="";
  		txt2="";
  		if (usrAction == 'add_to_existing'){
  			txt1="Looks like you added something to a shape that was already there. You're so creative!";

  			if (transformation == 'enclose_updated') {
  				txt2 = "I'm just gonna draw a big shape around that whole thing.";
  			}
  		}
  		else if (usrAction == 'connect_existing'){
  			txt1="I like how you connected those things together! ";
  			if (transformation == 'enclose_updated') {
  				txt2 = "You're really good at this whole art thing. I'll enclose them together to really emphasize that connection.";
  			}
  			else if (transformation == 'strengthen connection') {
  				txt2 = "I'm gonna make that connection SO STRONG.";
  			}
  		}
  		else if (usrAction == 'added_new_closed_object'){
  			txt1="Based on the rules I learned from my very smart teachers, I think you drew a closed shape.";
  			if (transformation == 'scale_in_place') {
  				txt2 = "I haven't really learned how to draw something new yet, so I'll copy yours and just make it a different size.";
  			}
  			else if (transformation == 'divide closure') {
  				txt2 = "I think I'll divide it up.";
  			}
  		}
  		else if (usrAction == 'added_new_open_object'){
  			txt1="My teachers taught me this is an open shape.";
  			if (transformation == 'close shape') {
  				txt2 = "I'll complete it to make it a closed shape. If I got that right, I'm going to feel super smart.";
  			}
  			else if (transformation == 'distort') {
  				txt2 = "I can't come up with my own new ideas yet, but I can take what you drew and distort it.";
  			}
  		}
  		else if (usrAction == 'added_new_complex_object'){
  			txt1='That one is interesting and kind of complex.';
  			if (transformation == 'shift') {
  				txt2 = "I'm not really sure what to do with that, so I'll just draw the same thing over here.";
  			}
  			else if (transformation == 'enclose') {
  				txt2 = "It looks really cool and I don't want to mess with it, so I'll just draw something around it.";
  			}
  		}

  		else if (usrAction == 'added_new_object_and_existing'){
  			txt1='My training tells me you added something new and also added to an existing shape.';
  			txt2="That's so many things at once, I don't even know what to do. I'll just draw something around it.";
  		}
  		else if (usrAction == 'added_multiple_objects'){
  			txt1='Whoa, you added several new things! You have so many good ideas.';
  			if (transformation == 'enclose_updated') {
  				txt2 = "Let me just draw something around this part.";
  			}
  			if (transformation == 'connect_components' | transformation == 'connect components') {
  				txt2 = "I decided to connect them because, like, everything is connected, man.";
  			}
  		}
  		txtStr = txt1 + " " + txt2;
  		//any rule based conditions we haven't accounted for
  		if (txt1 == "" | txt2 == "") {
  			txtStr = "I don't even know what I'm doing right now, I'm just trying stuff out."
  		}
    }



		txtDiv = createDiv(txtStr);
		txtDiv.id('dialogue');
		txtDiv.parent("#bubble");
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
    //$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    //$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    //text feeddback
    //sketch RNN based on quick draw
    if (displayMsg == true) {
      console.log('transformation=',transformation);
      console.log('usrAction=',usrAction);

      if (usrAction == "sketchRNN-QD Selected") {
        options = ["Let me just add something to what you just drew.",
                "I love that! Let me just extend what you did.",
                "We're totally sympatico. I like this whole drawing together thing.",
                "I'm basically the best octopus artist I know",
                "That looks awesome! How about if I add this?",
                "I've seen some doodles that used shapes kind of like this",
                "If you're not loving the doodly style I'm using, just choose a different option on your next turn!",
                "My training tells me this would fit well with what you drew.",
                "I got this idea from all the sketches and doodles I've been looking at lately."];
        txtStr = options[Math.floor(Math.random()*options.length)];
      }

		txtDiv = createDiv(txtStr);
		txtDiv.id('dialogue');
		txtDiv.parent("#bubble");
      displayMsg = false;  
    }
    //$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    //$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
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
  // for (const rb of radiobtns) {
  //     if (rb.checked) {
  //         selectedAgent = rb.value;
  //         break;
  //     }
  // }
  var currentSlide = $('.agent-selection').slick('slickCurrentSlide');
  let agents = ['Rule', 'SketchRNN-Art', 'SketchRNN-QD'];
	selectedAgent = agents[currentSlide];
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
    displayMsg = true;
    playerTurn = false;
    turnNum += 1;
    if (txtDiv) {
      txtDiv.remove();
    }

    transformation = "sketchRNN-QD invoked";
    usrAction = "sketchRNN-QD Selected";
    sketchRNNStart();
	}
	else {
		console.log("you selected - ",selectedAgent);
    playerTurn = false;
    turnNum += 1;
    if (txtDiv) {
      txtDiv.remove();
    }

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

	$('#dialogue').css('display', 'block');
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
	if (pencilPicked) {
		personDrawing = true;
		x = mouseX;
		y = mouseY;
	}
}

function stopDrawing() {
	if (pencilPicked) {
		personDrawing = false;
		x = mouseX;
		y = mouseY;
	}
}

function sketchRNNStart() {
  personDrawing = false;
  // transformation = "sketchRNN-QD invoked";
  // usrAction = "sketchRNN-QD Selected";
  // console.log("inside sketchRNNStart!",transformation, usrAction);

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
