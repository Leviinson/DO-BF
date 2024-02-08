'use strict'

// delete this function when add JT
// function debounce(func, wait, immediate) {
//   let timeout;

//   // Ця функція викликається, коли подія DOM викликана.
//   return function executedFunction() {
//     const context = this;
//     const args = arguments;

//     // Функція, яка викликається після закінчення часу debounce.
//     const later = function () {
//       // Нульовий timeout, щоб вказати що debounce закінчилася.
//       timeout = null;

//       // Викликаємо функцію, якщо immediate !== true,
//       // тобто ми викликаємо функцію в кінці, після wait часу.
//       if (!immediate) func.apply(context, args);
//     };

//     // Визначаємо чи потрібно викликати функцію спочатку.
//     const callNow = immediate && !timeout;

//     // clearTimeout зкидує очікування при кожному виконанні функції.
//     // Це крок, який не дозволяє виконання функції.
//     clearTimeout(timeout);

//     // Перезапускаємо період очікування debounce.
//     // setTimeout повертає істинне значення / truthy value
//     // (воно відрізняється в web и node)
//     timeout = setTimeout(later, wait);

//     // Викликаємо функцію спочатку, якщо immediate === true
//     if (callNow) func.apply(context, args);
//   };
// };

// document.addEventListener('DOMContentLoaded', function () {
//   sliderForCards(450, 224, 1);
// })

// removes mask from input type date
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.querySelector('.order-date-input');
  const dateInputMask = document.querySelector('.order-date-input input + input');

  dateInput.addEventListener('click', () => {
    dateInputMask.style.display = 'none';
  })
});

console.log('start mask');
// ORDER SUBMIT FORM
document.addEventListener('DOMContentLoaded', () => {
  console.log('start inside mask');
  const phoneInputClass = ".order-input-group .order-tel";
  const orderTels = document.querySelectorAll(phoneInputClass);
  // const orderForm = document.querySelector('.order-container');
  console.log('orderTels', orderTels);

  // const tels = ['', ''];

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
        // tels[i] = iti.getNumber();
        console.log('orderTels[i].value', orderTels[i].value);
        orderTels[i].value = iti.getNumber();
      })
    });

    iti.promise.then(function () {
      $(phoneInputClass).trigger("countrychange");
    });
  }

  const orderTermsInput = document.querySelector('.order-terms input');

  orderTermsInput.addEventListener('change', () => {
      const button = document.querySelector('.order-button');
      button.classList.remove('disabled-button');
      button.disabled = false;
  });

  // orderForm.addEventListener('submit', async (event) => {
  //   event.preventDefault();

  //   const customer_number = tels[0];
  //   const customerName = document.querySelector('.order-customer-name').value.trim();
  //   const email = document.querySelector('.order-customer-email').value;
  //   const isAnonim = !!document.querySelector('.order-switch-anonim input:checked');
  //   const isByCourier = document.querySelector('.order-by-courier').value;
  //   const isSpecifyAddress = !!document.querySelector('.order-switch-specify input:checked');
  //   const country = document.querySelector('.order-country').value;
  //   const region = document.querySelector('.order-region').value;
  //   const city = document.querySelector('.order-city').value;
  //   const street = document.querySelector('.order-street').value;
  //   const house = document.querySelector('.order-house').value;
  //   const flat = document.querySelector('.order-flat').value;
  //   const date = document.querySelector('.order-date').value;
  //   const isRecipientI = document.querySelector('.order-recipient-container input:checked + label').innerText;
  //   const recipientName = document.querySelector('.order-recipient-name').value;
  //   const recipient_number = tels[1];
  //   const isSurprice = !!document.querySelector('.order-switch-surprice input:checked');
  //   const postcard = document.querySelector('.order-postcard').value;
  //   const paymentType = document.querySelector('.order-paymentTypes-container input:checked + label').innerText;
  //   const terms = !!document.querySelector('.order-terms input:checked');


  //   console.log('isAnonim', {customer_number, customerName, email, isAnonim, isByCourier, isSpecifyAddress, country, region, city, street, 
  //     house, flat, date, isRecipientI, recipientName, recipient_number, isSurprice, postcard, paymentType, terms});
  //   // const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  //   try {
  //     const config = {
  //       headers: {
  //         'Content-Type': 'application/json',
  //         // 'X-CSRFToken': csrfmiddlewaretoken,
  //       }
  //     };
  //     const response = await axios.post(
  //       '/orders/',
  //       // { name, full_number, productId, csrfmiddlewaretoken },
  //       config
  //     );

  //     if (response) {
  //       const button = document.querySelector('.quick-order-modal-button');
  //       changeButtonColour(button);
  //     }
  //   } catch (error) {
  //     console.error('Помилка POST-запиту:', error);
  //   }
  // });
});

// Запуск слайдера вперше, додавання кнопок управління ітд.
document.addEventListener('DOMContentLoaded', function () {
  sliderForCards();
});
