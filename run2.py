from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkinter.messagebox as messagebox
from pathlib import Path
from PIL import Image, ImageTk
from itertools import count, cycle
import time
import pyaudio
import wave
import pygame
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
from scipy.io import wavfile
import matplotlib
matplotlib.use("Agg")


class ImageLabel(Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
            im = im.resize((25, 25))
        frames = []
 
        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
 
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
 
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()
 
    def unload(self):
        self.config(image=None)
        self.frames = None
 
    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # info = self._pa.get_host_api_info_by_index(0)
        # numdevices = info.get('deviceCount')
        # for i in range(0, numdevices):
        #     if (self._pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        #         print("Input Device id ", i, " - ", self._pa.get_device_info_by_host_api_device_index(0, i).get('name'))
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

class APP:

    def __init__(self, master):

        self.master = master

        Grid.rowconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 0, weight=1)

        self.frame_user = Frame(master)
        self.frame_recorder = Frame(master)


        self.user = USER(self.frame_user, self)
        self.recoder = RECODER(self.frame_recorder, self)

        self.frame_user.grid(row=0, column=0, sticky='nswe')
        self.frame_recorder.grid(row=0, column=0, sticky='nswe')

        self.frame_user.tkraise()
        

class USER:

    def __init__(self, master, controller):

        self.master = master
        self.controller = controller

        padx = 5
        pady = 5

        Grid.rowconfigure(master, 0, weight=2)
        Grid.rowconfigure(master, 1, weight=1)
        Grid.rowconfigure(master, 2, weight=2)
        Grid.rowconfigure(master, 3, weight=1)
        Grid.rowconfigure(master, 4, weight=2)
        Grid.rowconfigure(master, 5, weight=1)
        Grid.rowconfigure(master, 6, weight=2)
        Grid.rowconfigure(master, 7, weight=1)
        Grid.rowconfigure(master, 8, weight=1)
        Grid.columnconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 1, weight=8)

        fontStyle = tkFont.Font(family="Lucida Grande", size=20)
        master.option_add("*TCombobox*Listbox*Font", fontStyle)

        Label(master, text="姓名", font=fontStyle).grid(row=0, padx=padx, pady=pady, sticky='nswe')
        Label(master, text="Email", font=fontStyle).grid(row=2, padx=padx, pady=pady, sticky='nswe')
        Label(master, text="性別", font=fontStyle).grid(row=4, padx=padx, pady=pady, sticky='nswe')
        Label(master, text="年齡", font=fontStyle).grid(row=6, padx=padx, pady=pady, sticky='nswe')

        self.e1 = Entry(master, font=fontStyle)
        self.e2 = Entry(master, font=fontStyle)
        self.e3 = comboExample = ttk.Combobox(master, state="readonly", font=fontStyle, values=["男性", "女性","其他"])
        self.e4 = comboExample = ttk.Combobox(master, state="readonly", font=fontStyle, values=["10~20", "20~30","30~40", "40~50", "50~60", "60~70", "70~80", "80~90"])

        self.e1.grid(row=0, column=1, padx=padx, pady=pady, sticky='nswe')
        self.e2.grid(row=2, column=1, padx=padx, pady=pady, sticky='nswe')
        self.e3.grid(row=4, column=1, padx=padx, pady=pady, sticky='nsw')
        self.e4.grid(row=6, column=1, padx=padx, pady=pady, sticky='nsw')

        self.button_ok = Button(master, text="OK", font=fontStyle, command=self.click_ok)
        self.button_ok.grid(row=8, column=1, padx=padx, pady=pady, sticky='nse')

        self.error_name = Label(master, text="", foreground = 'red', font=fontStyle)
        self.error_email = Label(master, text="", foreground = 'red', font=fontStyle)
        self.error_gender = Label(master, text="", foreground = 'red', font=fontStyle)
        self.error_age = Label(master, text="", foreground = 'red', font=fontStyle)

        self.error_name.grid(row=1, column=1, padx=padx, pady=pady, sticky='nsw')
        self.error_email.grid(row=3, column=1, padx=padx, pady=pady, sticky='nsw')
        self.error_gender.grid(row=5, column=1, padx=padx, pady=pady, sticky='nsw')
        self.error_age.grid(row=7, column=1, padx=padx, pady=pady, sticky='nsw')

        self.fake_data()

    def fake_data(self):
        self.e1.insert(0, 'asd')
        self.e2.insert(0, 'asd@asd.asd')
        self.e3.current(0)
        self.e4.current(0)

    def click_ok(self):
        c1 = self.check_name()
        c2 = self.check_email()
        c3 = self.check_gender()
        c4 = self.check_age()

        if c1 and c2 and c3 and c4:
            print('ok')

            name = self.e1.get()
            email = self.e2.get()
            gender = self.e3.get()
            age = self.e4.get()

            gender2code = {'男性':'M', '女性':'F', '其他':'O'}
            age2code = {"10~20":'A', "20~30":'B',"30~40":'C', "40~50":'D', "50~60":'E', "60~70":'F', "70~80":'G', "80~90":'H'}

            self.controller.recoder.get_user_folder(name, email, gender2code[gender], age2code[age])
            self.controller.frame_recorder.tkraise()
        else:
            print('not ok')

    def check_name(self):
        name = self.e1.get()
        if name == '':
            self.error_name['text'] = '姓名不可空白'
            return False
        else:
            self.error_name['text'] = ''
            return True
            

    def check_email(self):
        import re

        email = self.e2.get()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_email['text'] = 'Email格式錯誤'
            return False
        else:
            self.error_email['text'] = ''
            return True
        

    def check_gender(self):
        gender = self.e3.get()
        if gender == '':
            self.error_gender['text'] = '性別不可空白'
            return False
        else:
            self.error_gender['text'] = ''
            return True

    def check_age(self):
        age = self.e4.get()
        if age == '':
            self.error_age['text'] = '年齡不可空白'
            return False
        else:
            self.error_age['text'] = ''
            return True
        
