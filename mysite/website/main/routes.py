from flask import Blueprint, render_template, request
from flask_login import current_user

from website.models import ComicBook, Cart, Library, WishList

main = Blueprint('main', __name__)


# The home page route
@main.route('/')
def home():
    top_picks = ComicBook.query.filter_by(top_pick=True).all()[:6]
    kadoko_list = ComicBook.query.filter_by(category_query='kadoko').all()[:6]
    latest = ComicBook.query.all()[-1:-7:-1]
    free = ComicBook.query.filter_by(price=-1).all()
    return render_template('main/home.html', title='Home', top_picks=top_picks,
                           kadoko_list=kadoko_list, latest=latest, freebies=free)


@main.route('/about')
def about():
    return render_template('main/about.html', title='About us')


@main.route('/comics')
def comics():
    comic_list = {
        'action': ComicBook.query.filter_by(category_query='action').all()[0:6],
        'jabulani': ComicBook.query.filter_by(category_query='jabulani').all()[0:6],
        'horror': ComicBook.query.filter_by(category_query="horror").all()[0:6],
        'comedy': ComicBook.query.filter_by(category_query='comedy').all()[0:6],
        'fantasy': ComicBook.query.filter_by(category_query='fantasy').all()[0:6],
        'romance': ComicBook.query.filter_by(category_query='romance').all()[0:6],
    }

    return render_template('main/comics.html', title='Comics', comics=comic_list)


@main.route('/comic-category/<category_query>')
def comic_category(category_query):
    page = request.args.get('page', 1, type=int)
    category_list = ComicBook.query.filter_by(category_query=category_query).paginate(page=page, per_page=8)

    left_over = len(category_list.items)
    rows = 1
    if left_over > 4:
        rows = 2
    return render_template('/main/category_info.html', title=category_list.items[0].category,
                           comics=category_list, len=len, rows=rows, left_over=left_over)


@main.route('/comic-info/<title_query>', methods=['GET', 'POST'])
def comic_info(title_query):
    # Get the book
    book = ComicBook.query.filter_by(title_query=title_query).first()

    if book is None:
        return "Book not found", 404  # Handle the case where the book is not found

    if current_user.is_authenticated:
        # Use foreign keys directly
        book_in_cart = Cart.query.filter_by(book_id=book.id, user_id=current_user.id).first()
        book_in_lib = Library.query.filter_by(book_id=book.id, user_id=current_user.id).first()
        book_in_wishlist = WishList.query.filter_by(book_id=book.id, user_id=current_user.id).first()
    else:
        book_in_cart = None
        book_in_lib = None
        book_in_wishlist = None

    return render_template('main/comic_info.html', title='Comics info', book=book,
                           in_wishlist=book_in_wishlist is not None,
                           in_lib=book_in_lib is not None, in_cart=book_in_cart is not None)


@main.route('/top-picks')
def top_picks():
    page = request.args.get('page', 1, type=int)
    top_picks_list = ComicBook.query.filter_by(top_pick=True).paginate(page=page, per_page=8)

    left_over = len(top_picks_list.items)
    rows = 1
    if left_over > 4:
        rows = 2

    return render_template('main/recommended.html', title='Top Picks', comics=top_picks_list, len=len,
                           rows=rows, left_over=left_over)
    
    
@main.route("/search")
def search():
    search_query = request.args.get("q")
    all_comics = ComicBook.query.all()
    title_list = [comic for comic in all_comics if search_query.lower() in comic.title.lower()]
    category_list = [comic for comic in all_comics if search_query.lower() in comic.category.lower()]
    author_list = [comic for comic in all_comics if search_query.lower() in comic.author.lower()]
    length = 1
    
    if len(title_list) == len(category_list) == len(author_list) == 0:
        length = 0
            
    return render_template("main/search.html", title=f"Search for\"{search_query}\"", search_query=search_query, all_comics=all_comics, length=length)
    

@main.route('/watch')
def series():
    return render_template('main/series.html', title='Watch Series')
