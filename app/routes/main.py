from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/ticker/<ticker>')
def ticker_details(ticker):
    return render_template('details.html', ticker=ticker)
