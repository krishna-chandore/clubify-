from django.contrib import admin
from django import forms
from clubapp.models import Contact, Club, ClubGalleryMedia, ClubResource, Event, ClubMembership
from clubapp.admin_key_crypto import decrypt_admin_key

# Inline class to allow adding gallery images within the Club admin page
class ClubGalleryMediaInline(admin.TabularInline):
    model = ClubGalleryMedia
    extra = 1  # Show one empty field by default for adding images


class ClubResourceInline(admin.TabularInline):
    model = ClubResource
    extra = 1

# Main Club admin configuration
class ClubAdminForm(forms.ModelForm):
    admin_key = forms.CharField(label='Admin Key', required=False, widget=forms.TextInput)

    class Meta:
        model = Club
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['admin_key'] = decrypt_admin_key(self.instance.admin_key)

    def clean_admin_key(self):
        value = self.cleaned_data.get('admin_key', '').strip()
        if not value and self.instance and self.instance.pk:
            return decrypt_admin_key(self.instance.admin_key)
        return value


class ClubAdmin(admin.ModelAdmin):
    form = ClubAdminForm
    list_display = ('name', 'admin_name')  # Columns to show in admin list view
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill the slug from the name
    inlines = [ClubGalleryMediaInline, ClubResourceInline]  # Attach the gallery image inline editor
    search_fields = ['name', 'admin_name']
# Register both models
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubGalleryMedia)


admin.site.register(Contact)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'date_time', 'is_approved')
    list_filter = ('is_approved', 'club')
    search_fields = ('title', 'description')

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('club', 'user', 'joined_at')