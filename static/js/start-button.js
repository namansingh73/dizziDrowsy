const container = document.body.querySelector(".dizzy-container");
const button = document.body.querySelector(
  ".dizzy-container .details button.button"
);
const toRemoveContainer = document.body.querySelector(".details");
const videoContainer = document.body.querySelector(
  ".dizzy-container .video-container"
);

const cursorOutline = document.body.querySelector(".cursor-dot-outline");
const cursorDot = document.body.querySelector(".cursor-dot");

function hasGetUserMedia() {
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

const hdConstraints = {
  video: { width: { min: 1280 }, height: { min: 720 } },
};

var tl = gsap.timeline();

tl.to(container, {
  opacity: 1,
  duration: 0.75,
  ease: "power2.in",
});

button.addEventListener("mousedown", async () => {
  if (hasGetUserMedia()) {
    tl.to(toRemoveContainer, {
      duration: 0.3,
      css: {
        opacity: 0,
        display: "none",
      },
    }).to(videoContainer, {
      duration: 0.6,
      scale: 1.5,
    });

    const videoFeed = document.body.querySelector(
      ".dizzy-container .video-container img.video-preview"
    );

    await navigator.mediaDevices.getUserMedia(hdConstraints);
    videoFeed.setAttribute(
      "src",
      "https://images.unsplash.com/photo-1556634202-129a046351c0?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80"
    );

    // force show result
    setTimeout(() => {
      window.location.replace("/dizzy-result");
    }, 5000);
  } else {
    alert("getUserMedia() is not supported by your browser");
  }
});
