'use strict'
// HEADER-desktop

// SEARCH-RESULTS
document.addEventListener('DOMContentLoaded', () => {
    const searchInputs = document.querySelectorAll('.search-input-trigger');
    const searchResultsContainers = document.querySelectorAll('.search-results-container');

    if (searchInputs.length !== searchResultsContainers.length) {
      console.error('Number of search inputs does not match the number of result containers.');
      return; // Stop execution if the number of inputs and containers don't match.
    }

    searchInputs.forEach((searchInput, index) => {
      const searchResultContainer = searchResultsContainers[index];
      
      document.addEventListener('click', (event) => {
        const activeTrigger = event.target.closest('.search-input-trigger');
  
        if (!event.target.closest('.search-results-container') && !activeTrigger) {
          closeDropdown(searchResultContainer);
        }
  
        if (activeTrigger) {
          searchInputs.forEach((trigger, i) => {
            if (activeTrigger !== trigger) {
              closeDropdown(searchResultsContainers[i]);
            }
          });
        }
      });
  
      searchInput.addEventListener('focus', () => {
        const dropdownHeight = '380px';
        openDropdown(searchResultContainer, dropdownHeight);
      });
    });

    const returnedScrollFunction = debounce(closeAllDropdowns, 500);
    window.addEventListener('scroll', returnedScrollFunction);
  
    function closeAllDropdowns() {
      searchResultsContainers.forEach(container => {
        closeDropdown(container);
      });
    }
})

// HEADER-CATEGORIES
document.addEventListener('DOMContentLoaded', () => {
  const productCategoriesTriggers = document.querySelectorAll('.product-categories-container-trigger');
  const productCategoriesContainers = document.querySelectorAll('.product-categories-container');

  if (productCategoriesTriggers.length !== productCategoriesContainers.length) {
    console.error('Number of product categories triggers does not match the number of product categories containers.');
    return; 
  }

  document.addEventListener('click', (event) => {
    const activeTrigger = event.target.closest('.product-categories-container-trigger');

    if (!event.target.closest('.product-categories-container') && !activeTrigger) {
      closeAllDropdowns();
    }

    if (activeTrigger) {
      productCategoriesTriggers.forEach((trigger, i) => {
        if (activeTrigger !== trigger) {
          closeDropdown(productCategoriesContainers[i]);
        } else {
          const dropdownHeight = '460px';
          openDropdown(productCategoriesContainers[i], dropdownHeight);
        }
      });
    }
  });

  const returnedScrollFunction = debounce(closeAllDropdowns, 200);
  window.addEventListener('scroll', returnedScrollFunction);

  function closeAllDropdowns() {
    productCategoriesContainers.forEach(container => {
      closeDropdown(container);
    });
  }
});

function closeDropdown(productCategoriesContainer) {
  productCategoriesContainer.style.maxHeight = '0';
  productCategoriesContainer.style.opacity = '0';
  productCategoriesContainer.style.pointerEvents = 'none';
  setTimeout(() => {
    productCategoriesContainer.style.display = 'none';
  }, 200); // Adjust the time to match your animation duration.

  productCategoriesContainer.classList.remove('open');
}

function openDropdown(productCategoriesContainer, dropdownHeight) {
  productCategoriesContainer.style.display = 'flex';
  setTimeout(() => {
    productCategoriesContainer.style.maxHeight = dropdownHeight;
    productCategoriesContainer.style.opacity = '1';
    productCategoriesContainer.style.pointerEvents = 'auto';
  }, 10); // Wait for the container to be displayed before animating.

  productCategoriesContainer.classList.add('open');
}

// MENU-MOBILE

let startX; // Начальная координата касания
const menu = document.getElementById('menu-header');
const body = document.querySelector('body');

function toggleMenu() {
  menu.classList.toggle('menu-open');
  body.classList.toggle('menu-opened');
}

function closeMenu() {
  menu.classList.remove('menu-open');
  body.classList.remove('menu-opened');
}

document.addEventListener('DOMContentLoaded', () => {
  // Обработчик события касания (touchstart)
  document.addEventListener('touchstart', function (e) {
    startX = e.touches[0].clientX; // Записываем начальную координату касания
  });

  // Обработчик события завершения касания (touchend)
  document.addEventListener('touchend', function (e) {
    const endX = e.changedTouches[0].clientX; // Получаем конечную координату касания
    const menuOpen = menu.classList.contains('menu-open');

    // Если меню открыто и пользователь свайпнул справа налево
    if (menuOpen && endX < startX) {
      closeMenu();
    }
  });

  const trigger = document.querySelector('.header-menu-trigger');
  trigger.addEventListener('click', toggleMenu);

  const overlay = document.getElementById('overlay');
  overlay.addEventListener('click', closeMenu);
});

// HEADER-AUTO-MARGIN

document.addEventListener('DOMContentLoaded', () => {
  const headerElement = document.querySelector('header');

  // Если элемент <header> найден
  if (headerElement) {
    // Находим следующий элемент с помощью nextElementSibling
    const nextElement = headerElement.nextElementSibling;

    // Если следующий элемент найден, добавляем класс "header-margin"
    if (nextElement) {
      nextElement.classList.add('header-margin');
    }
  }
});

