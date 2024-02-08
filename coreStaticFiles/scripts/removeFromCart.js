'use strict'

// deleting product from cart
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', async (event) => {
    const removeButton = event.target.closest('.remove-from-cart');

    if (!removeButton) {
      return;
    }

    const card = event.target.closest('.product-card');
    const id = card.dataset.productId;
    const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const isProductPage = card.classList.contains('product-data-container');
    const action = 'delete';
    const region = card.dataset.region
    const isBouquet = card.dataset.isBouquet.toLowerCase() === "true";
    
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfmiddlewaretoken,
        }
      };

      let requestBody
      if (isBouquet) {
        const bouquetSize = parseInt(card.dataset.selectedSize);
        if (!isNaN(bouquetSize) && bouquetSize % 1 === 0) {
          requestBody = { id, csrfmiddlewaretoken, bouquet_size: bouquetSize }
        } else {
          requestBody = { id, csrfmiddlewaretoken }
        }
      } else {
        requestBody = { id, csrfmiddlewaretoken }
      }
    const response = await axios.delete(
      `/${region}/cart/`,
      {
        data: requestBody,
        headers: config.headers
      }
    );

      if (response && isProductPage) {
        const addButton = card.querySelector('.add-to-cart');
        const addedToCartButton = card.querySelector('.product-cart-button-added');
        const count = card.querySelector('.count');

        addButton.hidden = false;
        addedToCartButton.hidden = true;
        setTotalCount(card, action);
        count.textContent = '1';
      }
      if (response && !isProductPage) {
        setTotalPrice(card);
        setTotalCount(card, action);

        card.classList.add('cart-remove-product');
        setTimeout(() => {
          card.remove();
        }, 300);
      }

      checkIsSameCardOnPage(id, 'remove');
    } catch (error) {
      console.error('Помилка DELETE-запиту:', error);
    }
  });
})