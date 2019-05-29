# Vagalume Lyrics Scraper

A simple scraper to get lyrics from "vagalume.com.br"

## How to use:

### There are 4 functions:
- **get_artists_list(style)**
  - Pass a string with the name of the style/genre of music you want to get the full list of artists.
  - Returns a dictionary containing artist's name as key and the respective link as item.
    
- **get_music_list(style or artists)**
  - Pass a style (this eliminate the necessity of calling "get_artists_list()") or a dictionary in the same format as the dict returned from "get_artists_list()"
  - Returns a dictionary containing artist's name as key and a music dictionary as item. The music dictinary is similar as the artists         dict, except the key is the title of the song and the item is the respective link.
    
- **get_lyrics(music_dict, return_list=False, continue_run=None)**
  - Main function. Downloads lyrics from Vagalume in the format "Run->Artist->Music.txt".
    'music_dict' must be a dictionary in the format of the returned dict from "get_music_list()"
  - Beware that some artists don't have registered      lyrics. 'return_list' return a list with the lyrics as items, otherwise returns         None. 'continue_run' allows to continue a previous run      (very useful for long requests...)

- **load_lyrics(lyrics_dir)**
  - Load a previous run.
  

