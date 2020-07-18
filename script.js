/*
  elisttm - scripts
*/


// toggles header content when clicked
function toggleHead() {
  var x = document.getElementById("header-content");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
