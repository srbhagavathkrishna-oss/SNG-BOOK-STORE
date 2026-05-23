
from PIL.ImageChops import difference
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64
from ai_engine import extract_text
from flask import request
import pandas as pd
app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.config[
    "UPLOAD_FOLDER"
] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

database_url = os.environ.get(
    "DATABASE_URL"
)

if database_url:

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = database_url

else:

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///books.db"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False



ADMIN_PASSWORD = "sng123"
import os

database_url = os.environ.get(
    "DATABASE_URL"
)

if database_url is None:

    database_url = "sqlite:///books.db"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = database_url

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

db = SQLAlchemy(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
def usd_to_inr(amount_usd):

    try:

        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD"
        )

        data = response.json()

        rate = data["rates"]["INR"]

        return round(amount_usd * rate, 2)

    except:

        return 0



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

    # BASIC DETAILS

    title = db.Column(
        db.String(300),
        default=""
    )

    author = db.Column(
        db.String(300),
        default=""
    )

    publication = db.Column(
        db.String(300),
        default=""
    )

    category = db.Column(
        db.String(100),
        default=""
    )

    language = db.Column(
        db.String(100),
        default=""
    )

    description = db.Column(
        db.Text,
        default=""
    )

    # PRICING

    purchase_price = db.Column(
        db.Float,
        default=0
    )

    final_price = db.Column(
        db.Float,
        default=0
    )

    discount = db.Column(
        db.Float,
        default=0
    )

    # STOCK

    show_quantity = db.Column(
        db.Integer,
        default=0
    )

    storage_quantity = db.Column(
        db.Integer,
        default=0
    )

    # LOCATION

    shelf_number = db.Column(
        db.String(10),
        default=""
    )

    rack_number = db.Column(
        db.String(10),
        default=""
    )

    # IMAGE

    image = db.Column(
        db.String(300),
        default=""
    )

    # MULTI CURRENCY

    currency_type = db.Column(
        db.String(20),
        default="INR"
    )

    foreign_price = db.Column(
        db.Float,
        default=0
    )

    converted_inr = db.Column(
        db.Float,
        default=0
    )

    # DATE

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
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

    books = Book.query.limit(12).all()

    return render_template(

        "public_home.html",

        books=books

    )
@app.route("/admin")

def admin():

    password = request.args.get(
        "password"
    )

    if password != ADMIN_PASSWORD:

        return """

        <h2>
        Wrong Password
        </h2>

        """

    return render_template(
        "admin_panel.html"
    )
@app.route("/admin-books")

def admin_books():

    books = Book.query.all()

    return render_template(

        "admin_books.html",

        books=books

    )
# ============================================
# ADMIN INVENTORY
# ============================================

@app.route("/admin-inventory")

def admin_inventory():

    books = Book.query.all()

    return render_template(

        "admin_inventory.html",

        books=books

    )


# =========================================================
# ADD BOOK
# =========================================================

@app.route("/add-book", methods=["GET", "POST"])

