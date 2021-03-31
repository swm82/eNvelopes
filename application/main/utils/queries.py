from ...models import User, Category, Transaction, Payee

def get_categories(user): 
    results = Category.query.filter_by(user_id=user).all()
    categories = { x.category_id: { 'name': x.name, 'amount': x.amount } for x in results }
    return categories



