'use strict'

document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', async (event) => {
    const addButton = event.target.closest('.add-to-cart');
    if (!addButton) {
      return;
    }

    const card = event.target.closest('.product-card');
    const id = card.dataset.productId;
    const csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const amountElement = card.querySelector('.count');
    const amount = amountElement ? +amountElement.textContent : 1;
    const isProductPage = card.classList.contains('product-data-container');
    const action = 'increace';
    const region = card.dataset.region;
    const isBouquet = card.dataset.isBouquet.toLowerCase() === "true";
    
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfmiddlewaretoken,
        }
      };

      let response
      if (isProductPage && isBouquet) {
        const bouquetSize = parseInt(card.dataset.selectedSize);
        if (!isNaN(bouquetSize) && bouquetSize % 1 === 0) {
          response = await axios.post(
            `/${region}/cart/`,
            { id, amount, csrfmiddlewaretoken, bouquet_size: bouquetSize },
            config
          );
        }
      } else {
        response = await axios.post(
          `/${region}/cart/`,
          { id, amount, csrfmiddlewaretoken},
          config
        );
      }
      
      addButton.style.display = "none";
      setTotalCount(card, action);

      if (isProductPage) {
        const addedToCartButton = document.querySelector('.product-cart-button-added');
        if(addedToCartButton) {
          addedToCartButton.hidden = false;
        }
      }
      
      if (!isProductPage) {
        const addedToCartButton = card.querySelector('.button-added-to-cart');

        addTemporaryToCart(card);
        if(addedToCartButton) {
          addedToCartButton.hidden = false;
        }
        increaseTotalPrice(card);
      }

      checkIsSameCardOnPage(id, 'add');
    } catch (error) {
      console.error('Помилка POST-запиту:', error);
    }
  });
});

function addTemporaryToCart(card) {
//   const cartElement = document.querySelector('.cart-cards-container');
  const cartOrder = document.querySelector('.order-cards-container');
  const cartSelected = document.querySelector('.order-selected-cards-container');
  const cartTotalPrice = document.getElementById("cartTotalPrice");

//   if (!cartElement) {
//     return;
//   }

  const cardData = card;
  const article = cardData.dataset.productArticle;
  const image = cardData.dataset.productImage;
  const name = cardData.dataset.productTitle;
  const newPrice = cardData.dataset.productDiscountPrice;
  const unitPrice = cardData.dataset.productPrice;
  const id = cardData.dataset.productId;
  const currency = cardData.dataset.productCurrency;
  const discount = +cardData.dataset.productDiscount || 0;
  const isBouquet = cardData.dataset.isBouquet;

//   cartElement.insertAdjacentHTML('beforeend', `
//     <div
//       class="card-l product-card product-card-temporary"
//       data-product-id="${id}"
//       data-product-new-price="${newPrice}"
//       data-product-unit-price="${unitPrice}"
//       data-is-bouquet="${isBouquet}"
//     >
//       ${discount
//         ? `<div class="discount">
//             <p class="p-16-auto-medium white">
//               ${discount}%
//             </p>
//           </div>`
//         : ''
//       }
//       <a href="${url}">
//         <div class="img-box">
//           <img
//             src="${image}"
//             alt="${name}"
//             itemprop="image"
//           />
//         </div>
//       </a>
//       <div class="prod-desc" itemprop="description">
//         <div class="card-top">
//           <div class="prod-title">
//             <h3 class="h2-24-auto-bold" itemprop="name">${name}</h3>
//             <p class="p-16-auto-regular">Артикул: ${article}</p>
//           </div>
//           <div class="card-btn">
//             <button class="delete-button icon remove-from-cart"></button>
//           </div>
//         </div>
//         <div class="card-bottom">
//           <div class="prod-price">
//             <div class="current-price">
//               <p class="p-16-auto-regular">Ціна:</p>
//               <p class="h2-24-auto-bold red">
//                 <span itemprop="price">${newPrice ? newPrice : unitPrice }</span>
//                 <span>${currency}</span>
//               </p>
//             </div>
//             <div class="old-price">
//               <p class="p-16-auto-medium grey">
//                 <span itemprop="price">${newPrice ? unitPrice : ''}</span>
//                 <span>${newPrice ? currency : ''}</span>
//               </p>
//             </div>
//           </div>
//           <div class="counter">
//             <button class="decrement icon grey"></button>
//             <span class="count p-14-auto-medium">1</span>
//             <button class="increment icon red"></button>
//           </div>
//         </div>
//       </div>
//     </div>
//   `);


  cartOrder.insertAdjacentHTML('beforeend', `
    <div class="card-xs product-card"
        data-product-id="${id}"
        data-product-new-price="${newPrice}"
        data-product-unit-price="${unitPrice}"
        data-product-price="${newPrice}"
        data-product-currency="${currency}"
        data-product-discount-price="${newPrice}"
        data-product-discount="${newPrice}"
        data-product-image="${image}"
        data-product-article="${article}"
        data-product-title="${name}"
        data-is-bouquet="${isBouquet}"
    >
      <div class="img-box">
        <img src="${image}" alt="Назва квітки" />
      </div>
      <div class="prod-desc">
        <div class="card-top">
          <div class="prod-title">
            <h3 class="h2-24-auto-medium">
                ${name}
            </h3>
          </div>
        </div>
        <div class="card-bottom">
          <div class="prod-price">
            <div class="current-price">
              <p class="h2-24-auto-medium red">
                ${newPrice} $
              </p>
            </div>
            <div class="old-price">
              <p class="p-16-auto-medium grey">
                ${unitPrice} $
              </p>
            </div>
          </div>
          <div class="card-btn">
                <button class="delete-button icon remove-from-cart" type="button"></button>
            </div>
          <div class="counter">
            <button class="decrement icon grey" type="button"></button>
            <span class="count p-14-auto-medium">
                1
            </span>
            <button class="increment icon red" type="button"></button>
          </div>
        </div>
      </div>
    </div>
  `);
   

  cartSelected.insertAdjacentHTML('beforeend', `
    <div class="card-s"
        data-product-id="${id}"
        data-product-new-price="${newPrice}"
        data-product-unit-price="${unitPrice}"
        data-product-price="${newPrice}"
        data-product-currency="${currency}"
        data-product-discount-price="${newPrice}"
        data-product-discount="${newPrice}"
        data-product-image="${image}"
        data-product-article="${article}"
        data-product-title="${name}"
        data-is-bouquet="${isBouquet}"
    >
        <div class="img-box">
            <img class="quick-order-modal-card-img" src="${image}" alt="${name}" />
        </div>
        <div class="prod-desc">
            <div class="card-top">
            <div class="prod-title">
                <h3 class="p-16-auto-medium quick-order-modal-card-title">${name}</h3>
                <p class="p-14-auto-regular quick-order-modal-card-article">Артикул: ${article}</p>
            </div>
            </div>
            <div class="card-bottom">
            <div class="prod-price">
                <div class="current-price">
                    <p class="p-14-auto-regular">Ціна:</p>
                    <p class="p-16-auto-medium red quick-order-modal-card-price">
                        ${newPrice} ${currency}
                    </p>
                </div>
                <div class="old-price">
                    <p class="p-16-auto-medium grey">
                        ${unitPrice} ${currency}
                    </p>
                </div>
            </div>
            <div class="product-count" id="counter">
                <p class="p-14-auto-medium"><span id="orderSpanCount${id}">1</span> шт.</p>
            </div>
            </div>
        </div>
    </div>
  `);
}