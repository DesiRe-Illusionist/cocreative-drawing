// playerClick = a => {

//   changeColor(color(255, 0, 0, 150));
//   $('#player1').attr('disabled', true);
//   $('.settings').toggleClass('hide');

//   currentSetting.col = convertStringtoColor($('#setting1 .active')[0].id);

//   setRadius('#myRange1');
// }

setRadius = (item) => {
  currentSetting.size = $(item)[0].value;
}

colButtonClick1 = (item) => {
  $('#setting1 .colorButton').removeClass('active');
  $(item).addClass('active');

  currentSetting.col = convertStringtoColor(item.id);
}

convertStringtoColor = colorName => {
  switch (colorName) {
    case 'sea':
      return color(54,62,167,150);
      break;
    case 'road':
      return color(174,170,200,150);
      break;
    case 'stone':
      return color(219,135,126,150);
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