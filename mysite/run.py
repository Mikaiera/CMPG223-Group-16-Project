from website import create_app
from website.models import db, Order

app = create_app()

# with app.app_context():
#     db.create_all()
#     print(Order.query.all())
if __name__ == '__main__':
    app.run(port=80, debug=True)