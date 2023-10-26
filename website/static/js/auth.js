const inputs = document.querySelectorAll(".input-field");
const toggle_btn = document.querySelectorAll(".toggle");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");
const requestMetaLogin = document.getElementById("request-meta-login");
const requestMetaSignup = document.getElementById("request-meta-signup");
requestMetaLogin.value = "login";
requestMetaSignup.value =  "signup"

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});

function mainLoop(){
  let index = 1;
  setInterval(() => {
    index ++;
    if (index > 3) { index = 1; }
    autoMoveSlider(index);
  }, 3000);
  }

toggle_btn.forEach((btn) => {
  btn.addEventListener("click", () => {
    main.classList.toggle("sign-up-mode");
    if (document.title == "Login - Scholarly") { document.title = "Signup - Scholarly"; }
    else { document.title = "Login - Scholarly"; }
  });
});

function moveSlider() {
  let index = this.dataset.value;

  const textSlider = document.querySelector(".text-group");
  textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

  bullets.forEach((bull) => bull.classList.remove("active"));
  this.classList.add("active");
}

function autoMoveSlider(index) {
  const textSlider = document.querySelector(".text-group");
  textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

  bullets.forEach((bull) => bull.classList.remove("active"));
  bullets[index-1].classList.add("active");
}

bullets.forEach((bullet) => {
  bullet.addEventListener("click", moveSlider);
});

mainLoop();