// <-- CATALOGUE VIEWED SECTION -->
document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.catalogue-card');

  const sliderLine = document.querySelector('.catalogue-slider-line');
  const frame = document.querySelector('.catalogue-slider');
  let currentIndex = 0;
  let frameWidth;
  let lineWidth;

  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
  }

  if (isTouchDevice()) {
    frame.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].clientX;
    });

    frame.addEventListener('touchend', function (e) {
      touchEndX = e.changedTouches[0].clientX;
      handleSwipe();
    });

    function handleSwipe() {
      const swipeThreshold = 50;

      if (touchEndX - touchStartX > swipeThreshold && currentIndex) {
        currentIndex = 0;
        rollSlider();
      } else if (touchStartX - touchEndX > swipeThreshold && !currentIndex) {
        currentIndex = 1;
        rollSlider();
      }
    }
  }

  function init() {
    cardWidth = document.querySelector('.catalogue-card').offsetWidth;
    lineWidth = sliderLine.scrollWidth + 30;
    frameWidth = frame.offsetWidth;
    rollSlider();
  }

  init();
  const returnedFunction = debounce(init, 1000);
  window.addEventListener('resize', returnedFunction);

  function rollSlider() {
    sliderLine.style.transform = `translateX(-${currentIndex * (lineWidth - frameWidth)}px)`;
  }
})
