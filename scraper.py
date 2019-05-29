from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep, time
import os
from tqdm import tqdm
import pickle

def get_artists_list(style):
    if os.path.isfile(f'{style}.pickle'):
        pickle_in = open(f"{style}.pickle","rb")
        artists = pickle.load(pickle_in)
        return artists
    else:
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get(f'https://www.vagalume.com.br/browse/style/{style}.html')
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        artists = {}
        for col in soup.find_all('ul', class_='namesColumn'):
            for artist_tag in col.find_all('a'):
                artist_name = artist_tag.text.upper()
                artist_link = artist_tag.get('href')
                artists[artist_name] = artist_link
        pickle_out = open(f"{style}.pickle","wb")
        pickle.dump(artists, pickle_out)
        pickle_out.close()
        return artists

def get_music_list(style=None,artists=None):
    if artists is None and isinstance(style, str):
        artists_dict = get_artists_list(style)
        file_name=f"{style}_musiclist.pickle"
    elif isinstance(artists, dict) and style is None:
        artists_dict = artists
        file_name='custom_artists_list.pickle'
    elif not isinstance(artists, dict) and style is None and not artists is None:
        raise TypeError(f'artist argument must be a dictionary, but is {type(artists)}')
    elif artists is None  and not isinstance(style, str) and not style is None:
        raise TypeError(f'style argument must be a string, but is {type(artists)}')
    elif artists is None and style is None:
        raise NameError('no arguments were passed. Please pass "style" or "artists"')
    else:
        raise NameError('both arguments were passed. Please pass "style" or "artists"')
    
    if os.path.isfile(file_name):
        print('Music dict found! Loading existing dict...')
        pickle_in = open(file_name,"rb")
        full_musics_dict = pickle.load(pickle_in)
        return full_musics_dict
    else:
        print('Music dict not found! Starting scraping...')
        full_musics_dict = {}
        driver = webdriver.Chrome('chromedriver.exe')
        for artist in tqdm(artists_dict):
            driver.get(f'https://www.vagalume.com.br{artists_dict[artist]}')
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            try:
                main_list = soup.body.find('div', id='pushStateView').find('div', id='artBody').find('div', id='body').find('div', class_='artistWrapper col1').find('div', class_='letrasWrapper col1-2').find('div', class_='topLetrasWrapper').find('ol', id='alfabetMusicList')
            except:
                print(f' ### Artist {artist} do not have any registered lyrics. Going to the next...')
                continue

            music_dict = {}
            for music in main_list.find_all('li'):
                try:
                    info_div = music.find('div', class_='flexSpcBet').find('div', class_='lineColLeft').find('a')
                    music_name = info_div.text.upper()
                    music_link = info_div.get('href')
                    music_dict[music_name] = music_link
                except:
                    continue
            full_musics_dict[artist] = music_dict
            sleep(1)
        pickle_out = open(file_name,"wb")
        pickle.dump(full_musics_dict, pickle_out)
        pickle_out.close()
        driver.dispose()
        return full_musics_dict

def load_lyrics(lyrics_dir):
    print('Loading lyrics in list...')
    lyrics_list = []
    for artist in tqdm(os.listdir(lyrics_dir)):
        for music in os.listdir(os.path.join(lyrics_dir, artist)):
            music_path = os.path.join(lyrics_dir, artist, music)
            with open(music_path,'r') as txt_file:
                lyrics_list.append(txt_file.read())
    return lyrics_list


def get_lyrics(music_dict, return_list=False, continue_run=None):
    if continue_run is None:
        run_name = f'lyric_data-{str(time())[:10]}'
        os.mkdir(run_name)
        for artist in music_dict:
            os.mkdir(os.path.join(run_name,artist))
    elif isinstance(continue_run, str):
        run_name = continue_run
    else:
        raise TypeError('continue_run must be a string')
    driver = webdriver.Chrome('chromedriver.exe')
    for artist in os.listdir(run_name):
        print(f'Downloading lyrics from {artist}...')
        artist_music_list = music_dict.get(artist)
        for music in tqdm(artist_music_list):
            blocked_char=['?', '/', '"', '|', '<', '>', ':','*']
            music_corr = music
            for bl in blocked_char:
                if bl in music and music==music_corr:
                    music_corr = music.replace(bl,'')
                elif bl in music and music!=music_corr:
                    music_corr = music_corr.replace(bl,'')
            file_name = f'{music_corr}.txt'
            if os.path.isfile(os.path.join(run_name, artist, file_name)):
                continue
            else:
                lyrics = ''
                driver.get(f'https://www.vagalume.com.br{artist_music_list.get(music)}')
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                try:
                    main_list = soup.body.find('div', id='pushStateView').find('div', id='artBody').find('div', id='body').find('div', class_='col1').find('div',id='lyricContent').find('div', class_='col1-2-1').find('div', id='lyrics')
                except:
                    print(f'@%#$!! lets check the link...{artist_music_list.get(music)}')
                    exit()
                for script in soup(["script", "style"]):
                    script.extract()
                raw_text = ''
                for elem in main_list.recursiveChildGenerator():
                    if isinstance(elem, str):
                        raw_text += elem.strip()
                    elif elem.name == 'br':
                        raw_text += '\n'
                lyrics = raw_text
                explicit__warn = 'Confirmação de Idade Esta letra possui restrição de idade , você deve ter mais que 18 anos para acessá-la. Sou maior de 18 anos'
                if lyrics[:-len(explicit__warn)] == explicit__warn: 
                    lyrics = lyrics[:-len(explicit__warn)]
                with open(os.path.join(run_name, artist, file_name), 'w') as lyrics_out:
                    lyrics_out.write(lyrics)
                print()
                sleep(0.2)
    print('Lyrics Downloaded!')
    if return_lyrics_list:
        return load_lyrics(run_game)
    else:
        return None
    
        
'''
Example using dict:

p_file = open('example_dict.pickle',"rb")
br_rappers = pickle.load(p_file)
p_file.close()
musics = get_music_list(artists=br_rappers)
lyrics = get_lyrics(musics)

Example using style:

SEARCHED_STYLE = 'jazz'
musics = get_music_list(style=SEARCHED_STYLE)
lyrics = get_lyrics(musics)
'''
