
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64
from ai_engine import extract_text

app = Flask(__name__)

# =========================================================
# DATABASE CONFIG
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER = "static/uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================================================
# BOOK MODEL
# =========================================================

class Book(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(300)
    )

    author = db.Column(
        db.String(300)
    )

    publication = db.Column(
        db.String(300)
    )

    mrp = db.Column(
        db.Float
    )

    currency = db.Column(
        db.String(20)
    )

    discount = db.Column(
        db.Float
    )

    final_price = db.Column(
        db.Float
    )

    show_quantity = db.Column(
        db.Integer,
        default=0
    )

    storage_quantity = db.Column(
        db.Integer,
        default=0
    )

    image = db.Column(
        db.String(300)
    )

# =========================================================
# TRANSACTION MODEL
# =========================================================

class Transaction(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    total_amount = db.Column(
        db.Float
    )

    payment_method = db.Column(
        db.String(100)
    )

    customer_name = db.Column(
        db.String(200)
    )

    mobile_number = db.Column(
        db.String(50)
    )

    date_time = db.Column(
        db.String(100)
    )

# =========================================================
# TRANSACTION ITEM MODEL
# =========================================================

class TransactionItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    transaction_id = db.Column(
        db.Integer
    )

    book_title = db.Column(
        db.String(300)
    )

    quantity = db.Column(
        db.Integer
    )

    price = db.Column(
        db.Float
    )

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =========================================================
# ADD BOOK
# =========================================================

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        title = request.form.get(
            "title", ""
        )

        author = request.form.get(
            "author", ""
        )

        publication = request.form.get(
            "publication", ""
        )

        mrp = float(
            request.form.get(
                "mrp", 0
            )
        )

        currency = request.form.get(
            "currency", "INR"
        )

        discount = float(
            request.form.get(
                "discount", 0
            )
        )

        show_quantity = int(
            request.form.get(
                "show_quantity", 0
            )
        )

        storage_quantity = int(
            request.form.get(
                "storage_quantity", 0
            )
        )

        # =================================================
        # CURRENCY CONVERSION
        # =================================================

        conversion_rates = {

            "INR": 1,
            "USD": 83,
            "EUR": 90,
            "GBP": 105,
            "JPY": 0.55

        }

        converted_price = (
            mrp *
            conversion_rates[currency]
        )

        final_price = converted_price - (

            converted_price *
            discount / 100

        )

        filename = ""

        # =================================================
        # FILE IMAGE
        # =================================================

        image = request.files.get("image")

        if image and image.filename != "":

            filename = image.filename

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            image.save(filepath)

        # =================================================
        # CAMERA IMAGE
        # =================================================

        captured_image = request.form.get(
            "captured_image"
        )

        if captured_image:

            image_data = captured_image.split(",")[1]

            image_bytes = base64.b64decode(
                image_data
            )

            filename = (

                "capture_" +

                datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                ) +

                ".png"

            )

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            with open(filepath, "wb") as f:

                f.write(image_bytes)

        # =================================================
        # SAVE BOOK
        # =================================================

        new_book = Book(

            title=title,

            author=author,

            publication=publication,

            mrp=converted_price,

            currency=currency,

            discount=discount,

            final_price=final_price,

            show_quantity=show_quantity,

            storage_quantity=storage_quantity,

            image=filename

        )

        db.session.add(new_book)

        db.session.commit()

        return redirect("/book-list")

    return render_template(
        "add_book.html"
    )

# =========================================================
# BOOK LIST
# =========================================================

@app.route("/book-list")
def book_list():

    books = Book.query.all()

    return render_template(

        "book_list.html",

        books=books

    )

# =========================================================
# SELL BOOK
# =========================================================

@app.route("/sell-book")
def sell_book():

    books = Book.query.all()

    return render_template(

        "sell_book.html",

        books=books

    )

# =========================================================
# COMPLETE SALE
# =========================================================

@app.route(
    "/complete-sale",
    methods=["POST"]
)

