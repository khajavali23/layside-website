# blogs/serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User  # if you later connect real authors


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = [
            'id',
            'name',
            'email',           # you might want to hide email in production
            'message',
            'rating',
            'created_at',
            'slug',
        ]
        read_only_fields = ['created_at', 'slug']


class BlogListSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Blog
        fields = [
            'id',
            'slug',
            'heading',
            'image',
            'category',
            'author',
            'author_designation',
            'createdAt',
            'tags',
            'show_on_homepage',
            'comment_count',
            # meta fields usually not needed in list view
        ]

class BlogDetailSerializer(serializers.ModelSerializer):
    comments = BlogCommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    latest_blogs = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id',
            'slug',
            'heading',
            'image',
            'category',
            'author',
            'author_designation',
            'content',
            'createdAt',
            'tags',
            'show_on_homepage',
            'meta_title',
            'meta_keyword',
            'meta_description',
            'comments',
            'comment_count',
            'latest_blogs',
        ]

    def get_latest_blogs(self, obj):
        latest = Blog.objects.filter(status=True)\
            .exclude(id=obj.id)\
            .order_by('-createdAt')[:2]

        return BlogListSerializer(latest, many=True, context=self.context).data

# Optional: if you want a very minimal homepage serializer
class HomepageBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'id',
            'slug',
            'heading',
            'image',
            'category',
            'author',
            'createdAt',
            'tags',
        ]





class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "title",
            "slug",
            "icon",
            "banner",
            "description",
            "priority",
            "show_on_homepage",
        ]



class DepartmentDetailSerializer(serializers.ModelSerializer):
    doctors = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = "__all__"
        # doctors will be appended automatically

    def get_doctors(self, obj):
        doctors = Doctor.objects.filter(
            department=obj,
            status=True
        ).order_by("priority")
        return DoctorListSerializer(doctors, many=True, context=self.context).data



class DoctorListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.title", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "slug",
            "photo",
            "designation",
            "department",
            "department_name",
            "experience_years",
            "education",
            "fee",
            "city",
            "priority",
            "show_on_homepage",
        ]


class DoctorDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.title", read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"




class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "priority",
            "created_at",
        ]




class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "name",
            "designation",
            "rating",
            "description",
            "priority",
            "created_at",
        ]

class TestimonialTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "name",
            "designation",
            "rating",
            "description",
            "priority",
            "created_at",
        ]



class TestimonialVideoSerializer(serializers.ModelSerializer):
    embed_url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "youtube_url",
            "embed_url",
            "thumbnail",
            "priority",
            "created_at",
        ]

    def get_embed_url(self, obj):
        return obj.get_youtube_embed()

    def get_thumbnail(self, obj):
        video_id = obj.get_youtube_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/0.jpg"
        return ""
    



class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = '__all__'

class MonthlyTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTiming
        fields = '__all__'





class HealthCheckupPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheckupPlan
        fields = [
            "id",
            "title",
            "slug",
            "price",
            "total_test_include",
            "tests",              # ✅ new field
            "image",
            "priority",
            "created_at",
        ]



class HealthCheckupBookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheckupBooking
        fields = [
            "id",
            "plan",
            "patient",
            "message",
            "status",
            "payment_id",
            "created_at",
        ]
        read_only_fields = ["status", "payment_id", "created_at"]




class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id",
            "heading",
            "description",
            "button_text",
            "button_url",
            "button_two_text",
            "button_two_url",
            "image_for_desktop",
            "image_for_mobile",
            "created_at",
        ]



class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "content",
            "created_at",
            "slug",
        ]
        read_only_fields = ["created_at", "slug"]




class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = [
            "id",
            "title",
            "image",
            "youtube_url",   # 👈 ADD
            "created_at",
        ]


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = [
            "id",
            "job_title",
            "department",
            "experience",
            "salary",
            "job_summary",
            "responsibilities",
            "skills",
            "qualifications",
            "slug",
            "created_at",
        ]




class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "message",
            "type",
            "created_at",
            "read_status",
            "redirection_url",
            "is_alarmed",
        ]


        
class CareerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerApplication
        fields = [
            "id",
            "name",
            "number",
            "email",
            "cover_letter",
            "cv",
            "job",
            "created_at",
            "slug",
        ]
        read_only_fields = ["created_at", "slug"]