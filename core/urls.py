from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),

    path('doctors/', doctors_frontend, name='frontend_doctors'),
    path('doctor/<slug:slug>/', doctor_detail, name='doctor_detail'),

    path('departments/', services, name='services'),

    # Main Department
    path(
        'departments/<slug:slug>/',
        department_detail,
        name='department_detail'
    ),

    path(
    'departments/<slug:department_slug>/<slug:sub_slug>/',
    sub_department_detail,
    name='sub_department_detail'
),
    path('contact/', contact, name='contact'),
    path('contact/create/', create_message, name='create_message'),

    path('gallery/', gallery, name='gallery'),

    path('blogs/', frontned_blogs, name='frontned_blogs'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),

    path('health-checkups/', health_checkups, name='health_checkups'),
    path('health-booking/', create_health_booking, name='create_health_booking'),

    path('careers/apply/', apply_job, name='apply_job'),
    path('careers/', careers, name='careers'),
    path('careers/<slug:slug>/', career_detail, name='career_detail'),

   
    
    path('insurance-schemes', insurance_schemes, name='insurance_schemes'),
    
    
    
    
    path('careers/apply/', apply_job, name='apply_job'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-conditions', terms_conditions, name='terms-conditions'),
    # path('appointment/create/', create_appointment, name='create_appointment'),
    

    # API endpoints
    path("api/doctors/<int:department_id>/", get_doctors_by_department),
    path("api/timings/<int:doctor_id>/<str:date>/", get_doctor_timings),
    path("api/book-appointment/", create_appointment_api),
    path('api/check-timings/<int:doctor_id>/<str:date>/', check_available_timings_api, name='check-available-timings'),
    # urls.py
    path("appointment/success/<int:pk>/", appointment_success, name="appointment_success"),


    # urls.py
    path('no-permission/', no_permission, name='no_permission'),
    path('account/login/', login, name='login'), 
    path('account/logout/', logout_user, name='logout_user'), 

    path('account/', dashboard, name='dashboard'), 
    path('account/departments/', departments, name='departments'), 
    # Sub Departments
path(
    'account/sub-departments/',
    sub_departments,
    name='sub_departments'
),

path(
    'account/sub-departments/create/',
    create_sub_department,
    name='create_sub_department'
),

path(
    'account/sub-departments/edit/<slug:slug>/',
    edit_sub_department,
    name='edit_sub_department'
),

path(
    'account/sub-departments/delete/<slug:slug>/',
    delete_sub_department,
    name='delete_sub_department'
),
    path('account/users/', user_list, name='user-list'),
    path('account/users/create/', user_create, name='user-create'),
    path('account/users/edit/<int:id>/', user_edit, name='user-edit'),
    path('account/users/delete/<int:id>/', user_delete, name='user-delete'),

    path('account/appointments/', appointments, name='appointments'), 


    path('account/doctors/', doctors, name='doctors'), 
    path('account/doctors/create/', create_doctor, name='create_doctor'), 
    path('account/doctors/update/<slug:slug>/', update_doctor, name='update_doctor'), 
    path('account/doctors/delete/<slug:slug>/', delete_doctor, name='delete_doctor'), 

    path('account/doctors/<int:doctor_id>/appointments/', doctor_appointments, name='doctor_appointments'),

    path("account/gallery/", GalleryListView.as_view(), name="gallery-list"),
    path("account/gallery/create/", GalleryCreateView.as_view(), name="gallery-create"),
    path("account/gallery/<int:pk>/edit/", GalleryUpdateView.as_view(), name="gallery-edit"),
    path("account/gallery/<int:pk>/delete/", gallery_delete, name="gallery-delete"),

    path('account/timing/<slug:slug>/', create_timing, name='create_timing'), 
    path('account/timing/delete/<str:pk>/', delete_timing, name='delete_timing'), 
    path('account/timing/delete/monthly/<str:pk>/', delete_timing_monthly, name='delete_timing_monthly'), 
    path('account/timing/monthly/create/<str:pk>/', create_monthly_timing, name='create_monthly_timing'), 
    path('account/leave/<slug:slug>/', create_leave, name='create_leave'), 
    path('account/leave/delete/<str:pk>/', delete_leave, name='delete_leave'), 
    path('api/create-timing/<slug:doctor_slug>/', create_timing_api, name='create_timing_api'),

    path("account/banners/", BannerListView.as_view(), name="banner-list"),
    path("account/banners/create/", BannerCreateView.as_view(), name="banner-create"),
    path("account/banners/<int:pk>/edit/", BannerUpdateView.as_view(), name="banner-edit"),
    path("account/banners/<int:pk>/delete/", banner_delete, name="banner-delete"),


    path('account/blogs/', blogs, name='blogs'),
    path('account/blogs/create/', create_blog, name='create_blog'),
    path('account/blogs/update/<slug:slug>/', update_blog, name='update_blog'),
    path('account/blogs/delete/<slug:slug>/', delete_blog, name='delete_blog'),
    path('account/blogs/<slug:slug>/', view_blog_comments, name='view_blog_comments'),
    path('account/blogs/<slug:blogSlug>/comments/<slug:commentSlug>/', view_blog_comment, name='view_blog_comment'),
    path('blog/<slug:blogSlug>/comment/delete/<slug:commentSlug>/', delete_blog_comment, name='delete-blog-comment'),



    path("account/faq/", FAQListView.as_view(), name="faq-list"),
    path("account/faq/create/", FAQCreateView.as_view(), name="faq-create"),
    path("account/faq/<int:pk>/edit/", FAQUpdateView.as_view(), name="faq-edit"),
    path("faq/<int:pk>/delete/", faq_delete, name="faq-delete"),

    path('account/departements/create', create_department, name='create_department'), 
    path("department/edit/<slug:slug>/", edit_department, name="edit_department"),
    path("department/delete/<slug:slug>/", delete_department, name="delete_department"),

    path("account/careers/", CareerListView.as_view(), name="career-list"),
    path("account/careers/create/", CareerCreateView.as_view(), name="career-create"),
    path("account/careers/<int:pk>/edit/", CareerUpdateView.as_view(), name="career-edit"),
    path("account/careers/<int:pk>/delete/", career_delete, name="career-delete"),
    path("account/careers/<int:pk>/applications/", CareerApplicationsByJobView.as_view(), name="career-applications"),


    path("account/health-plans/", HealthCheckupPlanListView.as_view(), name="health-plan-list"),
    path("account/health-plans/create/", HealthCheckupPlanCreateView.as_view(), name="health-plan-create"),
    path("account/health-plans/<int:pk>/edit/", HealthCheckupPlanUpdateView.as_view(), name="health-plan-edit"),
    path("account/health-plans/<int:pk>/delete/", health_checkup_plan_delete, name="health-plan-delete"),

    path("account/health-checkup-bookings/", HealthCheckupBookingListView.as_view(), name="health-checkup-booking-list"),

    path("account/messages/", MessageListView.as_view(), name="message-list"),
    path("account/messages/<slug:slug>/", MessageDetailView.as_view(), name="message-detail"),

    path("account/testimonials/", TestimonialListView.as_view(), name="testimonial-list"),
    path("account/testimonials/create/", TestimonialCreateView.as_view(), name="testimonial-create"),
    path("account/testimonials/<int:pk>/edit/", TestimonialUpdateView.as_view(), name="testimonial-edit"),
    path("account/testimonials/<int:pk>/delete/", testimonial_delete, name="testimonial-delete"),

    path('account/notifications/', notifications_list, name='notifications_list'),
    path('account/notifications/read/<int:pk>/', mark_notification_read, name='mark_notification_read'),


    path('account/appointments/<str:pk>/details/', view_appointment, name='view_appointment'),
    path('collect-cash-appointment/<str:pk>/', collect_cash_appointment, name='collect_cash_appointment'),
    path('account/appointments/cancel/<str:pk>/', cancel_appointment, name='cancel_appointment'), 

    path("api/notifications/", api_notifications_list, name="api_notifications"),
    path("api/notifications/read/<int:pk>/", api_mark_notification_read, name="api_mark_notification_read"),
    path("api/notifications/read-all/", api_mark_all_notifications_read, name="api_mark_all_notifications_read"),

]