const title = [
  "You are ready to drive.",
  "Drive at your own risk",
  "Cab seems to be your only option.",
];

const res = [
  "Result: Fit to drive",
  "Result: Recommended not to drive",
  "Result: Not fit to drive",
];

const color = ["", "warning", "danger"];

const buttons = [
  '<button class="button" data-level="" startDrive>Start Drive</button>',
  '<button class="button" data-level="warning">Book Cab</button><button class="button" data-level="muted" startDrive>Start ride anyways</button>',
  '<button class="button" data-level="danger" startDrive>Book cab</button>',
];

const maxNormal = 30;
const maxWarning = 50;

const currentValue = parseInt(
  document.body.querySelector(".score-container .score").innerHTML
);

const index = currentValue < maxNormal ? 0 : currentValue < maxWarning ? 1 : 2;

const result = document.querySelector(".result-container");
const scoreContainer = result.querySelector(".score-container");
const resultText = result.querySelector(".result-text");
const resultTitle = resultText.querySelector(".result");
const resText = resultText.querySelector("h4");
const resultActions = resultText.querySelector(".result-actions");

// var tl = gsap.timeline();

// gsap.to(".result-container", { ease: "power2.out", opacity: 1, duration: 1.5 });

scoreContainer.setAttribute("data-level", color[index]);
resText.innerText = res[index];
resultTitle.innerText = title[index];
resultActions.innerHTML = buttons[index];

const tl = gsap.timeline();

tl.to(scoreContainer, {
  ease: "power2.out",
  opacity: 1,
  duration: 0.5,
})
  .to(resText, {
    ease: "power2.out",
    opacity: 0.5,
    duration: 0.5,
  })
  .to(resultTitle, {
    ease: "power2.out",
    opacity: 1,
    duration: 0.5,
  })
  .to(resultActions, {
    ease: "power2.out",
    opacity: 1,
    duration: 0.5,
  });

const start = document.querySelector(".button[startDrive]");
start.addEventListener("mousedown", () => {
  gsap.to(result, { ease: "power2.in", opacity: 0, duration: 0.75 });
  setTimeout(() => {
    window.location.replace("/driving");
  }, 1500);
});