from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils import timezone
from .forms import ContactForm, EventForm
from .models import Club, ClubGalleryMedia, ClubMembership, ClubResource, Contact, Event
from .admin_key_crypto import decrypt_admin_key


def get_admin_club(user):
    return Club.objects.filter(admin_user=user).first()



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is None:
            email_user = User.objects.filter(email__iexact=username).first()
            if email_user:
                user = authenticate(request, username=email_user.username, password=password)

        if user:
            if Club.objects.filter(admin_user=user).exists():
                messages.error(request, "Club admins must use the Club Admin login.")
                return redirect('login')
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')


@login_required
def index(request):
    edit_event = request.GET.get('edit') == 'event'
    edit_event_id = request.GET.get('event_id')
    editing_event = None
    is_admin = request.user.is_superuser or Club.objects.filter(
        admin_user=request.user
    ).exists()

    if edit_event_id and is_admin:
        event_queryset = Event.objects.all() if request.user.is_superuser else Event.objects.filter(
            club__admin_user=request.user
        )
        editing_event = get_object_or_404(event_queryset, id=edit_event_id)

    now = timezone.now()

    # Only check clubs that currently have pending future events. This avoids
    # scanning every club on every homepage request.
    pending_club_ids = Event.objects.filter(
        is_approved=False,
        date_time__gte=now,
        club__isnull=False,
    ).values_list('club_id', flat=True).distinct()
    for club_id in pending_club_ids:
        auto_approve_next_event(club_id)

    events = Event.objects.filter(
        is_approved=True,
        date_time__gte=now,
    ).select_related('club', 'created_by').order_by('date_time')

    event_form = None
    managed_events = Event.objects.none()

    if is_admin:
        if editing_event:
            event_form = EventForm(
                request.POST or None,
                request.FILES or None,
                instance=editing_event,
            )
        else:
            event_form = EventForm(
                request.POST or None,
                request.FILES or None,
            )

        managed_events = Event.objects.all() if request.user.is_superuser else Event.objects.filter(
            club__admin_user=request.user
        )
        managed_events = managed_events.select_related('club').order_by('date_time')

        if request.method == 'POST' and 'delete_event' in request.POST:
            event_queryset = Event.objects.all() if request.user.is_superuser else Event.objects.filter(
                club__admin_user=request.user
            )
            event = get_object_or_404(event_queryset, id=request.POST.get('event_id'))
            club_id = event.club_id
            event.delete()
            if club_id:
                auto_approve_next_event(club_id)
            messages.success(request, "Event deleted successfully.")
            return redirect(f"{reverse('home')}?edit=event")

        if request.method == 'POST' and 'event_submit' in request.POST:
            if event_form.is_valid():
                event = event_form.save(commit=False)

                if editing_event:
                    event.created_by = editing_event.created_by
                    event.club = editing_event.club
                    event.is_approved = editing_event.is_approved
                else:
                    event.created_by = request.user
                    if request.user.is_superuser:
                        event.is_approved = True
                    else:
                        club = get_admin_club(request.user)
                        if not club:
                            messages.error(request, "You are not associated with a club.")
                            return redirect('home')
                        event.club = club
                        approved_exists = Event.objects.filter(
                            club=club,
                            is_approved=True,
                            date_time__gte=timezone.now(),
                        ).exists()
                        event.is_approved = not approved_exists

                try:
                    event.full_clean()
                    event.save()
                except ValidationError as exc:
                    for error in exc.messages:
                        event_form.add_error(None, error)
                else:
                    if event.is_approved:
                        messages.success(request, "Event approved and posted successfully!")
                    else:
                        messages.success(request, "Event submitted successfully! Awaiting approval.")
                    return redirect(f"{reverse('home')}?edit=event")
            else:
                messages.error(request, "Please correct the form errors.")

    return render(request, 'index.html', {
        'events': events,
        'event_form': event_form,
        'edit_event': edit_event,
        'editing_event': editing_event,
        'is_admin': is_admin,
        'managed_events': managed_events,
    })


