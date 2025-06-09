from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Email, Length
from app import app
from extensions import db
from models import User, Pet, HealthRecord, Reminder, Task
import requests
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Import necessary modules and classes
from forms import RegisterForm, LoginForm, PetForm, HealthRecordForm, ReminderForm, TaskForm

# Authentication Routes (Your Provided Code)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        password = form.password.data if form.password.data else ""
        hashed_password = generate_password_hash(password)
        # Create user with proper column names
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")  # For debugging
            if 'unique constraint' in str(e).lower():
                flash('Email already exists. Please use a different email.', 'danger')
            elif 'null value' in str(e).lower():
                flash('All required fields must be filled out.', 'danger')
            else:
                flash(f'Registration failed!', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        password = form.password.data if form.password.data is not None else ""
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

# Additional Routes (Examples from Previous Response)
@app.route('/dashboard')
@login_required
def dashboard():
    pets = Pet.query.filter_by(user_id=current_user.id).all()
    reminders = Reminder.query.join(Pet).filter(Pet.user_id == current_user.id).all()
    return render_template('dashboard.html', pets=pets, reminders=reminders, now=datetime.utcnow())

@app.route('/pet/add', methods=['GET', 'POST'])
@login_required
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        photo_filename = None
        try:
            # Handle photo upload
            if form.photo.data:
                photo_filename = secure_filename(form.photo.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.photo.data.save(upload_path)

            # Create pet with proper validation
            pet_data = {
                'user_id': current_user.id,
                'name': form.name.data,
                'species': form.species.data,
                'breed': form.breed.data,
                'photo': photo_filename
            }

            # Handle age conversion
            try:
                if form.age.data:
                    pet_data['age'] = int(form.age.data)
            except ValueError:
                flash('Invalid age value, setting age to None', 'warning')
                pet_data['age'] = None

            pet = Pet(**pet_data)
            db.session.add(pet)
            db.session.commit()
            flash('Pet added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file if database operation failed
            if photo_filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                except:
                    pass  # Ignore cleanup errors
            flash('Failed to add pet. Please try again.', 'danger')
            
    return render_template('pet_form.html', form=form, title='Add Pet')

@app.route('/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
        
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        try:
            if form.photo.data:
                photo_filename = secure_filename(form.photo.data.filename)
                form.photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                # Delete old photo if it exists
                if pet.photo:
                    old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], pet.photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                pet.photo = photo_filename
            
            pet.name = form.name.data
            pet.species = form.species.data
            pet.breed = form.breed.data
            try:
                pet.age = int(form.age.data) if form.age.data else None
            except ValueError:
                pet.age = None
            
            db.session.commit()
            flash('Pet updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update pet. Please try again.', 'danger')
            return redirect(url_for('edit_pet', pet_id=pet_id))
            
    return render_template('pet_form.html', form=form, title='Edit Pet')

@app.route('/pet/<int:pet_id>/health', methods=['GET', 'POST'])
@login_required
def health_record(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    form = HealthRecordForm()
    if form.validate_on_submit():
        try:
            date_str = form.date.data if form.date.data is not None else ""
            date_val = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
            record = HealthRecord(
                pet_id=pet_id,
                type=form.type.data if form.type.data is not None else "",
                date=date_val,
                details=form.details.data if form.details.data is not None else "",
                weight=float(form.weight.data) if form.weight.data else None
            )
            db.session.add(record)
            db.session.commit()
            flash('Health record added.', 'success')
            return redirect(url_for('pet_detail', pet_id=pet_id))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
    records = HealthRecord.query.filter_by(pet_id=pet_id).all()
    return render_template('health_record.html', form=form, pet=pet, records=records)

@app.route('/pet/<int:pet_id>/reminders', methods=['GET', 'POST'])
@login_required
def reminders(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    form = ReminderForm()
    if form.validate_on_submit():
        try:
            date_str = form.due_date.data if form.due_date.data is not None else ""
            due_date_val = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
            recurring_str = form.recurring.data if form.recurring.data is not None else ""
            recurring_val = recurring_str.lower() == 'true' if recurring_str else False
            
            reminder = Reminder(
                pet_id=pet_id,
                task=form.task.data if form.task.data is not None else "",
                due_date=due_date_val,
                recurring=recurring_val
            )
            db.session.add(reminder)
            db.session.commit()
            flash('Reminder added.', 'success')
            return redirect(url_for('pet_detail', pet_id=pet_id))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
    reminders = Reminder.query.filter_by(pet_id=pet_id).all()
    return render_template('reminders.html', form=form, pet=pet, reminders=reminders)

@app.route('/pet/<int:pet_id>/checklist', methods=['GET', 'POST'])
@login_required
def checklist(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(pet_id=pet_id, description=form.description.data)
        db.session.add(task)
        db.session.commit()
        flash('Task added.', 'success')
        return redirect(url_for('checklist', pet_id=pet_id))
    tasks = Task.query.filter_by(pet_id=pet_id).all()
    return render_template('checklist.html', form=form, pet=pet, tasks=tasks)

@app.route('/pet/<int:pet_id>/task/<int:task_id>/complete')
@login_required
def complete_task(pet_id, task_id):
    task = Task.query.get_or_404(task_id)
    if task.pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    flash('Task marked as completed!', 'success')
    return redirect(url_for('checklist', pet_id=pet_id))

@app.route('/pet/<int:pet_id>')
@login_required
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    health_records = HealthRecord.query.filter_by(pet_id=pet_id).order_by(HealthRecord.date.desc()).all()
    reminders = Reminder.query.filter_by(pet_id=pet_id).order_by(Reminder.due_date).all()
    tasks = Task.query.filter_by(pet_id=pet_id).all()
    return render_template('pet_detail.html', pet=pet, health_records=health_records, reminders=reminders, tasks=tasks)

@app.route('/pet/<int:pet_id>/care-tips')
@login_required
def care_tips(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    tips = {
        'dog': [
            'Regular exercise is essential',
            'Schedule annual vet checkups',
            'Keep vaccinations up to date',
            'Regular grooming and dental care'
        ],
        'cat': [
            'Clean litter box daily',
            'Provide scratching posts',
            'Regular play sessions',
            'Keep indoor cats entertained'
        ]
    }
    # Default to dog tips if species not recognized
    species = pet.species.lower() if pet.species else 'dog'
    pet_tips = tips.get(species, tips['dog'])
    return render_template('care_tips.html', pet=pet, tips=pet_tips)

# Add other routes (e.g., edit_pet, health_record, reminders, checklist, care_tips) here