var updateBtns = document.getElementsByClassName('btn-update-cart')
// var cartItemsTotalIndicator = document.getElementById('CartItemsTotalIndicator')

const NOT_AUTHENTICATED_ACTION = 'not_authenticated'


for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = parseInt(this.dataset.product_id)
        var action = this.dataset.action

        var user = document.getElementById('user').value
        if (user == 'AnonymousUser') {
            sendJSONResponse(0, NOT_AUTHENTICATED_ACTION)
        } else {
            sendJSONResponse(productId, action)
        }
        updateTotalItemsIndicator(action)
    })
}


function sendJSONResponse(productId, action) {
    var url = '/updateCart/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action,
        })
    })

        .then((response) => {
            return response.json()
        })

        .then((data) => {
            location.reload()
        })
}