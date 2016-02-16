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
  var tol = 15;

  return (Math.abs(x - 300) < tol && Math.abs(y - 88) < tol && Math.abs(width - 463) < tol && Math.abs(height - 346) < tol);
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
        // $('#cropping-helper').show();
        // creating popover rewarding cropping
        //
        // $('a#croppingpopover').popover({ trigger: 'manual', placement: 'bottom'});
        // $('a#croppingpopover').data('bs.popover').options.content = "Great! Now click 'submit'";
        // $('a#croppingpopover').popover("show");
      }
      else {
        $('#cropping-helper').removeClass("alert-success")
        $('#cropping-helper').addClass("alert-info")
        $('#cropping-helper-text').html("We've drawn a dotted line to guide you on this one. Click and drag to draw your box. You can adjust the box by dragging the sides.")
        // $('.cropping-helper').hide();
        // creating popover prompting cropping
        //
        // $('a#croppingpopover').popover({ trigger: 'manual', placement: 'right'});
        // $('a#croppingpopover').data('bs.popover').options.content = "We've drawn a dotted line to guide you. You can adjust the box by dragging the sides.";
        // $('a#croppingpopover').popover("show");
      }
    }
    else  // topside unchecked
    {
      // guide user towards a different system
      $('a#topbottompopover').data('bs.popover').options.content = "Click 'help' on the right for more info.";
      // $('a#croppingpopover').popover("hide");

      $('#cropping-helper').css('display', 'none');
    }

    $('a#topbottompopover').popover("show");

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
