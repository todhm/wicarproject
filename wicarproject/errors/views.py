from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,current_app
from application import db


error_app = Blueprint('error_app', __name__)


@error_app.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@error_app.app_errorhandler(500)
def internal_error(error):
    message = [str(x) for x in error.args]
    request._tracking_data = {
        'message':message
    }
    db.session.rollback()
    return render_template('errors/500.html'), 500


@error_app.app_errorhandler(403)
def invalid_request_error(error):
    db.session.rollback()
    return render_template('errors/403.html'), 403


@error_app.app_errorhandler(413)
def filesize_error(error):
    db.session.rollback()
    return render_template('errors/413.html'), 413
