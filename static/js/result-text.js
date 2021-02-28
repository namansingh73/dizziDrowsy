// result = [
//   "You seem to be fine!",
//   "Don't drive unnecessarily",
//   "Cab seems to be your only option.",
// ];

const result = document.querySelector(".result-container");
const start = document.querySelector(".button[startDrive]");

// var tl = gsap.timeline();

gsap.to(".result-container", { ease: "power2.out", opacity: 1, duration: 1.5 });

start.addEventListener("mousedown", () => {
  gsap.to(result, { ease: "power2.in", opacity: 0, duration: 0.75 });
  setTimeout(() => {
    window.location.replace("/driving");
  }, 1500);
});
