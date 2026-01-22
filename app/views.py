from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import UserProfile, ExerciseLog
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

@login_required
def dashboard(request):
    user = request.user
    try:
        profile = user.userprofile
        bmr = profile.calculate_bmr()
        suggested_cal = profile.calculate_suggested_calories(goal='lose') 
    except UserProfile.DoesNotExist:
        return redirect('create_profile')
    exercises = ExerciseLog.objects.filter(user=user).select_related('user__userprofile').order_by('-created_at')
    context = {
        'bmr': bmr,
        'suggested_cal': suggested_cal,
        'exercises': exercises,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_exercise(request):
    if request.method == 'POST':
        e_type = request.POST.get('type') 
        duration = request.POST.get('duration')
        if e_type and duration:
            ExerciseLog.objects.create(
                user=request.user,
                exercise_type=e_type,          
                duration_minutes=int(duration) 
            )
            return redirect('dashboard')   
    return render(request, 'add_exercise.html')

@login_required
def edit_exercise(request, pk):
    exercise = get_object_or_404(ExerciseLog, pk=pk)
    if request.user != exercise.user:
        return redirect('dashboard')
    if request.method == 'POST':
        new_type = request.POST.get('type')
        new_duration = request.POST.get('duration')
        if new_type and new_duration:
            exercise.exercise_type = new_type
            exercise.duration_minutes = int(new_duration)
            exercise.save() 
            return redirect('dashboard')
    context = {
        'exercise': exercise,
        'title': '記録編集'
    }
    return render(request, 'add_exercise.html', context)

@login_required
def delete_exercise(request, pk):
    exercise = get_object_or_404(ExerciseLog, pk=pk)
    if request.user != exercise.user:
        return redirect('dashboard')
    if request.method == 'POST':
        exercise.delete()
        return redirect('dashboard')
    return render(request, 'exercise_confirm_delete.html', {'exercise': exercise})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def create_profile(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        birth_date = request.POST.get('birth_date')
        activity = request.POST.get('activity_level')
        if gender and height and weight and birth_date:
            UserProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'gender': gender,
                    'height': float(height),
                    'weight': float(weight),
                    'birth_date': birth_date,
                    'activity_level': float(activity) if activity else 1.2
                }
            )
            return redirect('dashboard')
    return render(request, 'profile_form.html')