'use strict';

function sliderForCards(desktopCardHeight = 535, mobileCardHeight = 270, shiftIndex = 0) {
  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
  }

  document.querySelectorAll('.slider-product-container').forEach(function (slider) {
    const group = slider.querySelector('.slide_group');
    const slidesElements = slider.querySelectorAll('.slide-card-container');
    
    // Filtering slidesElements in case HTML contains empty elements with class="slide-card-container"
    // It might happen when the number of cards is a multiple of the number of cards in one slide
    const slides = [...slidesElements].filter(slide => {
      const cardXLElements = slide.querySelectorAll('.card-xl'); 
      return cardXLElements.length > 0;
    });

    const bulletArray = [];
    let currentIndex = slides.length > 1 ? 1 : 0;
    let touchStartX = 0;
    let touchEndX = 0;
    let cardHeight = window.innerWidth <= 700 ? mobileCardHeight : desktopCardHeight;
    let cardsInLine;

    setCardsInLine();
      
    if (slides[0]) {
      const cardXLElements = slides[0].querySelectorAll('.card-xl');
      setSliderHeight(cardXLElements);
    }

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

      // Вираховуємо і встановлюємо висоту слайдера відповідно до кількості карточок в ньому
      const cardXLElements = slides[newIndex].querySelectorAll('.card-xl');
      setSliderHeight(cardXLElements);

      setTimeout(function () {
        group.classList.remove('animated');

        slides[currentIndex].style.opacity = '0';
        slides[currentIndex].style.zIndex = '0';
        slides[newIndex].style.left = '0';
        group.style.left = '0';
        currentIndex = newIndex;
      }, 300);
    }

    // Set initial opacity to 1 for the first slide
    if (!slides[currentIndex]) {
      return;
    }

    slides[currentIndex].style.opacity = '1';
    slides[currentIndex].style.zIndex = 'var(--layer-2)';

    // В коді деякі слайдери з'являються асинхронно, тому перед тим як додати кнопки для
    // слайдера переконуємося що його вміст порожній і ми не додамо кнопки декілька разів
    slider.querySelector('.slide_buttons').innerHTML = '';

    // Додаємо умову, що кнопки слайдера не відображатимуться для одного слайда
    if (slides.length > 1) {
      slides.forEach(function (_slide, index) {
        const button = document.createElement('a');
        button.className = 'slide_btn';
        button.innerHTML = ' ';

        if (index === currentIndex) {
          button.classList.add('active');
        }

        button.addEventListener('click', function () {
          move(index);
        });

        slider.querySelector('.slide_buttons').appendChild(button);
        bulletArray.push(button);
      });

      // Викликаю функцію один раз щоб проініціалізувались стилі і відобразився перший слайд.
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

    function setCardsInLine() {
      if (window.innerWidth < 465 - shiftIndex * 105) {
        cardsInLine = 2 - shiftIndex;
      } else if (window.innerWidth <= 700 - shiftIndex * 47) {
        cardsInLine = 3 - shiftIndex;
      } else if (window.innerWidth < 970 - shiftIndex * 223) {
        cardsInLine = 2 - shiftIndex;
      } else {
        cardsInLine = 3 - shiftIndex;
      }
    }

    function setSliderHeight(cardXLElements) {
      slider.style.height = `${Math.ceil(cardXLElements.length / cardsInLine) * cardHeight}px`;
    }
  });
}

let swiper = new Swiper('.swiper2', {
	slidesPerView: 1,
	loop: false,
  autoHeight: true,
  autoplay: {
    delay: 5000,
  },
  speed: 500,
  allowTouchMove: true,
	pagination: {
		el: '.swiper-pagination',
		clickable: true,
	}
});
// swiper.autoplay.start();
// const swiperContainer = document.getElementById("swiper");
// swiperContainer.addEventListener("mouseenter", (e) => {
//   swiper.autoplay.stop();
// });
// swiperContainer.addEventListener("mouseleave", () => {
//   swiper.autoplay.start();
// });

document.addEventListener('DOMContentLoaded', function () {
  const returnedFunction = debounce(sliderForCards, 1000);
  window.addEventListener('resize', returnedFunction);
})

// Ця функція призначена для рендерингу секції з карточками продуктів у вказаному контейнері slider.
function renderProductSection(productsList, slider) {
  if (!slider) {
    return;
  }

  slider.innerHTML = `
  <div class="slide-card-container">
    ${productsList.map((product, i) => `
      ${layoutXlCard(product, i)}
        ${(i + 1) % 6 === 0
      ? `</div>
                <div class="slide-card-container">
              `
      : ''
    }
      `).join('')}
    </div>
  `
}

function layoutXlCard(product) {
  return (
    `
      <div 
        class="card-xl product-card" 
        data-product-id="${product.id}"
        data-product-new-price="${product.new_price}"
        data-product-unit-price="${product.unit_price}"
        data-is-added="${ product.is_in_cart }"
        data-is-bouquet="${ product.is_bouquet }"
        itemscope itemtype="http://schema.org/Product"
      >
        ${product.discount
          ? `<div class="discount">
              <p class="p-16-auto-medium white">
                ${product.discount}%
              </p>
            </div>`
          : ''
        }
        <a href="${product.url}">
          <div class="img-box">
            <img
              src="${product.image_url}"
              alt="${product.Name}"
              itemprop="image"
            />
          </div>
          <div class="prod-desc" itemprop="description">
            <div class="prod-title">
              <h3 class="h2-24-auto-bold" itemprop="name">
                ${product.Name}
              </h3>
            </div>
            <div class="prod-price">
              <div class="current-price">
                <p 
                  class="h2-24-auto-medium red"
                  itemprop="offers"
                  itemscope
                  itemtype="http://schema.org/Offer"
                >
                <span itemprop="price">${product.new_price ? product.new_price : product.unit_price }</span>
                <span itemprop="priceCurrency" content="${product.currency_symbol}">${product.currency_symbol}</span>
                </p>
              </div>
              <div class="old-price">
                <p
                  class="p-16-auto-medium grey"
                  itemprop="offers"
                  itemscope
                  itemtype="http://schema.org/Offer"
                >
                <span itemprop="price">${product.new_price ? product.unit_price : ''}</span>
                <span itemprop="priceCurrency" content="${product.currency_symbol}">${product.new_price ? product.currency_symbol: ''}</span>
                </p>
              </div>
            </div>
          </div>
        </a>
        <div class="card-btn">
          <Button
            type="button"
            class="button-main-text-icon p-16-auto-bold add-to-cart"
          >
            <span class="icon"></span>
            До кошика
          </Button>
          <Button
            type="button"
            class="button-main-text-icon p-16-auto-bold button-added-to-cart"
            hidden
          >
            <span class="icon"></span>
            У кошику
          </Button>
          <a
            class="p-16-auto-regular red quick-order-link"
            href="#"
            data-bs-toggle="modal"
            data-bs-target="#quickOrderModal"
            data-product-article="${product.sku}"
            data-product-image="${product.image_url}"
            data-product-title="${product.Name}"
            data-product-discount-price="${product.new_price || ''}"
            data-product-price="${product.unit_price}"
            data-product-id="${product.id}"
            data-product-currency="${product.currency_symbol}"
          >
            Швидке замовлення
          </a>
        </div>
      </div>
    `
  );
}

// set on load addToCart button content
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.product-card');

  checkIsAddedToCart(cards);
});
