'use strict'

// <!--SUGGESTED SECTION-->
// Запуск слайдера вперше, додавання кнопок управління ітд.
document.addEventListener('DOMContentLoaded', () => {
  sliderForCards();
});

// SET TOTAL PRICE ON DELETING PRODUCT FROM CART
function setTotalPrice(card) {
  const price = card.dataset.productNewPrice
    ? +card.dataset.productNewPrice
    : +card.dataset.productUnitPrice;
  const amount = +card.querySelector('.count').innerText;

  const totalPriceElement = document.querySelector('.cart-total-price');
  const oldTotalPrice = +totalPriceElement.innerText;
  const newTotalPrice = oldTotalPrice - (amount * price);
  totalPriceElement.textContent = newTotalPrice.toFixed(2);
}
