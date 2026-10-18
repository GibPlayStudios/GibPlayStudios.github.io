// Previous/next buttons for the room-theme strip. Without JavaScript the strip
// is still a normal horizontally scrollable list.
(function () {
  "use strict";
  var track = document.querySelector("[data-carousel-track]");
  var buttons = document.querySelector("[data-carousel-buttons]");
  if (!track || !buttons) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  buttons.hidden = false;
  buttons.addEventListener("click", function (event) {
    var button = event.target.closest("[data-carousel]");
    if (!button) return;
    var item = track.querySelector("li");
    var step = item ? item.getBoundingClientRect().width + 20 : track.clientWidth * 0.8;
    track.scrollBy({ left: Number(button.getAttribute("data-carousel")) * step, behavior: reduce.matches ? "auto" : "smooth" });
  });
})();
