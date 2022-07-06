import tkinter as tk
import pytube as pt
from tkinter import *
from tkinter import filedialog, messagebox
from pytube import YouTube
import os, urllib.request, io
from PIL import ImageTk, Image
import datetime

def browse_button():
        # Allow user to select a directory and store it in global var
        # called folder_path
        global folder_path
        filename = tk.filedialog.askdirectory()
        folder_path.set(filename)

class youtubeDownloader(tk.Tk):
    def __init__(self):
        global folder_path, url, downloadOptionChoice, file_name, urlStatus
        tk.Tk.__init__(self)
        folder_path=StringVar()
        url=StringVar()
        urlStatus=StringVar(value='InValid')
        file_name=StringVar()
        downloadOptionChoice=IntVar(value=0)
        self.winfo_toplevel().title('Youtube Downloader')

        self.frame=None
        self.switch_frame(StartPage)

        quitFrame = tk.Frame().grid()
        tk.Button(master=quitFrame, text='Quit', command=self.destroy).grid(sticky=N+S+E+W, padx=5, pady=5)
        
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.frame is not None:
            self.frame.grid_forget()
        self.frame = new_frame
        self.frame.grid(row=0, column=0)

class StartPage(tk.Frame):
    def __init__(self, master):
        global folder_path, url
        tk.Frame.__init__(self,master)
        self.winfo_toplevel().title('Youtube Downloader')

        self.enterUrl_label = tk.Label(master=self,text='Enter Youtube URL')
        self.enterUrl_label.grid(row=0, column=0, padx=5, pady=5)
        self.enterUrl_entry = tk.Entry(master=self, textvariable=url)
        self.enterUrl_entry.grid(row=0, column=1, padx=5, pady=5)

        self.browse_button = tk.Button(master=self,text='Browse Folder', command=browse_button)
        self.browse_button.grid(row=1,column=0, sticky=N+S+E+W, padx=5, pady=5)
        self.folderPath_entry = tk.Entry(master=self, textvariable=folder_path)
        self.folderPath_entry.grid(row=1, column=1)

        self.checkUrl_button = tk.Button(master=self,text='Check Url', state=tk.DISABLED, command=lambda: [self.validUrl(), master.switch_frame(PreviewPage) if urlStatus.get() == 'Valid' else master.switch_frame(StartPage)])
        self.checkUrl_button.grid(row=0,column=3, sticky=N+S+E+W, padx=5, pady=5, rowspan=2)

        folder_path.trace_add('write', self.switchButtonState)
        folder_path.trace_add('write', self.validFolderPath)
        url.trace_add('write', self.switchButtonState)

    def validUrl(self, *args):
        try:
            yt = YouTube(url.get())
            urlStatus.set('Valid')
        except:
            print('bad url')

    def validFolderPath(self, *args):
        if not (os.path.isdir(folder_path.get())):
            self.folderPath_entry.config({"background":"#FFA0A0"})
        else:
            self.folderPath_entry.config({"background":"white"})
    
    def switchButtonState(self, *args):
        if (len(url.get())>0 and len(folder_path.get())>0) and (os.path.isdir(folder_path.get())):
            self.checkUrl_button['state']=tk.NORMAL
        else:
            self.checkUrl_button['state']=tk.DISABLED

