// MonGoats site scripts: notifications dropdown + story-feed swipe controls.
// Plain JS, no build step — this project has no bundler configured.

document.addEventListener("DOMContentLoaded", function () {
  initNotifications();
  initFeedControls();
});

function initNotifications() {
  var toggle = document.getElementById("notif-toggle");
  var dropdown = document.getElementById("notif-dropdown");
  if (!toggle || !dropdown) return;

  toggle.addEventListener("click", function (e) {
    e.stopPropagation();
    var isOpen = !dropdown.hidden;
    dropdown.hidden = isOpen;
    toggle.setAttribute("aria-expanded", String(!isOpen));
  });

  document.addEventListener("click", function (e) {
    if (!dropdown.hidden && !dropdown.contains(e.target) && e.target !== toggle) {
      dropdown.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      dropdown.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

function initFeedControls() {
  var track = document.getElementById("feed-track");
  var prevBtn = document.getElementById("feed-prev");
  var nextBtn = document.getElementById("feed-next");
  if (!track) return;

  function cardStep() {
    var card = track.querySelector(".story-card");
    if (!card) return 320;
    var style = window.getComputedStyle(track);
    var gap = parseFloat(style.columnGap || style.gap || "20");
    return card.getBoundingClientRect().width + gap;
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      track.scrollBy({ left: -cardStep(), behavior: "smooth" });
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      track.scrollBy({ left: cardStep(), behavior: "smooth" });
    });
  }

  // Desktop click-and-drag to "swipe" the feed with a mouse, in addition
  // to native touch scrolling (which already works via scroll-snap on
  // mobile without any JS at all).
  var isDown = false;
  var startX = 0;
  var startScroll = 0;

  track.addEventListener("mousedown", function (e) {
    isDown = true;
    track.classList.add("dragging");
    startX = e.pageX;
    startScroll = track.scrollLeft;
  });

  window.addEventListener("mouseup", function () {
    isDown = false;
    track.classList.remove("dragging");
  });

  window.addEventListener("mousemove", function (e) {
    if (!isDown) return;
    e.preventDefault();
    track.scrollLeft = startScroll - (e.pageX - startX);
  });
}
