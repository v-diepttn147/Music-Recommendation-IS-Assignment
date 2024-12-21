from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.decorators import login_required

import random
import pickle as pkl

# Create your views here.
def index(request):

    #Display recent songs
    if not request.user.is_anonymous :
        recent = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        recent_id = [each['song_id'] for each in recent][:5]
        recent_songs_unsorted = Song.objects.filter(id__in=recent_id,recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(id=id))
    else:
        recent = None
        recent_songs = None

    first_time = False
    #Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(id=last_played_id)
        else:
            first_time = True
            last_played_song = Song.objects.get(id=17)

    else:
        first_time = True
        last_played_song = Song.objects.get(id=17)

    #Display all songs
    songs = Song.objects.all()

    #Display few songs on home page
    songs_all = list(Song.objects.all().values('id').order_by('?'))
    sliced_ids = [each['id'] for each in songs_all][:5]
    indexpage_songs = Song.objects.filter(id__in=sliced_ids)

    # Display Hindi Songs
    songs_hindi = list(Song.objects.filter(language='Hindi').values('id'))
    sliced_ids = [each['id'] for each in songs_hindi][:5]
    indexpage_hindi_songs = Song.objects.filter(id__in=sliced_ids)

    # Display English Songs
    songs_english = list(Song.objects.filter(language='English').values('id'))
    sliced_ids = [each['id'] for each in songs_english][:5]
    indexpage_english_songs = Song.objects.filter(id__in=sliced_ids)

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = songs.filter(Q(name__icontains=search_query)).distinct()
        context = {'all_songs': filtered_songs,'last_played':last_played_song,'query_search':True}
        return render(request, 'musicapp/index.html', context)

    context = {
        'all_songs':indexpage_songs,
        'recent_songs': recent_songs,
        'hindi_songs':indexpage_hindi_songs,
        'english_songs':indexpage_english_songs,
        'last_played':last_played_song,
        'first_time': first_time,
        'query_search':False,
    }
    return render(request, 'musicapp/index.html', context=context)


def hindi_songs(request):

    hindi_songs = Song.objects.filter(language='Hindi')

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    query = request.GET.get('q')

    if query:
        hindi_songs = Song.objects.filter(Q(name__icontains=query)).distinct()
        context = {'hindi_songs': hindi_songs}
        return render(request, 'musicapp/hindi_songs.html', context)

    context = {'hindi_songs':hindi_songs,'last_played':last_played_song}
    return render(request, 'musicapp/hindi_songs.html',context=context)


def english_songs(request):

    english_songs = Song.objects.filter(language='English')

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    query = request.GET.get('q')

    if query:
        english_songs = Song.objects.filter(Q(name__icontains=query)).distinct()
        context = {'english_songs': english_songs}
        return render(request, 'musicapp/english_songs.html', context)

    context = {'english_songs':english_songs,'last_played':last_played_song}
    return render(request, 'musicapp/english_songs.html',context=context)

@login_required(login_url='login')
def play_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('all_songs')


@login_required(login_url='login')
def play_song_index(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('index')

@login_required(login_url='login')
def play_recent_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()
    return redirect('recent')


def all_songs(request):
    songs = Song.objects.all()

    first_time = False
    #Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(id=last_played_id)
    else:
        first_time = True
        last_played_song = Song.objects.get(id=7)

    
    # apply search filters
    qs_singers = Song.objects.values_list('singer').all()
    s_list = [s.split(',') for singer in qs_singers for s in singer]
    all_singers = sorted(list(set([s.strip() for singer in s_list for s in singer])))
    qs_languages = Song.objects.values_list('language').all()
    all_languages = sorted(list(set([l.strip() for lang in qs_languages for l in lang])))
    
    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        search_singer = request.GET.get('singers') or ''
        search_language = request.GET.get('languages') or ''
        filtered_songs = songs.filter(Q(name__icontains=search_query)).filter(Q(language__icontains=search_language)).filter(Q(singer__icontains=search_singer)).distinct()
        context = {
        'songs': filtered_songs,
        'last_played':last_played_song,
        'all_singers': all_singers,
        'all_languages': all_languages,
        'query_search': True,
        }
        return render(request, 'musicapp/all_songs.html', context)

    context = {
        'songs': songs,
        'last_played':last_played_song,
        'first_time':first_time,
        'all_singers': all_singers,
        'all_languages': all_languages,
        'query_search' : False,
        }
    return render(request, 'musicapp/all_songs.html', context=context)


def recent(request):
    
    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)

    #Display recent songs
    recent = list(Recent.objects.filter(user=request.user).values('song_id').order_by('-id'))
    if recent and not request.user.is_anonymous :
        recent_id = [each['song_id'] for each in recent]
        recent_songs_unsorted = Song.objects.filter(id__in=recent_id,recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(id=id))
    else:
        recent_songs = None

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = recent_songs_unsorted.filter(Q(name__icontains=search_query)).distinct()
        context = {'recent_songs': filtered_songs,'last_played':last_played_song,'query_search':True}
        return render(request, 'musicapp/recent.html', context)

    context = {'recent_songs':recent_songs,'last_played':last_played_song,'query_search':False}
    return render(request, 'musicapp/recent.html', context=context)


