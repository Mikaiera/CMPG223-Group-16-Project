from flask import Blueprint, redirect, url_for, flash, abort, request
from flask_login import current_user, login_required

from website import db
from website.models import ComicBook, Cart, WishList, CardDetails

action = Blueprint('action', __name__)


@action.route('/add-to-cart/<title_query>', methods=['GET', 'POST'])
@login_required
def add_to_cart(title_query):
    comic_book = ComicBook.query.filter_by(title_query=title_query).first()
    
    if not comic_book:
        flash('Comic not found.', 'danger')
        return redirect(url_for('main.comic_info', title_query=title_query))

    cart_item = Cart.query.filter_by(book_id=comic_book.id, user_id=current_user.id).first()

    if cart_item:
        flash('Comic is already in your cart.', 'danger')
    else:
        cart_item = Cart(book_id=comic_book.id, user_id=current_user.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()
        flash('Item added to cart!', 'success')

    next_url = request.args.get('next', url_for('main.comic_info', title_query=title_query))
    return redirect(next_url)


@action.route("/increment-quantity/<title_query>", methods=['GET', 'POST'])
@login_required
def update_quantity(title_query):
    comic_book = ComicBook.query.filter_by(title_query=title_query).first()
    count = request.args.get("count", type=int)
    
    if not comic_book:
        flash('Comic not found.', 'danger')
        return redirect(url_for('main.comic_info', title_query=title_query))
    
    cart_item = Cart.query.filter_by(book_id=comic_book.id, user_id=current_user.id).first()

    if not comic_book:
        return redirect(url_for('main.comic_info', title_query=title_query))

    cart_item.quantity += count
    if cart_item.quantity < 1:
        cart_item.quantity = 1
    db.session.commit()
    
    next_url = request.args.get('next')
    if next_url is None:
        return redirect(url_for('main.comic_info', title_query=title_query))
    else:
        return redirect(next_url)

    
@action.route('/remove-from-cart/<title_query>', methods=['GET', 'POST'])
@login_required
def remove_from_cart(title_query):
    comic_book = ComicBook.query.filter_by(title_query=title_query).first()
    
    if not comic_book:
        flash('Comic not found.', 'danger')
        return redirect(url_for('users.cart'))
    
    # Fetch the cart item
    cart_item = Cart.query.filter_by(book_id=comic_book.id, user_id=current_user.id).all()
    
    for item in cart_item:
        if not item:
            flash('Item not found in cart.', 'warning')
            return redirect(url_for('users.cart'))

        # Check if its the user's cart
        if current_user.id != item.user_id:
            abort(403)
            
        db.session.delete(item)

    db.session.commit()
    flash('Item removed from cart!', 'success')

    next_url = request.args.get('next')
    if next_url is None:
        return redirect(url_for('users.cart'))
    else:
        return redirect(next_url)
    
@action.route('/add-to-wishlist/<title_query>', methods=['GET', 'POST'])
@login_required
def add_to_wishlist(title_query):
    comic_book = ComicBook.query.filter_by(title_query=title_query).first()
    
    if not comic_book:
        flash('Comic not found.', 'danger')
        return redirect(url_for('main.comic_info', title_query=title_query))

    # Add to wishlist using foreign keys
    item = WishList(book_id=comic_book.id, user_id=current_user.id)
    db.session.add(item)
    db.session.commit()
    flash('Item added to wishlist.', 'success')

    next_url = request.args.get('next')
    if next_url is None:
        return redirect(url_for('main.comic_info', title_query=title_query))
    else:
        return redirect(next_url)


@action.route('/remove-from-wishlist/<title_query>', methods=['GET', 'POST'])
@login_required
def remove_from_wishlist(title_query):
    comic_book = ComicBook.query.filter_by(title_query=title_query).first()
    
    if not comic_book:
        flash('Comic not found.', 'danger')
        return redirect(url_for('main.comic_info', title_query=title_query))

    # Fetch the wishlist item
    wishlist_item = WishList.query.filter_by(book_id=comic_book.id, user_id=current_user.id).first()

    if not wishlist_item:
        flash('Item not found in wishlist.', 'warning')
        return redirect(url_for('main.comic_info', title_query=title_query))

    # Ensure the current user owns the wishlist item
    if current_user.id != wishlist_item.user_id:
        abort(403)

    db.session.delete(wishlist_item)
    db.session.commit()
    flash('Item removed from wishlist.', 'success')

    next_url = request.args.get('next')
    if next_url is None:
        return redirect(url_for('main.comic_info', title_query=title_query))
    else:
        return redirect(next_url)

@action.route('/delete-payment-method/<card_number>', methods=['GET', 'POST'])
@login_required
def delete_payment_method(card_number):
    card = CardDetails.query.filter_by(card_number=card_number).first()
    db.session.delete(card)
    db.session.commit()

    if request.args.get('next') is None:
        return redirect(url_for('users.account',))
    else:
        return redirect(request.args.get('next'))
