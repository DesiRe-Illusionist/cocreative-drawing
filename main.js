// playerClick = a => {

//   changeColor(color(255, 0, 0, 150));
//   $('#player1').attr('disabled', true);
//   $('.settings').toggleClass('hide');

//   currentSetting.col = convertStringtoColor($('#setting1 .active')[0].id);

//   setRadius('#myRange1');
// }

setRadius = (item) => {
  currentSetting.size = $(item)[0].value;
  agentSetting.size = $(item)[0].value;
}

colButtonClick1 = (item) => {
  $('#setting1 .colorButton').removeClass('active');
  $(item).addClass('active');

  currentSetting.col = convertStringtoColor(item.id);
}

convertStringtoColor = colorName => {
  switch (colorName) {
    case 'red':
      return color(255, 0, 0);
      break;
    case 'green':
      return color(0, 255, 0;
      break;
    case 'blue':
      return color(0, 0, 255);
      break;
    case 'cyan':
      return color(0, 255, 255);
      break;
    case 'magenta':
      return color(255, 0, 255);;
      break;
    case 'yellow':
      return color(255, 255, 0);
      break;
    case 'black':
      return color(0, 0, 0);
      break;
    case 'grey':
      return color(127, 127, 127);
      break;
    case 'white':
      return color(255, 255, 255);
      break;
  }
}
