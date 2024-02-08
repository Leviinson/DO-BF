'use strict'

// SOCIALS BUTTONS
// SCROLL UP
// Получаем ссылку на кнопку прокрутки вверх
const scrollButton = document.getElementById('scroll-up');

// Добавляем обработчик события при клике на кнопку
scrollButton.addEventListener('click', function (e) {
  e.preventDefault(); // Предотвращаем переход по ссылке

  // Получаем текущую позицию прокрутки
  let currentPosition = window.pageYOffset || document.documentElement.scrollTop;

  // Определяем, насколько далеко нужно прокрутить страницу к верху
  let scrollStep = currentPosition / 20; // Здесь можно настроить скорость прокрутки

  // Запускаем анимацию прокрутки
  function scrollToTop() {
    currentPosition -= scrollStep;

    // Прокручиваем страницу
    window.scroll(0, currentPosition);

    // Если еще не достигли верха страницы, продолжаем анимацию
    if (currentPosition > 0) {
      window.requestAnimationFrame(scrollToTop);
    }
  }

  // Запускаем анимацию прокрутки
  scrollToTop();
});


// FEEDBACK-SHOW SOCIALS BUTTONS
const openCtaGroup = document.getElementById('open-cta');

const contactUsBtnGroup = document.querySelector('.contact-us-btn-group');

openCtaGroup.addEventListener('click', () => {
  contactUsBtnGroup.classList.toggle('show-contact-us-btn-group');
});
