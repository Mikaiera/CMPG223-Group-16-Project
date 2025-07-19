from datetime import datetime

from flask import Blueprint, flash, redirect, url_for, render_template, request, abort
from flask_login import login_required, current_user

from website import bcrypt,db
from website.models import ComicBook, Library, Cart, WishList, Freelancer, Order, User
from website.supplier.forms import AddComic, AddFreelancer

supplier = Blueprint('supplier', __name__)


# supplier pass: il0v#Ch33s301

@supplier.route('/supplier')
@login_required
def supplier_home():
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    return render_template('supplier/home.html', title='Admin')

# Add a book
@supplier.route('/supplier/add-comic', methods=['GET', 'POST'])
@login_required
def add_comic():
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    form = AddComic()

    if form.validate_on_submit():
        category = form.category.data
        title = form.title.data
        author = form.author.data.title()
        illustrator = form.illustrator.data.title()
        price = int(form.price.data)
        release_date = form.date.data.strftime('%d/%m/%Y')
        description = form.description.data
        top_pick = form.top_pick.data
        filename = form.cover_image.data.filename
        title_query = form.cover_image.data.filename[:-4].lower()
        category_query = category.replace(':', '').replace('\'', '').replace(' ', '-').lower()
        stock_quantity = form.stock_quantity.data
        
        book = ComicBook(category=category, title=title, author=author, illustrator=illustrator, price=price,
                         release_date=release_date, description=description, top_pick=top_pick, filename=filename,
                         title_query=title_query, category_query=category_query, stock_quantity=stock_quantity)
        db.session.add(book)
        db.session.commit()

        flash('Book added to shelves. ', 'success')
        return redirect(url_for('supplier.add_comic'))

    return render_template('supplier/add_book.html', title='Add a book', form=form)

@supplier.route('/supplier/update-book')
@login_required
def all_comics():
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    page = request.args.get('page', 1, type=int)
    comics = ComicBook.query.paginate(page=page, per_page=4)
    return render_template('supplier/all_comics.html', title='Update', comics=comics)


@supplier.route('/supplier/update-book/<title_query>', methods=['GET', 'POST'])
@login_required
def update_comic(title_query):
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    form = AddComic()

    book = ComicBook.query.filter_by(title_query=title_query).first()

    if request.method == 'GET':
        form.category.data = book.category
        form.title.data = book.title
        form.author.data = book.author
        form.illustrator.data = book.illustrator
        form.price.data = book.price
        form.date.data = datetime.strptime(book.release_date, '%d/%m/%Y')
        form.description.data = book.description
        form.top_pick.data = book.top_pick
        form.stock_quantity.data = book.stock_quantity

    if form.validate_on_submit():
        book.filename = form.cover_image.data.filename
        book.category = form.category.data
        book.title = form.title.data
        book.author = form.author.data.title()
        book.illustrator = form.illustrator.data.title()
        book.price = int(form.price.data)
        book.release_date = form.date.data.strftime('%d/%m/%Y')
        book.description = form.description.data
        book.title_query = form.cover_image.data.filename[:-4].lower()
        book.category_query = form.category.data.replace(':', '').replace('\'', '').replace(' ', '-').lower()
        book.stock_quantity = form.stock_quantity.data
        db.session.commit()
        flash(f'Comic has been updated', 'success')
        return redirect(url_for('supplier.all_comics'))

    return render_template('supplier/add_book.html', title='Add a book', form=form)

@supplier.route('/supplier/delete-book/<title_query>', methods=['GET', 'POST'])
@login_required
def delete_book(title_query):
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    page = request.args.get('page', 1, type=int)
    comic = ComicBook.query.filter_by(title_query=title_query).first()
    lib = Library.query.filter_by(comic_book=comic).all()
    cart = Cart.query.filter_by(comic_book=comic).all()
    wish = WishList.query.filter_by(comic_book=comic).all()

    # Remove from every library, cart and wishlist if a book is deleted from the database
    for i in lib:
        db.session.delete(i)
    for j in cart:
        db.session.delete(j)
    for k in wish:
        db.session.delete(k)
    db.session.delete(comic)
    db.session.commit()
    return redirect(url_for('supplier.all_comics', page=page))

