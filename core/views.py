from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages as msg
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, When, Value, IntegerField, Count
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import datetime
import urllib.parse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db.models import Q, Count, Sum
from .serializers import *
from rest_framework import generics, status, permissions
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.timezone import make_aware, get_current_timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateformat import DateFormat
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import now
from .forms import BlogCommentForm
from datetime import datetime
from datetime import date



class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        role = getattr(request.user.summary, 'role', None)

        if role not in self.allowed_roles:
            return HttpResponseForbidden("You are not allowed to access this page")

        return super().dispatch(request, *args, **kwargs)
    



class RoleRequiredMixin:
    allowed_roles = None
    exclude_roles = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        role = getattr(request.user.summary, 'role', None)

        # ✅ allow only specific roles
        if self.allowed_roles is not None:
            if role not in self.allowed_roles:
                return HttpResponseForbidden("You are not allowed")

        # ❌ exclude specific roles
        if self.exclude_roles is not None:
            if role in self.exclude_roles:
                return HttpResponseForbidden("You are not allowed")

        return super().dispatch(request, *args, **kwargs)
    





def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                user_role = request.user.summary.role
            except Summary.DoesNotExist:
                return redirect('no_permission')

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('no_permission')

        return wrapper
    return decorator


# Create your views here.
def homepage(request):
    return render(request, 'frontend/homepage.html')


def login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            msg.success(request, "Logged In")


            try:
                profile = Summary.objects.get(user=user)
            except ObjectDoesNotExist:
                msg.error(request,'Profile does not exist. You cannot access here.')
                return redirect('homepage')

        
            if profile:
                if profile.role == 'hr':
                    return redirect('hr_dashboard')
                if profile.role == 'frontdesk':
                    return redirect('dashboard')
                    
                if profile.role == 'admin':
                    return redirect('dashboard')
                    
                if profile.role == 'media':
                    return redirect('media_dashboard') #media______
                else:
                    return redirect('homepage')
            return redirect('dashboard')
            
        else:
            print("Error")
            msg.error(request, 'Invalid Credential')
            return render(request, 'backend/login.html')
    return render(request, 'backend/login.html')


# logout 
@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')


# views.py
def no_permission(request):
    return render(request, 'backend/no_permission.html')




@role_required(['super-admin'])
@login_required(login_url='login')
def user_list(request):
    users = User.objects.all().select_related('summary')
    return render(request, 'backend/user_list.html', {'users': users})


@role_required(['super-admin'])
@login_required(login_url='login')
def user_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        summary_form = SummaryForm(request.POST)

        if user_form.is_valid() and summary_form.is_valid():
            user = user_form.save(commit=False)

            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])

            user.save()

            summary = summary_form.save(commit=False)
            summary.user = user
            summary.save()

            return redirect('user-list')

        else:
            print("USER FORM ERRORS:", user_form.errors)
            print("SUMMARY FORM ERRORS:", summary_form.errors)

    else:
        user_form = UserForm()
        summary_form = SummaryForm()

    return render(request, 'backend/user_form.html', {
        'user_form': user_form,
        'summary_form': summary_form
    })


@role_required(['super-admin'])
@login_required(login_url='login')
def user_edit(request, id):
    user = get_object_or_404(User, id=id)
    summary, created = Summary.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        summary_form = SummaryForm(request.POST, instance=summary)

        if user_form.is_valid() and summary_form.is_valid():
            user = user_form.save(commit=False)

            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])

            user.save()
            summary_form.save()

            return redirect('user-list')

    else:
        user_form = UserForm(instance=user)
        summary_form = SummaryForm(instance=summary)

    return render(request, 'backend/user_form.html', {
        'user_form': user_form,
        'summary_form': summary_form
    })


