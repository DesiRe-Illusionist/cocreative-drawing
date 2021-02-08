playerClick = a => {
  let player = a.id;

  if (player == "player1") {
    changeColor(color(255, 0, 0, 150));
    $('#player1').attr('disabled', true);
    $('#player2').attr('disabled', false);
    $('.settings').toggleClass('hide');

    currentSetting.col = convertStringtoColor($('#setting1 .active')[0].id);

    setRadius('#myRange1');
  } else if (player == "player2") {
    changeColor(color(0, 255, 0, 150));
    $('#player1').attr('disabled', false);
    $('#player2').attr('disabled', true);
    $('.settings').toggleClass('hide');

    currentSetting.col = convertStringtoColor($('#setting2 .active')[0].id);

    setRadius('#myRange2');
  }
}

setRadius = (item) => {
  currentSetting.size = $(item)[0].value;
}

colButtonClick1 = (item) => {
  $('#setting1 .colorButton').removeClass('active');
  $(item).addClass('active');

  currentSetting.col = convertStringtoColor(item.id);
}

colButtonClick2 = (item) => {
  $('#setting2 .colorButton').removeClass('active');
  $(item).addClass('active');

  currentSetting.col = convertStringtoColor(item.id);
}

convertStringtoColor = colorName => {
  switch (colorName) {
    case 'red':
      return color(255, 0, 0, 150);
      break;
    case 'green':
      return color(0, 255, 0, 150);
      break;
    case 'blue':
      return color(0, 0, 255, 150);
      break;
    case 'cyan':
      return color(0, 255, 255, 150);
      break;
    case 'magenta':
      return color(255, 0, 255, 150);;
      break;
    case 'yellow':
      return color(255, 255, 0, 150);
      break;
    case 'black':
      return color(0, 0, 0, 150);
      break;
    case 'grey':
      return color(127, 127, 127, 150);
      break;
    case 'white':
      return color(255, 255, 255, 150);
      break;
  }
}