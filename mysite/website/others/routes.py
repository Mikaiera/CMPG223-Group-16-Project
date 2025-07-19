from datetime import datetime, UTC

from flask import Blueprint, redirect, abort, url_for, request, flash, render_template
from flask_login import login_required, current_user
from flask_mail import Message

from website import db, mail, bcrypt
from website.models import Cart, Library, WishList, CardDetails, User, OrderItem
from website.others.forms import CheckOut, ResetPassword, RequestReset, AddCardDetails

others = Blueprint('others', __name__)


@others.route('/account/add-card-details', methods=['GET', 'POST'])
@others.route('/account/add-card-details/', methods=['GET', 'POST'])
@login_required
def add_card_details():
    form = AddCardDetails()

    if form.validate_on_submit():
        card = CardDetails(
            owner=current_user,
            name=form.first_name.data + ' ' + form.last_name.data,
            card_number=form.card_number.data.replace(' ', ''),
            card_brand=form.card_brand.data,
            expiry_month=form.expiry_month.data,
            expiry_year=form.expiry_year.data,
            cvv=int(form.cvv.data)
        )
        db.session.add(card)
        db.session.commit()

        # print(type(form.card_brand.data))
        flash('Payment option added', 'success')
        if request.args.get('next'):
            return redirect(request.args.get('next'))
        else:
            return redirect(url_for('users.account'))

    return render_template('user/card_details.html', title='Add card details', form=form)

@others.route('/checkout', methods=['GET', 'POST'])
@others.route('/checkout/', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_list = Cart.query.filter_by(buyer=current_user).all()
    cards = CardDetails.query.filter_by(owner=current_user).all()
    checkout_form = CheckOut()

    total = sum(comic.comic_book.price * comic.quantity for comic in cart_list)

    if request.method == 'POST':
        for item in cart_list:
            # Reduce stock quantity
            if item.comic_book.stock_quantity >= item.quantity:  # Ensure there's enough stock
                item.comic_book.stock_quantity -= item.quantity
            else:
                flash(f'Not enough stock for {item.comic_book.title}. Only {item.comic_book.stock_quantity} left.', 'danger')
                return redirect(url_for('others.checkout'))

            lib = Library(comic_book=item.comic_book, bought_by=current_user, date_bought=datetime.now(UTC).strftime('%d/%m/%Y'))
            db.session.add(lib)
            wish = WishList.query.filter_by(comic_book=item.comic_book, buyer=current_user).first()
            if wish is not None:
                db.session.delete(wish)
            db.session.delete(item)
            
        try:
            db.session.commit()
            flash('Payment successful', 'success')
            return redirect(url_for('users.library'))
        except Exception:
            db.session.rollback() 
            flash('Payment failed. Please try again.', 'danger')
            abort(400)

    return render_template('other/checkout.html', title='Checkout', items=cart_list, length=len(cart_list),
                           total=total, form=checkout_form, cards=cards, length2=len(cards), round=round)



def send_reset_email(user):
    token = user.get_reset_token()
    mail_message = Message('Reset password',
                           sender='uhonedkteffo11@gmail.com',
                           recipients=[user.email])

    mail_message.body = f'''The reset link has been sent. Click on it to reset your password:

{url_for('others.reset_password', token=token, title='Reset Password', _external=True)}

If you did not make this request, you can ignore this email.
'''
    mail.send(mail_message)


@others.route('/reset-password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect('/')

    form = RequestReset()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('This email has been sent!', 'success')
            return render_template('other/request_sent.html', title='Reset Password')
        else:
            flash('This email does not exist!', 'danger')

    return render_template('other/request_reset.html', form=form, title='Reset Password')


@others.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect('/')

    user_id = User.verify_token(token)

    if user_id is None:
        flash('The token is either invalid or has expired!', 'danger')
        return redirect(url_for('others.request_reset'))

    user = User.query.filter_by(id=user_id).first()

    form = ResetPassword()

    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('You may now login with your new password', 'success')
        return redirect(url_for('users.login'))

    return render_template('other/reset_password.html', form=form, title='Reset Password')
