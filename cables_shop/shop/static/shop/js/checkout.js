var deliveryRadioBtns = document.getElementsByName('radioDeliveryType');
var deliveryPriceBlock = document.getElementsByClassName('delivery-price-block')[0];
var cartTotalPriceBlock = document.getElementById('cartTotalPriceBlock');

var addressInformationBlocks = document.getElementsByClassName('address-information-block');

// Prices 
var cartTotalPrice = parseInt(document.getElementById('cartTotalPrice').value);
var deliveryPrice = parseInt(document.getElementById('deliveryPrice').value);


// Event listener for radio buttons on change
for (var i = 0; i < deliveryRadioBtns.length; i++) {
    deliveryRadioBtns[i].addEventListener('change', function () {
        var deliveryType = this.value

        if (deliveryType == 'delivery') {
            deliveryPriceBlock.classList.remove('d-none')

            for (var i = 0; i < addressInformationBlocks.length; i++) {
                addressInformationBlocks[i].classList.remove('d-none')
            }

            cartTotalPriceBlock.innerText = cartTotalPrice + deliveryPrice
        } else if (deliveryType == 'selfPickUp') {
            deliveryPriceBlock.classList.add('d-none')

            for (var i = 0; i < addressInformationBlocks.length; i++) {
                addressInformationBlocks[i].classList.add('d-none')
            }

            cartTotalPriceBlock.innerText = cartTotalPrice
        }
    })
}