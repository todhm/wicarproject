from flask import Blueprint, render_template,session,make_response,request,flash,jsonify,redirect,url_for,current_app,abort


carterms_app = Blueprint('carterms_app',__name__,template_folder='templates')



@carterms_app.route('/policies/terms/service')
def term_service():
    return render_template('carterms/service.html',term_service="active")


@carterms_app.route('/policies/privacy')
def privacy():
    return render_template('carterms/privacy.html',privacy="active")


@carterms_app.route('/policies/terms/location')
def term_location():
    return render_template('carterms/term_location.html',term_location="active")

@carterms_app.route('/about')
def about_page():
    return render_template('carterms/about.html')

@carterms_app.route('/policies/cancellation')
def cancellation():
    return render_template('carterms/cancellation.html')

@carterms_app.route('/policies/cleaning')
def cleaning_policy():
    return render_template('carterms/cleaning.html')

@carterms_app.route('/policies/distance')
def distance_policy():
    return render_template('carterms/distance.html')

@carterms_app.route('/policies/latency')
def latency_policy():
    return render_template('carterms/late_return.html')
