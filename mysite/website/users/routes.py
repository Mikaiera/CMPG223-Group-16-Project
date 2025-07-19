from flask import Blueprint, render_template, redirect, url_for, flash, request,Flask, render_template,send_file,Response
from flask_login import current_user, login_user, logout_user, login_required
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from wtforms import StringField
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from website import bcrypt, db
from website.models import User, Cart, Library, CardDetails, WishList, ComicBook
from wtforms.validators import DataRequired
from website.users.forms import SignUp, Login, UpdatePassword, UpdateEmail

# Blueprint
users = Blueprint('users', __name__)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignUp()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email is already registered. Please log in or use a different email.', 'danger')
            return redirect(url_for('users.signup'))
        
        existing_phone = User.query.filter_by(phone=form.phone.data).first()
        if existing_phone:
            flash('Phone number is already registered. Please log in or use a different number.', 'danger')
            return redirect(url_for('users.signup'))
        
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        phone = form.phone.data
        age = form.age.data
        country = form.country.data
        address = form.address.data
 
        name_query = (first_name + '-' + last_name).replace(' - ', '-').replace(':', '').replace('\'', '').replace(' ', '-').lower()
        user_num = len(User.query.all()) + 1

        user = User(first_name=first_name, last_name=last_name, email=email, password=password, phone=phone,age=age, country=country, address= address)
        
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember.data)
        flash('Account created successfully', 'success')
        return redirect(url_for('main.home'))

    return render_template('user/signup.html', title='Sign up', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful', 'success')
            prev = request.args.get('next')
            if prev:
                return redirect(prev)
            return redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Incorrect email or password!', 'danger')
            return redirect(url_for('users.login'))
    return render_template('user/login.html', title='Login', form=form)


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    cards = CardDetails.query.filter_by(owner=current_user).all()
    amount = len(Library.query.filter_by(bought_by=current_user).all())
    return render_template('user/account_settings.html', title='Account', cards=cards, number=len(cards), amount=amount)


@users.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('main.home'))
    else:
        return redirect(url_for('main.home'))


@users.route('/account/update-email', methods=['GET', 'POST'])
@login_required
def update_email():
    form = UpdateEmail()
    if request.method == 'GET':
        form.email.data = current_user.email
    elif form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        user.email = form.email.data
        db.session.commit()
        flash('Your email has been updated!', 'success')
        return redirect(url_for('users.account'))
    return render_template('user/update_email.html', title='Account', form=form)


@users.route('/account/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePassword()

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if bcrypt.check_password_hash(user.password, form.current_password.data):
            user.password = bcrypt.generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('users.account'))
        else:
            flash('Your current password is incorrect.', 'danger')
    return render_template('user/update_password.html', title='Account', form=form)


@users.route('/cart')
@login_required
def cart():
    cart_list = Cart.query.filter_by(buyer=current_user).all()
    quantity = request.form.getlist("quantity")
    print(quantity)
    total = sum(comic.comic_book.price for comic in cart_list)
    return render_template('user/cart.html', title='Cart', items=cart_list, length=len(cart_list), total=total)


@users.route('/wishlist')
@login_required
def wishlist():
    wish_list = WishList.query.filter_by(buyer=current_user).all()
    in_cart = Cart.query.filter_by(buyer=current_user).first()
    return render_template('user/wishlist.html', title='Cart', items=wish_list, length=len(wish_list), in_cart=in_cart is not None)


@users.route('/library')
@login_required
def library():
    page = request.args.get('page', 1, type=int)
    library_items = Library.query.filter_by(bought_by=current_user).paginate(page=page, per_page=8)
    return render_template('user/library.html', title='Library', items=library_items, length=library_items.total, len=len)
   
@users.route("/report")
@login_required
def report():
    sort_order = request.args.get('sort_order', 'none')
    
    if sort_order == 'asc':
        top_picks_list = ComicBook.query.order_by(ComicBook.stock_quantity.asc()).limit(10).all()
        report_pdf_path = "mysite/website/static/report/asc_report.pdf"
    elif sort_order == 'desc':
        top_picks_list = ComicBook.query.order_by(ComicBook.stock_quantity.desc()).limit(10).all()
        report_pdf_path = "mysite/website/static/report/desc_report.pdf"
    else:
        top_picks_list = ComicBook.query.limit(10).all()
        report_pdf_path = "mysite/website/static/report/unsorted_report.pdf"
    
    library = Library.query.filter_by(bought_by=current_user).all()
  
    plt.figure(figsize=(11, 9))
    plt.bar([comic.title for comic in top_picks_list], [comic.stock_quantity for comic in top_picks_list])
    plt.xlabel('Comic Book')
    plt.ylabel('Stock Quantity')
    plt.title('Top 10 Comics by Stock Quantity')
    plt.xticks(rotation=45, ha="right")
    
    report_image_path = "mysite/website/static/images/stock_quantity.png"
    plt.savefig(report_image_path)
  
    c = canvas.Canvas(report_pdf_path, pagesize=(800, 600))
    c.drawImage(report_image_path, 100, 40, 600)
    c.save()
    
    comics = [(comic.title, comic.stock_quantity) for comic in top_picks_list]
    
    return render_template("user/report.html", title="Report", comics=comics, library=library)

@users.route('/report/download')
@login_required
def download_pdf():
    sort_order = request.args.get('sort_order', 'none')
    
    if sort_order == 'asc':
        file_path = "static/report/asc_report.pdf"
    elif sort_order == 'desc':
        file_path = "static/report/desc_report.pdf"
    else:
        file_path = "static/report/unsorted_report.pdf"
    
    return send_file(file_path, as_attachment=True, mimetype="application/pdf", download_name="report.pdf")


@users.route("/report-income")
@login_required
def report_income():
    period = request.args.get('period', 'annual')  # Default
    top_picks_list = ComicBook.query.all()
    
    # Calculate income based on the selected period
    income_values = []
    if period == 'quarterly':
        income_values = [comic.price * comic.stock_quantity / 4 for comic in top_picks_list]
    elif period == 'biannual':
        income_values = [comic.price * comic.stock_quantity / 2 for comic in top_picks_list]
    else:  
        income_values = [comic.price * comic.stock_quantity for comic in top_picks_list]
    
    
    comic_titles = [comic.title for comic in top_picks_list]

    plt.figure(figsize=(11, 9))
    plt.bar(comic_titles[:10], income_values[:10])
    plt.xlabel('Comic Book')
    plt.ylabel('Total Income (R)')
    plt.title(f'Total Income per Comic Book ({period.capitalize()})')
    
    plt.xticks(rotation=45, ha="right")
    plot_path = f"mysite/website/static/images/stock_income_{period}.png"
    pdf_path = f"mysite/website/static/report_income/report_{period}.pdf"
    
    plt.savefig(plot_path)
    
    try:
        c = canvas.Canvas(pdf_path, pagesize=(800, 600))
        c.drawImage(plot_path, 100, 40, 600)
        c.save()
    except Exception as e:
        return f"Error generating report: {str(e)}", 500
    
    # Prepare comics data for the template
    comics = [(comic.title, income) for comic, income in zip(top_picks_list, income_values)]
    comics = comics[:10]
    
    return render_template(
        "user/report_income.html",title="Report",comics=comics,period=period)

@users.route('/report-income/report_income.pdf')
@login_required
def download_income_pdf():
    period = request.args.get('period', 'annual')  # Default 
    return send_file(
        f"static/report_income/report_{period}.pdf",
        as_attachment=True,
        mimetype="pdf",
        download_name=f"report_income_{period}.pdf"
    )
