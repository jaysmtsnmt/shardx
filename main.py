import os, sys
if os.name == "nt" and sys.version_info >= (3,8):
    os.add_dll_directory(os.getcwd())

import discid
import musicbrainzngs
import vlc 
from time import sleep
from colorama import Fore, Back, Style, init
init(autoreset=True)

import tkinter as tk
from PIL import Image, ImageTk
from tkinter import PhotoImage


steps = 42

class cdExceptions(Exception):
    pass

class cd:
    def __init__(self, directory):
        """_summary_
        Class for CD reader. The disc is read by the discid library, and queried to musicbrains to obtain album data. 
        
        Vars: 
            self.album_info (_dict_): Dictionary storing the album info. 
            self.tracks (_list_): Nested dictionary in a list, storing individual track information.
            self.current_track (_dict_): Stores information about current track played.

        Args:
            directory (_str_): Directory for CD player/reader
        """
        
        musicbrainzngs.set_useragent("CD Player", "0.2", "jaydsoh@gmail.com")
        self.directory = directory
        self.current_track = None
        disc = discid.read()
        try:
            result = musicbrainzngs.get_releases_by_discid(disc.id, includes=["artists", "recordings"]) #query to musicbrainzngs
            # print(result)
            disckey = list(result.keys())
            disckey = disckey[0] #get the type of return data, can be cdstubs or disc
            
            if disckey == "cdstub": #anonymous contributions
                album_info = {}
                album_info["title"] = result.get(disckey).get("title")
                album_info["artist"] = result.get(disckey).get("artist")
                album_info["length"] = result.get(disckey).get("track-count")
                album_info["date"] = None
                raw_tracks = result.get(disckey).get("track-list")
                
                tracks = []
                for i in range(0, len(raw_tracks)):
                    trackdata = {}
                    trackdata["title"] = raw_tracks[i].get("title")
                    trackdata["length"] = int(raw_tracks[i].get("length"))/1000 #stores in seconds
                    tracks.append(trackdata)
                    
                self.tracks = tracks
                self.album_info = album_info
    
            elif disckey == "disc": 
                album_info = {}

                album_info["title"] = result.get(disckey).get("release-list")[0].get("title")
                album_info["artist"] = result.get(disckey).get("release-list")[0].get("artist-credit")[0].get("artist").get("name")
                album_info["date"] = result.get(disckey).get("release-list")[0].get("date")
                raw_tracks = result.get(disckey).get("release-list")[0].get("medium-list")[0].get("track-list")
                album_info["length"] = len(raw_tracks)
                #print(album_info) # {'title': 'To Love Again: The Duets', 'artist': 'Chris Botti', 'date': '2005-10-18', 'length': 13}
                
                tracks = []
                for i in range(0, len(raw_tracks)):
                    trackdata = {}
                    trackdata["title"] = raw_tracks[i].get("recording").get("title")
                    trackdata["length"] = int(raw_tracks[i].get("recording").get("length"))/1000 #stores in seconds
                    #print(trackdata)
                    tracks.append(trackdata)
            
                # self.Player = vlc.MediaPlayer(directory)
                self.tracks = tracks
                self.album_info = album_info
                
            else:
                raise cdExceptions("musicbrainzngs query not recognisable!")
            
        except musicbrainzngs.ResponseError: #Album not found, just display as normal
            album_info = {}
            album_info["title"] = "N/a"
            album_info["artist"] = "N/a"
            
            count = 0
            paths = []
            for path in os.listdir(r"D:\\"):
                if os.path.isfile(os.path.join(r"D:\\", path)):
                    paths.append(path)
                    count += 1
            
            album_info["length"] = count
            album_info["date"] = None
            raw_tracks = paths
            
            tracks = []
            for i in range(0, len(raw_tracks)):
                trackdata = {}
                trackdata["title"] = raw_tracks[i].split(".cda")[0]
                trackdata["length"] = None
                tracks.append(trackdata)
                
            self.tracks = tracks
            self.album_info = album_info
            
    def standard_time(self, time): #time is passed as seconds, returned as m:0s (integer)
        """_summary_
        Standard function for formatting seconds into a readable format. 
        
        Args:
            time (_int_): seconds

        Returns::
        
            minutes (_str_): minutes
            seconds (_str_): seconds (with 0 or without 0)
        """
        
        minutes = int((time/60)//1)
        seconds = int(round(((time/60)%1)*60, 0))
        
        if seconds < 10:
            seconds = f"0{seconds}"
        
        return str(minutes), str(seconds)

    def play_callback(self, track_number=1):
        # self.Player.audio_set_track(track_number)
        # self.Player.play()
        self.Player = vlc.MediaPlayer(self.directory, f":cdda-track={track_number}")
        self.Player.play()
        
        self.current_track = self.tracks[int(track_number)-1]
        
        if track_number < 10:
            track_number = "0" + str(track_number)
        
        else:
            track_number = str(track_number)
        
        print(Fore.WHITE, f'\n{track_number} Currently Playing | {self.current_track.get("title")} by {self.album_info.get("artist")} |')

class UI:
    def __init__(self): 
        self.window = tk.Tk()
        self.window.minsize(width=500, height=600)
        self.window.title("ShardX")
        self.window.configure(background="black")

    def home_main(self):
        tk.Frame(self.window, width=500, height=100, bg="black").pack(side=tk.TOP)
        self.f_mid = tk.LabelFrame(self.window, text=" cd-rom ", width=300, height=400, bg="black", foreground="white")
        self.f_mid.pack(padx=50, side=tk.TOP)   
        self.f_mid.pack_propagate(False)
        tk.Frame(self.f_mid, width=80, height=40, bg="black").pack(side=tk.TOP)
        
        icon_size = 200
        image = Image.open(r"The CT Project\Modules\6.png").resize((icon_size+10,icon_size+10))
        image_tk = ImageTk.PhotoImage(image)
        f_icon = tk.Label(self.f_mid, image=image_tk, width=icon_size, height=icon_size, pady=60, padx=60)
        f_icon.image = image_tk
        f_icon.pack(anchor="center", side=tk.TOP)
        f_icon.pack_propagate(False)
        
    def home_controls(self):
        # frame_main = tk.Frame(self.window, bg="black", width=500, height=600)
        # frame_main.pack()
        # frame_main.pack_propagate(False)
        
        height, width = 9, 8
        
        f_controls = tk.Frame(self.f_mid, width=200, height=30, bg="black")
        f_controls.pack(anchor="center", side=tk.TOP)
        f_controls.propagate(False)
        
        b_rewind = tk.Button(f_controls, text="⏪", width=width, height=height, bg='gray50')
        b_play = tk.Button(f_controls, text="▶️", width=width, height=height, bg='gray50')
        b_skip = tk.Button(f_controls, text="⏩", width=width, height=height, bg='gray50')
        
        b_rewind.pack(anchor="center", side=tk.LEFT)  
        b_play.pack(anchor="center", side=tk.LEFT)
        b_skip.pack(anchor="center", side=tk.LEFT)
        
    def song_display(self):
        song = "Home | Norah Jones "
        
        song_screen = tk.Label(self.f_mid, text=song, width=28, height=1, bg="gray88", foreground="black", font=("Courier New Bold", 8))
        song_screen.pack(side=tk.TOP, pady=15)
        
# interface = UI()
# interface.home_main()
# interface.song_display()
# interface.home_controls()
# interface.window.mainloop()

def main_test():
    #initialise cd class
    dvd = cd("cdda:///D:/")

    #Print out full dvd menu and all its tracks
    print(Fore.WHITE + f"| Album Information | {dvd.album_info.get('title')} | {dvd.album_info.get('artist')} |")
    for i in range(0, len(dvd.tracks)):
        track = dvd.tracks[i]
        
        if track.get("length") == None:
            minutes, seconds = "00", "00"
            
        else:
            minutes, seconds = dvd.standard_time(track.get("length"))

        track_number = i + 1
        if track_number < 10:
            track_number = f"0{track_number}"
            
        else:
            track_number = str(track_number)
        
        print(f" {track_number} {track.get('title')} | {minutes}:{seconds}")
        
    print("")

    track_index = int(input("[PLAY] Select a Track: "))

    is_Playing = False
    interface = ""

    while True: 
        if is_Playing:
            minutes, seconds = dvd.standard_time(dvd.Player.get_time()/1000)

            if dvd.current_track.get("length") == None:
                end_minutes, end_seconds = dvd.standard_time(dvd.Player.get_length()/1000)
                
            else:    
                end_minutes, end_seconds = dvd.standard_time(dvd.current_track.get("length"))
                
            n_steps = int(round(dvd.Player.get_position()*steps, 0))
            
            progress_bar = n_steps*"=" + (steps-n_steps)*"-"
            
            if interface != f'''{minutes}:{seconds} |{progress_bar}| {end_minutes}:{end_seconds}''':
                interface = f'''{minutes}:{seconds} |{progress_bar}| {end_minutes}:{end_seconds}'''
            print(Fore.WHITE, interface, end='\r')
            
            if not dvd.Player.is_playing():
                is_Playing = False
            
        else: 
            if track_index <= int(dvd.album_info.get("length")): #continue playing the next song
                dvd.play_callback(track_index)
                sleep(3)
                is_Playing = True
                
                track_index += 1
                
            else:
                quit()
            
main_test()