'use strict'

// CALL-BACK-MODAL
$(document).ready(function () {
  const phoneInputClass = ".call-back-modal-tel";
  const callBackForm = document.querySelector('.call-back-modal-form');
  const callBackInputTel = document.querySelector(phoneInputClass);
  const callBackInputName = document.querySelector('.call-back-modal-name');
  const callBackButton = document.querySelector('.call-back-modal-button');
  const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  const iti = window.intlTelInput(callBackInputTel, {
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

    // Маска заповнювач, яка замінює усі чила на 0
    const mask = newPlaceholder.replace(/[1-9]/g, "0");

    // Накладання маски на input
    $(this).mask(mask);
  });

  // Слушатель события input на поле ввода номера телефона 
  callBackInputTel.addEventListener('input', checkInputs);

  // Слушатель события input на поле ввода имени 
  callBackInputName.addEventListener('input', checkInputs);

  // Функція для перевірки стану кнопки
  function checkInputs() {
    const nameValue = callBackInputName.value.trim();

    const isNameValid = nameValue !== ''; // Перевірка імені
    const isPhoneValid = iti.isValidNumber(); // Проверка номеру телефону

    // Условие для активации/деактивации кнопки
    if (isNameValid && isPhoneValid) {
      callBackButton.classList.remove('disabled-button');
      callBackButton.disabled = false;
    } else {
      callBackButton.classList.add('disabled-button');
      callBackButton.disabled = true;
    }
  }

  // Остальной код остается без изменений
  callBackForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const full_number = iti.getNumber();
    const name = callBackInputName.value.trim();

    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfmiddlewaretoken,
        }
      };
      const response = await axios.post(
        '/feedbacks/',
        { full_number, name, csrfmiddlewaretoken },
        config
      );

      if (response) {
        // const button = document.querySelector('.call-back-modal-button');
        changeButtonColour(callBackButton);
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