# ============================== Freelancers =====================================
@supplier.route('/supplier/add-freelancer', methods=['GET', 'POST'])
@login_required
def add_freelancer():
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    form = AddFreelancer()

    if form.validate_on_submit():
        freelancer = Freelancer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            address=form.address.data,
            country=form.country.data
        )
        
        db.session.add(freelancer)
        db.session.commit()

        flash('Freelancer added.', 'success')
        return redirect(url_for('supplier.add_freelancer'))

    return render_template('supplier/add_freelancer.html', title='Add a freelancer', form=form)


@supplier.route('/supplier/all-freelancers')
@login_required
def all_freelancers():
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '', type=str)
    sort_by = request.args.get('sort_by', 'first_name', type=str)
    order = request.args.get('order', 'asc', type=str)

    freelancers = Freelancer.query

    if query:
        freelancers = freelancers.filter(
            Freelancer.first_name.ilike(f'%{query}%') | 
            Freelancer.last_name.ilike(f'%{query}%') |
            Freelancer.email.ilike(f'%{query}%')
        )

    if sort_by and order:
        order_func = getattr(getattr(Freelancer, sort_by), order)
        freelancers = freelancers.order_by(order_func())

    freelancers = freelancers.paginate(page=page, per_page=4)

    return render_template('supplier/all_freelancers.html', title='All Freelancers', freelancers=freelancers)


@supplier.route('/supplier/update-freelancer/<int:id>', methods=['GET', 'POST'])
@login_required
def update_freelancer(id):
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    freelancer = Freelancer.query.get_or_404(id)
    form = AddFreelancer()

    if request.method == 'GET':
        form.first_name.data = freelancer.first_name
        form.last_name.data = freelancer.last_name
        form.email.data = freelancer.email
        form.phone.data = freelancer.phone
        form.address.data = freelancer.address
        form.country.data = freelancer.country

    if form.validate_on_submit():
        freelancer.first_name = form.first_name.data
        freelancer.last_name = form.last_name.data
        freelancer.email = form.email.data
        freelancer.phone = form.phone.data
        freelancer.address = form.address.data
        freelancer.country = form.country.data

        db.session.commit()
        flash('Freelancer has been updated.', 'success')
        return redirect(url_for('supplier.all_freelancers'))

    return render_template('supplier/add_freelancer.html', title='Update a freelancer', form=form)


@supplier.route('/supplier/delete-freelancer/<int:freelancer_id>', methods=['POST'])
@login_required
def delete_freelancer(freelancer_id):
    if current_user.email != 'supplier@supplier.com':
        abort(403)

    page = request.args.get('page', 1, type=int)
    freelancer = Freelancer.query.get_or_404(freelancer_id)

    db.session.delete(freelancer)
    db.session.commit()

    flash('Freelancer has been deleted successfully.', 'success')
    return redirect(url_for('supplier.all_freelancers', page=page))

# ============================== Orders =====================================
@supplier.route('/supplier/all-orders')
@login_required
def all_orders():
    if current_user.email != 'supplier@supplier.com':
        abort(403)
    
    sort_by = request.args.get('sort_by', 'date_ordered')
    order = request.args.get('order', 'asc')
    query = request.args.get('query', '')

    orders_query = Order.query.filter(
        (Order.id == query) |
        (Order.customer.has(User.first_name.ilike(f'%{query}%'))) |
        (Order.customer.has(User.last_name.ilike(f'%{query}%'))) |
        (Order.customer.has(User.email.ilike(f'%{query}%')))
    )

    # Apply sorting
    if order == 'asc':
        orders_query = orders_query.order_by(getattr(Order, sort_by).asc())
    else:
        orders_query = orders_query.order_by(getattr(Order, sort_by).desc())

    # Paginate the results
    page = request.args.get('page', 1, type=int)
    orders_page = orders_query.paginate(page=page, per_page=4)

    return render_template('supplier/all_orders.html', title='All Orders', orders=orders_page)

# @supplier.route('/supplier/all-orders')
# @login_required
# def all_orders():
#     orders = Order.query.all()
#     return render_template('supplier/all_orders.html', orders=orders)

@supplier.route('/supplier/view-order/<int:order_id>', methods=['GET'])
@login_required
def view_order(order_id):
    if current_user.email != 'supplier@supplier.com':
        abort(403)
        
    order = Order.query.get_or_404(order_id)
    return render_template('supplier/view_order.html', order=order)

@supplier.route('/supplier/delete-order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    if current_user.email != 'supplier@supplier.com':
        abort(403)
        
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('supplier.all_orders'))

