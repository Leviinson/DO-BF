'use strict';

// SLIDER-header

document.addEventListener('DOMContentLoaded', function () {
  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
  }

  document.querySelectorAll('.slider-container-header').forEach(function (slider) {
    const group = slider.querySelector('.slide_group');
    const slides = slider.querySelectorAll('.slide-header');
    const bulletArray = [];
    let currentIndex = 1;
    let timeout;
    let touchStartX = 0;
    let touchEndX = 0;

    function move(newIndex) {
      let animateLeft, slideLeft;

      advance();

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

    function advance() {
      clearTimeout(timeout);
      timeout = setTimeout(function () {
        if (currentIndex < (slides.length - 1)) {
          move(currentIndex + 1);
        } else {
          move(0);
        }
      }, 4000); // Change the interval to 4000ms (4 seconds)
    }

    // Set initial opacity to 1 for the first slide
    if (slides[currentIndex]) {
      slides[currentIndex].style.opacity = '1';
      slides[currentIndex].style.zIndex = 'var(--layer-2)';
    }

    if (!slider.querySelector('.next_btn')) {
      return;
    }

    slider.querySelector('.next_btn').addEventListener('click', function () {
      if (currentIndex < (slides.length - 1)) {
        move(currentIndex + 1);
      } else {
        move(0);
      }
    });

    slider.querySelector('.previous_btn').addEventListener('click', function () {
      if (currentIndex !== 0) {
        move(currentIndex - 1);
      } else {
        move(slides.length - 1);
      }
    });

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

    // Start the automatic slide transition
    move(0);
    advance();
  });
});

// QUICK-SELECTION-MENU

document.addEventListener('DOMContentLoaded', function () {
  const quickSelectionMenuForm = document.querySelector('.quick-selection-menu-form');
  const quickSelectionMenuBtn = document.querySelector('.disabled-button');
  const quickSelectionMenuMinBudget = document.querySelector('.quick-selection-menu-min-budget');
  const quickSelectionMenuMaxBudget = document.querySelector('.quick-selection-menu-product-max-budget');

  quickSelectionMenuForm.addEventListener('input', quickSelectionMenuInputs);
    // // Якщо введено ім'я і валідний номер телефону - кнопка "Залишити заявку" стане активною
    function quickSelectionMenuInputs() {
      const subcategory = document.querySelector('.quick-selection-menu-category:checked')?.dataset?.slug;
      const minBudget = quickSelectionMenuMinBudget.value;
      const maxBudget = quickSelectionMenuMaxBudget.value;

      quickSelectionMenuBtn.classList.toggle('disabled-button', !(subcategory || minBudget || maxBudget));
      quickSelectionMenuBtn.disabled = !(subcategory || minBudget || maxBudget);
    }

  // QUICK-SELECTION-MENU SUBMIT

  // Слухач подій для quick selection menu при події submit
  // const quickSelectionMenuForm = document.querySelector('.quick-selection-menu-form');
  quickSelectionMenuForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const quickSelectionMenuResults = document.querySelector('.quick-selection-menu-results');
    const quickSelectionMenuSlider = document.querySelector('.quick-selection-menu-slider');
    const quickSelectionMenuCountProducts = document.querySelector('.quick-selection-menu-count');

    const subcategory = document.querySelector('.quick-selection-menu-category:checked')?.dataset?.slug;
    const currency = document.querySelector('.header-container').dataset.currencyName;
    const region = document.querySelector('.header-container').dataset.region;
    const minBudget = +document.querySelector('.quick-selection-menu-min-budget').value;
    const maxBudget = +document.querySelector('.quick-selection-menu-product-max-budget').value;

    try {
      const response = await axios({
        url: `/product/${region}/`,
        params: {
          subcategory,
          minBudget,
          maxBudget: maxBudget ? maxBudget : '',
          currency
        },
      });

      const { results } = response?.data;

      if (results) {
        quickSelectionMenuResults.hidden = false;
        quickSelectionMenuCountProducts.innerText = results.length;
        renderProductSection(results, quickSelectionMenuSlider);
        sliderForCards();

        const cards = quickSelectionMenuResults.querySelectorAll('.product-card');
        checkIsAddedToCart(cards);
      } else {
        quickSelectionMenuResults.hidden = true;
      }
    } catch (error) {
      console.error('Помилка GET-запиту:', error);
    }
  });
})