def complete_sale():

    data = request.get_json()

    cart = data.get("cart", [])

    if not cart:

        return jsonify({

            "message":
            "Cart Empty"

        })

    total_amount = 0

    # CREATE TRANSACTION

    transaction = Transaction(

        customer_name="",

        mobile_number="",

        payment_method="Cash",

        total_amount=0,

        date_time=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    )

    db.session.add(transaction)

    # IMPORTANT

    db.session.commit()

    # SAVE ITEMS

    for item in cart:

        subtotal = (
            item["price"]
            *
            item["quantity"]
        )

        total_amount += subtotal

        # SAVE TRANSACTION ITEM

        transaction_item = TransactionItem(

            transaction_id=
            transaction.id,

            book_title=
            item["title"],

            quantity=
            item["quantity"],

            price=
            item["price"]

        )

        db.session.add(
            transaction_item
        )

        # UPDATE STOCK

        book = Book.query.get(
            item["id"]
        )

        if book:

            qty = item["quantity"]

            show_qty = (
                book.show_quantity or 0
            )

            storage_qty = (
                book.storage_quantity or 0
            )

            # REMOVE FROM SHOW

            if show_qty >= qty:

                book.show_quantity -= qty

            else:

                remaining = (
                    qty - show_qty
                )

                book.show_quantity = 0

                if storage_qty >= remaining:

                    book.storage_quantity -= remaining

    # UPDATE TOTAL

    transaction.total_amount = (
        total_amount
    )

    db.session.commit()

    return jsonify({

        "message":
        "Sale Completed Successfully",

        "transaction_id":
        transaction.id

    })

    # =================================================
    # SAVE ITEMS
    # =================================================

    for item in cart:

        transaction_item = TransactionItem(

            transaction_id=transaction.id,

            book_title=item["title"],

            quantity=item["quantity"],

            price=item["price"]

        )

        db.session.add(transaction_item)

        # =============================================
        # STOCK UPDATE
        # =============================================

        book = Book.query.filter_by(
            title=item["title"]
        ).first()

        if book:

            quantity = item["quantity"]

            if book.show_quantity >= quantity:

                book.show_quantity -= quantity

            else:

                remaining = (
                    quantity -
                    book.show_quantity
                )

                book.show_quantity = 0

                book.storage_quantity -= remaining

                if book.storage_quantity < 0:

                    book.storage_quantity = 0

    db.session.commit()

    return jsonify({

        "message":
        "Sale Completed Successfully"

    })

# =========================================================
# TRANSACTIONS
# =========================================================

@app.route("/transactions")
def transactions():

    try:

        transactions_data = Transaction.query.all()

    except:

        transactions_data = []

    try:

        items_data = TransactionItem.query.all()

    except:

        items_data = []

    return render_template(

        "transactions.html",

        transactions=transactions_data,

        items=items_data

    )

# =========================================================
# DELETE BOOK
# =========================================================

@app.route("/delete-book/<int:id>")
def delete_book(id):

    book = Book.query.get(id)

    if book:

        db.session.delete(book)

        db.session.commit()

    return redirect("/book-list")
# =========================================================
# TRANSACTION DETAILS
# =========================================================

@app.route("/transaction/<int:id>")
def transaction_detail(id):

    transaction = Transaction.query.get(id)

    items = TransactionItem.query.filter_by(
        transaction_id=id
    ).all()

    return render_template(

        "transaction_detail.html",

        transaction=transaction,

        items=items

    )


# =========================================================
# ADVANCED DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    transactions = Transaction.query.all()

    items = TransactionItem.query.all()

    books = Book.query.all()

    # TOTALS

    total_sales = 0

    total_books_sold = 0

    total_transactions = len(transactions)

    total_profit = 0

    daily_sales = 0

    weekly_sales = 0

    monthly_sales = 0

    inventory_value = 0

    low_stock_books = []

    best_selling = {}

    today = datetime.now()

    # TRANSACTION ANALYTICS

    for transaction in transactions:

        amount = (
            transaction.total_amount or 0
        )

        total_sales += amount

        # DAILY SALES

        try:

            transaction_date = datetime.strptime(

                transaction.date_time,

                "%Y-%m-%d %H:%M:%S"

            )

            days_difference = (

                today - transaction_date

            ).days

            if days_difference == 0:

                daily_sales += amount

            if days_difference <= 7:

                weekly_sales += amount

            if days_difference <= 30:

                monthly_sales += amount

        except:

            pass

    # ITEMS ANALYTICS

    for item in items:

        qty = item.quantity or 0

        price = item.price or 0

        total_books_sold += qty

        # PROFIT ESTIMATION

        profit = price * qty * 0.20

        total_profit += profit

        # BEST SELLING

        if item.book_title in best_selling:

            best_selling[item.book_title] += qty

        else:

            best_selling[item.book_title] = qty

    # INVENTORY ANALYTICS

    for book in books:

        stock = (

            (book.show_quantity or 0)
            +
            (book.storage_quantity or 0)

        )

        price = book.final_price or 0

        inventory_value += (

            stock * price

        )

        if stock <= 5:

            low_stock_books.append(book)

    # SORT BEST SELLING

    best_selling_books = sorted(

        best_selling.items(),

        key=lambda x: x[1],

        reverse=True

    )[:5]

    return render_template(

        "dashboard.html",

        total_sales=total_sales,

        total_books_sold=
        total_books_sold,

        total_transactions=
        total_transactions,

        total_profit=
        total_profit,

        daily_sales=
        daily_sales,

        weekly_sales=
        weekly_sales,

        monthly_sales=
        monthly_sales,

        inventory_value=
        inventory_value,

        low_stock_books=
        low_stock_books,

        best_selling_books=
        best_selling_books

    )
