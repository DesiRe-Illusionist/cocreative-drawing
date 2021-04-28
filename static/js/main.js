// playerClick = a => {

//   changeColor(color(255, 0, 0, 150));
//   $('#player1').attr('disabled', true);
//   $('.settings').toggleClass('hide');

//   currentSetting.col = convertStringtoColor($('#setting1 .active')[0].id);

//   setRadius('#myRange1');
// }

$(document).ready(function () {
  $('.agent-selection').slick({
    infinite: true,
    slidesToShow: 1,
    arrows: true,
    prevArrow: $('.prev'),
    nextArrow: $('.next')
  });
});

changeAgent = (i) => {
  var currentSlide = $('.agent-selection').slick('slickCurrentSlide');
  let im = (currentSlide+i)%3;
  $('#octo-img').attr('src', `../static/image/octo${im}.png`);
}


clickPencil = () => {
  if (pencilPicked) {
    pencilPicked = false;
    $('#pencil').attr('src', '../static/image/pencil.png');
    $('#pencil-text').html('HOLD TO START DRAWING');
    $('canvas').css('cursor', 'not-allowed');
    finishTurn();
  } else {
    pencilPicked = true;
    $('#pencil').attr('src', '../static/image/slate.png');
    $('#pencil-text').html('CLICK TO END TURN');
    $('canvas').css('cursor', 'url(../static/image/user_cursor.png) 64 64, auto');
    $('#bubble').css('display', 'none');
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