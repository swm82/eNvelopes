
// TODO: catch errors
// TODO: input validation
$('#add-cash-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) 
    var category = button.data('category') 
    var modal = $(this)
    modal.find('#modal-category').val(category)
})

$('#add-transaction-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) 
    var category = button.data('category')
    var modal = $(this)
    const title = modal.find('.modal-title').text('Add Income')
    if (button.data('inflow')) {
    title.text('Add Income')
    } else {
    title.text('Add Transaction')
    }
    modal.find('#transaction-category').val(category)
})

window.addEventListener('load', (e) => {
    // let loader = document.querySelector('.loader')
    // let container = document.querySelector('.layout-content')
    // let loading_logo = document.querySelector('.loading-logo')
    url = 'http://127.0.0.1:5000/api'
    fetch(url)
    .then(response=> response.json())
    .then(data => {
        data['categories'].forEach(item =>  {
        if (item['name'] !== 'Inflow') addEnvelope(item)
        else {
            unbudgeted_amount = document.getElementById('unbudgeted-amount')
            unbudgeted_amount.textContent = '$' + (item['amount']/100)
            unbudgeted_amount.id = `${item['id']}-amount`
            unbudgeted_amount.setAttribute('data-category', item['id'])
            // TODO: add income modal
        }
        })
        let payee_selector = document.getElementById('payee-list')
        data['payees'].forEach(item => {
        let choice = document.createElement('option')
        choice.textContent = item['name']
        payee_selector.appendChild(choice)
        })
        // setTimeout(() => loading_logo.style.animation = 'shrink .5s ease-in-out', 2000)
        // setTimeout(() => container.removeChild(loader), 2500)
    })
})

document.querySelector('#add-cash-button').addEventListener('click', e => {
    const url = 'http://127.0.0.1:5000/api/add_to_category'
    const button = e.target;
    const category_id = button.nextElementSibling.value
    const amount_input = document.querySelector('#add-cash-amount')
    const amount = amount_input.value
    amount_input.value = ''
    const data = {'category_id': category_id, 'amount': amount}
    const resp = sendPostRequest(url, data)
    resp.then(result =>  {
        const category_amount = parseInt(result['category_amount']) / 100
        const inflow_amount = parseInt(result['inflow_amount']) / 100
        const inflow_card = document.querySelector('.unbudgeted-amount')
        const card_to_update = document.getElementById(`${category_id}-amount`)
        card_to_update.textContent = '$' + category_amount
        card_to_update.style.transform = 'scale(1.7)'
        inflow_card.textContent = '$' + inflow_amount
        inflow_card.style.transform = 'scale(1.7)'
        setTimeout(() => {
        card_to_update.style.transform = 'scale(1.0)'
        inflow_card.style.transform = 'scale(1.0)'
        }, 200)
    })
})

const sendPostRequest = (url, data) => {
    const request = fetch(url, {
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    method: 'POST',
    body: JSON.stringify(data)
    })
    return request.then(response => response.json())
}

document.getElementById('submit-transaction').addEventListener('click', e => {
    url = 'http://127.0.0.1:5000/api/add_transaction'
    category_id = document.getElementById('transaction-category').value
    amount_input = document.getElementById('transaction-amount')
    amount = amount_input.value
    amount_input.value = ''
    payee = document.querySelector('#transaction-payee').value
    data = {'category': category_id, 'amount': amount}
    if (payee) {
    data['payee_name'] = payee
    }
    const resp = sendPostRequest(url, data)
    resp.then(result =>  {
    amount =  parseInt(result['category_amount']) / 100
    category = result['category_id']
    let card_to_update = document.getElementById(`${category}-amount`)
    card_to_update.textContent = '$' + amount
    card_to_update.style.transform = 'scale(1.7)'
    setTimeout(() => card_to_update.style.transform = 'scale(1.0)', 200)
    })
})


document.getElementById('add-category-button').addEventListener('click', e => {
    url = 'http://127.0.0.1:5000/api/add_category'
    name_field = document.getElementById('new-category-name')
    data = { 'name': name_field.value }
    const resp = sendPostRequest(url, data)
    resp.then(result =>  {
    addEnvelope(result)
    })
    name_field.value = ""
})

function removeEnvelope(category) {
    let card_to_delete = document.getElementById(`${category}-card`)
    let container = card_to_delete.parentNode
    url = 'http://127.0.0.1:5000/api/delete_category'
    data = { 'id': category }
    const resp = sendPostRequest(url, data)
    resp.then(result =>  {
    unbudgeted_amount = document.querySelector('.unbudgeted-amount')
    unbudgeted_amount.textContent = '$' + (result['inflow_amount']/100)
    container.removeChild(card_to_delete)
    })
}

const updateAmount = (selector, amount) => {
    const to_update = document.querySelector(selector)
    to_update.textContent = '$' + (amount / 100)
}

function addEnvelope(data) {
    let name = data['name']
    let amt = '$' + (parseInt(data['amount'])/100)
    let id = data['id']
    let container = document.querySelector('#envelopes')
    let add_card = document.querySelector('#add-category-card')
    const card = newElement('article','test2 card bg-light col-md-3 col-sm-6 m-2')
    card.id = `${id}-card`
    const action_buttons = newElement('div', 'd-flex justify-content-between')
    const delete_button = newElement('button', 'btn btn-danger mt-3 mr-3 round-button')
    delete_button.addEventListener('click', () => removeEnvelope(id))
    delete_button.innerHTML = '<i class="far fa-trash-alt"></i>'
    const add_transaction_button = newElement('button','btn btn-success mt-3 round-button')
    addAttributes(add_transaction_button, {'data-toggle': 'modal', 'data-target': '#add-transaction-modal', 'data-category': id })
    add_transaction_button.innerHTML = '<i class="fas fa-plus"></i>'
    appendInOrder(action_buttons, [delete_button, add_transaction_button])

    const card_body = newElement('div', 'card-body text-center')
    const card_title = newElement('h1', 'card-title')
    addText(card_title, name)
    const amount_button = newElement('button','btn btn-primary amount-button')
    addAttributes(amount_button, {'data-toggle': 'modal', 'data-target': '#add-cash-modal', 'data-category': id })
    amount_button.id = `${id}-amount`
    addText(amount_button, amt)
    appendInOrder(card_body, [card_title, amount_button])
    appendInOrder(card, [action_buttons, card_body])
    container.insertBefore(card, add_card)
}

const appendInOrder = (parent, children) => {
    for (child of children) {
        parent.appendChild(child)
    }
}

const newElement = (tag, className) => {
    const el = document.createElement(tag)
    el.className = className
    return el
}

const addAttributes = (el, attrs) => {
    for (const attr in attrs) {
    el.setAttribute(attr, attrs[attr])
    }
}

const addText = (el, text) => {
    const textNode = document.createTextNode(text)
    el.appendChild(textNode)
}

