import os
import django
import sys
sys.path.append('..')
# Set the project settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'musicplayer.settings'  # Replace with your project's name
os.environ['PYTHONPATH'] = os.getcwd()
from asgiref.sync import sync_to_async

# Initialize Django
django.setup()

from musicapp.models import Song 


import pandas as pd

df = pd.read_pickle('../pickles/music1K5_with_youtube_search.pkl')


mapping_youtube_id_with_file_name = {}
files = os.listdir('../media/new_song/mp3_files')
for file in files:
    mapping_youtube_id_with_file_name[file[:11]] = file


# Wrap the create method in sync_to_async
async def add_song_async(row_data):
    new_song = await sync_to_async(Song.objects.create)(
        name=row_data['name'],
        album="",
        language="English",  # Adjust based on your model setup
        song_img=row_data['preview'],  # File path
        year=2024,
        singer=row_data['artist'],
        song_file=row_data['mp3_file']  # File path
    )
    print("New song added:", new_song)


# Wrap the delete method in sync_to_async
async def remove_song_async(song_name):
    try:
        # Fetch the song by name
        song_to_delete = await sync_to_async(Song.objects.get)(name=song_name)
        
        # Delete the song
        await sync_to_async(song_to_delete.delete)()
        
        print(f"Song '{song_name}' has been removed.")
    except Song.DoesNotExist:
        print(f"Song '{song_name}' does not exist.")

for i in range(len(df)):
    row = df.iloc[i]
    try:
        search_result = row['search_result']
        link = search_result['result'][0].get('link')
        year = row['year']
        track_id = row['track_id']
        song_name = row['song']
        singer = row['artist']
        if link is not None:
            id = link.replace('https://www.youtube.com/watch?v=', '')
            # if title is None:
            title = mapping_youtube_id_with_file_name.get(id, None)
            #     continue
            mp3_file = f'new_song/mp3_files/{title}'
            preview_file = f'new_song/preview/{track_id}.png'
            if os.path.exists(os.path.join('../media',mp3_file)) and os.path.exists(os.path.join('../media',preview_file)):
                row_data = {
                    'name': song_name,
                    'preview': preview_file,
                    'artist': singer,
                    'mp3_file': mp3_file
                }
                print(row_data)
                # await add_song_async(row_data)
            # await remove_song_async(song_name)
    except Exception as e:
        print(e)
        continue