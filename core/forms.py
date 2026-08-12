from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget




STATUS_CHOICES = [
    (True, 'Active'),
    (False, 'Inactive')
]



class DepartmentForm(forms.ModelForm):
    
    description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Department
        fields = ['title', 'icon', 'priority', 'breadcamp', 'show_on_homepage', 'banner',  'description', 'status', 'meta_description', 'meta_keyword','meta_title', 'slug']

        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES, attrs={
                'class': 'form-control'
            }),
            'banner': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
            
            'icon': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL3(this)",
                "accept": "image/*"
            }),
            
            'breadcamp': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL2(this)",
                "accept": "image/*"
            }),
            
        }  
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_keyword'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['banner'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['breadcamp'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['icon'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['priority'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].required = True



class SubDepartmentForm(forms.ModelForm):

    description = forms.CharField(
        widget=CKEditorWidget(),
        required=False
    )

    class Meta:
        model = SubDepartment

        fields = [
            'department',
            'title',
            'slug',
            'icon',
            'description',
            'priority',
            'status',
            'meta_title',
            'meta_keyword',
            'meta_description',
        ]

        widgets = {
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),

            'status': forms.Select(
                choices=STATUS_CHOICES,
                attrs={
                    'class': 'form-control'
                }
            ),

            'icon': forms.FileInput(attrs={
                'class': 'file__input',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['department'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['icon'].widget.attrs['class'] = 'form-control'
        self.fields['priority'].widget.attrs['class'] = 'form-control'
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'
        self.fields['meta_keyword'].widget.attrs['class'] = 'form-control'
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'

        self.fields['slug'].required = True
class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = [
            'name', 'department', 'priority', 'designation', 'experience_years', 'fee', 'email', 'number', 'gender',
            'education', 'city', 'photo', 'status', 'show_on_homepage', 'description', 'meta_description', 'meta_keyword', 'meta_title', 'slug'
        ]
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'photo': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['department'].widget.attrs['class'] = 'form-control'
        self.fields['designation'].widget.attrs['class'] = 'form-control'
        self.fields['experience_years'].widget.attrs['class'] = 'form-control'
        self.fields['fee'].widget.attrs['class'] = 'form-control'
        self.fields['priority'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['gender'].widget.attrs['class'] = 'form-control'
        self.fields['education'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_keyword'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].widget.attrs['class'] = 'form-control'  # Added this line
        self.fields['slug'].required = True


class AvailableTimeForm(forms.ModelForm):
    class Meta:
        model = AvailableTime
        fields = ['day', 'start_time', 'end_time', 'slot']



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'
        self.fields['end_time'].widget.attrs['class'] = 'form-control'
        self.fields['slot'].widget.attrs['class'] = 'form-control'



class MonthlyTimeForm(forms.ModelForm):
    class Meta:
        model = MonthlyTiming
        fields = ['date', 'start_time', 'end_time', 'slot']



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'
        self.fields['end_time'].widget.attrs['class'] = 'form-control'
        self.fields['slot'].widget.attrs['class'] = 'form-control'




class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['date', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['reason'].widget.attrs['class'] = 'form-control'








class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['heading', 'slug', 'show_on_homepage', 'image', 'category', 'author', 'content', 'status', 'tags', 'author_designation', 'meta_description', 'meta_keyword','meta_title']
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'onchange' : "readURL(this)",
                "accept": "image/*"
            }),
        }
        
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['heading'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['author_designation'].widget.attrs['class'] = 'form-control'
        self.fields['author'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['tags'].widget.attrs['class'] = 'form-control'
        self.fields['show_on_homepage'].widget.attrs['class'] = 'form-check-input'  # Added this line






class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "priority"]
        widgets = {
            "question": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "answer": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
        }




class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            "name",
            "designation",
            "rating",
            "description",
            "youtube_url",   # 👈 NEW
            "priority",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "designation": forms.TextInput(attrs={"class": "form-control"}),
            "rating": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "youtube_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://youtube.com/watch?v=..."
            }),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        youtube = cleaned_data.get("youtube_url")
        name = cleaned_data.get("name")
        description = cleaned_data.get("description")

        if not youtube and not (name and description):
            raise forms.ValidationError(
                "Add either text testimonial OR YouTube video"
            )

        return cleaned_data




class HealthCheckupPlanForm(forms.ModelForm):
    # 👇 Custom field to input tests
    tests = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter tests separated by comma (e.g. Blood Pressure, CBC, Sugar)"
            }
        ),
        help_text="Enter tests separated by comma"
    )

    class Meta:
        model = HealthCheckupPlan
        fields = [
            "title",
            "tests",
            "priority",
            "total_test_include",
            "price",
            "image",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),
            "total_test_include": forms.NumberInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert list → comma separated for edit form
        if self.instance and self.instance.tests:
            self.fields["tests"].initial = ", ".join(self.instance.tests)

    def clean_tests(self):
        tests = self.cleaned_data.get("tests", "")
        if tests:
            return [t.strip() for t in tests.split(",") if t.strip()]
        return []




class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            "heading",
            "description",
            "button_text",
            "button_url",
            "button_two_text",
            "button_two_url",
            "image_for_desktop",
            "image_for_mobile",
            "status",
        ]
        widgets = {
            "heading": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "button_text": forms.TextInput(attrs={"class": "form-control"}),
            "button_url": forms.URLInput(attrs={"class": "form-control"}),
            "button_two_text": forms.TextInput(attrs={"class": "form-control"}),
            "button_two_url": forms.URLInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }



class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ["title", "image", "youtube_url"]  # ✅ added
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "youtube_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://youtube.com/watch?v=..."
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        youtube_url = cleaned_data.get("youtube_url")

        # ✅ must provide at least one
        if not image and not youtube_url:
            raise forms.ValidationError("Add either an image or a YouTube URL")

        return cleaned_data
    

    

class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = [
            "job_title",
            "department",
            "experience",
            "salary",
            "job_summary",
            "responsibilities",
            "skills",
            "qualifications",
            "status",
        ]
        widgets = {
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "experience": forms.NumberInput(attrs={"class": "form-control"}),
            "salary": forms.NumberInput(attrs={"class": "form-control"}),
            "qualifications": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }




class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['name', 'email', 'rating', 'message']