def add_book():

    if request.method == "POST":

        try:

            # =========================================
            # BASIC DETAILS
            # =========================================

            title = request.form.get(
                "title", ""
            )

            author = request.form.get(
                "author", ""
            )

            publication = request.form.get(
                "publication", ""
            )

            category = request.form.get(
                "category", ""
            )

            language = request.form.get(
                "language", ""
            )

            description = request.form.get(
                "description", ""
            )

            # =========================================
            # PRICING
            # =========================================

            purchase_price = float(

                request.form.get(
                    "purchase_price", 0
                ) or 0

            )

            discount = float(

                request.form.get(
                    "discount", 0
                ) or 0

            )

            currency = request.form.get(
                "currency",
                "INR"
            )

            foreign_amount = float(

                request.form.get(
                    "foreign_amount", 0
                ) or 0

            )

            # =========================================
            # LIVE CURRENCY CONVERSION
            # =========================================

            conversion_rates = {

                "INR": 1,
                "USD": 83,
                "EUR": 90,
                "GBP": 105,
                "AED": 22.6,
                "SAR": 22.1,
                "QAR": 22.8,
                "JPY": 0.55

            }

            converted_inr = (

                foreign_amount *

                conversion_rates.get(
                    currency,
                    1
                )

            )

            # =========================================
            # FINAL PRICE
            # =========================================

            final_price = purchase_price - (

                purchase_price *

                discount / 100

            )

            # =========================================
            # STOCK
            # =========================================

            show_quantity = int(

                request.form.get(
                    "show_quantity", 0
                ) or 0

            )

            storage_quantity = int(

                request.form.get(
                    "storage_quantity", 0
                ) or 0

            )

            # =========================================
            # SHELF & RACK
            # =========================================

            shelf_number = request.form.get(
                "shelf_number", ""
            )

            rack_number = request.form.get(
                "rack_number", ""
            )

            # =========================================
            # IMAGE VARIABLES
            # =========================================

            filename = ""

            # =========================================
            # FILE UPLOAD IMAGE
            # =========================================

            image = request.files.get("image")

            if image and image.filename != "":

                filename = image.filename

                filepath = os.path.join(

                    app.config[
                        "UPLOAD_FOLDER"
                    ],

                    filename

                )

                image.save(filepath)

            # =========================================
            # CAMERA CAPTURE IMAGE
            # =========================================

            captured_image = request.form.get(
                "captured_image"
            )

            if captured_image:

                image_data = captured_image.split(
                    ","
                )[1]

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

                    app.config[
                        "UPLOAD_FOLDER"
                    ],

                    filename

                )

                with open(filepath, "wb") as f:

                    f.write(image_bytes)

            # =========================================
            # CREATE BOOK OBJECT
            # =========================================

            new_book = Book(

                title=title,

                author=author,

                publication=publication,

                category=category,

                language=language,

                description=description,

                purchase_price=purchase_price,

                final_price=final_price,

                discount=discount,

                currency_type=currency,

                foreign_price=foreign_amount,

                converted_inr=converted_inr,

                show_quantity=show_quantity,

                storage_quantity=storage_quantity,

                shelf_number=shelf_number,

                rack_number=rack_number,

                image=filename

            )

            # =========================================
            # SAVE TO DATABASE
            # =========================================

            db.session.add(new_book)

            db.session.commit()

            # =========================================
            # SUCCESS REDIRECT
            # =========================================

            return redirect(url_for("book_list"))

        # =========================================
        # ERROR HANDLING
        # =========================================

        except Exception as e:

            return f"""

            <h1>Add Book Error</h1>

            <p>{str(e)}</p>

            """

    # =========================================
    # LOAD PAGE
    # =========================================

    return render_template(
        "add_book.html"
    )
# =========================================================
# BULK IMPORT BOOKS
# =========================================================

# ============================================
# BULK IMPORT
# ============================================

@app.route("/bulk-import",
methods=["GET","POST"])

