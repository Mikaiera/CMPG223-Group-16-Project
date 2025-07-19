import datetime

from website import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from website.config import Config

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
# from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_query = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.name}'


class ComicBook(db.Model):
    id = Column(Integer, primary_key=True)
    category = Column(String(100), unique=False, nullable=False)
    title = Column(String(100), unique=True, nullable=False)
    author = Column(String(100), unique=False, nullable=False)
    illustrator = Column(String(100), unique=False)
    price = Column(Float, nullable=False)
    release_date = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    description = Column(String(500), nullable=False)
    top_pick = Column(Boolean, nullable=True)

    title_query = Column(String, nullable=False, unique=True)
    category_query = Column(String, nullable=False)

    filename = Column(String, unique=True, nullable=False)

    # Relationships
    cart_items = db.relationship('Cart', backref='comic_book', lazy=True)
    wishlist_items = db.relationship('WishList', backref='comic_book', lazy=True)
    library_items = db.relationship('Library', backref='comic_book', lazy=True)
    
    def __repr__(self):
        return (f'Comic(Category: {self.category}, Title: {self.title},' +
                f' Author: {self.author}, Query: {self.title_query})')


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False, default=13)
    address = Column(String(200), nullable=False)
    country = Column(String, nullable=False)
    date_joined = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))

    # Relationships
    card_details = db.relationship('CardDetails', backref='owner', lazy=True)
    library = db.relationship('Library', backref='bought_by', lazy=True)
    cart = db.relationship('Cart', backref='buyer', lazy=True)
    wishlist = db.relationship('WishList', backref='buyer', lazy=True)

    def get_reset_token(self, expiry_time=300):
        s = Serializer(Config.SECRET_KEY, expiry_time)
        return s.dumps({'user_id': self.id}).decode()

    @staticmethod
    def verify_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id

    def __repr__(self):
        return f'User(ID: {self.id}, Email: {self.email})'


class Cart(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = Column(Integer, db.ForeignKey('comic_book.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<Cart(user_id={self.user_id}, book_id={self.book_id}, quantity={self.quantity})>'


class WishList(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('comic_book.id'), nullable=False)
    
    def __repr__(self):
        return f'<WishList(user_id={self.user_id}, book_id={self.book_id})>'


class Library(db.Model):
    id = Column(Integer, primary_key=True)
    date_bought = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('comic_book.id'), nullable=False)

    def __repr__(self):
        return f'<Library(user_id={self.user_id}, book_id={self.book_id}, date_bought={self.date_bought})>'

# This is for the payment details
class CardDetails(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    card_number = Column(String, nullable=False, unique=True)
    card_brand = Column(String, nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    cvv = Column(Integer, unique=False, nullable=False)

    # Relationships
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Card(**** {self.card_number[-1:-5:-1]})'


class Series(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_query = Column(String, nullable=False)
    cover_image = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    date_aired = Column(String, nullable=False)
    bg_image = Column(String, nullable=True)


class Freelancer(db.Model):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False, default=13)
    address = Column(String(200), nullable=False)
    country = Column(String, nullable=False)
    date_joined = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))

class Order(db.Model):
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    date_ordered = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))
    total_amount = Column(Float, nullable=False)

    def __repr__(self):
        return f'Order(ID: {self.id}, Customer: {self.customer.first_name} {self.customer.last_name}, Total: {self.total_amount})'

class OrderItem(db.Model):
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False) 
    comic_id = Column(Integer, nullable=False)  
    quantity = Column(Integer, nullable=False)
    date_ordered = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f'OrderItem(Order ID: {self.customer_id}, Comic ID: {self.comic_id}, Quantity: {self.quantity}, Price: {self.price})'

class Customer(db.Model):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(200), nullable=False)
    date_joined = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f'Customer(ID: {self.id}, Name: {self.first_name} {self.last_name})'


# import datetime

# from website import db, login_manager
# from flask_login import UserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from website.config import Config

# from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# class Category(db.Model):
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     name_query = Column(String, nullable=False)

#     def __repr__(self):
#         return f'{self.name}'


# class ComicBook(db.Model):
#     # Book details
#     id = Column(Integer, primary_key=True)
#     category = Column(String(100), unique=False, nullable=False)
#     title = Column(String(100), unique=True, nullable=False)
#     author = Column(String(100), unique=False, nullable=False)
#     illustrator = Column(String(100), unique=False)
#     price = Column(Float, nullable=False)
#     release_date = Column(String, nullable=False)
#     description = Column(String(500), nullable=False)
#     top_pick = Column(Boolean, nullable=True)

#     # The name to get the book by
#     title_query = Column(String, nullable=False, unique=True)
#     category_query = Column(String, nullable=False)