// HEADER SCROLL HIDING
// Функціонал для хедера, щоб він частково ховався при скролі вниз і з'являвся
// при скролі вгору і наведенні на нього
document.addEventListener('DOMContentLoaded', () => {
  let lastScrollTop = 0;
  // let isMouseOverHeader = false;

  // Отримуємо посилання на елемент хедера
  const header = document.querySelector(".header-desktop");
  const headerAccordions = document.querySelectorAll('.accordion-button-header');

  // Додаємо обробник події наведення мишки на хедер
  header.addEventListener("mouseenter", () => {
    // isMouseOverHeader = true;
    // Показуємо хедер
    header.classList.remove("header-desktop-hidden");
  });

  header.addEventListener("click", () => {
    // isMouseOverHeader = true;
    header.classList.remove("header-desktop-hidden");
  });

  window.addEventListener("scroll", () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop) {
      // Скролінг вниз, приховати хедер
      document.querySelector(".header-desktop").classList.add("header-desktop-hidden");
      // Перевіряємо, чи акордеони згорнуті, і згортаємо його, якщо ні
      headerAccordions.forEach((accordion) => {
        if (!accordion.classList.contains('collapsed')) {
          accordion.click(); // Клік на акордеоні, щоб згорнути його
        }
      });

      // Отримуємо активний елемент
      const activeElement = document.activeElement;

      // Знімаємо фокус з активного елемента щоб сховались дропдаун чи сьорч вспливаючі вікна
      if (activeElement) {
        activeElement.blur();
      }
    } else {
      // Скролінг вгору, показати хедер
      document.querySelector(".header-desktop").classList.remove("header-desktop-hidden");
    }

    lastScrollTop = scrollTop;
  });
})

// SEARCH-INPUT-DEBOUNCE
// Функціонал який дозволяє дочекатися доки користувач повністю введе 
// те що шукає в search-input щоб не робити зайвих запитів на сервер
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('.search-input-trigger');
  const searchInputModal = document.querySelector('.search-input-trigger-mobile');
  const searchInputContent = document.querySelector('.search-results-container');
  const searchInputContentMobile = document.querySelector('.search-container-mobile');
  const currency = document.querySelector('.header-container').dataset.currencyName;
  const region = document.querySelector('.header-container').dataset.region;

  function createSearchHandler(inputElement) {
    return debounce(async function () {
      const trimmedValue = inputElement.value.trim();
      if (!trimmedValue) {
        return;
      }
      try {
        const response = await axios({
          url: `/product/${region}/`,
          params: { search: trimmedValue, currency },
        });

        if (response.data.results) {
          const { results } = response.data;
          searchInputContent.innerHTML = loyautXSCard(results);
          searchInputContentMobile.innerHTML = loyautXSCard(results);
        }
      } catch (error) {
        console.error('Помилка POST-запиту:', error);
      }
    }, 2000);
  }

  const searchInputHandler = createSearchHandler(searchInput);
  const searchInputModalHandler = createSearchHandler(searchInputModal);

  if (searchInput) {
    searchInput.addEventListener('input', searchInputHandler);
  }

  if (searchInputModal) {
    searchInputModal.addEventListener('input', searchInputModalHandler);
  }
});

function debounce(func, wait, immediate) {
  let timeout;

  // Ця функція викликається, коли подія DOM викликана.
  return function executedFunction() {
    const context = this;
    const args = arguments;

    // Функція, яка викликається після закінчення часу debounce.
    const later = function () {
      // Нульовий timeout, щоб вказати що debounce закінчилася.
      timeout = null;

      // Викликаємо функцію, якщо immediate !== true,
      // тобто ми викликаємо функцію в кінці, після wait часу.
      if (!immediate) func.apply(context, args);
    };

    // Визначаємо чи потрібно викликати функцію спочатку.
    const callNow = immediate && !timeout;

    // clearTimeout зкидує очікування при кожному виконанні функції.
    // Це крок, який не дозволяє виконання функції.
    clearTimeout(timeout);

    // Перезапускаємо період очікування debounce.
    // setTimeout повертає істинне значення / truthy value
    // (воно відрізняється в web и node)
    timeout = setTimeout(later, wait);

    // Викликаємо функцію спочатку, якщо immediate === true
    if (callNow) func.apply(context, args);
  };
};

// Функція для рендеру карточок типу XS
function loyautXSCard(productsList) {
  return (
    `
      <ul>
        ${productsList.map((product) => `
          <li>
            <a class="card-xs" href="${product.url}">
              ${product.discount
                ? `<div class="discount">
                    <p class="p-16-auto-medium white">
                      ${product.discount}%
                    </p>
                  </div>`
                : ''
              }
              <div class="img-box">
                <img src="${product.image_url}" alt="${product.Name}" />
              </div>
              <div class="prod-desc">
                <div class="card-top">
                  <div class="prod-title">
                    <h3 class="p-16-auto-bold">
                    ${product.Name}
                    </h3>
                    <p class="p-16-auto-regular">
                      Артикул: ${product.sku}
                    </p>
                  </div>
                </div>
                <div class="card-bottom">
                  <div class="prod-price">
                    <div class="current-price">
                      <p class="p-16-auto-regular">
                        Ціна:
                      </p>
                      <p class="p-16-auto-bold red">
                        ${product?.new_price
        ? product.new_price + ` ${product.currency_symbol}`
        : product.unit_price + ` ${product.currency_symbol}`
      }
                      </p>
                    </div>
                    <div class="old-price">
                      <p class="p-14-auto-medium grey">
                        ${product?.new_price ? product.unit_price + ` ${product.currency_symbol}` : ''}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </a>
          </li>
        `).join('')}
      </ul>
    `
  );
};
