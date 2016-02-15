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
}

document.addEventListener('keydown', function(event) {
  console.log(event.keyCode)
  if (event.keyCode == 90) { // 90 = 'z'
      document.getElementById("zero_butterflies").checked = "checked";
      checkform();
      document.getElementById("main_form").submit();
  }
}, true);
