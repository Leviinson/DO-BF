'use strict'

// COUNTER

document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', async (event) => {
    const decrementBtn = event.target.closest('.decrement');
    const incrementBtn = event.target.closest('.increment');
    const totalCountElements = document.querySelectorAll('.products-count');
    const totalPriceElement = document.querySelector('.cart-total-price');
    if (!decrementBtn && !incrementBtn) {
      return;
    }

    const card = event.target.closest('.product-card');
    const countSpan = card.querySelector('.count');
    const totalOrderElement = document.getElementById("orderSpanCount"+card.dataset.productId);
    
    const price = card.dataset.productNewPrice
    ? +card.dataset.productNewPrice
    : +card.dataset.productUnitPrice;

    let newTotalPrice;
    if (totalPriceElement) {
      newTotalPrice = +totalPriceElement.textContent;
    }

    let count = +countSpan.textContent || 1;
    let totalCount = +totalCountElements[0].innerText;
    let totalOrderCount = +totalOrderElement.innerText;
    
    

    if (decrementBtn && count <= 1) {
      return;
    }

    const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const id = card.dataset.productId;
    // const region = document.querySelector('.cart-cards-container').dataset?.region || '';
    const region = document.querySelector('.header-container').dataset.region;


    count = decrementBtn ? count - 1 : count + 1;
    totalCount = decrementBtn ? totalCount - 1 : totalCount + 1;
    totalOrderCount = decrementBtn ? totalOrderCount - 1 : totalOrderCount + 1;

    if (totalPriceElement) {
      newTotalPrice = decrementBtn ? newTotalPrice - price : newTotalPrice + price;
    }

    const action = decrementBtn ? 'decreace' : 'increace';
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
          requestBody = { id, amount: count, csrfmiddlewaretoken, bouquet_size: bouquetSize };
        } else {
          requestBody = { id, amount: count, csrfmiddlewaretoken };
        }
         
      } else {
          requestBody = { id, amount: count, csrfmiddlewaretoken };
      }
      
      const response = await axios.put(
        `/${region}/cart/`,
        requestBody,
        config
      );

      if (response.status === 204) {
        countSpan.textContent = count;
        totalCountElements[0].innerText = totalCount;
        totalCountElements[1].innerText = totalCount;

        if (totalPriceElement) {
          totalPriceElement.innerText = newTotalPrice.toFixed(2);
        }
        
        setTotalCount2(card, action);
        if(totalOrderElement) {
          totalOrderElement.innerText = totalOrderCount;
        }
      }

      // if (response.status === 204 && decrementBtn && totalPriceElement) {
      //   decreaseTotalPrice(card);
      // }

      // if (response.status === 204 && incrementBtn && totalPriceElement) {
      //   increaseTotalPrice(card);
      // }
    } catch (error) {
      console.error('Помилка PUT-запиту:', error);
    }
  })
});
