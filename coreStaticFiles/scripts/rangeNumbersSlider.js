'use strict';

// RANGE-FROM-TO-SLIDER
// Слайдер-повзунок для інпутів типу намбер
(function () {
  const sliders = document.querySelectorAll('#rangeSlider');

  sliders.forEach(function (parent) {
    const rangeS = parent.querySelectorAll('input[type=range]');
    const numberS = parent.querySelectorAll('input[type=number]');

    rangeS.forEach(function (el) {
      el.oninput = function () {
        let slide1 = parseFloat(rangeS[0].value);
        let slide2 = parseFloat(rangeS[1].value);

        if (slide1 > slide2) {
          [slide1, slide2] = [slide2, slide1];
        }

        numberS[0].value = slide1;
        numberS[1].value = slide2;
      };
    });

    numberS.forEach(function (el) {
      el.oninput = function () {
        let number1 = parseFloat(numberS[0].value);
        let number2 = parseFloat(numberS[1].value);

        if (number1 > number2) {
          let tmp = number1;
          numberS[0].value = number2;
          numberS[1].value = tmp;
        }

        rangeS[0].value = number1;
        rangeS[1].value = number2;
      };
    });
  });
})();