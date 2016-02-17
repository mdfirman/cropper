function wings_checked()
{
  var chx = document.getElementsByName('topbottom');
  for (var i=0; i<chx.length; i++) {
  // If you have more than one radio group, also check the name attribute
  // for the one you want as in && chx[i].name == 'choose'
  // Return true from the function on first match of a checked item
    if (chx[i].type == 'radio' && chx[i].checked) {
      return true;
    }
  }
}

function bad_image()
{
  return !(document.getElementById("one_butterfly").checked);
}

function cropped()
{
  return Number(document.getElementById("x").value) > 0;
}

function goodcropstep2()
{
  // checking that the cropping for training step 2 is good enough
  var x = Number(document.getElementById("x").value)
  var y = Number(document.getElementById("y").value)
  var width = Number(document.getElementById("width").value)
  var height = Number(document.getElementById("height").value)
  var right = x + width;
  var bottom = y + height;
  var tol = 12;

  return (Math.abs(x - 300) < tol && Math.abs(y - 88) < tol && Math.abs(right - 763) < tol && Math.abs(bottom - 434) < tol);
}

function goodcropstep3()
{
  // checking that the cropping for training step 2 is good enough
  var x = Number(document.getElementById("x").value)
  var y = Number(document.getElementById("y").value)
  var width = Number(document.getElementById("width").value)
  var height = Number(document.getElementById("height").value)
  var right = x + width;
  var bottom = y + height;
  var tol = 12;

  return (Math.abs(x - 400) < tol && Math.abs(y - 186) < tol && Math.abs(right - 755) < tol && Math.abs(bottom - 483) < tol);
}

function goodcropstep5()
{
  // checking that the cropping for training step 2 is good enough
  var x = Number(document.getElementById("x").value)
  var y = Number(document.getElementById("y").value)
  var width = Number(document.getElementById("width").value)
  var height = Number(document.getElementById("height").value)
  var right = x + width;
  var bottom = y + height;
  var tol = 12;

  return (Math.abs(x - 404) < tol && Math.abs(y - 190) < tol && Math.abs(right - 651) < tol && Math.abs(bottom - 506) < tol);
}

