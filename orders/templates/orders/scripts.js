'use strict'

document.addEventListener('DOMContentLoaded', function () {
  let switchAddress = document.getElementById("switchAddress");
  switchAddress.addEventListener("change", () => {
    if(switchAddress.checked) {
      document.getElementById("autocompleteAddress").style.display = "none";
      document.getElementById("id_flat").style.display = "none";
      document.getElementById("autocompleteCity").style.display = "none";
      document.getElementById("autocompleteRegion").style.display = "none";
      document.getElementById("autocompleteCountry").style.display = "none";
    }
    else {
      document.getElementById("autocompleteAddress").style.display = "block";
      document.getElementById("id_flat").style.display = "block";
      document.getElementById("autocompleteCity").style.display = "block";
      document.getElementById("autocompleteRegion").style.display = "block";
      document.getElementById("autocompleteCountry").style.display = "block";
    }
  });

  if(switchAddress.checked) {
    document.getElementById("autocompleteAddress").style.display = "none";
    document.getElementById("id_flat").style.display = "none";
    document.getElementById("autocompleteCity").style.display = "none";
    document.getElementById("autocompleteRegion").style.display = "none";
    document.getElementById("autocompleteCountry").style.display = "none";
  }
  
  // Запуск слайдера вперше, додавання кнопок управління ітд.
  sliderForCards(450, 224, 1);

  // removes mask from input type date
  const dateInputGroup = document.querySelector('.order-date-input');
  const dateInput = document.querySelector('.order-date');
  const dateInputMask = document.querySelector('.order-date-mask');

  dateInputGroup.addEventListener('click', () => {
    dateInputMask.style.display = 'none';
  })

  // gives access to submit the form after accepting the terms
  const orderTermsInput = document.querySelector('.order-terms input');

  orderTermsInput.addEventListener('change', () => {
      const button = document.querySelector('.order-button');
      button.classList.remove('disabled-button');
      button.disabled = false;
  });

  // set min date for input type date current day
  const today = new Date().toISOString().split('T')[0];
  dateInput.min = today;
})

//  HANDLE PHONE NUMBERS VALUES
$(document).ready(function () {
  const phoneInputClass = ".order-tel";
  const orderTels = document.querySelectorAll(phoneInputClass);
  const orderTelsHidden = document.querySelectorAll('.order-tel-hidden');

  for (let i = 0; i < orderTels.length; i++) {
    const iti = window.intlTelInput(orderTels[i], {
      formatOnDisplay: true,
      hiddenInput: `full_number${i}`,
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

      // зберігаємо в масив введений номер телефону
      orderTels[i].addEventListener('input', () => {
        orderTelsHidden[i].value = iti.getNumber();
      })
    });

    iti.promise.then(function () {
      $(phoneInputClass).trigger("countrychange");
    });
  }
});

// HIDING RECEPIENT DATA
document.addEventListener('DOMContentLoaded', function () {
  const recipientElementsGroup = document.querySelector('.order-recipient-group');
  const recipientIsCustomer = document.querySelector('#isRecipientCustomer');
  const recipientIsNotCustomer = document.querySelector('#isRecipientNotCustomer');
  const isPresent = document.querySelectorAll('.order-present');
  const recipientName = document.querySelector('.order-recipient-name');
  const recipientPhone = document.querySelector('.order-recipient-phone');

  recipientElementsGroup.addEventListener('click', (event) => {
    const target = event.target.closest('input');

    if (target === recipientIsNotCustomer) {
      recipientIsNotCustomer.checked = true;
      recipientIsCustomer.checked = false;

      isPresent.forEach(present => present.style.display = 'flex');
      recipientName.required = true;
      recipientPhone.required = true;
    } else {
      recipientIsNotCustomer.checked = false;
      recipientIsCustomer.checked = true;

      isPresent.forEach(present => present.style.display = 'none');
      recipientName.required = false;
      recipientPhone.required = false;
    }
  })
});