def auto_approve_next_event(club_id):
    now = timezone.now()
    if Event.objects.filter(
        club_id=club_id,
        is_approved=True,
        date_time__gte=now,
    ).exists():
        return

    next_pending = Event.objects.filter(
        club_id=club_id,
        is_approved=False,
        date_time__gte=now,
    ).order_by('date_time').first()

    if next_pending:
        next_pending.is_approved = True
        next_pending.save(update_fields=['is_approved'])


@login_required
def join_clubs(request):
    clubs = Club.objects.all().order_by('name')
    return render(request, 'join_clubs.html', {'clubs': clubs})


@login_required
def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    edit_about = request.GET.get('edit') == 'about'
    edit_mission = request.GET.get('edit') == 'mission'
    edit_past_events = request.GET.get('edit') == 'past-events'
    edit_admin = request.GET.get('edit') == 'admin'
    edit_resources = request.GET.get('edit') == 'resources'
    edit_gallery = request.GET.get('edit') == 'gallery'
    edit_name = request.GET.get('edit') == 'name'

    is_admin = request.user.is_superuser or request.user == club.admin_user
    is_member = ClubMembership.objects.filter(club=club, user=request.user).exists()

    if request.method == 'POST':
        if is_admin and 'save_about' in request.POST:
            club.description = request.POST.get('description', '').strip()
            club.save(update_fields=['description'])
            messages.success(request, 'Description updated successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'save_mission' in request.POST:
            club.mission = request.POST.get('mission', '').strip()
            club.save(update_fields=['mission'])
            messages.success(request, 'Mission updated successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'save_past_events' in request.POST:
            club.past_events = request.POST.get('past_events', '').strip()
            club.save(update_fields=['past_events'])
            messages.success(request, 'Past events updated successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'save_admin' in request.POST:
            club.admin_name = request.POST.get('admin_name', '').strip()
            club.save(update_fields=['admin_name'])
            messages.success(request, 'Admin information updated successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'add_resource' in request.POST:
            title = request.POST.get('title', '').strip()
            link = request.POST.get('link', '').strip() or None
            resource_file = request.FILES.get('file')
            resource = ClubResource(
                club=club,
                title=title,
                link=link,
                file=resource_file,
            )
            try:
                resource.full_clean()
                resource.save()
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)
            else:
                messages.success(request, 'Resource added successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'delete_resource' in request.POST:
            resource_id = request.POST.get('resource_id')
            deleted, _ = ClubResource.objects.filter(id=resource_id, club=club).delete()
            if deleted:
                messages.success(request, 'Resource deleted successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'upload_media' in request.POST:
            media_file = request.FILES.get('media_file')
            if not media_file:
                messages.error(request, 'Please select a media file.')
            else:
                media = ClubGalleryMedia(club=club, file=media_file)
                try:
                    media.full_clean()
                    media.save()
                except ValidationError as exc:
                    for error in exc.messages:
                        messages.error(request, error)
                else:
                    messages.success(request, 'Media uploaded successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'delete_media' in request.POST:
            media_id = request.POST.get('media_id')
            deleted, _ = ClubGalleryMedia.objects.filter(id=media_id, club=club).delete()
            if deleted:
                messages.success(request, 'Media deleted successfully.')
            return redirect('club_detail', slug=slug)

        if is_admin and 'save_name' in request.POST:
            name = request.POST.get('club_name', '').strip()
            if not name:
                messages.error(request, 'Club name cannot be empty.')
                return redirect('club_detail', slug=slug)

            club.name = name
            if request.FILES.get('club_image'):
                club.image = request.FILES['club_image']
            try:
                club.full_clean()
                club.save()
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)
            else:
                messages.success(request, 'Club updated successfully.')
            return redirect('club_detail', slug=club.slug)

        if 'join_club' in request.POST:
            ClubMembership.objects.get_or_create(club=club, user=request.user)
            messages.success(request, f'You have joined {club.name}!')
            return redirect('club_detail', slug=slug)

        if 'leave_club' in request.POST:
            ClubMembership.objects.filter(club=club, user=request.user).delete()
            messages.info(request, f'You have left {club.name}.')
            return redirect('club_detail', slug=slug)

    context = {
        'club': club,
        'edit_about': edit_about,
        'edit_mission': edit_mission,
        'edit_past_events': edit_past_events,
        'edit_resources': edit_resources,
        'edit_admin': edit_admin,
        'edit_gallery': edit_gallery,
        'edit_name': edit_name,
        'is_admin': is_admin,
        'is_member': is_member,
        'member_count': club.member_count,
        'upcoming_events_count': club.upcoming_events_count,
    }
    return render(request, 'club_detail.html', context)


from django.utils import timezone

def contact(request):
    if request.method == 'POST':
        if 'consent' not in request.POST:
            messages.error(request, 'Please accept the consent checkbox before submitting.')
            return redirect('home')

        form = ContactForm(request.POST)
        if form.is_valid():
            contact_obj = form.save(commit=False)
            contact_obj.date = timezone.localdate()
            contact_obj.save()

            messages.success(request, 'Your message has been sent!')
        else:
            messages.error(request, 'Please enter valid contact details.')

        return redirect('home')

    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        errors = []

        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Enter a valid email address.')
        if not password:
            errors.append('Password is required.')
        else:
            try:
                validate_password(password, user=None)
            except ValidationError as exc:
                errors.extend(exc.messages)
        if User.objects.filter(username=email).exists():
            errors.append('User with this email already exists.')

        if errors:
            return render(request, 'login.html', {
                'signup_errors': errors,
                'signup_name': name,
                'signup_email': email,
            })

        try:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
            )
        except IntegrityError:
            messages.error(request, 'An account with that email already exists.')
            return redirect('login')

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')

    return redirect('login')


@login_required
def club_dashboard(request):
    club = get_admin_club(request.user)
    if club:
        return redirect('club_detail', slug=club.slug)
    messages.error(request, 'No club is assigned to your account.')
    return redirect('home')


def club_admin_login(request):
    if request.method == 'POST':
        if 'recover_key' in request.POST:
            email = request.POST.get('recovery_email', '').strip().lower()
            user = User.objects.filter(email__iexact=email).first()
            club = get_admin_club(user) if user else None

            if club:
                raw_key = decrypt_admin_key(club.admin_key)
                if raw_key:
                    try:
                        send_mail(
                            subject='Your Clubify Admin Key',
                            message=(
                                f'Hello {club.admin_name},\n\n'
                                f'Your current Clubify Admin Key is: {raw_key}\n\n'
                                'If you did not request this, contact the Clubify administrator.'
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=False,
                        )
                    except Exception:
                        messages.error(request, 'We could not send the admin key email. Please try again later.')
                    else:
                        messages.success(request, 'Your current admin key has been sent to your email.')
                else:
                    messages.error(request, 'Your admin key cannot be recovered. Please set a new key from Django Admin.')
            else:
                messages.info(request, 'If that email belongs to a club admin, the current admin key will be sent.')
        else:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            admin_key = request.POST.get('admin_key', '')
            user = authenticate(request, username=username, password=password)
            if user is None:
                email_user = User.objects.filter(email__iexact=username).first()
                if email_user:
                    user = authenticate(request, username=email_user.username, password=password)

            if user:
                club = get_admin_club(user)
                valid_admin_key = False

                if club:
                    valid_admin_key = (admin_key == decrypt_admin_key(club.admin_key))

                if valid_admin_key:
                    login(request, user)
                    return redirect('home')

                messages.error(request, 'Invalid admin credentials.')
            else:
                messages.error(request, 'Invalid admin credentials.')

    return render(request, 'club_admin_login.html')


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user

            if request.user.is_superuser:
                event.is_approved = True
            else:
                club = get_admin_club(request.user)
                if not club:
                    messages.error(request, 'You are not linked to a club.')
                    return redirect('home')
                event.club = club
                approved_exists = Event.objects.filter(
                    club=club,
                    is_approved=True,
                    date_time__gte=timezone.now(),
                ).exists()
                event.is_approved = not approved_exists

            try:
                event.full_clean()
                event.save()
            except ValidationError:
                messages.error(request, 'Please correct the form errors.')
            else:
                if event.is_approved:
                    messages.success(request, 'Event approved and posted successfully!')
                else:
                    messages.success(request, 'Event submitted successfully! Awaiting approval.')
                return redirect('home')
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        form = EventForm()

    return render(request, 'event_form.html', {'form': form})


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related('club'),
        id=event_id,
        is_approved=True,
    )
    return render(request, 'event_detail.html', {'event': event})