# =========================================================
# EDIT BOOK
# =========================================================

@app.route(
    "/edit-book/<int:id>",
    methods=["GET", "POST"]
)

def edit_book(id):

    book = Book.query.get(id)

    if not book:

        return redirect("/book-list")

    if request.method == "POST":

        book.title = request.form.get(
            "title"
        )

        book.author = request.form.get(
            "author"
        )

        book.publication = request.form.get(
            "publication"
        )

        book.mrp = float(

            request.form.get(
                "mrp"
            ) or 0

        )

        book.discount_percent = float(

            request.form.get(
                "discount_percent"
            ) or 0

        )

        book.final_price = (

            book.mrp
            -
            (
                book.mrp
                *
                book.discount_percent
                / 100
            )

        )

        book.show_quantity = int(

            request.form.get(
                "show_quantity"
            ) or 0

        )

        book.storage_quantity = int(

            request.form.get(
                "storage_quantity"
            ) or 0

        )

        db.session.commit()

        return redirect("/book-list")

    return render_template(

        "edit_book.html",

        book=book

    )
# =========================================================
# BOOK DETAILS
# =========================================================
@app.route("/book/<int:id>")
def book_details(id):

    book = Book.query.get_or_404(id)

    return render_template(
        "book_details.html",
        book=book
    )


    
# =========================================================
# BILL PAGE
# =========================================================

@app.route("/bill/<int:id>")
def bill(id):

    transaction = Transaction.query.get(id)

    items = TransactionItem.query.filter_by(
        transaction_id=id
    ).all()

    if not transaction:

        return redirect("/transactions")

    return render_template(

        "bill.html",

        transaction=transaction,

        items=items

    )
# =========================================================
# AI SEARCH
# =========================================================

@app.route(
    "/ai-search",
    methods=["POST"]
)

def ai_search():

    try:

        print("AI SEARCH STARTED")

        if "image" not in request.files:

            print("NO IMAGE FOUND")

            return jsonify([])

        image = request.files["image"]

        if image.filename == "":

            print("EMPTY IMAGE")

            return jsonify([])

        # SAVE IMAGE

        image_path = os.path.join(

            "static/uploads",

            image.filename

        )

        image.save(image_path)

        print("IMAGE SAVED")

        # OCR

        extracted_text = extract_text(

            image_path

        )

        print("OCR TEXT:", extracted_text)

        extracted_text = extracted_text.lower()

        # SEARCH BOOKS

        books = Book.query.all()

        matched_books = []

        for book in books:

            title = (
                book.title or ""
            ).lower()

            author = (
                book.author or ""
            ).lower()

            if (

                title in extracted_text

                or

                extracted_text in title

                or

                author in extracted_text

            ):

                matched_books.append({

                    "id": book.id,

                    "title": book.title,

                    "author": book.author,

                    "price": book.final_price,

                    "image": book.image,

                    "stock":

                    (
                        (book.show_quantity or 0)

                        +

                        (book.storage_quantity or 0)

                    )

                })

        print("MATCHES:", len(matched_books))

        return jsonify(matched_books)

    except Exception as e:

        print("AI SEARCH ERROR:", e)

        return jsonify([])
# =========================================================
# MAIN
# =========================================================

with app.app_context():

    db.create_all()

if __name__ == "__main__":

    app.run(debug=True)


# =========================================================
# DELETE TRANSACTION
# =========================================================

@app.route("/delete-transaction/<int:id>")
def delete_transaction(id):

    transaction = Transaction.query.get(id)

    items = TransactionItem.query.filter_by(
        transaction_id=id
    ).all()

    # DELETE ITEMS

    for item in items:

        db.session.delete(item)

    # DELETE TRANSACTION

    if transaction:

        db.session.delete(transaction)

    db.session.commit()

    return redirect("/transactions")

