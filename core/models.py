from django.db import models
from ckeditor.fields import RichTextField
import uuid
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.




class Summary(models.Model):
    ROLE_CHOICES = [
        ('receptionist', 'receptionist'),
        ('doctor', 'doctor'),
        ('super-admin', 'super-admin'),
        ('admin', 'admin')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} Profile'
    


  


class Department(models.Model):

    title = models.CharField(max_length=200)
    banner = models.FileField(upload_to='departments', null=True, blank=True)
    breadcamp = models.FileField(upload_to='dep-banner', default='static/images/default.png')
    priority = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    icon = models.FileField(upload_to='dep-icons', default='static/images/default.png')  # Default icon path
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    show_on_homepage = models.BooleanField(default=False)  # Control homepage display

    meta_title = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
        
        



class Doctor(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    education = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='doctors')
    slug = models.SlugField(unique=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = RichTextField()
    show_on_homepage = models.BooleanField(default=False) 

    meta_title = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name





class AvailableTime(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_times')
    day = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField()
    slot = models.PositiveIntegerField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, default='active')
    remaining_slots = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f'{self.doctor.name} - {self.day} {self.start_time} to {self.end_time}'

class MonthlyTiming(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()    
    status = models.CharField(max_length=10, default='active')
    end_time = models.TimeField()
    slot = models.PositiveIntegerField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_monthly_times')
    remaining_slots = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.slot})"








class Leave(models.Model):
    date = models.DateField(default=timezone.now)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='leave_date')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    def __str__(self):
        return f"{self.doctor} - {self.date}"









class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    disease = models.CharField(max_length=255, null=True, blank=True, default='')
    slug = models.SlugField(unique=True, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')  # Add gender field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Patient.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Appointment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    message = models.TextField(null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    selected_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # New field
    is_app = models.BooleanField(default=False, blank=True, null=True)
    is_video = models.BooleanField(default=False)
    user_id = models.CharField(max_length=250,  blank=True, null=True)
    video_link = models.URLField(null=True, blank=True)
    video_link_expires_at = models.DateTimeField(null=True, blank=True)
    is_video_active = models.BooleanField(default=False)
    is_pay_at_hospital = models.BooleanField(default=False)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    schedule = GenericForeignKey('content_type', 'object_id')
    prescription = models.FileField(
        upload_to='prescriptions/',
        null=True,
        blank=True
    )

        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.patient.name}-{self.date}')
            original_slug = self.slug
            counter = 1
            while Appointment.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        return f'Appointment with {self.selected_doctor} on {self.date} at {self.schedule}'



    
    
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read_status = models.BooleanField(default=False)
    redirection_url = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, default='appointment')
    object_id = models.PositiveIntegerField(default=1)
    is_alarmed = models.BooleanField(default=False)  # New field
    first_read_by = models.ForeignKey(User, related_name='first_read_notifications', null=True, blank=True, on_delete=models.SET_NULL)  # New field


    def __str__(self):
        return self.message





class HealthCheckupPlan(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    priority = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        default=10
    )

    slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)

    total_test_include = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(
        upload_to='health_checkup_plans/',
        blank=True,
        null=True
    )

    # ✅ New field to store multiple tests
    tests = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tests included in this plan"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while HealthCheckupPlan.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class HealthCheckupBooking(models.Model):
    plan = models.ForeignKey(HealthCheckupPlan, on_delete=models.CASCADE, related_name='bookings')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_checkup_bookings')
    payment_id = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.patient.name} - {self.plan.title}"




class RazorpayPaymentDetails(models.Model):

    PAYMENT_FOR = (
        ('APPOINTMENT', 'APPOINTMENT'),
        ('CHECKUP', 'CHECKUP'),
        ('OFFER', 'OFFER'),
    )

    payment_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()  # Amount in paise
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='razorpay_payment_details', null=True, blank=True)
    payment_for = models.CharField(max_length=12, choices=PAYMENT_FOR, default='APPOINTMENT')
    booking = models.OneToOneField(HealthCheckupBooking, on_delete=models.CASCADE, related_name='razorpay_payment_details', null=True, blank=True)

    

    def __str__(self):
        return f'Payment {self.payment_id} for Appointment {self.payment_for}'
    
    
    