@role_required(['super-admin'])
@login_required(login_url='login')
def user_delete(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('user-list')





@role_required(['super-admin', 'admin', 'doctor', 'receptionist'])
@login_required(login_url='login')
def dashboard(request):

    today = timezone.now().date()
    now = timezone.now()

    today_completed_qs = Appointment.objects.filter(
        date=today,
        status='COMPLETED'
    ).select_related('patient', 'selected_doctor', 'department')

    context = {
        "total_blogs": Blog.objects.count(),
        "total_patients": Patient.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "today_appointments": today_completed_qs.count(),
        "month_appointments": Appointment.objects.filter(
            date__month=now.month,
            date__year=now.year
        ).count(),
        "total_doctors": Doctor.objects.count(),
        "total_departments": Department.objects.count(),
        "total_messages": Message.objects.count(),
        "total_notifications": Notification.objects.count(),
        "total_checkups": HealthCheckupBooking.objects.count(),
        "total_careers": Career.objects.count(),
        "total_applications": CareerApplication.objects.count(),
        "today_completed_qs": today_completed_qs
    }

    return render(request, "backend/dashboard.html", context)


@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def departments(request):
    departments = Department.objects.all().order_by("priority")
    context = {
        'departments': departments
    }
    return render(request, 'backend/departments.html', context)

@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def create_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Department created successfully")
            return redirect("departments")  # change if you have list page
    else:
        form = DepartmentForm()

    return render(request, "backend/create-department.html", {"form": form})




# ✏️ Edit Department
@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def edit_department(request, slug):
    department = get_object_or_404(Department, slug=slug)

    if request.method == "POST":
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            form.save()
            msg.success(request, "Department updated successfully")
            return redirect("departments")  # change if needed
    else:
        form = DepartmentForm(instance=department)

    return render(request, "backend/create-department.html", {
        "form": form,
        "is_edit": True
    })


# 🗑 Delete Department
@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def delete_department(request, slug):
    department = get_object_or_404(Department, slug=slug)
    department.delete()
    msg.success(request, "Department deleted successfully")
    return redirect("departments")



# 🔹 Get all notifications
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_notifications_list(request):
    notifications = Notification.objects.filter(read_status=False).order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


# 🔹 Mark single notification as read
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.read_status = True
    notification.first_read_by = request.user
    notification.save()

    return Response({"message": "Notification marked as read"})


# 🔹 Mark all notifications as read
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_mark_all_notifications_read(request):
    Notification.objects.filter(read_status=False).update(
        read_status=True,
        first_read_by=request.user
    )
    return Response({"message": "All notifications marked as read"})


@login_required(login_url='login')
def notifications_list(request):
    notifications = Notification.objects.all().order_by('-created_at')

    return render(request, "backend/notifications.html", {
        "notifications": notifications
    })


@login_required(login_url='login')
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    # mark as read
    notification.read_status = True

    # set first reader only once
    if not notification.first_read_by:
        notification.first_read_by = request.user

    notification.save()

    return redirect(request.META.get('HTTP_REFERER', 'notifications_list'))


# doctors view 
@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def doctors(request):

    doctors = Doctor.objects.annotate(
        is_priority_null=Case(
            When(priority=None, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('is_priority_null', 'priority')
    context ={ 'doctors': doctors }
    return render(request, 'backend/doctors.html', context)

@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def create_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            print("Coming Hhere")
            doctor = form.save(commit=False)
            doctor.save()
            msg.success(request, "Doctor Added Successfully")
            return redirect('doctors')  # Replace with your redirect URL
        
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
                    print(error_messages)
            msg.error(request, error_messages)
    form = DoctorForm()
    return render(request, 'backend/create-doctor.html', {'form': form})

@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def update_doctor(request, slug):
    doctor = Doctor.objects.get(slug=slug)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.save()
            msg.success(request, "Doctor Updated Successfully")
            return redirect('doctors')  # Replace with your redirect URL
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
            msg.error(request, error_messages)
    else:
        form = DoctorForm(instance =doctor)
    return render(request, 'backend/update-doctor.html', {'form': form, 'doctor':doctor})

@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def delete_doctor(request, slug):

    try:
        doctor = Doctor.objects.get(slug=slug)
        doctor.delete()
        msg.success(request, 'Doctor deleted successfully.')
        return redirect('doctors')
    except Doctor.DoesNotExist:
        msg.error(request, 'doctor not found.')
        return redirect('doctor')


@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def create_monthly_timing(request, pk):
    if request.method == 'POST':
        form2 = MonthlyTimeForm(request.POST)
        if form2.is_valid():
            timing = form2.save(commit=False)
            doctor = get_object_or_404(Doctor, id=pk)
            timing.doctor = doctor  # Assign the doctor to the timing instance
            timing.remaining_slots = timing.slot


            # Check if the start date is today or in the future
            if timing.date < timezone.now().date():
                msg.error(request, "The date must be today or in the future. Past dates are not allowed.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # Check if the start time is less than end time
            if timing.start_time >= timing.end_time:
                msg.error(request, "Ending Time must be greater than Starting Time.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # Check if the same doctor has any other timing in this time range
            overlapping_timings = MonthlyTiming.objects.filter(
                doctor=doctor,
                date=timing.date,
                start_time__lt=timing.end_time,
                end_time__gt=timing.start_time
            )

            if overlapping_timings.exists():
                msg.error(request, "The doctor already has another timing in this time range. Please choose a different time.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            # If all checks pass, save the timing
            timing.save()
            msg.success(request, "Timing Updated Successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            # Gather all form errors
            error_messages = "Please correct the errors below:\n"
            for field, errors in form2.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}\n"
            msg.error(request, error_messages)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    



@role_required(['super-admin', 'admin', 'doctor'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_timing_api(request, doctor_slug):
    doctor = get_object_or_404(Doctor, slug=doctor_slug)
    selected_slots = request.data.get('selected_slots', [])
    slot_count = request.data.get('slot', 1)

    if not selected_slots:
        return Response({"error": "No slots selected"}, status=status.HTTP_400_BAD_REQUEST)

    for slot in selected_slots:
        day, times = slot.split(' ', 1)
        start_time, end_time = times.split('-')

        # Convert strings to time objects
        start_time_obj = datetime.datetime.strptime(start_time.strip(), '%H:%M').time()
        end_time_obj = datetime.datetime.strptime(end_time.strip(), '%H:%M').time()

        # Check for overlapping times
        overlapping_timings = AvailableTime.objects.filter(
            doctor=doctor,
            day=day,
            status='active',
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj
        )

        if overlapping_timings.exists():
            return Response(
                {"error": f"The doctor already has another timing in this time range for {day}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the available time object
        AvailableTime.objects.create(
            doctor=doctor,
            day=day,
            start_time=start_time_obj,
            end_time=end_time_obj,
            slot=slot_count,
            status='active',
            remaining_slots=slot_count
        )

    return Response({"success": "Timings added successfully"}, status=status.HTTP_201_CREATED)


@role_required(['super-admin', 'admin', 'doctor'])      
@login_required(login_url='login')
def create_timing(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    timings = AvailableTime.objects.filter(doctor=doctor, status='active').order_by('day', 'start_time')
    monthly_timing = MonthlyTiming.objects.filter(doctor=doctor, status='active')

    if request.method == 'POST':
        form = AvailableTimeForm(request.POST)
        form2 = MonthlyTimeForm(request.POST)
        if form.is_valid():
            timing = form.save(commit=False)
            timing.doctor = doctor
            timing.remaining_slots = timing.slot

            # Check if the same doctor has any other timing in this time
            overlapping_timings = AvailableTime.objects.filter(
                doctor=doctor,
                day=timing.day,
                status='active',
                start_time__lt=timing.end_time,
                end_time__gt=timing.start_time
            )

            # Check if the start time is less than end time
            if timing.start_time >= timing.end_time:
                msg.error(request, "Ending Time must be greater than Starting Time.")
            elif overlapping_timings.exists():
                msg.error(request, "The doctor already has another timing in this time range. Please choose a different time.")
            else:
                timing.save()
                msg.success(request, "Timing Updated Successfully")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            error_messages = "Please correct the errors below:<br>"
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages += f"{field}: {error}<br>"
            msg.error(request, error_messages)
    else:
        form = AvailableTimeForm()
        form2 = MonthlyTimeForm()

    return render(request, 'backend/create-timing.html', {'doctor': doctor, 'form': form, 'timings': timings, 'form2': form2, 'monthly_timing': monthly_timing})




@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def leave_appointments(request):

    # Retrieve the appointment IDs from the query string
    appointment_ids = request.GET.getlist('upcoming_appointment_ids')

    upcoming_appointments_list = []
    now = timezone.now()

    if appointment_ids:
        appointments = Appointment.objects.filter(id__in=appointment_ids, status="COMPLETED")

        # Process each appointment
        for appointment in appointments:
            payment_details = RazorpayPaymentDetails.objects.filter(status = 'COMPLETED',appointment=appointment).first()
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            # Determine the appointment datetime based on the related object
            if isinstance(related_object, AvailableTime):
                appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            else:
                appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

            # Only consider upcoming appointments
            if appointment_datetime >= now:
                detailed_appointment = {
                    'appointment': appointment,
                    'payment_details': payment_details,
                    'related_object': related_object
                }
                upcoming_appointments_list.append(detailed_appointment)

    # Render the response with the list of upcoming appointments
    return render(request, 'backend/leave-appointments.html', {
        'upcoming_appointments_list': upcoming_appointments_list,
    })


@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def delete_timing(request, pk):


    try:
        timing = AvailableTime.objects.get(id=pk)

        # Check if there are any appointments for this timing
        appointments = Appointment.objects.filter(
            content_type=ContentType.objects.get_for_model(AvailableTime),
            object_id=timing.id
        )

        # Separate past and upcoming appointments
        upcoming_appointments = appointments.filter(date__gte=timezone.now(), status='COMPLETED')
        past_appointments = appointments.filter(date__lt=timezone.now())

        if upcoming_appointments.exists():
        
            # Mark timing as inactive
            timing.status = 'inactive'
            timing.save()

            msg.warning(request, f'Timing has {upcoming_appointments.count()} upcoming appointment(s). The timing is now inactive, and new appointments cannot be created. Please attend to the already booked appointments.')

            # Collect upcoming appointment IDs to pass to the next view
            upcoming_appointment_ids = list(upcoming_appointments.values_list('id', flat=True))

            # Construct the query string
            query_string = urllib.parse.urlencode({'upcoming_appointment_ids': upcoming_appointment_ids}, doseq=True)
            url = f"{reverse('leave_appointments')}?{query_string}"

            # Redirect to leave_appointments URL with query parameters
            return redirect(url)

        else:
            # Delete timing if there are no upcoming appointments
            timing.status = 'inactive'
            timing.save()
            msg.success(request, 'Timing deleted successfully.')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except AvailableTime.DoesNotExist:
        msg.error(request, 'Timing not found.')
        return redirect('doctor')

@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def delete_timing_monthly(request, pk):
    try:
        timing = MonthlyTiming.objects.get(id=pk)
        
        # Check if there are any appointments for this timing
        appointments = Appointment.objects.filter(content_type=ContentType.objects.get_for_model(MonthlyTiming), object_id=timing.id)
        
        # Separate past and upcoming appointments
        upcoming_appointments = appointments.filter(date__gte=timezone.now(), status='COMPLETED')
        past_appointments = appointments.filter(date__lt=timezone.now())

        if upcoming_appointments.exists():
            # Make status inactive for upcoming appointments and provide a message
            timing.status = 'inactive'
            timing.save()
            msg.warning(request, f'This iming has {upcoming_appointments.count()} upcoming appointment(s). The timing is now inactive, and new appointments cannot be created. Please attend to the already booked appointments.')

            # Collect upcoming appointment IDs to pass to the next view
            upcoming_appointment_ids = list(upcoming_appointments.values_list('id', flat=True))

            # Construct the query string
            query_string = urllib.parse.urlencode({'upcoming_appointment_ids': upcoming_appointment_ids}, doseq=True)
            url = f"{reverse('leave_appointments')}?{query_string}"

            # Redirect to leave_appointments URL with query parameters
            return redirect(url)
        else:
            # Delete timing if there are no upcoming appointments
            timing.status = 'inactive'
            timing.save()
            msg.success(request, 'Timing deleted successfully.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except MonthlyTiming.DoesNotExist:
        msg.error(request, 'Timing not found.')
        return redirect('doctor')






@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def create_leave(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    leaves = Leave.objects.filter(doctor=doctor)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        # Convert the dates to actual date objects
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Ensure the start date is today or in the future
        if start_date < timezone.now().date():
            msg.error(request, "The leave start date must be today or in the future.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Ensure the end date is not before the start date
        if end_date < start_date:
            msg.error(request, "The end date cannot be before the start date.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create leave entries for each day in the range
        current_date = start_date
        while current_date <= end_date:
            if Leave.objects.filter(doctor=doctor, date=current_date).exists():
                msg.error(request, f"The doctor already has a leave on {current_date}. Please choose a different date.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            Leave.objects.create(doctor=doctor, date=current_date, reason=reason)
            current_date += datetime.timedelta(days=1)

        msg.success(request, "Leave created successfully.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'backend/leave-request.html', {'doctor': doctor, 'leaves': leaves})

    
@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def delete_leave(request, pk):
    leave = get_object_or_404(Leave, id=pk)
    
    # Check if the leave date is in the past
    if leave.date < timezone.now().date():
        msg.error(request, "You cannot delete this leave because this leave is already taken.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    leave.delete()
    msg.success(request, "Leave deleted successfully.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))






@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def doctor_appointments(request, doctor_id):

    # Fetch the doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    search_query = request.GET.get('search', '')
    active_tab = request.GET.get('tab', 'upcoming')  # Default to upcoming tab
    now = timezone.now()

    # Filter appointments for the doctor based on status
    completed_appointments = Appointment.objects.filter(selected_doctor=doctor, status='COMPLETED').order_by('-date')
    cancelled_appointments = Appointment.objects.filter(selected_doctor=doctor, status='CANCELLED').order_by('-date')

    # Apply search query if provided
    if search_query:
        completed_appointments = completed_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )
        cancelled_appointments = cancelled_appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(patient__phone_number__icontains=search_query) |
            Q(selected_doctor__name__icontains=search_query)
        )

    past_appointments = []
    upcoming_appointments = []
    cancelled_appointments_list = []

    # Process completed appointments
    for appointment in completed_appointments:
        content_type = appointment.content_type

        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'  # Handle missing object case

        # Determine the appointment datetime and timing details
        if isinstance(related_object, AvailableTime):
            appointment_datetime = timezone.datetime.combine(appointment.date, related_object.start_time)
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"
        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            appointment_datetime = timezone.datetime.combine(appointment.date, timezone.datetime.min.time())
            timing_details = "Timing deleted"
        else:
            appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

        # Make appointment_datetime timezone-aware
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details,
            'timing_details': timing_details
        }

        if appointment_datetime < now:
            past_appointments.append(detailed_appointment)
        else:
            upcoming_appointments.append(detailed_appointment)

    # Process cancelled appointments
    for appointment in cancelled_appointments:
        content_type = appointment.content_type
        
        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'  # Handle missing object case

        # Determine timing details
        if isinstance(related_object, AvailableTime):
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"
        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            timing_details = "Timing deleted"
        else:
            timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

        payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()

        detailed_appointment = {
            'appointment': appointment,
            'related_object': related_object,
            'payment_details': payment_details,
            'timing_details': timing_details
        }

        cancelled_appointments_list.append(detailed_appointment)

    # Pagination setup
    paginator_past = Paginator(past_appointments, 20)  # Show 10 past appointments per page
    paginator_upcoming = Paginator(upcoming_appointments, 20)  # Show 10 upcoming appointments per page
    paginator_cancelled = Paginator(cancelled_appointments_list, 20)  # Show 10 cancelled appointments per page

    page_number_past = request.GET.get('page_past')
    page_number_upcoming = request.GET.get('page_upcoming')
    page_number_cancelled = request.GET.get('page_cancelled')

    past_appointments_paginated = paginator_past.get_page(page_number_past)
    upcoming_appointments_paginated = paginator_upcoming.get_page(page_number_upcoming)
    cancelled_appointments_paginated = paginator_cancelled.get_page(page_number_cancelled)

    context = {
        'doctor': doctor,
        'past_appointments': past_appointments_paginated,
        'upcoming_appointments': upcoming_appointments_paginated,
        'cancelled_appointments': cancelled_appointments_paginated,
        'search_query': search_query,
        'active_tab': active_tab,
    }
    return render(request, 'backend/doctor-appointment.html', context)







# blog View Section 
@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def blogs(request):

    blogs = Blog.objects.all()
    context = {'blogs': blogs}
    return render(request, 'backend/blogs.html', context)


@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def delete_blog(request,slug):
    blog = Blog.objects.get(slug=slug)
    blog.delete()
    msg.success(request, "Blog Deleted Successfully")
    return redirect("blogs")




@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def create_blog(request):

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg.success(request, "Blog created successfully")
            return redirect('blogs')
        else:
            msg.error(request, "There were errors in your form. Please correct them.")
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    msg.error(request, f"Error in {field}: {error}")
    else:
        form = BlogForm()
    return render(request, 'backend/create-blog.html', {'form': form})


@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def update_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            msg.success(request,"Blog Updated Successfully")
            return redirect('blogs')  
        else:
            msg.error(request, "There were errors in your form. Please correct them.")
            print(form.errors)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'backend/update-blog.html', {'form': form, 'blog': blog} )




@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def view_blog_comments(request, slug):
    blog = Blog.objects.get(slug=slug)
    comments = BlogComment.objects.filter(blog=blog)
    comments_count = BlogComment.objects.filter(blog=blog).count()

    now = datetime.now().strftime('%I:%M %p')

    context = {
        'blog': blog,
        'comments': comments,
        'comments_count': comments_count,
        'now': now
    }

    return render(request, 'backend/blog-comments-view.html', context)



@role_required(['super-admin', 'admin', 'doctor'])
@login_required(login_url='login')
def view_blog_comment(request, blogSlug, commentSlug):
    blog = get_object_or_404(Blog, slug=blogSlug)
    comment = get_object_or_404(BlogComment, slug=commentSlug)
    comments_count = BlogComment.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {
        'blog': blog,
        'comment': comment,
        'comments_count': comments_count,
        'now': now,
        'rating_range': range(1, 6)  # Pass a range of 1 to 5 for star ratings
    }
    return render(request, 'backend/blog-comments-view-inner.html', context)



@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def delete_blog_comment(request, blogSlug, commentSlug):
    blog = get_object_or_404(Blog, slug=blogSlug)
    comment = get_object_or_404(BlogComment, slug=commentSlug, blog=blog)

    comment.delete()
    msg.success(request, "Comment deleted successfully")

    return redirect('view_blog_comments', slug=blogSlug)



class CareerListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']   # 👈 ACCESS

    model = Career
    template_name = "backend/careers.html"
    context_object_name = "careers"
    ordering = ["-created_at"]


class CareerCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']

    model = Career
    form_class = CareerForm
    template_name = "backend/career-form.html"
    success_url = reverse_lazy("career-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Career"
        return context


class CareerUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']

    model = Career
    form_class = CareerForm
    template_name = "backend/career-form.html"
    success_url = reverse_lazy("career-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Career"
        return context
    



@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def career_delete(request, pk):
    career = get_object_or_404(Career, pk=pk)
    career.delete()
    msg.success(request, "Career deleted successfully")
    return redirect("career-list")


class FAQListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['super-admin']   # 👈 ONLY SUPER ADMIN

    model = FAQ
    template_name = "backend/faqs.html"
    context_object_name = "faqs"
    ordering = ["priority", "-created_at"]


class FAQCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    allowed_roles = ['super-admin']

    model = FAQ
    form_class = FAQForm
    template_name = "backend/faq-form.html"
    success_url = reverse_lazy("faq-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create FAQ"
        return context


class FAQUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    allowed_roles = ['super-admin']

    model = FAQ
    form_class = FAQForm
    template_name = "backend/faq-form.html"
    success_url = reverse_lazy("faq-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit FAQ"
        return context
    



@role_required(['super-admin'])
@login_required(login_url='login')
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    msg.success(request, "FAQ deleted successfully")
    return redirect("faq-list")



class HealthCheckupPlanListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']

    model = HealthCheckupPlan
    template_name = "backend/plan-list.html"
    context_object_name = "plans"
    ordering = ["priority", "-created_at"]


class HealthCheckupPlanCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']

    model = HealthCheckupPlan
    form_class = HealthCheckupPlanForm
    template_name = "backend/plan-form.html"
    success_url = reverse_lazy("health-plan-list")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.tests = form.cleaned_data.get("tests", [])
        self.object.save()
        msg.success(self.request, "Health plan created successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Health Plan"
        return context


class HealthCheckupPlanUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']

    model = HealthCheckupPlan
    form_class = HealthCheckupPlanForm
    template_name = "backend/plan-form.html"
    success_url = reverse_lazy("health-plan-list")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.tests = form.cleaned_data.get("tests", [])
        self.object.save()
        msg.success(self.request, "Health plan updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Health Plan"
        return context
    



@login_required(login_url='login')
@role_required(['admin', 'super-admin'])
def health_checkup_plan_delete(request, pk):
    plan = get_object_or_404(HealthCheckupPlan, pk=pk)
    plan.delete()
    msg.success(request, "Plan deleted successfully")
    return redirect("health-plan-list")





class HealthCheckupBookingListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    exclude_roles = ['doctor']   # 👈 THIS LINE

    model = HealthCheckupBooking
    template_name = "backend/booking-list.html"
    context_object_name = "bookings"
    ordering = ["-created_at"]



class BannerListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['super-admin']   # 👈 only super-admin

    model = Banner
    template_name = "backend/banners.html"
    context_object_name = "banners"
    ordering = ["-created_at"]


class BannerCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    allowed_roles = ['super-admin']   # 👈 only super-admin

    model = Banner
    form_class = BannerForm
    template_name = "backend/banner-form.html"
    success_url = reverse_lazy("banner-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Banner"
        return context


class BannerUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    allowed_roles = ['super-admin']   # 👈 only super-admin

    model = Banner
    form_class = BannerForm
    template_name = "backend/banner-form.html"
    success_url = reverse_lazy("banner-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Banner"
        return context
    


@login_required(login_url='login')
@role_required(['super-admin'])
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    msg.success(request, "Banner deleted successfully")
    return redirect("banner-list")

class MessageListView(LoginRequiredMixin, ListView):
    login_url = "login"
    model = Message
    template_name = "backend/messages.html"
    context_object_name = "contact_messages"
    ordering = ["-created_at"]


class MessageDetailView(LoginRequiredMixin, DetailView):
    login_url = "login"
    model = Message
    template_name = "backend/messages-detail.html"
    context_object_name = "message"
    slug_field = "slug"
    slug_url_kwarg = "slug"



class GalleryListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['super-admin']   # 👈 ONLY SUPER ADMIN

    model = Gallery
    template_name = "backend/gallery.html"
    context_object_name = "galleries"
    ordering = ["-created_at"]


class GalleryCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    allowed_roles = ['super-admin']

    model = Gallery
    form_class = GalleryForm
    template_name = "backend/gallery-form.html"
    success_url = reverse_lazy("gallery-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Gallery"
        return context


class GalleryUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    allowed_roles = ['super-admin']

    model = Gallery
    form_class = GalleryForm
    template_name = "backend/gallery-form.html"
    success_url = reverse_lazy("gallery-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Gallery"
        return context
    


@login_required(login_url='login')
@role_required(['super-admin'])
def gallery_delete(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    gallery.delete()
    msg.success(request, "Gallery deleted successfully")
    return redirect("gallery-list")  # ✅ FIXED




class CareerApplicationsByJobView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    allowed_roles = ['admin', 'super-admin']   # 👈 ACCESS CONTROL

    model = CareerApplication
    template_name = "backend/application.html"
    context_object_name = "applications"

    def get_queryset(self):
        self.career = Career.objects.get(id=self.kwargs["pk"])
        return CareerApplication.objects.filter(job=self.career).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["career"] = self.career
        return context
    
@role_required(['super-admin', 'admin', 'doctor', 'receptionist'])
@login_required(login_url='login')
def appointments(request):

    search_upcoming = request.GET.get('search_upcoming', '')
    search_completed = request.GET.get('search_completed', '')
    search_cancelled = request.GET.get('search_cancelled', '')
    now = timezone.now()
    active_tab = request.GET.get('tab', 'upcoming')

    completed_appointments = Appointment.objects.filter(status="COMPLETED").order_by('-date')
    cancelled_appointments = Appointment.objects.filter(status="CANCELLED").order_by('-date')

    past_appointments = []
    upcoming_appointments_list = []
    cancelled_appointments_list = []

    # ✅ Process completed appointments
    for appointment in completed_appointments:
        payment_details = RazorpayPaymentDetails.objects.filter(status='COMPLETED', appointment=appointment).first()
        content_type = appointment.content_type
        
        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except ObjectDoesNotExist:
            related_object = 'Timing deleted'
        
        # ✅ FINAL FIXED LOGIC
        if isinstance(related_object, AvailableTime):
            appointment_datetime = timezone.datetime.combine(
                appointment.date,
                related_object.start_time
            )

        elif isinstance(related_object, str) and related_object == 'Timing deleted':
            appointment_datetime = timezone.datetime.combine(
                appointment.date,
                timezone.datetime.min.time()
            )

        elif hasattr(related_object, 'start_time'):
            appointment_datetime = timezone.datetime.combine(
                appointment.date,
                related_object.start_time
            )

        else:
            # 👉 Doctor fallback (NO ERROR NOW)
            appointment_datetime = timezone.datetime.combine(
                appointment.date,
                timezone.datetime.min.time()
            )

        appointment_datetime = timezone.make_aware(
            appointment_datetime,
            timezone.get_current_timezone()
        )

        detailed_appointment = {
            'appointment': appointment,
            'payment_details': payment_details,
            'related_object': related_object
        }

        if appointment_datetime < now:
            past_appointments.append(detailed_appointment)
        else:
            upcoming_appointments_list.append(detailed_appointment)

    # ✅ Process cancelled appointments (SAFE)
    for appointment in cancelled_appointments:
        payment_details = RazorpayPaymentDetails.objects.filter(
            status='COMPLETED',
            appointment=appointment
        ).first()

        content_type = appointment.content_type

        try:
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)
        except:
            related_object = None

        detailed_appointment = {
            'appointment': appointment,
            'payment_details': payment_details,
            'related_object': related_object
        }

        cancelled_appointments_list.append(detailed_appointment)

    # Filters
    past_appointments = [
        appt for appt in past_appointments
        if search_completed.lower() in (
            appt['appointment'].patient.name.lower()
            or appt['appointment'].patient.phone_number
            or appt['appointment'].patient.email
            or appt['appointment'].selected_doctor.name.lower()
        )
    ]

    upcoming_appointments_list = [
        appt for appt in upcoming_appointments_list
        if search_upcoming.lower() in (
            appt['appointment'].patient.name.lower()
            or appt['appointment'].patient.phone_number
            or appt['appointment'].patient.email
            or appt['appointment'].selected_doctor.name.lower()
        )
    ]

    cancelled_appointments_list = [
        appt for appt in cancelled_appointments_list
        if search_cancelled.lower() in (
            appt['appointment'].patient.name.lower()
            or appt['appointment'].patient.phone_number
            or appt['appointment'].patient.email
            or appt['appointment'].selected_doctor.name.lower()
        )
    ]

    paginator_past = Paginator(past_appointments, 20)
    page_past_obj = paginator_past.get_page(request.GET.get('page_past'))

    paginator_upcoming = Paginator(upcoming_appointments_list, 20)
    page_upcoming_obj = paginator_upcoming.get_page(request.GET.get('page_upcoming'))

    paginator_cancelled = Paginator(cancelled_appointments_list, 20)
    page_cancelled_obj = paginator_cancelled.get_page(request.GET.get('page_cancelled'))

    context = {
        'past_appointments': page_past_obj,
        'upcoming_appointments': page_upcoming_obj,
        'cancelled_appointments': page_cancelled_obj,
        'search_upcoming': search_upcoming,
        'search_completed': search_completed,
        'search_cancelled': search_cancelled,
        'active_tab': active_tab
    }

    return render(request, 'backend/appointments.html', context)

@login_required(login_url='login')
def view_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    content_type = appointment.content_type

    try:
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)
    except ObjectDoesNotExist:
        related_object = 'Timing deleted'

    # ✅ FINAL SAFE TIMING LOGIC
    if isinstance(related_object, AvailableTime):
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            related_object.start_time
        )
        timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

    elif isinstance(related_object, str) and related_object == 'Timing deleted':
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            timezone.datetime.min.time()
        )
        timing_details = "Timing deleted"

    elif hasattr(related_object, 'start_time'):
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            related_object.start_time
        )
        timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

    else:
        # 👉 Doctor fallback (no time slot)
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            timezone.datetime.min.time()
        )
        timing_details = "Time not specified"

    appointment_datetime = timezone.make_aware(
        appointment_datetime,
        timezone.get_current_timezone()
    )

    payment_details = RazorpayPaymentDetails.objects.filter(
        status='COMPLETED',
        appointment=appointment
    ).first()

    formatted_date = DateFormat(appointment.date).format('d-m-Y')

    detailed_appointment = {
        'appointment': appointment,
        'related_object': related_object,
        'payment_details': payment_details,
        'appointment_datetime': appointment_datetime,
        'timing_details': timing_details,
        'formatted_date': formatted_date,
    }

    phone_number = appointment.patient.phone_number

    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number

    whatsapp_link = f"https://wa.me/{phone_number}"

    return render(
        request,
        'backend/appointment-view.html',
        {
            'detailed_appointment': detailed_appointment,
            'whatsapp_link': whatsapp_link
        }
    ) 
def collect_cash_appointment(request, pk):
    # Fetch the appointment by its primary key
    appointment = get_object_or_404(Appointment, id=pk)

    # Check if the appointment is already marked as COMPLETED
    if appointment.status == 'COMPLETED':
        try:
            order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
            # Fetch the associated payment details
            payment = RazorpayPaymentDetails.objects.get(appointment=appointment)
            payment.status = 'COMPLETED'
            payment.order_id = order_id
            payment.save()
            
            # Add a success message
            msg.success(request, "Payment marked as COMPLETED successfully.")
        except RazorpayPaymentDetails.DoesNotExist:
            # Handle case if payment details are missing
            msg.error(request, "Payment details not found for this appointment.")
    else:
        # Handle case where appointment is not completed
        msg.error(request, "Appointment status is not COMPLETED, so payment cannot be collected.")

    # Redirect to the same page (or wherever `request.META['HTTP_REFERER']` points to)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login')
def cancel_appointment(request, pk):
    
    
    try:
        appointment = Appointment.objects.get(id=pk)
        appointment.status = 'CANCELLED'
        appointment.save()
        msg.success(request, "Appointment Cancelled")
    except Appointment.DoesNotExist:
        msg.error(request, "Appointment does not exist.")

    # Redirect back to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    




@api_view(["GET"])
def get_doctors_by_department(request, department_id):
    doctors = Doctor.objects.filter(
        department_id=department_id,
        status=True
    ).order_by("priority")

    serializer = DoctorListSerializer(doctors, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(["GET"])
def get_doctor_timings(request, doctor_id, date):

    date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    monthly_ct = ContentType.objects.get_for_model(MonthlyTiming)
    weekly_ct = ContentType.objects.get_for_model(AvailableTime)

    # -------------------------------
    # MONTHLY TIMINGS
    # -------------------------------
    monthly = MonthlyTiming.objects.filter(
        doctor_id=doctor_id,
        date=date_obj,
        status="active"
    ).order_by("start_time")

    if monthly.exists():

        booked_ids = Appointment.objects.filter(
            selected_doctor_id=doctor_id,
            date=date_obj,
            status="COMPLETED",
            content_type=monthly_ct
        ).values_list("object_id", flat=True)

        result = monthly.exclude(id__in=booked_ids)

        serializer = MonthlyTimingSerializer(result, many=True)
        return Response(serializer.data)

    # -------------------------------
    # WEEKLY TIMINGS
    # -------------------------------
    day_name = date_obj.strftime("%A").lower()

    weekly = AvailableTime.objects.filter(
        doctor_id=doctor_id,
        day=day_name,
        status="active"
    ).order_by("start_time")

    booked_ids = Appointment.objects.filter(
        selected_doctor_id=doctor_id,
        date=date_obj,
        status="COMPLETED",
        content_type=weekly_ct
    ).values_list("object_id", flat=True)

    result = weekly.exclude(id__in=booked_ids)

    serializer = AvailableTimeSerializer(result, many=True)
    return Response(serializer.data)






# views.py
@api_view(["POST"])
def create_appointment_api(request):
    data = request.data

    # validation (keep your existing)

    patient, _ = Patient.objects.get_or_create(
        email=data["email"],
        defaults={
            "name": data["name"],
            "phone_number": data["phone_number"],
            "gender": data["gender"]
        }
    )

    try:
        schedule = AvailableTime.objects.get(id=data["time"])
    except:
        schedule = MonthlyTiming.objects.get(id=data["time"])

    appointment = Appointment.objects.create(
        patient=patient,
        department_id=data["department"],
        selected_doctor_id=data["doctor"],
        date=data["date"],
        payment_method="CASH",
        status="COMPLETED",
        content_type=ContentType.objects.get_for_model(schedule),
        object_id=schedule.id
    )

    schedule.remaining_slots -= 1
    schedule.save()


    Notification.objects.create(
        message=f"New appointment booked for {appointment.selected_doctor.name}",
        type="appointment",
        object_id=appointment.id,
        redirection_url=reverse("view_appointment", args=[appointment.id])
    )

    # ✅ IMPORTANT
    return Response({
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id
    }, status=201)




# views.py
def appointment_success(request, pk):
    appointment = Appointment.objects.select_related(
        "selected_doctor", "department", "patient"
    ).get(id=pk)

    content_type = appointment.content_type

    try:
        related_object = content_type.get_object_for_this_type(id=appointment.object_id)
    except ObjectDoesNotExist:
        related_object = 'Timing deleted'

    # ✅ FINAL SAFE TIMING LOGIC
    if isinstance(related_object, AvailableTime):
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            related_object.start_time
        )
        timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

    elif isinstance(related_object, str) and related_object == 'Timing deleted':
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            timezone.datetime.min.time()
        )
        timing_details = "Timing deleted"

    elif hasattr(related_object, 'start_time'):
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            related_object.start_time
        )
        timing_details = f"{related_object.start_time.strftime('%I:%M %p')} to {related_object.end_time.strftime('%I:%M %p')}"

    else:
        # 👉 Doctor fallback (no time slot)
        appointment_datetime = timezone.datetime.combine(
            appointment.date,
            timezone.datetime.min.time()
        )
        timing_details = "Time not specified"

    appointment_datetime = timezone.make_aware(
        appointment_datetime,
        timezone.get_current_timezone()
    )

    context = {
        "appointment": appointment,
        "timing_details": timing_details
    }

    return render(request, "frontend/appointment_success.html", context)
# Api Views  


class BlogListAPIView(generics.ListAPIView):
    """
    GET /api/blogs/
    GET /api/blogs/?homepage=true
    """
    permission_classes = [AllowAny]
    serializer_class = BlogListSerializer
    
    def get_queryset(self):
        queryset = Blog.objects.filter(status=True)\
                              .annotate(comment_count=Count('comments'))\
                              .order_by('-createdAt')
        
        # ?homepage=true → only show_on_homepage=True blogs
        if self.request.query_params.get('homepage', '').lower() in ('true', '1', 'yes'):
            queryset = queryset.filter(show_on_homepage=True)
            
        return queryset


class BlogDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Blog.objects.filter(status=True)\
                          .annotate(comment_count=Count('comments'))

# Bonus: if you want separate minimal endpoint just for homepage
class HomepageBlogsAPIView(generics.ListAPIView):
    """
    GET /api/blogs/homepage/
    Returns only blogs where show_on_homepage=True and status=True
    """
    permission_classes = [AllowAny]
    serializer_class = HomepageBlogSerializer
    
    def get_queryset(self):
        return Blog.objects.filter(
            status=True,
            show_on_homepage=True
        ).order_by('-createdAt')
    




class BlogCommentCreateAPIView(generics.CreateAPIView):
    """
    POST /api/blogs/<slug>/comment/
    """
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        blog_slug = self.kwargs.get('slug')
        blog = get_object_or_404(Blog, slug=blog_slug, status=True)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(blog=blog)

        return Response(
            {
                "message": "Comment posted successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    



    

class DepartmentListAPIView(generics.ListAPIView):
    """
    GET /api/departments/
    GET /api/departments/?homepage=true
    """
    permission_classes = [AllowAny]
    serializer_class = DepartmentListSerializer

    def get_queryset(self):
        queryset = Department.objects.filter(status=True).order_by("priority")

        if self.request.query_params.get("homepage", "").lower() in ("true", "1", "yes"):
            queryset = queryset.filter(show_on_homepage=True)

        return queryset


class DepartmentDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DepartmentDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Department.objects.filter(status=True)



class DoctorListAPIView(generics.ListAPIView):
    """
    GET /api/doctors/
    GET /api/doctors/?homepage=true
    """
    permission_classes = [AllowAny]
    serializer_class = DoctorListSerializer

    def get_queryset(self):
        queryset = Doctor.objects.filter(status=True).select_related("department").order_by("priority")

        if self.request.query_params.get("homepage", "").lower() in ("true", "1", "yes"):
            queryset = queryset.filter(show_on_homepage=True)

        return queryset


class DoctorDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/doctors/<slug>/
    """
    permission_classes = [AllowAny]
    serializer_class = DoctorDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Doctor.objects.filter(status=True).select_related("department")
    


class FAQListAPIView(generics.ListAPIView):
    """
    GET /api/faqs/
    Returns all FAQs ordered by priority
    """
    permission_classes = [AllowAny]
    serializer_class = FAQSerializer

    def get_queryset(self):
        return FAQ.objects.all().order_by("priority")
    


class TestimonialListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    login_url = "login"
    exclude_roles = ['receptionist']

    model = Testimonial
    template_name = "backend/testimonials.html"
    context_object_name = "testimonials"
    ordering = ["priority", "-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["video_testimonials"] = Testimonial.objects.filter(
            youtube_url__isnull=False
        ).exclude(youtube_url="").order_by("priority", "-created_at")

        context["normal_testimonials"] = Testimonial.objects.filter(
            youtube_url__isnull=True
        ).order_by("priority", "-created_at")

        return context

class TestimonialCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    login_url = "login"
    exclude_roles = ['receptionist']

    model = Testimonial
    form_class = TestimonialForm
    template_name = "backend/testimonial-form.html"
    success_url = reverse_lazy("testimonial-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Testimonial"
        return context


class TestimonialUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    login_url = "login"
    exclude_roles = ['receptionist']

    model = Testimonial
    form_class = TestimonialForm
    template_name = "backend/testimonial-form.html"
    success_url = reverse_lazy("testimonial-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Testimonial"
        return context


@login_required(login_url='login')
@role_required(['super-admin', 'admin', 'doctor'])  # 👈 exclude receptionist
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    msg.success(request, "Testimonial deleted successfully")
    return redirect("testimonial-list")





class TestimonialListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        normal = Testimonial.objects.filter(
            youtube_url__isnull=True
        ).order_by("priority")

        video = Testimonial.objects.filter(
            youtube_url__isnull=False
        ).exclude(youtube_url="").order_by("priority")

        normal_data = TestimonialTextSerializer(normal, many=True).data
        video_data = TestimonialVideoSerializer(video, many=True).data

        return Response({
            "normal_testimonials": normal_data,
            "video_testimonials": video_data
        })



class CreateAppointmentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        disease = request.data.get('disease') or ''
        date = request.data.get('date')
        message = request.data.get('message') or ''

        date = request.data.get('date')
        message = request.data.get('message')
        department_id = request.data.get('department')
        doctor_id = request.data.get('selected_doctor')
        payment_method = request.data.get('payment_method', 'online')  # Default to 'online' if not provided
        schedule_id = request.data.get('schedule_id')
        gender = request.data.get('gender')
        registration_fee_include = request.data.get('registration_fee')
        discount_percentage = float(request.data.get('discount', 0))  # Get discount percentage
        prescription = request.FILES.get('prescription')    
        registration_fee = 'paid'

        if registration_fee_include == 'on':
            registration_fee = 'unpaid'

        # Debug statements
        print(f"Name: {name}, Email: {email}, Phone: {phone_number}, Disease: {disease}, Gender: {gender}")
        print(f"Date: {date}, Message: {message}, Department: {department_id}")
        print(f"Doctor: {doctor_id}, Payment Method: {payment_method}, Schedule ID: {schedule_id}")
        print(f"Discount: {discount_percentage}%")

        # Check if all required fields are present
        if not all([name, email, phone_number, date, department_id, doctor_id, schedule_id, gender]):
            return Response({"error": "Missing one or more required fields."}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(Doctor, id=doctor_id)
        leave_exists = Leave.objects.filter(doctor=doctor, date=date).exists()
        if leave_exists:
            return Response({"error": "The selected doctor is on leave on the specified date."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get patient
        patient, created = Patient.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone_number': phone_number, 'disease': disease, 'gender': gender}
        )

        # Get department and doctor
        department = get_object_or_404(Department, id=department_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Determine if the schedule is monthly or weekly
        try:
            monthly_timing = MonthlyTiming.objects.get(uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(MonthlyTiming)
            object_id = monthly_timing.id
            start_time = monthly_timing.start_time
        except MonthlyTiming.DoesNotExist:
            available_time = get_object_or_404(AvailableTime, uuid=schedule_id)
            content_type = ContentType.objects.get_for_model(AvailableTime)
            object_id = available_time.id
            start_time = available_time.start_time

        # Combine date and start_time to form a datetime
        appointment_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        appointment_datetime = timezone.datetime.combine(appointment_date, start_time)
        appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

        if appointment_datetime <= timezone.now():
            return Response({"error": "The appointment datetime must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        # Create appointment
        if payment_method == 'pay_at_hospital':
            appointment = Appointment.objects.create(
                date=date,
                message=message,
                payment_id='',  # This will be filled after Razorpay payment if online
                payment_method=payment_method,
                patient=patient,
                department=department,
                selected_doctor=doctor,
                content_type=content_type,
                object_id=object_id,
                status='COMPLETED',
                is_pay_at_hospital = True,
                prescription=prescription,   # 👈 ADD THIS

                discount=discount_percentage  # Save discount percentage
            )
            Notification.objects.create(
                message=f"{appointment.patient.name} booked an appointment with {appointment.selected_doctor.name} for Pay at Hospital",
                read_status=False,
                redirection_url=reverse('view_appointment', args=[appointment.id]),
                object_id=appointment.id,
                type='appointment'
            )
        else:
            return JsonResponse({'error': 'Payment Gateway is not integrated'}, status=500)


        amount = int(doctor.fee) * 100  # amount in paise
        if registration_fee != 'paid':
            amount += 27000  # add registration fee in paise

        # Apply discount
        if discount_percentage > 0:
            discount_amount = (amount * discount_percentage) / 100
            amount -= int(discount_amount)


        if payment_method == 'online':
            return JsonResponse({'error': 'Payment Gateway is not integrated'}, status=500)

                
        if payment_method == 'pay_at_hospital':
            # Create RazorpayPaymentDetails with custom ID for cash payments
            RazorpayPaymentDetails.objects.create(
                payment_id=str(uuid.uuid4()),  # Generate a custom UUID
                order_id='',
                signature='',
                amount=amount,
                currency='INR',
                payment_method='cash',
                status='PENDING',  # Directly mark as completed for cash payments
                appointment=appointment
            )
            
            try:
                related_object = content_type.get_object_for_this_type(id=appointment.object_id)
            except ObjectDoesNotExist:
                related_object = 'Timing deleted'  # Set to 'Timing deleted' if object doesn't exist
            
            # Ensure `appointment.date` is a valid `datetime.date` object
            if isinstance(appointment.date, str):
                appointment_date = datetime.datetime.strptime(appointment.date, '%Y-%m-%d').date()
            else:
                appointment_date = appointment.date

            # Handle different cases for `related_object`
            if isinstance(related_object, AvailableTime):
                appointment_datetime = timezone.datetime.combine(appointment_date, related_object.start_time)
            elif isinstance(related_object, str) and related_object == 'Timing deleted':
                # Assign a default time for deleted timings
                appointment_datetime = timezone.datetime.combine(appointment_date, timezone.datetime.min.time())
            else:
                appointment_datetime = timezone.datetime.combine(related_object.date, related_object.start_time)

            # Make the datetime timezone-aware
            appointment_datetime = make_aware(appointment_datetime, get_current_timezone())

            # Return response for non-online payment method
            return Response({
                'appointment_id': appointment.id,
                'payment_method' : 'pay_at_hospital',
                'name': name,
                'appointment_datetime': appointment_datetime,
                'email': email,
                'phone_number': phone_number,
                'description': 'Appointment Booking'
            }, status=status.HTTP_201_CREATED)

        # Return response for non-online payment method
        return Response({
            'appointment_id': appointment.id,
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'description': 'Appointment Booking'
        }, status=status.HTTP_201_CREATED)







@api_view(['GET'])
def check_available_timings_api(request, doctor_id, date):

    try:
        # Parse the date
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Get the doctor
        doctor = get_object_or_404(Doctor, id=doctor_id)

        closed_dates = [
            # You can easily add more dates later
        ]

        if date_obj in closed_dates:
            return Response(
                {'error': 'The hospital will not be open on the selected date.'},
                status=400
            )

        # Check if the doctor is on leave on the specified date
        if Leave.objects.filter(doctor=doctor, date=date_obj).exists():
            return Response({'error': 'Doctor is on leave on this day.'}, status=400)

        # Check for monthly timings with remaining slots
        monthly_timings = MonthlyTiming.objects.filter(
            doctor=doctor, 
            status='active', 
            date=date_obj, 
            remaining_slots__gte=1
        ).order_by('start_time')
        monthly_serializer = MonthlyTimingSerializer(monthly_timings, many=True)

        # Check for available times based on the day of the week
        day_of_week = date_obj.strftime('%A').lower()
        available_times = AvailableTime.objects.filter(
            doctor=doctor, 
            status='active', 
            day=day_of_week
        )

        # Filter available times based on remaining slots
        valid_available_times = []
        for available_time in available_times:
            appointments_on_same_day = Appointment.objects.filter(
                date=date_obj,
                selected_doctor=doctor,
                status='COMPLETED',
                content_type=ContentType.objects.get_for_model(AvailableTime),
                object_id=available_time.id
            ).count()
            remaining_slots = available_time.slot - appointments_on_same_day
            if remaining_slots >= 1:
                valid_available_times.append(available_time)

        # Sort the valid available times by start time before serialization
        valid_available_times.sort(key=lambda x: x.start_time)
        available_times_serializer = AvailableTimeSerializer(valid_available_times, many=True)

        # Combine both sets of timings
        combined_timings = {
            'monthly_timings': monthly_serializer.data,
            'weekly_timings': available_times_serializer.data
        }

        # Return the combined timings response
        return Response(combined_timings, status=200)

    except Exception as e:
        return Response({'error': 'An error occurred while checking available timings.'}, status=500)





class HealthCheckupPlanListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = HealthCheckupPlanSerializer

    def get_queryset(self):
        return HealthCheckupPlan.objects.filter(status=True).order_by("priority")


class HealthCheckupPlanDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = HealthCheckupPlanSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return HealthCheckupPlan.objects.filter(status=True)




class HealthCheckupBookingCreateAPIView(APIView):
    """
    POST /api/health-checkups/book/
    Create a health checkup booking
    """

    def post(self, request, *args, **kwargs):
        print("Coming Here")
        name = request.data.get("name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        plan_id = request.data.get("plan_id")
        message = request.data.get("message", "")

        print(name, email, phone_number, plan_id)

        # Validate required fields
        if not all([name, email, phone_number, plan_id]):
            print("Error")
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get plan
        plan = get_object_or_404(HealthCheckupPlan, id=plan_id, status=True)

        print(plan)

        # Create or get patient
        patient, _ = Patient.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                
            }
        )

        print(patient)
        # Create booking
        booking = HealthCheckupBooking.objects.create(
            plan=plan,
            patient=patient,
            message=message,
            status="COMPLETED"
        )

        # ✅ Create Notification
        Notification.objects.create(
            message=f"{booking.patient.name} booked {booking.plan.title} health checkup",
            read_status=False,
            redirection_url=reverse("health-checkup-booking-list"),
            object_id=booking.id,
            type="health_checkup"
        )

        print(booking)
        serializer = HealthCheckupBookingCreateSerializer(booking)

        return Response({
            "message": "Health checkup booked successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)





class BannerListAPIView(generics.ListAPIView):
    """
    GET /api/banners/
    Returns all active banners
    """
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer

    def get_queryset(self):
        return Banner.objects.filter(status=True).order_by("-created_at")



class BannerDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/banners/<id>/
    """
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Banner.objects.filter(status=True)
    





class MessageCreateAPIView(generics.CreateAPIView):
    """
    POST /api/messages/
    Create a new message
    """
    permission_classes = [AllowAny]
    serializer_class = MessageCreateSerializer
    queryset = Message.objects.all()

    def perform_create(self, serializer):
        message_obj = serializer.save()

        # ✅ Create notification
        Notification.objects.create(
            message=f"New message received from {message_obj.name}",
            read_status=False,
            redirection_url=reverse("message-detail", args=[message_obj.slug]),
            object_id=message_obj.id,
            type="message"
        )




class GalleryListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        images = Gallery.objects.filter(image__isnull=False).exclude(image="")
        videos = Gallery.objects.filter(youtube_url__isnull=False).exclude(youtube_url="")

        image_data = GalleryImageSerializer(images, many=True).data
        video_data = GalleryVideoSerializer(videos, many=True).data

        return Response({
            "images": image_data,
            "videos": video_data
        })

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "title", "image", "created_at"]


class GalleryVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "title", "youtube_url", "created_at"]


class CareerListAPIView(generics.ListAPIView):
    """
    GET /api/careers/
    Returns all active careers
    """
    permission_classes = [AllowAny]
    serializer_class = CareerSerializer

    def get_queryset(self):
        return Career.objects.filter(status=True).order_by("-created_at")


class CareerDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/careers/<slug>/
    """
    permission_classes = [AllowAny]
    serializer_class = CareerSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Career.objects.filter(status=True)
    


class CareerApplyAPIView(APIView):
    """
    POST /api/careers/apply/
    Apply for a job
    """

    def post(self, request, *args, **kwargs):
        name = request.data.get("name")
        number = request.data.get("number")
        email = request.data.get("email")
        job_id = request.data.get("job")
        cover_letter = request.data.get("cover_letter", "")
        cv = request.FILES.get("cv")

        # Validate required fields
        if not all([name, number, email, job_id, cv]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        job = get_object_or_404(Career, id=job_id, status=True)

        application = CareerApplication.objects.create(
            name=name,
            number=number,
            email=email,
            cover_letter=cover_letter,
            cv=cv,
            job=job
        )

        # ✅ Create notification
        Notification.objects.create(
            message=f"New job application for {job.job_title} from {application.name}",
            read_status=False,
            redirection_url=reverse("career-applications", args=[job.id]),
            object_id=application.id,
            type="career_application"
        )

        serializer = CareerApplicationCreateSerializer(application)

        return Response(
            {
                "message": "Application submitted successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    




@api_view(['GET'])
def appointment_detail_api(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    content_type = appointment.content_type

    try:
        related_object = content_type.get_object_for_this_type(
            id=appointment.object_id
        )
    except Exception:
        related_object = None

    # 🔹 Ensure date is date object
    if isinstance(appointment.date, str):
        appointment_date = datetime.datetime.strptime(
            appointment.date, "%Y-%m-%d"
        ).date()
    else:
        appointment_date = appointment.date

    # 🔹 Build datetime
    if related_object and hasattr(related_object, "start_time"):
        appointment_datetime = datetime.datetime.combine(
            appointment_date, related_object.start_time
        )
    else:
        appointment_datetime = datetime.datetime.combine(
            appointment_date, datetime.time.min
        )

    appointment_datetime = make_aware(
        appointment_datetime, get_current_timezone()
    )

    # 🔹 Format time to AM/PM
    formatted_time = appointment_datetime.strftime("%I:%M %p")
    formatted_date = appointment_datetime.strftime("%d %b %Y")

    return Response({
        "id": appointment.id,
        "patient_name": appointment.patient.name,
        "doctor_name": appointment.selected_doctor.name,
        "appointment_date": formatted_date,
        "appointment_time": formatted_time,
        "appointment_datetime": appointment_datetime,
        "payment_method": appointment.payment_method,
    })






@api_view(['GET'])
def view_user_appointment_api(request):
    email = request.GET.get('email')
    appointments_data = []

    if email:
        current_time = timezone.now()

        all_appointments = Appointment.objects.filter(
            patient__email=email,
            status='COMPLETED',
        ).order_by('-date')

        for appointment in all_appointments:
            content_type = appointment.content_type
            related_object = content_type.get_object_for_this_type(id=appointment.object_id)

            payment = RazorpayPaymentDetails.objects.filter(
                status='COMPLETED',
                appointment=appointment
            ).first()

            if related_object:
                start_time = related_object.start_time.strftime('%I:%M %p')
                end_time = related_object.end_time.strftime('%I:%M %p')
            else:
                start_time = None
                end_time = None

            payment_status = None
            payment_method = None
            order_id = None

            if payment and payment.status == "COMPLETED":
                payment_status = "Paid"
                payment_method = payment.payment_method
                order_id = payment.order_id

            appointments_data.append({
                "appointment_id": appointment.id,
                "patient_name": appointment.patient.name,
                "patient_email": appointment.patient.email,
                "doctor_name": appointment.selected_doctor.name if appointment.selected_doctor else None,
                "department": appointment.department.title if appointment.department else None,
                "appointment_date": appointment.date,
                "start_time": start_time,
                "end_time": end_time,
                "payment_status": payment_status,
                "payment_method": payment_method,
                "order_id": order_id,
                "status": appointment.status
            })

    return Response({
        "email": email,
        "appointments": appointments_data
    })

def home(request):
    banners = Banner.objects.filter(
        status=True
    ).order_by('-created_at')

    # ✅ ALL ACTIVE TIME SLOTS
    time_slots = AvailableTime.objects.filter(
        status='active'
    ).order_by('day', 'start_time')

    homepage_doctors = Doctor.objects.filter(
        status=True,
        show_on_homepage=True
    ).order_by('priority')[:10]

    all_doctors = Doctor.objects.filter(
        status=True
    ).order_by('priority')

    testimonials = Testimonial.objects.all().order_by(
        'priority',
        '-created_at'
    )

    blogs = Blog.objects.filter(
        status=True,
        show_on_homepage=True
    ).order_by('-createdAt')[:3]

    departments = Department.objects.filter(
        status=True,
        show_on_homepage=True
    ).order_by('priority')

    return render(request, 'frontend/index.html', {
        'banners': banners,
        'doctors': homepage_doctors,
        'all_doctors': all_doctors,
        'testimonials': testimonials,
        'blogs': blogs,
        'departments': departments,
        'time_slots': time_slots,
        'today': now().date()
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=True)

    # TAGS
    tags = []
    if blog.tags:
        tags = [tag.strip() for tag in blog.tags.split(',')]

    # RECENT BLOGS
    recent_blogs = Blog.objects.filter(status=True)\
        .exclude(id=blog.id)\
        .order_by('-createdAt')[:5]

    # GALLERY
    gallery_items = Gallery.objects.all().order_by('-created_at')[:6]

    # COMMENTS
    comments = blog.comments.all().order_by('-created_at')

    # ✅ ADD DEPARTMENTS (same as doctor page)
    departments = Department.objects.filter(status=True).order_by('priority')

    # COMMENT FORM
    if request.method == "POST":
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.save()
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = BlogCommentForm()

    return render(request, 'frontend/blog-details.html', {
        'blog': blog,
        'tags': tags,
        'recent_blogs': recent_blogs,
        'gallery_items': gallery_items,
        'comments': comments,
        'form': form,
        'departments': departments,  # ✅ added
    })

def about(request):

    doctors = Doctor.objects.filter(
        status=True,
        show_on_homepage=True
    ).order_by('priority')[:10]

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/about.html', {
        'doctors': doctors,
        'departments': departments
    })

def doctors_frontend(request):

    doctors = Doctor.objects.filter(
        status=True
    ).order_by('priority')

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/doctors.html', {
        'doctors': doctors,
        'departments': departments
    })


def doctor_detail(request, slug):

    doctor = get_object_or_404(
        Doctor,
        slug=slug,
        status=True
    )

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/doctor-details.html', {
        'doctor': doctor,
        'departments': departments
    })


def services(request):
    departments = Department.objects.filter(status=True).order_by('priority')
    return render(request, 'frontend/services.html',{
        'departments': departments
    })

def department_detail(request, slug):
    department = get_object_or_404(
        Department,
        slug=slug,
        status=True
    )

    doctors = Doctor.objects.filter(
        department=department,
        status=True
    )

    sub_departments = department.sub_departments.filter(
        status=True
    ).order_by('priority', 'title')

    return render(request, 'frontend/services-details.html', {
        'department': department,
        'doctors': doctors,
        'departments': Department.objects.filter(status=True),
        'sub_departments': sub_departments,
    }) 


def sub_department_detail(request, department_slug, sub_slug):

    department = get_object_or_404(
        Department,
        slug=department_slug,
        status=True
    )

    sub_department = get_object_or_404(
        SubDepartment,
        department=department,
        slug=sub_slug,
        status=True
    )

    doctors = Doctor.objects.filter(
        department=department,
        status=True
    )

    departments = Department.objects.filter(
        status=True
    )

    sub_departments = SubDepartment.objects.filter(
        department=department,
        status=True
    )

    return render(
        request,
        'frontend/sub-department-details.html',
        {
            'department': department,
            'sub_department': sub_department,
            'doctors': doctors,
            'departments': departments,
            'sub_departments': sub_departments,
        }
    )

def contact(request):

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/contact.html', {
        'departments': departments
    })


def create_message(request):
    print("HIT")
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        content = request.POST.get("content")

        Message.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            content=content
        )

        messages.success(request, "Message sent successfully!")
        return redirect('/contact/')  # 👈 better than homepage

    return redirect('/contact/')
def gallery(request):

    gallery_items = Gallery.objects.all().order_by('-created_at')

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/gallery.html', {
        'gallery_items': gallery_items,
        'departments': departments
    })


def frontned_blogs(request):

    blogs = Blog.objects.filter(
        status=True
    ).order_by('-createdAt')

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/blogs.html', {
        'blogs': blogs,
        'departments': departments
    })


def health_checkups(request):

    plans = HealthCheckupPlan.objects.filter(
        status=True
    ).order_by('priority', '-created_at')

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/health_checkups.html', {
        'plans': plans,
        'departments': departments,
        'today': date.today()
    })

def create_health_booking(request):
    if request.method == "POST":

        # Prevent past date booking
        booking_date = request.POST.get("date")

        if booking_date:
            from datetime import date

            selected_date = date.fromisoformat(booking_date)

            if selected_date < date.today():
                messages.error(request, "Past dates are not allowed")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone_number")
        plan_id = request.POST.get("plan_id")
        message = request.POST.get("message")

        # Validation
        if not all([first_name, phone, plan_id]):
            messages.error(request, "Please fill all required fields")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Get plan
        plan = get_object_or_404(HealthCheckupPlan, id=plan_id)

        # Create / get patient
        patient, created = Patient.objects.get_or_create(
            phone_number=phone,
            defaults={
                "name": f"{first_name} {last_name}".strip(),
                "email": f"{phone}@auto.com"
            }
        )

        if not created:
            patient.name = f"{first_name} {last_name}".strip()
            patient.save()

        # Create booking
        booking = HealthCheckupBooking.objects.create(
            plan=plan,
            patient=patient,
            message=message,
            status="PENDING"
        )

        # Notification
        Notification.objects.create(
            message=f"{patient.name} booked {plan.title}",
            redirection_url="/backend/health-bookings/",
            object_id=booking.id,
            type="health_checkup"
        )

        # Success
        messages.success(request, "Health checkup booked successfully!")

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('/')

def careers(request):

    careers = Career.objects.filter(
        status=True
    ).order_by('-created_at')

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/careers.html', {
        'careers': careers,
        'departments': departments
    })

def career_detail(request, slug):
    job = get_object_or_404(Career, slug=slug)
    return render(request, 'frontend/career_detail.html', {'job': job})


def apply_job(request):
    if request.method != "POST":
        return HttpResponse("Invalid request")

    job_id = request.POST.get("job")
    print("JOB ID:", job_id)  # DEBUG

    # Validate job id
    if not job_id or not job_id.isdigit():
        return HttpResponse("Invalid Job ID")

    # Safe fetch (NO DoesNotExist now)
    job = get_object_or_404(Career, id=int(job_id))

    # Get form data
    name = request.POST.get("name")
    phone = request.POST.get("number")
    email = request.POST.get("email")
    experience = request.POST.get("experience")
    cover_letter = request.POST.get("cover_letter")
    cv = request.FILES.get("cv")

    # Basic validation
    if not name or not phone or not email:
        return HttpResponse("Please fill required fields")

    # Save
    JobApplication.objects.create(
        job=job,
        name=name,
        phone=phone,
        email=email,
        experience=experience,
        cover_letter=cover_letter,
        resume=cv
    )

    return redirect("/careers/?applied=success")





def insurance_schemes(request):

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/insurance_schemes.html', {
        'departments': departments
    })




def apply_job(request):
    if request.method == "POST":
        name = request.POST.get("name")
        number = request.POST.get("number")
        email = request.POST.get("email")
        cover_letter = request.POST.get("cover_letter")
        job_id = request.POST.get("job")
        cv = request.FILES.get("cv")

        job = get_object_or_404(Career, id=job_id)

        CareerApplication.objects.create(
            name=name,
            number=number,
            email=email,
            cover_letter=cover_letter,
            job=job,
            cv=cv
        )

        return redirect('/careers/')

    return redirect('/careers/')

def privacy_policy(request):

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/privacy-policy.html', {
        'departments': departments
    })


def terms_conditions(request):

    departments = Department.objects.filter(
        status=True
    ).order_by('priority')

    return render(request, 'frontend/terms-conditions.html', {
        'departments': departments
    })
    

def sub_departments(request):
    sub_departments = SubDepartment.objects.all().order_by('priority', '-created_at')

    return render(request, 'backend/sub-departments.html', {
    'sub_departments': sub_departments
})


def create_sub_department(request):

    if request.method == "POST":

        form = SubDepartmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            msg.success(
                request,
                "Sub Department created successfully"
            )

            return redirect("sub_departments")

    else:

        form = SubDepartmentForm()

    return render(
        request,
        "backend/create-sub-department.html",
        {
            "form": form
        }
    )

@role_required(['super-admin', 'admin'])
@login_required(login_url='login')
def edit_sub_department(request, slug):

    sub_department = get_object_or_404(
        SubDepartment,
        slug=slug
    )

    if request.method == 'POST':

        form = SubDepartmentForm(
            request.POST,
            request.FILES,
            instance=sub_department
        )

        if form.is_valid():

            form.save()

            msg.success(
                request,
                "Sub Department updated successfully"
            )

            return redirect('sub_departments')

    else:

        form = SubDepartmentForm(
            instance=sub_department
        )

    return render(
        request,
        'backend/edit-sub-department.html',
        {
            'form': form,
            'is_edit': True,
        }
    )

def delete_sub_department(request, slug):
    sub_department = get_object_or_404(
        SubDepartment,
        slug=slug
    )

    sub_department.delete()

    messages.success(
        request,
        "Sub Department deleted successfully."
    )

    return redirect("sub_departments")