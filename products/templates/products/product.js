'use strict'

// <!-- SIMILAR PRODUCTS SECTION -->
// Запуск слайдера вперше, додавання кнопок управління ітд
document.addEventListener('DOMContentLoaded', () => {
  sliderForCards();
});

//  <--/*PRODUCT IMAGE SLIDER */-->
document.addEventListener('DOMContentLoaded', () => {

  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
  }

  document.querySelectorAll('.product-slider-container').forEach(function (slider) {
    const group = slider.querySelector('.product-slides');
    const slides = slider.querySelectorAll('.product-slide');
    const bulletArray = [];
    let currentIndex = slides.length > 1 ? 1 : 0;
    let touchStartX = 0;
    let touchEndX = 0;

    function move(newIndex) {
      let animateLeft, slideLeft;

      if (group.classList.contains('animated') || currentIndex === newIndex) {
        return;
      }

      bulletArray[currentIndex].classList.remove('active');
      bulletArray[newIndex].classList.add('active');

      if (newIndex > currentIndex) {
        slideLeft = '100%';
        animateLeft = '-100%';
      } else {
        slideLeft = '-100%';
        animateLeft = '100%';
      }

      group.classList.add('animated');

      slides[newIndex].style.opacity = '1';
      slides[newIndex].style.zIndex = 'var(--layer-2)';
      slides[newIndex].style.left = slideLeft;
      group.style.left = animateLeft;

      setTimeout(function () {
        group.classList.remove('animated');

        slides[currentIndex].style.opacity = '0';
        slides[currentIndex].style.zIndex = '0';
        slides[newIndex].style.left = '0';
        group.style.left = '0';
        currentIndex = newIndex;
      }, 500);
    }

    // Set initial opacity to 1 for the first slide

    if (!slides[currentIndex]) {
      return;
    }

    slides[currentIndex].style.opacity = '1';
    slides[currentIndex].style.zIndex = 'var(--layer-2)';

    // В коді деякі слайдери з'являються асинхронно, тому перед тим як додати кнопки для
    // слайдера переконуємося що його вміст порожній і ми не додамо кнопки декілька разів
    // slider.querySelector('.product-slider-buttons').innerHTML = '';


    // Додаємо умову, що кнопки слайдера не відображатимуться для одного слайда
    if (slides.length > 1) {
      slides.forEach(function (slide, index) {
        const button = document.createElement('a');
        button.className = 'slide_btn';
        button.innerHTML = ' ';

        if (index === currentIndex) {
          button.classList.add('active');
        }

        button.addEventListener('click', function () {
          move(index);
        });

        slider.querySelector('.product-slider-buttons').appendChild(button);
        bulletArray.push(button);
      });

      move(0);
    }
    // Swipe Gesture Handling
    if (isTouchDevice()) {
      slider.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].clientX;
      });

      slider.addEventListener('touchend', function (e) {
        touchEndX = e.changedTouches[0].clientX;
        handleSwipe();
      });

      function handleSwipe() {
        const swipeThreshold = 50;

        if (touchEndX - touchStartX > swipeThreshold) {
          if (currentIndex !== 0) {
            move(currentIndex - 1);
          } else {
            move(slides.length - 1);
          }
        } else if (touchStartX - touchEndX > swipeThreshold) {
          if (currentIndex < slides.length - 1) {
            move(currentIndex + 1);
          } else {
            move(0);
          }
        }
      }
    }
  });
})

// Adding styles for bouquets according to choosen size
document.addEventListener('DOMContentLoaded', () => {
  const radioInputs = document.querySelectorAll('.product-size');

  if (!radioInputs.length) {
    return;
  }

  const card = document.querySelector('.product-card');
  const size = card.dataset.selectedSize;

  radioInputs.forEach(input => {
    const inputSize = input.dataset.size;

    if (inputSize === size) {
      input.checked = true;
    }
  });
});

// set on load addToCart button content
document.addEventListener('DOMContentLoaded', () => {
  const addToCartButton = document.querySelector('.add-to-cart');
  const addedToCartButton = document.querySelector('.product-cart-button-added');
  const isAdded = addToCartButton.dataset.isAdded;

  if(isAdded === 'True') {
    addToCartButton.hidden = true;
    addedToCartButton.hidden = false;
  }
});
