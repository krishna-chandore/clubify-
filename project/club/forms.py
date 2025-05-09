# club/forms.py
from django import forms
from .models import ClubMedia

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = ClubMedia
        fields = ['title', 'description', 'media_file']

# club/forms.py (add this under MediaUploadForm)
class EventForm(forms.ModelForm):
    class Meta:
        model = ClubEvent
        fields = ['title', 'date', 'description']

# club/forms.py (add this form)
class PostForm(forms.ModelForm):
    class Meta:
        model = ClubPost
        fields = ['content']

