var cableTypeCheckboxes = document.getElementsByClassName('cable-type-filter')
var productCards = document.getElementsByClassName('cable-card')


// Cable Types filtering
for (var i = 0; i < cableTypeCheckboxes.length; i++) {
    cableTypeCheckboxes[i].addEventListener('change', function () {
        var cableTypeId = this.dataset.type_id

        if (this.checked) {
            for (var j = 0; j < productCards.length; j++) {
                var cardType = productCards[j].dataset.type

                if (cardType == cableTypeId) {
                    productCards[j].classList.remove('hide-product')

                }
            }
        } else {
            for (var j = 0; j < productCards.length; j++) {
                var cardType = productCards[j].dataset.type

                if (cardType == cableTypeId) {
                    productCards[j].classList.add('hide-product')
                }
            }
        }
    })
}