class RECODER:

    def __init__(self, master, controller):

        self.master = master
        self.controller = controller

        Grid.rowconfigure(master, 0, weight=8)
        Grid.rowconfigure(master, 1, weight=2)
        Grid.rowconfigure(master, 2, weight=1)
        Grid.columnconfigure(master, 0, weight=1)

        self.padx = 5
        self.pady = 5

        # frame_wavplot = Frame(master, background='red')
        # frame_command= Frame(master, background='blue')
        # frame_controlbar= Frame(master, background='yellow')
        self.frame_wavplot = Frame(master)
        self.frame_command= Frame(master)
        self.frame_controlbar= Frame(master)

        Grid.rowconfigure(self.frame_controlbar, 0, weight=2)
        Grid.rowconfigure(self.frame_controlbar, 1, weight=2)
        Grid.rowconfigure(self.frame_controlbar, 2, weight=2)

        self.frame_wavplot.grid(row=0, column=0, sticky='nswe')
        self.frame_command.grid(row=1, column=0, sticky='nswe')
        self.frame_controlbar.grid(row=2, column=0, sticky='nswe')

        self.fontStyle = tkFont.Font(family="Lucida Grande", size=16)
        self.fontStyle1 = tkFont.Font(family="Lucida Grande", size=25)

        self.command_list = None
        self.command_idx = 0
        self.recording = False

        self.label_wavplot = Label(self.frame_wavplot)
        self.label_wavplot.grid(sticky='nswe')
        self.wavplotw = None
        self.wavploth = None

        # Label(frame_wavplot, text="wavplot frame", font=self.fontStyle).grid(row=0, padx=self.padx, pady=self.pady, sticky='nswe')

        self.label_command = Label(self.frame_command, text="", font=self.fontStyle1)
        self.label_command.grid(row=2, padx=self.padx, pady=self.pady, sticky='nswe')
        

        self.btn_play = Button(self.frame_controlbar, text="播放提示音", font=self.fontStyle, command=self.play_wav)
        self.btn_prev = Button(self.frame_controlbar, text="上一個", font=self.fontStyle, command=self.prev_command)
        self.btn_next = Button(self.frame_controlbar, text="下一個", font=self.fontStyle, command=self.next_command)
        self.btn_record = Button(self.frame_controlbar, text="錄製音檔", font=self.fontStyle, command=self.record_wav)
        self.btn_play_record = Button(self.frame_controlbar, text="播放錄音", font=self.fontStyle, command=self.play_record_wav)
        self.recording_gif = ImageLabel(self.frame_controlbar)
        self.recording_gif.load('recording.gif')
        self.lbl_record_time = Label(self.frame_controlbar, text="錄製時間: {:02d}:{:02d}:{:02d}".format(0, 0, 0), font=self.fontStyle)
        self.lbl_command_percent = Label(self.frame_controlbar, text="目前/總數: {:04d} / {:04d}".format(0, 0), font=self.fontStyle)
        self.lbl_already_record = Label(self.frame_controlbar, foreground = 'black', text="指令 --- 錄音音檔 尚未存在".format(0, 0), font=self.fontStyle)
        self.lbl_micinfo = Label(self.frame_controlbar, foreground = 'green', text="錄音裝置: ---".format(0, 0), font=self.fontStyle)


        self.btn_play.grid(row=0, column=0, padx=self.padx, sticky='nswe')
        self.btn_prev.grid(row=0, column=1, padx=self.padx, sticky='nswe')
        self.btn_next.grid(row=0, column=2, padx=self.padx, sticky='nswe')
        self.btn_record.grid(row=0, column=3, padx=self.padx, sticky='nswe')
        self.btn_play_record.grid(row=0, column=4, padx=self.padx, sticky='nswe')
        self.recording_gif.grid(row=0, column=5, padx=self.padx, sticky='nswe')
        self.recording_gif.grid_forget()
        self.lbl_record_time.grid(row=0, column=6, padx=self.padx, sticky='nswe')
        self.lbl_command_percent.grid(row=0, column=7, padx=self.padx, sticky='nswe')
        self.lbl_already_record.grid(row=1, columnspan=7, padx=self.padx, pady=self.pady, sticky='w')
        self.lbl_micinfo.grid(row=2, columnspan=7, padx=self.padx, pady=self.pady, sticky='w')

        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        print('pyaudio info:', info)
        print('microphone info:', p.get_device_info_by_host_api_device_index(0, info['defaultInputDevice']).get('name'))
        self.lbl_micinfo['text'] = "錄音裝置: {}".format(p.get_device_info_by_host_api_device_index(0, info['defaultInputDevice']).get('name'))

        # Label(frame_controlbar, text="controlbar frame", font=self.fontStyle).grid(row=0, padx=padx, pady=pady, sticky='nswe')

    def get_user_folder(self, name, email, gender, age):
        print('user info:', name, email, gender, age)
        self.name = name
        self.email = email
        self.gender = gender
        self.age = age
        self.user_id = '_'.join([email.split('@')[0], gender, age])
        print(self.user_id)

        Path(self.user_id).mkdir(exist_ok=True, parents=True)
        with open(Path(self.user_id) / 'user_info.txt', 'w') as fw:
            fw.write('name:' + ' ' + self.name + '\n')
            fw.write('email:' + ' ' + self.email + '\n')
            fw.write('gender:' + ' ' + self.gender + '\n')
            fw.write('age:' + ' ' + self.age + '\n')

        self.init_menu(self.controller.master)

    def init_menu(self,master):   
        from functools import partial
        mbar = Menu(master)                      
        fmenu = Menu(mbar,tearoff=False)         
        mbar.add_cascade(label='指令集',menu=fmenu,font=self.fontStyle) 
        fmenu.add_command(label="指令集 1", command=partial(self.open_command_list, 1, '指令集 1'))
        # fmenu.add_command(label="指令集 2", command=partial(self.open_command_list, 2, '指令集 2'))
        # fmenu.add_command(label="指令集 3", command=partial(self.open_command_list, 3, '指令集 3'))
        # fmenu.add_command(label="指令集 4", command=partial(self.open_command_list, 4, '指令集 4'))
        # fmenu.add_command(label="指令集 5", command=partial(self.open_command_list, 5, '指令集 5'))
        fmenu.add_separator()
            
        master.config(menu=mbar)

    def open_command_list(self, number, comand_type):
        self.command_number = number
        self.command_idx = 0
        print('select command file:', number)
        if number == 0:
            command_file = 'commands.txt'
            messagebox.showinfo("OK", '讀取指令集ALL')
        else:
            command_file = 'commands_{}.txt'.format(number)
            messagebox.showinfo("OK", '讀取指令集{}'.format(comand_type))

        self.command_list = []
        with open(Path('command_pack2') / command_file, encoding="utf-8") as fp:
            for line in fp:
                command, command_idx, wav_file = line.strip().split('\t')
                self.command_list.append([command, command_idx, wav_file])

        print('load commands list count:', len(self.command_list))

        self.check_user_folder(self.user_id)
        self.init_wavplot_folder(self.user_id)
        self.set_now_command(self.command_idx)

    def check_user_folder(self, user_id):
        check_file = Path(user_id) / 'record_command.txt'
        self.record_command = {}
        if check_file.exists():
            with open(check_file) as fp:
                for line in fp:
                    command, command_idx, wav_file = line.strip().split('\t')
                    self.record_command[command] = [command, command_idx, wav_file]
        else:
            with open(check_file, 'w') as fw:
                pass

        print(len(self.record_command))

    def init_wavplot_folder(self, user_id):

        if self.wavplotw == None and self.wavploth == None:
            self.wavplotw = self.frame_wavplot.winfo_width()
            self.wavploth = self.frame_wavplot.winfo_height()

        self.wavplot_folder = Path(user_id) / 'wavplot'
        self.wavplot_folder.mkdir(exist_ok=True, parents=True)

        # import matplotlib.pyplot as plt
        # data = np.zeros(44100*3)
        # plt.plot(data)
        # # plt.axis('off')
        # plt.ylim(-0.5, 0.5)
        # plt.savefig(self.wavplot_folder / 'init_wavplot.png') 
        # # plt.clf()
        # plt.close()

        data = np.zeros(44100*3)
        sr = 44100
        times = np.arange(len(data))/float(sr)
        print("Sample rate: {} Hz".format(sr))
        import matplotlib.pyplot as plt
        plt.fill_between(times, data) 
        plt.xlim(times[0], times[-1])
        plt.xlabel('time (s)')
        plt.ylabel('amplitude')
        plt.savefig(self.wavplot_folder / 'init_wavplot.png') 
        plt.close()

        self.image = Image.open(self.wavplot_folder / 'init_wavplot.png')
        self.image = self.image.resize((self.wavplotw, self.wavploth))
        self.render_image = ImageTk.PhotoImage(self.image)

        self.label_wavplot.configure(image=self.render_image)


    def set_now_command(self, command_idx):

        if pygame.mixer.music.get_busy() == True:
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        if self.recording:  ## 如果上一個指令還沒停就按其他的，先停止錄音並儲存上一個再繼續
            self.btn_record['text'] = "錄製音檔"
            self.recording = False
            self.recfile2.stop_recording()
            self.recfile2.close()
            self.recording_gif.grid_forget()
            self.get_wav_plot(renew=True)
        
        self.label_command['text'] = self.command_list[command_idx][0]
        self.command_wav_file = self.command_list[command_idx][2]
        self.record_wav_file = Path(self.user_id) / "{}_{}-{}.wav".format(self.user_id, self.command_number, self.command_list[command_idx][1])
        self.record_wav_plot = Path(self.wavplot_folder) / "{}_{}-{}.png".format(self.user_id, self.command_number, self.command_list[command_idx][1])
        print('提示音檔', self.command_wav_file)
        print('儲存音檔', self.record_wav_file)
        print('-'*20)
        self.lbl_record_time['text'] = "錄製時間: {:02d}:{:02d}:{:02d}".format(0, 0, 0)
        self.lbl_command_percent['text'] = "目前/總數: {:04d} / {:04d}".format(self.command_idx+1, len(self.command_list))

        if self.record_wav_file.exists():
            self.lbl_already_record['foreground'] = 'black'
            self.lbl_already_record['text'] = "指令 {} 錄音音檔 儲存於 {}".format(self.command_list[command_idx][0], str(self.record_wav_file))
            
        else:
            self.lbl_already_record['foreground'] = 'red'
            self.lbl_already_record['text'] = "指令 {} 錄音音檔 尚未存在".format(self.command_list[command_idx][0], str(self.record_wav_file))

        # print(self.wavplotw)
        # print(self.wavploth)
        self.get_wav_plot()
    
    def get_wav_plot(self, renew=False):

        if self.record_wav_file.exists() == False:
            self.image = Image.open(self.wavplot_folder / 'init_wavplot.png')
            self.image = self.image.resize((self.wavplotw, self.wavploth))
            self.render_image = ImageTk.PhotoImage(self.image)

        else:
            if self.record_wav_plot.exists() == False or renew == True:
                print('renew:', renew)
                print('generate wav plot for record wav file:', self.record_wav_file)
                # data, sr = sf.read(self.record_wav_file)
                sr, data = wavfile.read(self.record_wav_file)
                times = np.arange(len(data))/float(sr)

                abs_data = np.power(data, 2)
                # print(abs_data)
                thresh_data = abs_data[np.where(abs_data > 500)]
                # print(thresh_data)
                if len(thresh_data) == 0:
                    messagebox.showinfo("OK", '音檔energy過小，請確認是否有錄音正確')
                else:
                    avg_amp = np.mean(thresh_data)
                    print('平均energy', avg_amp)
                    if avg_amp < 4000:
                        messagebox.showinfo("OK", '音檔energy過小，請確認是否有錄音正確')

                print('音檔長度', len(data) / sr)
                print("Sample rate: {} Hz".format(sr))
                import matplotlib.pyplot as plt
                plt.fill_between(times, data) 
                plt.xlim(times[0], times[-1])
                plt.xlabel('time (s)')
                plt.ylabel('amplitude')
                plt.savefig(self.record_wav_plot) 
                plt.close()
                # plt.plot(data)
                # # plt.axis('off')
                # plt.ylim(-0.5, 0.5)
                # plt.savefig(self.record_wav_plot) 
                # # plt.clf()
                # plt.close()

            self.image = Image.open(self.record_wav_plot)
            self.image = self.image.resize((self.wavplotw, self.wavploth))
            self.render_image = ImageTk.PhotoImage(self.image)
            # self.image.save(self.record_wav_plot.parent / (self.record_wav_plot.stem+'_1'+'.png'))

        self.label_wavplot.configure(image=self.render_image)
        ## https://stackoverflow.com/questions/3482081/how-to-update-the-image-of-a-tkinter-label-widget  看看下面這句有沒有用(prevent garbage collection的部分)
        # self.label_wavplot.image = self.render_image

    def play_wav(self):
        if self.command_list == None:
            messagebox.showinfo("OK", '請先選擇錄音指令集')
            return False

        pygame.mixer.music.load(self.command_wav_file)
        pygame.mixer.music.play(loops=0)

    def play_record_wav(self):
        if self.command_list == None:
            messagebox.showinfo("OK", '請先選擇錄音指令集')
            return False

        if self.record_wav_file.exists() == False:
            messagebox.showinfo("OK", '指令尚未進行錄音')
            return False
        pygame.mixer.music.load(str(self.record_wav_file))
        pygame.mixer.music.play(loops=0)

    def prev_command(self):
        if self.command_list == None:
            messagebox.showinfo("OK", '請先選擇錄音指令集')
            return False

        if self.command_idx != 0:
            self.command_idx -= 1
        self.set_now_command(self.command_idx)
        

    def next_command(self):
        if self.command_list == None:
            messagebox.showinfo("OK", '請先選擇錄音指令集')
            return False

        if self.command_idx != len(self.command_list)-1:
            self.command_idx += 1
        self.set_now_command(self.command_idx)

    def record_wav(self):
        if self.command_list == None:
            messagebox.showinfo("OK", '請先選擇錄音指令集')
            return False

        if self.recording:
            self.btn_record['text'] = "錄製音檔"
            self.recording = False
            self.recfile2.stop_recording()
            self.recfile2.close()
            self.recording_gif.grid_forget()
            self.get_wav_plot(renew=True)
            self.set_now_command(self.command_idx)
        else:
            pygame.mixer.music.unload()
            self.btn_record['text'] = "停止錄製"
            self.start_time = time.time()
            self.recording = True
            self.play_speak_wav = False
            self.get_time_elapsed()
            self.rec = Recorder(channels=1)
            self.recfile2 = self.rec.open(str(self.record_wav_file), 'wb')
            self.recfile2.start_recording()  
            self.recording_gif.grid(row=0, column=5, padx=self.padx, sticky='nswe')

    def get_time_elapsed(self):
        if self.recording == True:
            duration = time.time() - self.start_time
            minutes = int(duration/60)
            seconds = int(duration-minutes*60.0)
            hseconds = int((duration - minutes*60.0 - seconds) *100)
            # if seconds == 1 and self.play_speak_wav == False:
            #     self.play_speak_wav = True
            #     pygame.mixer.music.load('speak.wav')
            #     pygame.mixer.music.play(loops=0)
            self.lbl_record_time.config(text="{:02d}:{:02d}:{:02d}".format(minutes, seconds, hseconds))
            # self.after(10, self.get_time_elapsed)
            self.controller.master.after(10, self.get_time_elapsed)
        else:
            duration = time.time() - self.start_time
            minutes = int(duration/60)
            seconds = int(duration-minutes*60.0)
            hseconds = int((duration - minutes*60.0 - seconds) *100)
            self.lbl_record_time.config(text="{:02d}:{:02d}:{:02d}".format(minutes, seconds, hseconds))


        

if __name__=='__main__':
    root = Tk()
    root.title('指令錄音器')
    root.geometry('960x480+500+200')

    pygame.mixer.init()
    
    app = APP(root)

    root.mainloop()


    # pygame.mixer.init()
    # pygame.mixer.music.load('command_pack2\\00001.wav')
    # pygame.mixer.music.play(loops=0)
    