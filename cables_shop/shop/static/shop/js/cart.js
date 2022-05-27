var updateBtns = document.getElementsByClassName('btn-update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var itemId = this.dataset.item_id
        var action = this.dataset.action

        var user = document.getElementById('user').value
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated')
        } else {
            updateUserOrder(itemId, action)
        }
    })
}

function updateUserOrder(itemId, action) {
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'itemId': itemId,
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