// MODAL-INDIVIDUAL-ORDER
$(document).ready(function () {
  const phoneInputClass = ".individual-order-modal-tel";
  const individualOrderForm = document.querySelector('.individual-order-modal-form');
  const individualOrderName = document.querySelector('.individual-order-modal-name');
  const individualOrderTel = document.querySelector(phoneInputClass);
  const individualOrderMinBudget = document.querySelector('.individual-order-modal-min-budget');
  const individualOrderMaxBudget = document.querySelector('.individual-order-modal-max-budget');
  const individualOrderButton = document.querySelector('.individual-order-modal-button');
  const individualOrderFileInput = document.querySelector('.individual-order-modal-file-input');
  const individualOrderFilePlaceholder = document.querySelector('.individual-order-modal-placeholder');
  const individualOrderFileCloseIcon = document.querySelector('.individual-order-modal-icon-close');
  const individualOrderFileLoadIcon = document.querySelector('.individual-order-modal-icon-load');
  const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  const iti = window.intlTelInput(individualOrderTel, {
    formatOnDisplay: true,
    hiddenInput: "full_number",
    preferredCountries: ['ua', 'pl'],
    utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/11.0.14/js/utils.js"
  });

  $(phoneInputClass).on("countrychange", function (event) {
    // Отримання інформації про вибрану країну, щоб знати яку країну обрано
    const selectedCountryData = iti.getSelectedCountryData();

    // Отримання номера зразка для вибраної країни, щоб використати його як плейсхолдер
    const newPlaceholder = intlTelInputUtils.getExampleNumber(selectedCountryData.iso2, true, intlTelInputUtils.numberFormat.INTERNATIONAL);

    // Обнулення телефонного номеру
    iti.setNumber("");

    // Маска заповнювач, яка замінить усі чила на 0
    const mask = newPlaceholder.replace(/[1-9]/g, "0");

    // Накладання маски на input
    $(this).mask(mask);
  });

  // Слухач подій на полях для вводу 
  // потрібeн для того щоб зробити кнопку активною
  individualOrderForm.addEventListener('input', checkIndividualOrderInputs);

  // // Якщо введено ім'я і валідний номер телефону - кнопка "Залишити заявку" стане активною
  function checkIndividualOrderInputs() {
    const nameValue = individualOrderName.value.trim();
    const minPrice = individualOrderMinBudget.value;
    const maxPrice = individualOrderMaxBudget.value;

    individualOrderButton.classList.toggle('disabled-button', !(nameValue && iti.isValidNumber() && minPrice && maxPrice));
    individualOrderButton.disabled = !(nameValue && iti.isValidNumber() && minPrice && maxPrice);
  }

  // Коли користувач завантажить зображення в полі де завантажується файл
  // з'явиться напис з назвою завантаженого файла і іконка "Х" при кліку
  // на яку файл видалиться з завантажених і повернуться дефолтний вміст поля
  individualOrderFileInput.addEventListener('change', () => {
    if (individualOrderFileInput.files.length > 0) {
      individualOrderFileLoadIcon.style.display = 'none';
      individualOrderFileCloseIcon.style.display = 'block';
      individualOrderFilePlaceholder.classList.add('individual-order-modal-placeholder-loaded');
      individualOrderFilePlaceholder.innerText = individualOrderFileInput.files[0].name;
      individualOrderFileCloseIcon.addEventListener('click', deleteFile);
    }
  });

  // Функція для видалення завантаженого фото
  function deleteFile() {
    individualOrderFileInput.value = '';
    individualOrderFileLoadIcon.style.display = 'block';
    individualOrderFileCloseIcon.style.display = 'none';
    individualOrderFilePlaceholder.classList.remove('individual-order-modal-placeholder-loaded');
    individualOrderFilePlaceholder.innerText = 'Фото прикладу';
  }

  // Обробник події 'submit' при натисканні кнопки "Залишити заявку"
  individualOrderForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = individualOrderName.value.trim();
    const full_number = iti.getNumber();
    const minBudget = individualOrderMinBudget.value;
    const maxBudget = individualOrderMaxBudget.value;
    const file = individualOrderFileInput.files[0];

    try {
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      };
      const response = await axios.post(
        '/individual-orders/',
        { name, full_number, minBudget, maxBudget, file, csrfmiddlewaretoken },
        config
      );

      if (response) {
        const button = document.querySelector('.individual-order-modal-button');
        changeButtonColour(button);
      }

    } catch (error) {
      console.error('Помилка POST-запиту:', error);
    }
  });

  // Коли плагін завантажується вперше потрібно тригернути "countrychange" подію вручну
  iti.promise.then(function () {
    $(phoneInputClass).trigger("countrychange");
  });
}
);

// <-- SLIDER-CARDS  -->
document.addEventListener('DOMContentLoaded', function () {
  sliderForCards();
});
