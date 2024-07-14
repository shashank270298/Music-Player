from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import Player
import random
import sys
import threading
import time
from pygame import mixer
from cx_Oracle import DatabaseError
from MyExceptions import *


class View:
    def __init__(self,root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x500")
        self.root.config(bg="silver")

        self.LabelPhoto = PhotoImage(file="F:/MY_PROJECTS/Music_Player/images/MusicPlayer.gif")
        self.icon = PhotoImage(file="F:/MY_PROJECTS/Music_Player/images/PiMusicPlayer.gif")
        self.root.iconphoto(self.root,self.icon)

        self.flexLabel = Label(self.root,image=self.LabelPhoto,relief="raised",borderwidth=3)
        self.playSongLabel = Label(self.root,bg="Silver",font="Forte")
        self.PlayButton = Button(self.root,text="Play",bg="Orange")
        self.PauseUnpauseButton = Button(self.root,text="Pause/Unpause",bg="Orange")
        self.StopButton = Button(self.root,text="Stop",bg="Orange")
        self.PreviousSong = Button(self.root,text="Previous Song",bg="Orange")
        self.AddSongButton = Button(self.root,text="Add Song",bg="Orange")
        self.RemoveSong = Button(self.root,text="Remove Song",bg="Orange")
        self.startSongTime = Label(self.root,text="00:00")
        self.SongProgress = ttk.Progressbar(self.root)
        self.endSongTime = Label(self.root,text="00:00")
        self.SongList = Listbox(self.root,font="Forte")
        self.VolumeControl = Scale(self.root,orient="horizontal")
        self.VolumeControl.set(50)
        self.LoadSongFromFavourite = Button(self.root,text="Load Favourites",bg="Orange")
        self.AddFavourite = Button(self.root,text="Add favourite",bg="Orange")
        self.RemoveFavourite = Button(self.root,text="Remove favourite",bg="Orange")

        self.flexLabel.grid(row=0, column=0, columnspan=2, rowspan=4)
        self.playSongLabel.grid(row=0,column=2,columnspan=6,sticky=E+W+S+N)
        self.PlayButton.grid(row=2,column=3,sticky=E+W+S+N)
        self.PauseUnpauseButton.grid(row=2,column=4,sticky=E+W+S+N)
        self.StopButton.grid(row=2,column=5,sticky=E+W+S+N)
        self.PreviousSong.grid(row=3,column=3,sticky=E+W+N+S)
        self.AddSongButton.grid(row=3,column=4,sticky=E+W+S+N)
        self.RemoveSong.grid(row=3,column=5,sticky=E+W+S+N)
        self.startSongTime.grid(row=4,column=0,sticky=E)
        self.SongProgress.grid(row=4, column=1,rowspan=1,columnspan=4, sticky=E + W)
        self.endSongTime.grid(row=4,column=5,sticky=W)
        self.SongList.grid(row=5,column=0, rowspan=3,columnspan=6,sticky=E+W)
        self.VolumeControl.grid(row=8,column=0,columnspan=3,sticky=E+W)
        self.LoadSongFromFavourite.grid(row=8,column=3,sticky=E+W+N+S)
        self.AddFavourite.grid(row=8,column=4,sticky=E+W+N+S)
        self.RemoveFavourite.grid(row=8,column=5,sticky=E+W+N+S)

        self.setup_player()

    def setup_player(self):
        try:
            self.my_player = Player.Player()
            if self.my_player.get_db_status():
                messagebox.showinfo("Success","Successfully connected to Database.")
                self.LoadSongFromFavourite.config(command=self.load_song_from_favourite)
                self.AddFavourite.config(command=self.add_song_to_favourite)
                self.RemoveFavourite.config(command=self.remove_song_from_favourite)
            else:
                raise Exception("Favourites can't be Save or load.")

        except Exception as ex:
            messagebox.showerror("Error",ex)
            self.LoadSongFromFavourite.config(state="disabled")
            self.RemoveFavourite.config(state="disabled")
            self.AddFavourite.config(state="disabled")

        self.VolumeControl.config(from_=0,to=100,command=self.change_volume)
        self.AddSongButton.config(command=self.add_song)
        self.RemoveSong.config(command=self.remove_song)
        self.PlayButton.config(command=self.play_song)
        self.StopButton.config(command=self.stop_song)
        self.PauseUnpauseButton.config(command=self.pause_song)
        self.SongList.bind("<Double-1>",self.list_double_click)
        self.root.protocol("WM_DELETE_WINDOW",self.close_window)
        self.PreviousSong.config(command=self.load_previous_song)
        self.isPaused = False
        self.isPlaying = False
        self.my_thread = None
        self.isThreadRunning = False
        self.stopThread = False

    def change_volume(self,val):
        volume_level = float(val)/100
        self.my_player.set_volume(volume_level)

    def add_song(self):
        song_name = self.my_player.add_song()
        if song_name is None:
            return
        self.SongList.insert(END,song_name)
        rcolor = lambda :random.randint(0,255)
        red = hex(rcolor())
        green = hex(rcolor())
        blue = hex(rcolor())
        red = red[2:]
        green = green[2:]
        blue = blue[2:]

        if len(red) == 1:
            red = '0'+red
        if len(green) == 1:
            green = '0'+green
        if len(blue) == 1:
            blue = '0'+blue

        mycolor = '#'+red+green+blue

        self.SongList.config(fg=mycolor)

    def remove_song(self):
        self.rem_song_index_tuple = self.SongList.curselection()
        try:
            if len(self.rem_song_index_tuple) == 0:
                raise NoSongSelectedError("Please select a song.")
            song_name = self.SongList.get(self.rem_song_index_tuple[0])
            self.SongList.delete(self.rem_song_index_tuple[0])
            self.my_player.remove_song(song_name)
            self.my_player.stop_song()

        except (NoSongSelectedError) as ex1:
            messagebox.showerror("Error", ex1)

    def show_song_details(self):
        self.song_length = int(self.my_player.get_song_length(self.song_name))
        min,sec = divmod(self.song_length,60)
        self.endSongTime.config(text=str(min)+":"+str(sec))
        self.startSongTime.config(text="00:00")
        ext_index = self.song_name.rfind(".")
        strng = self.song_name[0:ext_index]
        if len(strng)>14:
            strng = strng[0:14]+"..."
        self.playSongLabel.config(text=strng)

    def play_song(self):
        if self.isThreadRunning==True:
            self.my_player.stop_song()
            self.isPlaying=False
            time.sleep(1)
        self.sel_song_index_tuple = self.SongList.curselection()
        try:
            if len(self.sel_song_index_tuple)==0:
                raise NoSongSelectedError("Please select a song.")
            self.song_name=self.SongList.get(self.sel_song_index_tuple[0])
            self.show_song_details()
            self.my_player.play_song()
            self.SongProgress.config(length=self.song_length)
            self.SongProgress.config(maximum=self.song_length)
            self.setup_thread()
        except (NoSongSelectedError) as ex1:
            messagebox.showerror("Error",ex1)

    def stop_song(self):
        if self.isThreadRunning==True:
            self.my_player.stop_song()
            self.stopThread=True
            self.isThreadRunning=False
            self.isPlaying=False
            time.sleep(1)

    def pause_song(self):
        if self.isPlaying:
            if self.isPaused==False:
                self.my_player.pause_song()
                self.isPaused=True
            else:
                self.my_player.unpause_song()
                self.isPaused=False

    def load_previous_song(self):
        try:
            if hasattr(self,"sel_song_index_tuple")==False:
                raise  NoSongSelectedError("Please select a song.")
            self.prev_song_index=self.sel_song_index_tuple[0]-1
            if self.prev_song_index==-1:
                self.prev_song_index=self.SongList.size()-1
            self.SongList.select_clear(0,END)
            self.SongList.selection_set(self.prev_song_index)
            self.play_song()
        except (NoSongSelectedError) as ex1:
            messagebox.showerror("Error",ex1)

    def list_double_click(self,e):
        if self.isThreadRunning==True:
            self.stopThread=True
        self.play_song()

    def load_song_from_favourite(self):
        try:
            load_result=self.my_player.load_songs_from_favourites()
            result=load_result[0]
            if result.find("No songs present")!=-1:
                messagebox.showinfo("Favourites Empty","No songs in favourites")
                return
            self.SongList.delete(0,END)
            song_dict=load_result[1]
            for song_name in song_dict:
                self.SongList.insert(END,song_name)
            rcolor = lambda: random.randint(0, 255)
            red = hex(rcolor())
            green = hex(rcolor())
            blue = hex(rcolor())
            red = red[2:]
            green = green[2:]
            blue = blue[2:]

            if len(red) == 1:
                red = '0' + red
            if len(green) == 1:
                green = '0' + green
            if len(blue) == 1:
                blue = '0' + blue

            mycolor = '#' + red + green + blue

            self.SongList.config(fg=mycolor)
            messagebox.showinfo("Success", "Favourites loaded successfully")
        except(DatabaseError) as ex2:
            messagebox.showerror("Error", "Song cannot be added due to error in DB connection")


    def add_song_to_favourite(self):
        fav_song_index_tuple=self.SongList.curselection()
        try:
            if len(fav_song_index_tuple)==0:
                raise NoSongSelectedError("Please select song to add")
            song_name = self.SongList.get(fav_song_index_tuple[0])
            result = self.my_player.add_song_to_favourites(song_name)
            messagebox.showinfo("Success",result)
        except(NoSongSelectedError) as ex1:
            messagebox.showerror("Error",ex1)
        except(DatabaseError) as ex2:
            messagebox.showerror("Error","Song cannot be added due to error in DB connection")

    def remove_song_from_favourite(self):
        remove_song_index_tuple=self.SongList.curselection()
        try:
            if len(remove_song_index_tuple)==0:
                raise NoSongSelectedError("Please select song to remove.")
            song_name = self.SongList.get(remove_song_index_tuple[0])
            result = self.my_player.remove_songs_from_favourites(song_name)
            if result.find("deleted")!=-1:
                messagebox.showinfo("Removed","Song removed from favourites.")
            else:
                messagebox.showerror("Error","Song not present in favourites.")
        except(NoSongSelectedError) as ex1:
            messagebox.showerror("Error", ex1)
        except(DatabaseError) as ex2:
            messagebox.showerror("Error", "Song cannot be added due to error in DB connection")


    def setup_thread(self):
        self.my_thread=threading.Thread(target=self.show_timer, args=(self.song_length,))
        self.isPlaying = True
        self.isThreadRunning=True
        self.my_thread.start()


    def show_timer(self,total_sec):
        curr_sec = 1
        self.SongProgress.stop()
        while curr_sec<=total_sec:
            if self.isPaused==True:
                continue
            else:
                min,sec = divmod(curr_sec,60)
                self.startSongTime.config(text=str(min)+":"+str(sec))
                time.sleep(1)
                curr_sec+=1
                self.SongProgress.step()
                if self.stopThread==True:
                    break
        print("Thread Terminated")
        if self.stopThread==False:
            self.load_next_song()
        else:
            self.stopThread=False

    def load_next_song(self):
        self.next_song_index = self.sel_song_index_tuple[0]+1
        if self.next_song_index==self.my_player.get_song_count():
            self.next_song_index=0
        self.SongList.select_clear(0,END)
        self.SongList.selection_set(self.next_song_index)
        self.play_song()

    def close_window(self):
        ans = messagebox.askyesno("Close Music Player","Do you want to exit ?")
        if ans:
            self.stopThread=True
            self.my_player.close_player()
            self.root.destroy()


playerWindow = Tk()
viewPlayer = View(playerWindow)
playerWindow.mainloop()
