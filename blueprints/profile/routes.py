from . import profile_bp
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
import os
from werkzeug.utils import secure_filename

@profile_bp.route('/')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@profile_bp.route('/upload', methods=['POST'])
@login_required
def upload_photo():
    photo = request.files.get("photo")
    if not photo:
        flash("Моля, избери снимка.", "warning")
        return redirect(url_for("profile.profile"))

    if not photo.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        flash("Позволени формати: PNG, JPG, JPEG", "danger")
        return redirect(url_for("profile.profile"))

    filename = f"{current_user.username}_{secure_filename(photo.filename)}"
    upload_path = os.path.join("static", "uploads")
    os.makedirs(upload_path, exist_ok=True)
    photo.save(os.path.join(upload_path, filename))

    current_user.profile_image = filename
    db.session.commit()
    flash("Снимката е обновена успешно!", "success")
    return redirect(url_for("profile.profile"))


@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    old = request.form.get('old_password')
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not current_user.check_password(old):
        flash("Грешна текуща парола.", "danger")
        return redirect(url_for('profile.profile'))

    if new != confirm:
        flash("Паролите не съвпадат.", "warning")
        return redirect(url_for('profile.profile'))

    current_user.set_password(new)
    db.session.commit()
    flash("Паролата е обновена успешно!", "success")
    return redirect(url_for('profile.profile'))


@profile_bp.route('/update', methods=['POST'])
@login_required
def update_profile():
    first = request.form.get('first_name')
    last = request.form.get('last_name')

    if first:
        current_user.first_name = first
    if last:
        current_user.last_name = last

    if 'profile_image' in request.files:
        image = request.files['profile_image']
        if image.filename:
            os.makedirs("static/uploads", exist_ok=True)
            img_path = os.path.join("static", "uploads", f"{current_user.username}.jpg")
            image.save(img_path)
            current_user.profile_image = f"{current_user.username}.jpg"

    db.session.commit()
    flash("Профилът е обновен успешно!", "success")
    return redirect(url_for('profile.profile'))