class Blog(models.Model):
    image = models.ImageField(upload_to='blog_images/')
    category = models.CharField(max_length=50)
    createdAt = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=50)
    author_designation = models.CharField(max_length=50)
    content = RichTextField()
    status = models.BooleanField(default=True)
    tags = models.CharField(max_length=50, blank=True)  # Field to store tags
    slug = models.SlugField(unique=True, blank=True)
    heading = models.TextField()
    show_on_homepage = models.BooleanField(default=False)  # New field to control homepage display

    meta_title = models.TextField(null=True, blank=True)
    meta_keyword = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.heading)
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)


    def __str__(self):
        return self.heading





class BlogComment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while BlogComment.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.heading}"






class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    priority = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
class Testimonial(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        blank=True,
        null=True
    )

    youtube_url = models.URLField(blank=True, null=True)  # 👈 NEW

    priority = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.youtube_url:
            return "Video Testimonial"
        return f"{self.name} ({self.rating}⭐)"

    def get_youtube_embed(self):
        if not self.youtube_url:
            return ""

        url = self.youtube_url.strip()

        if "watch?v=" in url:
            return url.replace("watch?v=", "embed/")

        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        elif "shorts/" in url:
            video_id = url.split("shorts/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        return ""
    

    def get_youtube_id(self):
        if not self.youtube_url:
            return ""

        url = self.youtube_url

        if "watch?v=" in url:
            return url.split("watch?v=")[-1]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[-1]
        elif "shorts/" in url:
            return url.split("shorts/")[-1].split("?")[0]

        return ""

class Banner(models.Model):
    heading = models.CharField(max_length=255, default='',  null=True, blank=True)
    description = models.TextField( null=True, blank=True, default='')
    button_text = models.CharField(max_length=100,  null=True, blank=True, default='')
    button_url = models.URLField(default='https://google.com',  null=True, blank=True)
    button_two_text = models.CharField(max_length=100,  null=True, blank=True, default='')
    button_two_url = models.URLField(default='https://google.com',  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_for_desktop = models.ImageField(upload_to='banners/desktop/')
    image_for_mobile = models.ImageField(upload_to='banners/mobile/')
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.heading





class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Message.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)



    def __str__(self):
        return self.name
    
    


class Gallery(models.Model):
    title = models.CharField(max_length=255, default='')
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)  # 👈 NEW
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_youtube_embed(self):
        if self.youtube_url:
            if "watch?v=" in self.youtube_url:
                return self.youtube_url.replace("watch?v=", "embed/")
            elif "youtu.be/" in self.youtube_url:
                return self.youtube_url.replace("youtu.be/", "www.youtube.com/embed/")
            elif "youtube.com/shorts/" in self.youtube_url:
                video_id = self.youtube_url.split("shorts/")[-1].split("?")[0]
                return f"https://www.youtube.com/embed/{video_id}"
        return ""
    
    def get_youtube_id(self):
        if self.youtube_url:
            if "watch?v=" in self.youtube_url:
                return self.youtube_url.split("watch?v=")[-1]
            elif "youtu.be/" in self.youtube_url:
                return self.youtube_url.split("youtu.be/")[-1]
            elif "shorts/" in self.youtube_url:
                return self.youtube_url.split("shorts/")[-1].split("?")[0]
        return ""
class Career(models.Model):

    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200, null=True, blank=True)
    experience = models.PositiveIntegerField(help_text="Years of experience required", null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    responsibilities = RichTextField(null=True, blank=True)
    skills = RichTextField(null=True, blank=True)
    job_summary = RichTextField(null=True, blank=True)
    qualifications = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.job_title)
            original_slug = self.slug
            counter = 1
            while Career.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)



    def __str__(self):
        return self.job_title






class CareerApplication(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    email = models.EmailField()
    cover_letter = models.TextField(blank=True, null=True)
    cv = models.FileField(upload_to='cvs/')
    created_at = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='career_application')
    slug = models.SlugField(unique=True, blank=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while CareerApplication.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)


