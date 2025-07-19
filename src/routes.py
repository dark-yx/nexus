from flask import render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .. import db
from ..models.entities.User import User
from ..db import create_user, get_user_by_email, get_user, update_user, save_or_update_user, check_user_credits, update_user_credits, get_user_credits, save_feedback, record_transaction, get_user_id_from_payment, get_user_history, get_user_preferred_language, update_user_preferred_language, get_user_by_username
import json

# Aquí irán todas las rutas de la aplicación
@main.route('/')
def index():
    if not session.get("user"):
        return redirect(url_for("main.marketing_consultant"))
    user_data = session.get("user")
    display_name = session.get("display_name")
    given_name = session.get("given_name")
    return render_template('index.html', user_data=user_data, display_name=display_name, given_name=given_name, pretty=json.dumps(user_data, indent=4))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user_by_email(email)

        if user and user.check_password(password):
            login_user(user)
            session["user_id"] = user.id
            session["display_name"] = user.display_name
            session["user"] = {
                'personData': {"emailAddresses": [{"value": user.email}]}
            }
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('main.index'))
        
        flash('Correo o contraseña incorrectos.', 'danger')
        return render_template('login.html')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        display_name = request.form.get('display_name')

        if get_user_by_email(email):
            flash('El correo ya está en uso.', 'danger')
            return render_template('register.html')

        create_user(email=email, password=password, display_name=display_name)
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión con éxito.', 'success')
    return redirect(url_for('main.login'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user(current_user.id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        update_user(
            user.id,
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            meta_access_token=request.form.get('meta_access_token'),
            app_secret=request.form.get('app_secret'),
            app_id=request.form.get('app_id'),
            ad_account_id=request.form.get('ad_account_id')
        )
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', user=user)

@main.route('/comprar-creditos')
def comprar_creditos():
    return render_template('comprar_creditos.html', planes=config.credit_plans)


@main.route('/producto/<plan_name>')
def producto_detalle(plan_name):
    plan = config.credit_plans.get(plan_name)
    if not plan:
        return "Plan no encontrado", 404
    return render_template('producto.html', plan=plan, plan_name=plan_name)


@main.route('/pago_exitoso')
def pago_exitoso():
    payment_id = request.args.get("paymentId")
    payer_id = request.args.get("PayerID")
    user_id = request.args.get("user_id") or session.get("user_id")
    credits = request.args.get("credits")
    amount = request.args.get("amount")

    if not all([payment_id, payer_id, credits, amount]):
        return jsonify({"error": "Faltan parámetros de pago"}), 400

    try:
        credits = int(credits)
        amount = float(amount)

        if not user_id:
            user_id = get_user_id_from_payment(payment_id)
            if not user_id:
                return jsonify({"error": "No se pudo determinar el usuario"}), 400

        if record_transaction(user_id, payment_id, payer_id, amount, credits, "completed"):
            update_user_credits(user_id, credits)
            return render_template("pago_exitoso.html", paymentId=payment_id, payerId=payer_id, amount=amount, credits=credits)
        else:
            return render_template("pago_fallido.html", message="Error al registrar la transacción")
    
    except Exception as e:
        return jsonify({"error": "Error interno", "debug_info": str(e)}), 500


@main.route('/pago_cancelado')
def pago_cancelado():
    return render_template("pago_cancelado.html")

from ..agents.derek_ai import DerekAI
from src.lead_scoring import LeadScoringSystem
from werkzeug.utils import secure_filename
import os

derek_ai = DerekAI()

@main.route('/derek', methods=['POST'])
@login_required
def derek():
    user_input = request.form.get('input')
    user_id = session.get("user_id")
    result = derek_ai.orchestrate(user_input, user_id, db)
    return jsonify(result)

@main.route('/analisis-web', methods=['GET', 'POST'])
@login_required
def analisis_web():
    if request.method == 'POST':
        data = request.form.to_dict()
        user_id = session.get("user_id")
        chart_data, resumen = analizar_embudo(data, user_id, db)
        return render_template('analisis.html', chart_data=chart_data, resumen=resumen)
    return render_template('analisis.html')

@main.route('/keyword_research', methods=['GET', 'POST'])
@login_required
def keyword_research_route():
    if request.method == 'POST':
        client = None # Reemplazar con la inicialización del cliente de Google Ads
        customer_id = '' # Reemplazar con el ID de cliente de Google Ads
        location_ids = [''] # Reemplazar con los IDs de ubicación
        language_id = '' # Reemplazar con el ID de idioma
        keyword_texts = request.form.get('keywords').split(',')
        page_url = request.form.get('url')
        user_id = session.get("user_id")
        results = run_keyword_research(client, customer_id, location_ids, language_id, keyword_texts, page_url, user_id, db)
        return render_template('keyword_research.html', results=results)
    return render_template('keyword_research.html')

@main.route('/lead_scoring', methods=['GET', 'POST'])
@login_required
def lead_scoring():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            clearbit_api_key = os.environ.get('CLEARBIT_API_KEY')
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            lead_scoring_system = LeadScoringSystem(clearbit_api_key=clearbit_api_key, openai_api_key=openai_api_key)
            results, error, chart_html = lead_scoring_system.run(file_path)

            if error:
                flash(error, 'danger')
                return redirect(request.url)

            return render_template('lead_scoring_results.html', results=results, chart_html=chart_html)
    return render_template('lead_scoring.html')

# ... (y así sucesivamente para todas las demás rutas)