@login_required(login_url='login')
def detail(request, song_id):
    songs = Song.objects.filter(id=song_id).first()

    # Add data to recent database
    if list(Recent.objects.filter(song=songs,user=request.user).values()):
        data = Recent.objects.filter(song=songs,user=request.user)
        data.delete()
    data = Recent(song=songs,user=request.user)
    data.save()

    #Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.get(id=7)


    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct
    is_favourite = Favourite.objects.filter(user=request.user).filter(song=song_id).values('is_fav')

    if request.method == "POST":
        if 'playlist' in request.POST:
            playlist_name = request.POST["playlist"]
            q = Playlist(user=request.user, song=songs, playlist_name=playlist_name)
            q.save()
            messages.success(request, "Song added to playlist!")
        elif 'add-fav' in request.POST:
            is_fav = True
            query = Favourite(user=request.user, song=songs, is_fav=is_fav)
            print(f'query: {query}')
            query.save()
            messages.success(request, "Added to favorite!")
            return redirect('detail', song_id=song_id)
        elif 'rm-fav' in request.POST:
            is_fav = True
            query = Favourite.objects.filter(user=request.user, song=songs, is_fav=is_fav)
            print(f'user: {request.user}')
            print(f'song: {songs.id} - {songs}')
            print(f'query: {query}')
            query.delete()
            messages.success(request, "Removed from favorite!")
            return redirect('detail', song_id=song_id)

    context = {'songs': songs, 'playlists': playlists, 'is_favourite': is_favourite,'last_played':last_played_song}
    return render(request, 'musicapp/detail.html', context=context)


def mymusic(request):
    return render(request, 'musicapp/mymusic.html')


def playlist(request):
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct
    context = {'playlists': playlists}
    return render(request, 'musicapp/playlist.html', context=context)


def playlist_songs(request, playlist_name):
    songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        playlist_song = Playlist.objects.filter(playlist_name=playlist_name, song__id=song_id, user=request.user)
        playlist_song.delete()
        messages.success(request, "Song removed from playlist!")

    context = {'playlist_name': playlist_name, 'songs': songs}

    return render(request, 'musicapp/playlist_songs.html', context=context)


def favourite(request):
    songs = Song.objects.filter(favourite__user=request.user, favourite__is_fav=True).distinct()
    print(f'songs: {songs}')
    
    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        favourite_song = Favourite.objects.filter(user=request.user, song__id=song_id, is_fav=True)
        favourite_song.delete()
        messages.success(request, "Removed from favourite!")
    context = {'songs': songs}
    return render(request, 'musicapp/favourite.html', context=context)


# @login_required(login_url='login')
# def play_next_song(request, song_id):
#     with open('pickles/music_data_clustered.pkl', 'rb') as f:
#         music_data = pkl.load(f)
#     mapping_song_cluster = dict(zip(music_data['song'], music_data['cluster']))

#     all_songs = list(Song.objects.all().order_by('id'))
    
#     current_index = next((i for i, song in enumerate(all_songs) if song.id == song_id), None)
    
#     if current_index is not None and current_index + 1 < len(all_songs):
#         next_song = all_songs[current_index + 1]
#     else:
#         next_song = all_songs[0]  # Loop back to the first song
    
#     data = Recent(song=next_song, user=request.user)
#     data.save()
#     return redirect('play_song', song_id=next_song.id)



@login_required(login_url='login')
def play_next_song(request, song_id):
    # Load the clustered music data
    try:
        with open('pickles/music_data_clustered.pkl', 'rb') as f:
            music_data = pkl.load(f)
    except FileNotFoundError:
        raise Http404("Clustered music data file not found.")
    
    # Create a mapping of song names to their clusters
    mapping_song_cluster = dict(zip(music_data['song'], music_data['cluster']))

    try:
        # Get the current song and its name
        current_song = Song.objects.get(id=song_id)
        current_song_name = current_song.name
    except Song.DoesNotExist:
        raise Http404("Current song not found.")
    
    # Find the cluster ID for the current song
    current_cluster = mapping_song_cluster.get(current_song_name, 0)
    if current_cluster is None:
        raise Http404("Cluster information for the current song not found.")
    
    # Find all songs in the same cluster
    songs_in_cluster = [
        song for song in Song.objects.all()
        if mapping_song_cluster.get(song.name) == current_cluster
    ]
    
    if not songs_in_cluster:
        raise Http404("No songs found in the same cluster.")

    # Randomly pick the next song from the same cluster
    next_song = random.choice(songs_in_cluster)
    
    # Log the next song for the user
    data = Recent(song=next_song, user=request.user)
    data.save()
    
    # Redirect to the next song
    return redirect('play_song', song_id=next_song.id)


@login_required(login_url='login')
def play_previous_song(request, song_id):
    all_songs = list(Song.objects.all().order_by('id'))
    current_index = next((i for i, song in enumerate(all_songs) if song.id == song_id), None)
    
    if current_index is not None and current_index > 0:
        previous_song = all_songs[current_index - 1]
    else:
        previous_song = all_songs[-1]  # Loop back to the last song
    
    data = Recent(song=previous_song, user=request.user)
    data.save()
    return redirect('play_song', song_id=previous_song.id)
