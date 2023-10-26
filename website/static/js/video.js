const inputs = document.querySelectorAll(".input-field");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});

$(document).ready(function(){
    $('.menu-toggle').click(function(){
      $('nav').toggleClass('active');
    })
  })