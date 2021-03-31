window.addEventListener('load', (e) => {
    url = 'http://127.0.0.1:5000/api/transactions'
    fetch(url)
        .then(response=> response.json())
        .then(data => {
            const transactions = document.querySelector('#transactions-body')
            // const firstTransaction = transactions.firstChild
            data.forEach(transaction => addTransaction(transactions, transaction))
        })
})

const addTransaction = (container, transaction, before) => {
    let row = newElement('tr')
    let category = newElement('td', 'transaction-category')
    addText(category, transaction['category_name'] ? transaction['category_name'] : '')
    let payee = newElement('td', 'transaction-payee')
    addText(payee, transaction['payee_name'] ? transaction['payee_name'] : '')
    let amount = newElement('td', 'transaction-amount')
    addText(amount, transaction['category_name'] == 'Inflow' ? `$${(parseInt(transaction['amount']) / 100) * - 1}` :`$${parseInt(transaction['amount']) / 100}`)
    amount.style.color = transaction['amount'] < 0 ? 'green' : 'red'
    let time = newElement('td', 'transaction-time')
    addText(time, transaction['time'])
    let delete_button = newElement('button', 'btn btn-danger')
    delete_button.addEventListener('click', e => deleteTransaction(e))
    addText(delete_button, 'Delete')
    const id = document.createElement('input')
    id.setAttribute('type', 'hidden')
    id.setAttribute('value', transaction['id'])
    appendInOrder(row, [category, payee, amount, time, delete_button, id])
    container.appendChild(row)
}

const deleteTransaction = (e) => {
    const curr_button = e.target
    const id = curr_button.nextSibling.getAttribute('value')
    // API DELETE
    url = 'http://127.0.0.1:5000/api/delete_transaction'
    data = {'transaction_id': id}
    fetch(url, {
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result =>  {
        })

    row = curr_button.parentNode
    table = document.querySelector('#transactions-body')
    table.removeChild(row)
}


const appendInOrder = (parent, children) => {
    for (child of children) {
        parent.appendChild(child)
    }
}

const newElement = (tag, className) => {
    const el = document.createElement(tag)
    if (className) el.className = className
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
