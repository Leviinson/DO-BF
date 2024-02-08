'use strict'

// MODAL-QUICK-ORDER
$(document).ready(function () {
  const phoneInputClass = ".quick-order-modal-tel";
  const quickOrderForm = document.querySelector('.quick-order-modal-form');
  const quickOrderName = document.querySelector('.quick-order-modal-name');
  const quickOrderTel = document.querySelector(phoneInputClass);
  const quickOrderButton = document.querySelector('.quick-order-modal-button');

  const iti = window.intlTelInput(quickOrderTel, {
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

  // Слухачі подій на полях для вводу номеру телефону і ім'я
  // потрібні для того щоб зробити кнопку активною
  quickOrderName.addEventListener('input', checkQuickOrderInputs)
  quickOrderTel.addEventListener('input', checkQuickOrderInputs)


  // // Якщо введено ім'я і валідний номер телефону - кнопка "Залишити заявку" стане активною
  function checkQuickOrderInputs() {
    const name = quickOrderName.value.trim();

    quickOrderButton.classList.toggle('disabled-button', !(name && iti.isValidNumber()));
    quickOrderButton.disabled = !(name && iti.isValidNumber());
  }

  // Обробник події 'submit' при натисканні кнопки "Залишити заявку"
  quickOrderForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = quickOrderName.value.trim();
    const full_number = iti.getNumber();
    const productId = document.querySelector('.quick-order-modal-id').textContent;
    const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfmiddlewaretoken,
        }
      };
      const response = await axios.post(
        '/quick-orders/',
        { name, full_number, productId, csrfmiddlewaretoken },
        config
      );

      if (response) {
        const button = document.querySelector('.quick-order-modal-button');
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
});

// Додаємо інформацію з вибраної карточки в modal quick order
document.addEventListener('DOMContentLoaded', function () {
  // Знаходимо карточку по якій було здійснено клік
  document.addEventListener('click', (event) => {
    const card = event.target.closest('.quick-order-link');

    if (!card) {
      return;
    }

    // Отримуємо з дата-атрибута дані карточки по якій було зроблено клік
    const productArticle = card.dataset.productArticle;
    const productImage = card.dataset.productImage;
    const productTitle = card.dataset.productTitle;
    const productDiscountPrice = card.dataset.productDiscountPrice;
    const productPrice = card.dataset.productPrice;
    const productId = card.dataset.productId;
    const currency = card.dataset.productCurrency;

    // Знаходимо позиції в modal quick order куди потрібно вставити дані карточки
    const prodTitle = document.querySelector('.quick-order-modal-card-title');
    const prodArticle = document.querySelector('.quick-order-modal-card-article');
    const currentPrice = document.querySelector('.quick-order-modal-card-price');
    const oldPrice = document.querySelector('.quick-order-modal-card-old-price');
    const prodImg = document.querySelector('.quick-order-modal-card-img');
    const elementForId = document.querySelector('.quick-order-modal-id');

    // Призначаємо дані продукта в картку в modal quick order
    prodTitle.textContent = `${productTitle}`;
    prodArticle.textContent = `Артикул: ${productArticle}`;
    currentPrice.textContent = `${productDiscountPrice ? productDiscountPrice : productPrice} ${currency}`;
    oldPrice.textContent = `${productDiscountPrice ? productPrice + currency : ''}`;
    prodImg.src = productImage;
    prodImg.alt = productTitle;
    elementForId.textContent = productId;
  });
});