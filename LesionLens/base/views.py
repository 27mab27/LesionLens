import os
import time
from django.http import HttpResponse, JsonResponse
import numpy as np
from PIL import Image
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from ultralytics import YOLO
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Patient, Diagnosis
from django.contrib.auth import get_user_model
from .decorators import approved_specialist_required
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404



MODEL_PATH = os.path.join(settings.BASE_DIR, 'static', 'yolo_weights', 'best.pt')
model = YOLO(MODEL_PATH)

CustomUser = get_user_model()

# 🔁 Shared YOLO logic
def run_yolo_on_image(patient, image_path):
    start_time = time.time()
    results = model.predict(
        source=image_path,
        conf=0.5,
        iou=0.45,
        hide_labels=True,
        hide_conf=True
    )
    end_time = time.time()
    inference_time = round(end_time - start_time, 2)

    if results and len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        cls_id = int(box.cls[0])
        class_name = model.names.get(cls_id, f"Class {cls_id}")
        confidence = float(box.conf[0])
    else:
        class_name = "No lesions detected"
        confidence = 0.0

    annotated_array = results[0].plot(boxes=True, labels=False, conf=False)
    annotated_image = Image.fromarray(annotated_array)
    annotated_image.save(image_path)

    return class_name, confidence, inference_time

@approved_specialist_required
@approved_specialist_required
def home(request):
    class_name = None
    confidence = None
    inference_time = None
    annotated_url = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        image_file = request.FILES.get('xray_image')

        if image_file and email:
            patient = Patient.objects.filter(email=email).first()
            if not patient:
                patient = Patient.objects.create(
                    email=email,
                    full_name=full_name,
                    created_by=request.user  # optional if you track who added them
                )

            diagnosis = Diagnosis.objects.create(
                patient=patient,
                image=image_file,
                status="Pending"
            )

            image_path = diagnosis.image.path

            # YOLO Inference
            start_time = time.time()
            results = model.predict(
                source=image_path,
                conf=0.5,
                iou=0.45,
                hide_labels=True,
                hide_conf=True
            )
            end_time = time.time()
            inference_time = round(end_time - start_time, 2)

            if results and len(results[0].boxes) > 0:
                box = results[0].boxes[0]
                cls_id = int(box.cls[0])
                class_name = model.names.get(cls_id, f"Class {cls_id}")
                confidence = float(box.conf[0])
            else:
                class_name = "No lesions detected"
                confidence = 0.0

            # Annotate + overwrite
            annotated_array = results[0].plot(boxes=True, labels=False, conf=False)
            annotated_image = Image.fromarray(annotated_array)
            annotated_image.save(image_path)

            diagnosis.status = class_name
            diagnosis.save()

            annotated_url = diagnosis.image.url

    return render(request, 'home.html', {
        'class_name': class_name,
        'confidence': confidence,
        'inference_time': inference_time,
        'annotated_url': annotated_url
    })


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('manage_users')
        elif request.user.role == 'specialist' and request.user.is_approved:
            return redirect('home')
        else:
            messages.error(request, 'Your account is not approved yet.')
            logout(request)
            return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('manage_users')
            elif user.role == 'specialist' and user.is_approved:
                return redirect('home')
            else:
                messages.error(request, 'Your account is not approved yet.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('manage_users')
        elif hasattr(request.user, 'specialist') and request.user.specialist.is_approved:
            return redirect('home')
        else:
            messages.error(request, 'Your account is not approved yet.')
            logout(request)
            return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('manage_users')
            elif hasattr(user, 'specialist') and user.specialist.is_approved:
                return redirect('home')
            else:
                messages.error(request, 'Your account is not approved yet.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')

    


User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']  
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='specialist',
            is_approved=False
        )
        user.phone = phone
        user.save()

        messages.success(request, "Account created. Wait for admin approval.")
        return redirect('login')

    return render(request, 'signup.html')

  
      

def add_user(request):
    return render(request, 'add_user.html')

@approved_specialist_required
def add_patient(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        gender = request.POST.get('gender', '')
        age = request.POST.get('age', '')
        city = request.POST.get('city', '')
        weight = request.POST.get('weight', '')
        height = request.POST.get('height', '')
        description = request.POST.get('description', '')

        Patient.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            age=age,
            city=city,
            weight=weight,
            height=height,
            description=description,
            created_by=request.user  # 👈 New field
        )

        messages.success(request, "Patient added successfully!")
        return redirect('home')

    return render(request, 'add_patient.html')



@login_required
def profile_tab(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)

        if request.FILES.get('profile_photo'):
            user.profile_photo = request.FILES['profile_photo']

        user.save()
        return redirect('profile_tab')

    return render(request, 'profile_tab.html', {'user': user})


@approved_specialist_required
def diagnosis_history(request):
    user = request.user
    patients = Patient.objects.filter(created_by=user).prefetch_related('diagnosis_set')

    records = []
    for patient in patients:
        latest_diagnosis = patient.diagnosis_set.order_by('-date').first()
        records.append({
            'patient': patient,
            'diagnosis': latest_diagnosis
        })

    return render(request, 'diagnosis_history.html', {'records': records})




def retrieve_password(request):
    return render(request, 'retrieve_password.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def role_based_redirect(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'specialist' and user.is_approved:
        return redirect('home')
    return redirect('login')  # fallback for others or unapproved

def get_patient_name(request):
    email = request.GET.get('email')
    if email:
        try:
            patient = Patient.objects.get(email=email)
            return JsonResponse({'name': patient.full_name})
        except Patient.DoesNotExist:
            return JsonResponse({'name': ''})
    return JsonResponse({'name': ''})


def ajax_diagnose_now(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            patient = Patient.objects.get(email=email)
            diagnosis = Diagnosis.objects.filter(patient=patient).order_by('-date').first()

            if not diagnosis or not diagnosis.image:
                return JsonResponse({'error': 'No image found.'}, status=404)

            image_path = diagnosis.image.path

            start_time = time.time()
            results = model.predict(
                source=image_path,
                conf=0.5,
                iou=0.45,
                hide_labels=True,
                hide_conf=True
            )
            end_time = time.time()

            if results and len(results[0].boxes) > 0:
                box = results[0].boxes[0]
                cls_id = int(box.cls[0])
                class_name = model.names.get(cls_id, f"Class {cls_id}")
            else:
                class_name = "No lesions detected"

            diagnosis.status = class_name
            diagnosis.save()

            return JsonResponse({
                'status': class_name,
                'date': diagnosis.date.strftime("%Y-%m-%d")
            })

        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        patient.full_name = request.POST.get('full_name')
        patient.email = request.POST.get('email')
        patient.phone = request.POST.get('phone')
        patient.gender = request.POST.get('gender')
        patient.age = request.POST.get('age')
        patient.city = request.POST.get('city')
        patient.weight = request.POST.get('weight')
        patient.height = request.POST.get('height')
        patient.description = request.POST.get('description')
        patient.save()
        messages.success(request, "Patient updated successfully.")
        return redirect('diagnosis_history')  # or wherever you want to redirect

    return render(request, 'edit_patient.html', {'patient': patient})




@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        if 'approve_id' in request.POST:
            specialist_id = request.POST['approve_id']
            specialist = CustomUser.objects.get(id=specialist_id, role='specialist')
            specialist.is_approved = True
            specialist.save()
        elif 'delete_id' in request.POST:
            specialist_id = request.POST['delete_id']
            CustomUser.objects.filter(id=specialist_id, role='specialist').delete()
        return redirect('manage_users')

    specialists = CustomUser.objects.filter(role='specialist')
    return render(request, 'manage_users.html', {'specialists': specialists})


