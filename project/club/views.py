# club/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClubLeader, ClubMedia

@login_required
def leader_dashboard(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
        media = ClubMedia.objects.filter(club=club)
    except ClubLeader.DoesNotExist:
        return render(request, 'club/no_permission.html')

    return render(request, 'club/leader_dashboard.html', {'club': club, 'media': media})

@login_required
def edit_club(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
    except ClubLeader.DoesNotExist:
        return redirect('no_permission')

    if request.method == 'POST':
        club.name = request.POST['name']
        club.description = request.POST['description']
        if 'logo' in request.FILES:
            club.logo = request.FILES['logo']
        club.save()
        return redirect('leader_dashboard')

    return render(request, 'club/edit_club.html', {'club': club})

    # Extend views.py to support media upload
from django.contrib import messages
from .forms import MediaUploadForm

@login_required
def upload_media(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
    except ClubLeader.DoesNotExist:
        return redirect('no_permission')

    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.club = club
            media.uploaded_by = request.user
            media.save()
            messages.success(request, "Media uploaded successfully!")
            return redirect('leader_dashboard')
    else:
        form = MediaUploadForm()

    return render(request, 'club/upload_media.html', {'form': form})

from .models import ClubEvent  # Add if not already imported

@login_required
def create_event(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
    except ClubLeader.DoesNotExist:
        return redirect('no_permission')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('create_event')
    else:
        form = EventForm()

    events = ClubEvent.objects.filter(club=club).order_by('-date')
    return render(request, 'club/create_event.html', {'form': form, 'events': events})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(ClubEvent, id=event_id, club__clubleader__user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('create_event')
    else:
        form = EventForm(instance=event)
    return render(request, 'club/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(ClubEvent, id=event_id, club__clubleader__user=request.user)
    event.delete()
    return redirect('create_event')


from .models import ClubEvent  # Add if missing

@login_required
def leader_dashboard(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
        media = ClubMedia.objects.filter(club=club)
        events = ClubEvent.objects.filter(club=club).order_by('-date')
    except ClubLeader.DoesNotExist:
        return render(request, 'club/no_permission.html')

    return render(request, 'club/leader_dashboard.html', {
        'club': club,
        'media': media,
        'events': events,
    })

# club/views.py (add this view)
@login_required
def create_post(request):
    try:
        club_leader = ClubLeader.objects.get(user=request.user)
        club = club_leader.club
    except ClubLeader.DoesNotExist:
        return redirect('no_permission')

    posts = ClubPost.objects.filter(club=club).order_by('-created_at')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.club = club
            post.author = request.user
            post.save()
            return redirect('create_post')
    else:
        form = PostForm()

    return render(request, 'club/create_post.html', {'form': form, 'posts': posts})
