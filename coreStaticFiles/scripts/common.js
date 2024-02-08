'use strict'

// Функція яка змінює колір на зелений при успішній відправці форми на сервер,
// закриває модальне вікно і відновлює оригінальний колір 
function changeButtonColour(element) {
  element.classList.add('greenButton');

  setTimeout(() => {
    const closeButton = document.querySelectorAll('.btn-close');
    closeButton.forEach(btn => btn.click());
    element.classList.remove('greenButton');
  }, 1000);
};

function decreaseTotalPrice(card) {
  const price = card.dataset.productNewPrice
    ? +card.dataset.productNewPrice
    : +card.dataset.productUnitPrice;

  const totalPriceElement = document.querySelector('.cart-total-price');
  const oldTotalPrice = +totalPriceElement.innerText;
  const newTotalPrice = oldTotalPrice - price;
  totalPriceElement.textContent = newTotalPrice.toFixed(2);
}

function increaseTotalPrice(card) {
  const totalPriceElement = document.querySelector('.cart-total-price');

  if (!totalPriceElement) {
    return;
  }

  const price = card.dataset.productNewPrice
    ? +card.dataset.productNewPrice
    : +card.dataset.productUnitPrice;

    const oldTotalPrice = +totalPriceElement.textContent;
    const newTotalPrice = oldTotalPrice + price;
    totalPriceElement.textContent = newTotalPrice.toFixed(2);
}

function setTotalCount(card, action) {
  const totalCountElements = document.querySelectorAll('.products-count');
  let amount;

  switch (action) {
    case 'increace':
      [...totalCountElements].forEach(element => {
        const oldTotalCount = +element.textContent;
        element.textContent = oldTotalCount + 1 ;
      })
      break;
    case 'decreace':
      [...totalCountElements].forEach(element => {
        const oldTotalCount = +element.textContent;
        element.textContent = oldTotalCount - 1;
      })
      break;
    case 'delete':
      amount = +card.querySelector('.count').innerText;
      [...totalCountElements].forEach(element => {
        const oldTotalCount = +element.textContent;
        element.textContent = oldTotalCount - amount;
      })
      break;
  
    default:
      break;
  }
}

function setTotalCount2(card, action) {
  const totalCountElements = document.querySelectorAll('.products-count');
  let amount;

  switch (action) {
    case 'delete':
      amount = +card.querySelector('.count').innerText;
      [...totalCountElements].forEach(element => {
        const oldTotalCount = +element.textContent;
        element.textContent = oldTotalCount - amount;
      })
      break;
  
    default:
      break;
  }
}

function checkIsAddedToCart(cards) {
  if (!cards.length) {
    return;
  }

  cards.forEach(card => {
    const addToCartButton = card.querySelector('.add-to-cart');
    const addedToCartButton = card.querySelector('.button-added-to-cart');
    const isAdded = card.dataset.isAdded;
  
    if(isAdded === 'True' || isAdded === 'true') {
      addToCartButton.hidden = true;
      addedToCartButton.hidden = false;
    }
  })
}

function checkIsSameCardOnPage(id, action) {
  const cards = document.querySelectorAll('.product-card');

  if (!cards.length) {
    return;
  }

  cards.forEach(card => {
    const addToCartButton = card.querySelector('.add-to-cart');
    const cardId = card.dataset.productId; 
    const addedToCartButton = card.querySelector('.button-added-to-cart')
      ? card.querySelector('.button-added-to-cart')
      : card.querySelector('.product-cart-button-added');

    if (!addedToCartButton) {
      return;
    }

    if (id === cardId && action === 'add') {
      addToCartButton.hidden = true;
      addedToCartButton.hidden = false;
    }

    if (id === cardId && action === 'remove') {
      addToCartButton.hidden = false;
      addedToCartButton.hidden = true;
    }
  })
}