class PreviewPage(tk.Frame):
    def __init__(self,master):
        global folder_path, url
        tk.Frame.__init__(self,master)
        self.winfo_toplevel().title('Preview Download')
        
        #gather youtube information and thumbnail
        yt = YouTube(url.get())
        urlRequest = urllib.request.urlopen(yt.thumbnail_url)
        raw_data = urlRequest.read()
        urlRequest.close()
        im = Image.open(io.BytesIO(raw_data)).resize((256, 144))
        self.displayImage = ImageTk.PhotoImage(im)

        if len(file_name.get()) == 0:
            file_name.set(yt.streams.get_highest_resolution().default_filename)

        #title frame
        title_frame = tk.Frame(master=self,)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=5, pady=5)
        tk.Label(master=title_frame, text='Location: ', anchor=E).grid(row=1, column=0, sticky=E)
        tk.Label(master=title_frame, textvariable=folder_path).grid(row=1, column=1)
        tk.Label(master=title_frame, text='File Name: ', anchor=E).grid(row=2, column=0, sticky=E)
        tk.Entry(master=title_frame, textvariable=file_name).grid(row=2, column=1, sticky=N+S+E+W)
        
        if not (os.path.isdir(folder_path.get())):
            messagebox.showwarning('Warning', 'Directory Does Not Exist')
            master.switch_frame(StartPage)
        if (os.path.isfile(os.path.join(folder_path.get(), file_name.get()))):
            messagebox.showwarning('Warning', 'File Already Exists, Please rename or no file will be downloaded')

        #thumbnail frame
        thumbnail_frame = tk.Frame(master=self)
        thumbnail_frame.grid(row=1, column=0, sticky=N+S+E+W, padx=5, pady=5)
        self.thumbnail_label = tk.Label(master=thumbnail_frame, text='thumbnail', image=self.displayImage).grid()       
        
        #youtube details frme
        yt_frame = tk.Frame(master=self)
        yt_frame.grid(row=1, column=1, sticky=N+S+E+W, padx=5, pady=5)
        tk.Label(master=yt_frame, text='Title: ').grid(row=0, column=0, sticky='e', padx=5)
        tk.Label(master=yt_frame, text=yt.title, justify=tk.LEFT).grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(master=yt_frame, text='Views: ').grid(row=1, column=0, sticky='e', padx=5)
        tk.Label(master=yt_frame, text="{:,}".format(yt.views), justify=tk.LEFT).grid(row=1,column=1, sticky='w', padx=5)
        tk.Label(master=yt_frame, text='Length: ').grid(row=2, column=0, sticky='e', padx=5)
        tk.Label(master=yt_frame, text=datetime.timedelta(seconds=yt.length), justify=tk.LEFT).grid(row=2, column=1, sticky='w', padx=5)

        #download
        downloadOption_button = tk.Button(master=self, text='Download Options', command=lambda: master.switch_frame(DowbloadOpetionsPage) if not os.path.isfile(os.path.join(folder_path.get(), file_name.get())) else messagebox.showwarning('Error', 'File name already exists'))
        downloadOption_button.grid(row=2, column=1, sticky=N+S+E+W, padx=5)

        #back button to go back to startpage
        tk.Button(master=self, text='Back', command=lambda: master.switch_frame(StartPage)).grid(row=2, column=0, sticky=N+S+E+W, padx=5)

class DowbloadOpetionsPage(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.winfo_toplevel().title('Download Options')

        yt = YouTube(url.get())
        tk.Label(master=self, text='Download Options').grid(row=0, column=0, padx=5)

        fullChoice = Radiobutton(master=self, text='Video and Audio', variable=downloadOptionChoice, value=1)
        fullChoice.grid(row=2, column=0, sticky='w', padx=5)
        audioOnlyChoice = Radiobutton(master=self, text='Audio Only', variable=downloadOptionChoice, value=2)
        audioOnlyChoice.grid(row=3, column=0, sticky='w', padx=5)
        #videoOnlyChoice = Radiobutton(master=self, text='Video Only', variable=downloadOptionChoice, value=3)
        #videoOnlyChoice.grid(row=4, column=0, sticky='w', padx=5)

        self.download_button = tk.Button(master=self, text='Download', state=DISABLED, command=lambda: master.switch_frame(DownloadingStatus))
        self.download_button.grid(row=4, column=0, sticky=N+S+E+W, padx=5)

        tk.Button(master=self, text='Back', command=lambda: master.switch_frame(PreviewPage)).grid(row=5, column=0, sticky=N+S+E+W, padx=5)
        

        downloadOptionChoice.trace_variable("w",self.switchButtonState)

    def switchButtonState(self, *args):
        if (downloadOptionChoice.get()>0):
            self.download_button['state']=tk.NORMAL
        else:
            self.download_button['state']=tk.DISABLED

class DownloadingStatus(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.winfo_toplevel().title('Downloading')
        tk.Label(master=self, text='Downloaded').grid(row=0, column=0)

        yt = YouTube(url.get())
        if (downloadOptionChoice.get() == 1):
            stream = yt.streams.get_highest_resolution()
        if (downloadOptionChoice.get() == 2):
            stream = yt.streams.get_audio_only()        

        stream.download(output_path=folder_path.get(), filename=file_name.get())

        tk.Button(master=self, text='Another?', command=lambda: [url.set(''), master.switch_frame(StartPage)]).grid(row=1, column=0, sticky=N+S+E+W, padx=5)

if __name__ == '__main__':
    app=youtubeDownloader()
    app.mainloop()
    

#tracking difference