#     # file path to the cover image
#     filename = Column(String, unique=True, nullable=False)

#     # Relationships
#     cart = db.relationship('Cart', backref='book', lazy=True)
#     wishlist = db.relationship('WishList', backref='book', lazy=True)
#     library = db.relationship('Library', backref='book', lazy=True)

#     def __repr__(self):
#         return (f'Comic(Category: {self.category}, Title: {self.title},' +
#                 f' Author: {self.author}, Query: {self.title_query})')


# class User(db.Model, UserMixin):
#     id = Column(Integer, primary_key=True)
#     email = Column(String(100), unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     age = Column(Integer, nullable=False, default=7)
#     country = Column(String, nullable=False)
#     date_joined = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))

#     # Relationships
#     card_details = db.relationship('CardDetails', backref='owner', lazy=True)
#     library = db.relationship('Library', backref='bought_by', lazy=True)
#     cart = db.relationship('Cart', backref='buyer', lazy=True)
#     wishlist = db.relationship('WishList', backref='buyer', lazy=True)

#     def get_reset_token(self, expiry_time=300):
#         s = Serializer(Config.SECRET_KEY, expiry_time)
#         return s.dumps({'user_id': self.id}).decode()

#     @staticmethod
#     def verify_token(token):
#         s = Serializer(Config.SECRET_KEY)
#         try:
#             user_id = s.loads(token)['user_id']
#         except:
#             return None
#         return user_id

#     def __repr__(self):
#         return f'User(ID: {self.id}, Email: {self.email})'


# class Cart(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     book_id = Column(Integer, ForeignKey('comic_book.id'), nullable=False)

#     def __repr__(self):
#         return f'Cart(ID: {self.user_id}, Book: {self.book.title}, Buyer: {self.buyer.email})'


# class WishList(db.Model):
#     id = Column(Integer, primary_key=True)

#     # Relationships
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     book_id = Column(Integer, ForeignKey('comic_book.id'), nullable=False)

#     def __repr__(self):
#         return f'WishList(ID: {self.user_id}, Book: {self.book.title.title()}, Buyer: {self.buyer.email})'


# class Library(db.Model):
#     id = Column(Integer, primary_key=True)
#     date_bought = Column(String, nullable=False)

#     # Relationships
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     book_id = Column(Integer, ForeignKey('comic_book.id'), nullable=False)

#     def __repr__(self):
#         return f'Item(ID: {self.user_id}, Book: {self.book.title})'


# class CardDetails(db.Model):
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     card_number = Column(String, nullable=False, unique=True)
#     card_brand = Column(String, nullable=False)
#     expiry_month = Column(Integer, nullable=False)
#     expiry_year = Column(Integer, nullable=False)
#     cvv = Column(Integer, unique=False, nullable=False)

#     # Relationships
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

#     def __repr__(self):
#         return f'Card(**** {self.card_number[-1:-5:-1]})'


# class Series(db.Model):
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     name_query = Column(String, nullable=False)
#     cover_image = Column(String, nullable=False)
#     rating = Column(Float, nullable=True)
#     date_aired = Column(String, nullable=False)
#     bg_image = Column(String, nullable=True)


# class Freelancer(db.Model):
#     # Book details
#     id = Column(Integer, primary_key=True)
#     series = Column(String, unique=False, nullable=False)
#     name = Column(String, unique=True, nullable=False)
#     director = Column(String, unique=False, nullable=False)
#     rating = Column(Float, nullable=True)
#     release_date = Column(String, nullable=False)
#     description = Column(String(500), nullable=False)
#     Freelancer_num = Column(Integer)

#     # The name to get the book by
#     name_query = Column(String, nullable=False, unique=True)
#     series_query = Column(String, nullable=False)

#     def __repr__(self):
#         return (f'Freelancer(Series: {self.series}, Name: {self.name}, Freelancer number: {self.Freelancer_num}' +
#                 f' Director: {self.director}')

# class Order(db.Model):
#     id = Column(Integer, primary_key=True)
#     customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
#     date_ordered = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))
#     total_amount = Column(Float, nullable=False)

#     def __repr__(self):
#         return f'Order(ID: {self.id}, Customer: {self.customer.first_name} {self.customer.last_name}, Total: {self.total_amount})'

# class Customer(db.Model):
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String(100), nullable=False)
#     last_name = Column(String(100), nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     phone_number = Column(String(20), nullable=False)
#     address = Column(String(200), nullable=False)
#     date_joined = Column(String, nullable=False, default=datetime.datetime.now(datetime.UTC).strftime('%d %B %Y'))

#     # Relationships
#     orders = db.relationship('Order', backref='customer', lazy=True)

#     def __repr__(self):
#         return f'Customer(ID: {self.id}, Name: {self.first_name} {self.last_name})'