// http://stackoverflow.com/questions/13931688/disable-enable-submit-button-until-all-forms-have-been-filled
function checkform()
{
  // here we want to check if we aren't allowed to crop, and if so disable all elements
  if (bad_image())
  {
    $(".container > img").cropper("clear");
    $(".img-container > img").cropper("clear");
    $(".img-container > img").cropper("disable");
    $(".onlyone").css("visibility", "hidden");
  }
  else {
    $(".img-container > img").cropper("enable");
    $(".onlyone").css("visibility", "visible");
  }

  var f = document.forms["main_form"].elements;
  var cansubmit = (wings_checked() && cropped()) || bad_image();
  document.getElementById('submitter').disabled = !cansubmit;

  // First training step
  if (parseInt($('#my-data').data().trainstep) == 1) {
    console.log('Here')
    if (document.getElementById("zero_butterflies").checked) {
      $('#submit-popover').popover('show');
    }
    else {
      document.getElementById('submitter').disabled = true;
      $('#submit-popover').popover('hide');
    }
  }

  // second training step
  else if (parseInt($('#my-data').data().trainstep) == 2) {

    $('a#topbottompopover').popover({ trigger: 'manual', placement: 'right'});

    var enabled = document.getElementById("topside").checked && goodcropstep2();
    console.log(enabled);
    document.getElementById('submitter').disabled = !enabled;

    if (document.getElementById("topside").checked) {
      // show that we've done a good job
      $('a#topbottompopover').data('bs.popover').options.content = "Great job! Now move on to cropping.";
      $('#cropping-helper').css('display', 'block');

      // check how the cropping is going
      if (goodcropstep2()) {
        $('#cropping-helper').removeClass("alert-info")
        $('#cropping-helper').addClass("alert-success")
        $('#cropping-helper-text').html("<strong>Success!</strong><br/>Click 'submit' above to continue.")
        $('a#topbottompopover').popover('hide')
      }
      else {
        $('#cropping-helper').removeClass("alert-success")
        $('#cropping-helper').addClass("alert-info")
        $('#cropping-helper-text').html("We've drawn a dotted line to guide you on this one. Click and drag to draw your box. You can adjust the box by dragging the sides.")
        $('a#topbottompopover').popover("show");
      }
    }
    else  // topside unchecked
    {
      // guide user towards a different checkbox
      $('a#topbottompopover').data('bs.popover').options.content = "Click 'help' on the right for more info.";
      $('a#topbottompopover').popover("show");
      $('#cropping-helper').css('display', 'none');
    }
  }

  // third training step
  else if (parseInt($('#my-data').data().trainstep) == 3) {

    $('a#topbottompopover').popover({ trigger: 'manual', placement: 'right'});

  var enabled = document.getElementById("bottomside").checked && goodcropstep3();
  document.getElementById('submitter').disabled = !enabled;

    if (document.getElementById("bottomside").checked) {
      // show that we've done a good job
      $('a#topbottompopover').data('bs.popover').options.content = "Great job! Now move on to cropping.";
      $('#cropping-helper').css('display', 'block');

      // check how the cropping is going
      if (goodcropstep3()) {
        $('#cropping-helper').removeClass("alert-info")
        $('#cropping-helper').addClass("alert-success")
        $('#cropping-helper-text').html("<strong>Success!</strong><br/>Click 'submit' above to continue.")
        $('a#topbottompopover').popover('hide')
      }
      else {
        $('#cropping-helper').removeClass("alert-success")
        $('#cropping-helper').addClass("alert-info")
        $('#cropping-helper-text').html("We've drawn a dotted line to guide you on this one. Click and drag to draw your box. You can adjust the box by dragging the sides.")
        $('a#topbottompopover').popover("show");
      }
    }
    else  // bothside unchecked
    {
      // guide user towards a different checkbox
      $('a#topbottompopover').data('bs.popover').options.content = "Click 'help' on the right for more info.";
      $('a#topbottompopover').popover("show");
      $('#cropping-helper').css('display', 'none');
    }
  }

  // Fourth training step
  else if (parseInt($('#my-data').data().trainstep) == 4) {
    if (document.getElementById("many_butterflies").checked) {
      $('#submit-popover').popover('show');
    }
    else {
      document.getElementById('submitter').disabled = true;
      $('#submit-popover').popover('hide');
    }
  }

  // fifth training step
  else if (parseInt($('#my-data').data().trainstep) == 5) {

  $('a#topbottompopover').popover({ trigger: 'manual', placement: 'right'});

  console.log(document.getElementById("bothside").checked)
  console.log(goodcropstep5())
  // console.log((!document.getElementById("bothside").checked && (!goodcropstep5())))
  var enabled = document.getElementById("bothside").checked && goodcropstep5();
  document.getElementById('submitter').disabled = !enabled;

    if (document.getElementById("bothside").checked) {
      // show that we've done a good job
      $('a#topbottompopover').data('bs.popover').options.content = "Great job! Now move on to cropping.";
      $('#cropping-helper').css('display', 'block');

      // check how the cropping is going
      if (goodcropstep5()) {
        $('#cropping-helper').removeClass("alert-info")
        $('#cropping-helper').addClass("alert-success")
        $('#cropping-helper-text').html("<strong>Success!</strong><br/>Click 'submit' above to continue.")
        $('a#topbottompopover').popover('hide')
      }
      else {
        $('#cropping-helper').removeClass("alert-success")
        $('#cropping-helper').addClass("alert-info")
        $('#cropping-helper-text').html("This time, we haven't drawn a dotted line. Click and drag to draw your box, until this message changes. You can adjust the box by dragging the sides.")
        $('a#topbottompopover').popover("show");
      }
    }
    else  // bothside unchecked
    {
      // guide user towards a different checkbox
      $('a#topbottompopover').data('bs.popover').options.content = "Click 'help' on the right for more info.";
      $('a#topbottompopover').popover("show");
      $('#cropping-helper').css('display', 'none');
    }
  }

}

document.addEventListener('keydown', function(event) {
  console.log(event.keyCode)
  if (event.keyCode == 90) { // 90 = 'z'
      document.getElementById("zero_butterflies").checked = "checked";
      checkform();
      document.getElementById("main_form").submit();
  }
}, true);
