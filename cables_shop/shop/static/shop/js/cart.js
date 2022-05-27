var updateBtns = document.getElementsByClassName('btn-update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var itemId = this.dataset.item
        var action = this.dataset.action

        var user = document.getElementById('user').value
        console.log('USER:', user)
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated')
        } else {
            console.log('User is authenticated. Sending data...')
        }
    })
}