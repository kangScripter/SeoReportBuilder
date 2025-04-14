# app/routes.py

from flask import Blueprint, session, redirect, url_for, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html')

@main_bp.route('/report')
def report_builder():
    if 'credentials' not in session:
        return redirect(url_for('auth.authorize'))
    return render_template('drag_drop.html')