def bulk_import():

    if request.method == "POST":

        file = request.files.get("file")

        if not file:

            return "No file uploaded"

        filename = file.filename.lower()

        try:

            # CSV

            if filename.endswith(".csv"):

                df = pd.read_csv(file)

            # EXCEL

            elif filename.endswith(".xlsx"):

                df = pd.read_excel(file)

            else:

                return "Unsupported file format"

            # LOOP ROWS
            purchase_price = float(
            pd.to_numeric(
            row.get("purchase_price",0),
            errors="coerce"
            ) or 0
            )

            discount = float(
            pd.to_numeric(
            row.get("discount",0),
            errors="coerce"
            ) or 0
            )

            final_price = float(
            pd.to_numeric(
            row.get("final_price",0),
            errors="coerce"
            ) or 0
            )

            for _, row in df.iterrows():

                book = Book(

                    title=row.get("title",""),

                    author=row.get("author",""),

                    publication=row.get(
                        "publication",""
                    ),

                    category=row.get(
                        "category",""
                    ),

                    language=row.get(
                        "language",""
                    ),

                    description=row.get(
                        "description",""
                    ),

                    purchase_price=float(
                        row.get(
                        "purchase_price",0
                        )
                    ),

                    

                    show_quantity=int(
                        row.get(
                        "show_quantity",0
                        )
                    ),

                    storage_quantity=int(
                        row.get(
                        "storage_quantity",0
                        )
                    ),

                    shelf_number=str(
                        row.get(
                        "shelf_number",""
                        )
                    ),

                    rack_number=str(
                        row.get(
                        "rack_number",""
                        )
                    )
                    purchase_price=purchase_price,

                    discount=discount,

                    final_price=final_price,
                )

                db.session.add(book)

            db.session.commit()

            return redirect(
                "/admin-inventory"
            )

        except Exception as e:

            return str(e)

    return render_template(
        "bulk_import.html"
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
# ============================================
# ANALYTICS
# ============================================

@app.route("/analytics")

def analytics():

    total_books = Book.query.count()

    total_transactions = Transaction.query.count()

    total_stock = db.session.query(

        db.func.sum(
            Book.show_quantity
        )

    ).scalar()

    if total_stock is None:

        total_stock = 0

    books = Book.query.all()

    return render_template(

        "analytics.html",

        total_books=total_books,

        total_transactions=total_transactions,

        total_stock=total_stock,

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
            book = Book.query.get(item["id"])

            if book:

                sold_qty = int(item["quantity"])

                book.show_quantity = max(

                0,

                (book.show_quantity or 0)

                - sold_qty

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

    book = Book.query.get_or_404(id)

    if request.method == "POST":

        # =========================================
        # STOCK MANAGEMENT
        # =========================================

        old_show = book.show_quantity or 0

        new_show = int(

            request.form.get(
                "show_quantity"
            ) or 0

        )

        difference = new_show - old_show

        if difference > 0:

            book.storage_quantity = max(

                0,

                (book.storage_quantity or 0)

                - difference

            )

        book.show_quantity = new_show

        # =========================================
        # BASIC DETAILS
        # =========================================

        book.title = request.form.get(
            "title", ""
        )

        book.author = request.form.get(
            "author", ""
        )

        book.publication = request.form.get(
            "publication", ""
        )

        book.category = request.form.get(
            "category", ""
        )

        book.language = request.form.get(
            "language", ""
        )

        book.description = request.form.get(
            "description", ""
        )

        # =========================================
        # PRICING
        # =========================================

        purchase_price = float(

            request.form.get(
                "purchase_price", 0
            ) or 0

        )

        discount = float(

            request.form.get(
                "discount", 0
            ) or 0

        )

        currency = request.form.get(
            "currency",
            "INR"
        )

        foreign_amount = float(

            request.form.get(
                "foreign_amount", 0
            ) or 0

        )

        conversion_rates = {

            "INR": 1,
            "USD": 83,
            "EUR": 90,
            "GBP": 105,
            "AED": 22.6,
            "SAR": 22.1,
            "QAR": 22.8,
            "JPY": 0.55

        }

        converted_inr = (

            foreign_amount *

            conversion_rates.get(
                currency,
                1
            )

        )

        final_price = purchase_price - (

            purchase_price *
            discount / 100

        )

        book.purchase_price = purchase_price

        book.final_price = final_price

        book.discount = discount

        book.currency_type = currency

        book.foreign_price = foreign_amount

        book.converted_inr = converted_inr

        # =========================================
        # STORAGE
        # =========================================

        book.storage_quantity = int(

            request.form.get(
                "storage_quantity", 0
            ) or 0

        )

        # =========================================
        # LOCATION
        # =========================================

        book.shelf_number = request.form.get(
            "shelf_number", ""
        )

        book.rack_number = request.form.get(
            "rack_number", ""
        )

        # =========================================
        # IMAGE UPDATE
        # =========================================

        image = request.files.get("image")

        if image and image.filename != "":

            filename = image.filename

            filepath = os.path.join(

                app.config[
                    "UPLOAD_FOLDER"
                ],

                filename

            )

            image.save(filepath)

            book.image = filename

        # =========================================
        # SAVE
        # =========================================

        db.session.commit()

        return redirect(url_for("book_list"))

    return render_template(

        "edit_book.html",

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
# DELETE TRANSACTION
# =========================================================

@app.route("/delete-transaction/<int:id>")

def delete_transaction(id):

    transaction = Transaction.query.get(id)

    items = TransactionItem.query.filter_by(

        transaction_id=id

    ).all()

    for item in items:

        db.session.delete(item)

    if transaction:

        db.session.delete(transaction)

    db.session.commit()

    return redirect("/transactions")
@app.route("/admin-secret")

def admin_secret():

    return render_template(
        "admin_links.html"
    )


# =========================================================
# MAIN
# =========================================================

with app.app_context():

    db.create_all()

if __name__ == "__main__":

    app.run(debug=True)

