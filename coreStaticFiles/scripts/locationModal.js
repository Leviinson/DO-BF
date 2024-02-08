'use strict'

// PLACE AUTOCOMPLETE

let autocompleteCountryLocation;
let autocompleteRegionLocation;
let autocompleteCityLocation;
let autocompleteCountry;
let autocompleteRegion;
let autocompleteCity;
let autocompleteAddress;

let selectedPlace;
let countryLocation = '';
let regionLocation = '';
let cityLocation = '';
let country = '';
let region = '';
let city = '';
const countryLocationElement = document.querySelector('#autocompleteCountryLocation');
const regionLocationElement = document.querySelector('#autocompleteRegionLocation');
const cityLocationElement = document.querySelector('#autocompleteCityLocation');
const countryElement = document.querySelector('#autocompleteCountry');
const regionElement = document.querySelector('#autocompleteRegion');
const cityElement = document.querySelector('#autocompleteCity');
const addressElement = document.querySelector('#autocompleteAddress');

const button = document.querySelector('.location-button');

let isLocation = false;

document.addEventListener('DOMContentLoaded', () => {
  window.initAutocomplete = initAutocomplete;
});

function initAutocomplete() {
  autocompleteCountryLocation = new google.maps.places.Autocomplete(
    countryLocationElement,
    {
      types: ["country"],
      fields: ["address_components", "name"],
    }
  );

  autocompleteRegionLocation = new google.maps.places.Autocomplete(
    regionLocationElement,
    {
      types: ["administrative_area_level_1", "administrative_area_level_2"],
      fields: ["address_components", "name"],
    }
  );

  autocompleteCityLocation = new google.maps.places.Autocomplete(
    cityLocationElement,
    {
      types: ["(cities)"],
      fields: ["address_components", "name"],
    }
  );

  if (addressElement) {
    autocompleteCountry = new google.maps.places.Autocomplete(
      countryElement,
      {
        types: ["country"],
        fields: ["address_components", "name"],
      }
    );

    autocompleteRegion = new google.maps.places.Autocomplete(
      regionElement,
      {
        types: ["administrative_area_level_1", "administrative_area_level_2"],
        fields: ["address_components", "name"],
      }
    );

    autocompleteCity = new google.maps.places.Autocomplete(
      cityElement,
      {
        types: ["(cities)"],
        fields: ["address_components", "name"],
      }
    );

    autocompleteAddress = new google.maps.places.Autocomplete(
      addressElement,
      {
        types: ["address"],
        fields: ["address_components", "name"],
      }
    );

    autocompleteCountry.addListener('place_changed', onPlaceChangedCountry);
    autocompleteRegion.addListener('place_changed', onPlaceChangedRegion);
    autocompleteCity.addListener('place_changed', onPlaceChangedCity);
    autocompleteAddress.addListener('place_changed', onPlaceChangedAddress);
  }

  autocompleteCountryLocation.addListener('place_changed', onPlaceChangedCountryLocation);
  autocompleteRegionLocation.addListener('place_changed', onPlaceChangedRegionLocation);
  autocompleteCityLocation.addListener('place_changed', onPlaceChangedCityLocation);
}

function onPlaceChangedCountryLocation() {
  isLocation = true;
  selectedPlace = autocompleteCountryLocation.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedRegionLocation() {
  isLocation = true;
  selectedPlace = autocompleteRegionLocation.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedCityLocation() {
  isLocation = true;
  selectedPlace = autocompleteCityLocation.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedCountry() {
  isLocation = false;
  selectedPlace = autocompleteCountry.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedRegion() {
  isLocation = false;
  selectedPlace = autocompleteRegion.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedCity() {
  isLocation = false;
  selectedPlace = autocompleteCity.getPlace();
  fillIn(selectedPlace);
}

function onPlaceChangedAddress() {
  isLocation = false;
  selectedPlace = autocompleteAddress.getPlace();
  fillIn(selectedPlace);
}

function fillIn(place) {
  let address1 = "";
  console.log(place);

  if (isLocation) {
    countryLocationElement.value = '';
    regionLocationElement.value = '';
    cityLocationElement.value = '';
  } else {
    countryElement.value = '';
    regionElement.value = '';
    cityElement.value = '';
    addressElement.value = '';
  }

  for (const component of place.address_components) {
    const componentType = component.types[0];

    switch (componentType) {
      case "street_number": {
        address1 += component.long_name;
        break;
      }

      case "route": {
        const hiddenAddres = document.querySelector('.order-address');
        const hiddenAddresValue = { street: component.long_name, building: address1 }
        address1 = `${component.long_name}${address1 ? ', ' + address1 : ''}`;
        addressElement.value = address1;
        hiddenAddres.value = JSON.stringify(hiddenAddresValue);
        console.log('hiddenAddres.value', hiddenAddresValue);
        break;
      }

      case "locality":
        if (isLocation) {
          cityLocationElement.value = component.long_name;
          cityLocation = component.long_name;
        } else {
          cityElement.value = component.long_name;
          city = component.long_name;
        }
        break;

      case "administrative_area_level_1":
        if (isLocation) {
          regionLocationElement.value = component.long_name;
          regionLocation = component.long_name;
        } else {
          regionElement.value = component.long_name;
          region = component.long_name;
        }
        break;

      case "administrative_area_level_2":
        if (isLocation) {
          regionLocationElement.value = component.long_name;
          regionLocation = component.long_name;
        } else {
          regionElement.value = component.long_name;
          region = component.long_name;
        }
        break;

      case "country":
        if (isLocation) {
          countryLocationElement.value = component.long_name;
          countryLocation = component.short_name;
        } else {
          countryElement.value = component.long_name;
          country = component.short_name;
        }
        break;
    }

    button.classList.toggle('disabled-button', !(countryLocationElement.value && regionLocationElement.value && cityLocationElement.value))
  }
}
