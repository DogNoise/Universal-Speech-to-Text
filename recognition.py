# -*- coding: UTF-8 -*-    
'''
---IMPORT---
numpy - used for volume calculations
time - only used time.sleep function
speech_recognition - used for speech recognition
threading - used for thread managment
pydub - used for splitting audio file into chunks
io - used to store chunks in RAM memory
'''
import numpy as np
import time
import speech_recognition as sr
import threading
import pydub
from pydub.silence import detect_silence
import pydub.effects as py_eff
import io
import pyaudio
DEB = True  # Should print debugging info

'''
print_green, print_red, print_grey, print_yellow are used only for debugging 
'''


def print_green(string):
    print('\x1b[1;30;42m' + str(string) + '\x1b[0m')


def print_red(string):
    print('\x1b[1;30;41m' + str(string) + '\x1b[0m')


def print_grey(string):
    print('\x1b[0;30;47m' + str(string) + '\x1b[0m')


def PrintYellow(string):
    print('\x1b[6;30;43m' + str(string) + '\x1b[0m')


# class used to do transccription
class RecognizeVoice():
    def __init__(self):
        self.r = sr.Recognizer()

        # set default microphone
        self.m = sr.Microphone()
        self.p = self.m.get_pyaudio().PyAudio()  # store pyaudio library
        self.audio_level_run, self.file_recognition_run = True, True  # volume thread and file recognition status
        self.audio_level = [0, 0]
        self.transcription_array = []
        self.numer_of_chunks = -1  # def number of chunks
        self.transcription_lang = None

    def set_audio_noise_floor(self):
        '''
        Function used to set noise floor of microphone
        :return:
        '''
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

    def get_list_of_avaliable_microphones(self):
        '''
        :return: returns array of names of avaliable microphones
        '''

        # get data about microphones
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        names_arr = []
        index_arr=[]

        # for every micophone
        for i in range(0, numdevices):
            # if number of chunnels is >0 - means that microphone is avaliable
            all_mics=self.p.get_device_info_by_host_api_device_index(0, i)
            if (all_mics.get('maxInputChannels')) > 0:
                names_arr.append(all_mics.get('name'))
                index_arr.append(all_mics.get('index'))
                DEB and print_grey(str(self.p.get_device_info_by_host_api_device_index(0, i)))
        return [names_arr,index_arr]

    def callback(self, recognizer, audio, pass_ID=None):
        '''
        Function used to send request to voice recognition API
        :param recognizer: speech_recognition recognizer object
        :param audio: audio that needs processing
        :param pass_ID: pass additional info to return
        :return: return is a stored in self.transcriptionArr
        '''

        assert str(
            type(recognizer)) == "<class 'speech_recognition.Recognizer'>", "callback didn't get proper recognizer"
        assert str(type(audio)) == "<class 'speech_recognition.AudioData'>", "callback didn't get proper audio"

        try:
            if self.transcription_lang == None:
                # set recognizer
                output = recognizer.recognize_google(audio, show_all=True)
                # print debbinging info
                DEB and PrintYellow("callback - No language selected - EN")
            else:
                # set recognizer
                output = recognizer.recognize_google(audio, show_all=True, language=str(self.transcription_lang))
                # print debbinging info
                DEB and PrintYellow("callback - Language selected {}".format(self.transcription_lang))

            # checks if output really exists. It can be len=0 when no connection, or when error occur
            if len(output) > 0:
                output_array = []

                # for every transcription avaliable
                for index, result in enumerate(output["alternative"]):
                    if index == 0:
                        # first transcription (main) also has a confidence parameter
                        output_array.append([result["transcript"], result["confidence"]])
                    else:
                        output_array.append([result["transcript"]])
                # append successful transcription
                self.transcription_array.append(output_array if pass_ID == None else [output_array, pass_ID])
            else:
                # append -1 - no transcription
                self.transcription_array.append(-1 if pass_ID == None else [-1, pass_ID])

        except sr.UnknownValueError:
            # when couldn't recognize anything
            print_red("Couldn't recognize anything")
        except sr.RequestError as e:
            # print when other erorr occurs
            print_red("Other recognizer error -> {}".format(e))
        except Exception as e:
            print_red("Other error -> {}".format(e))

    def process_file_chunk(self, chunk, chunk_index):
        '''
        Function used to process audio chunk
        :param chunk: audio chunk
        :param chunk_index: index of chunk
                :param langCode: optional language argument
        '''

        # save chunk chunk into RAM as BytesIO
        chunk = py_eff.normalize(chunk)
        audio_chunk = io.BytesIO()
        audio_chunk = chunk.export(audio_chunk, format='wav')
        audio_chunk.seek(0)

        # chunk processing thread
        def start_chunk_thread(self, audio_chunk):
            if self.file_recognition_run:  # if should work
                with sr.AudioFile(audio_chunk) as source:
                    self.audio = self.r.record(source)
                self.callback(self.r, self.audio, pass_ID=chunk_index)

        # start chunk processing thread
        chunk_thread = threading.Thread(target=start_chunk_thread, args=(self, audio_chunk))
        chunk_thread.start()

    def start_file_voice_recognition(self, file_path, lang_code=None):
        '''
        Function that is used to start voice recognition for WAV files only
        self.FileRecognitionRun is used to stop threads - if False it will stop working
        :param file_path: path to WAV file
        :param lang_code: optional language argument
        :return:
        '''

        DEB and PrintYellow("Path of selected file -> ".format(file_path))

        assert type(file_path) == str, "FilePath should be a string, but it's {}, filePath:{}".format(type(file_path),
                                                                                                      file_path)

        if lang_code != None:
            self.transcription_lang = lang_code

        self.numer_of_chunks = -1  # number of Chunks
        self.transcription_array = []  # clear transcription array
        self.file_recognition_run = True  # set thread flag to true

        max_chunk_lenght = 30000  # maximum chunk lenght in ms
        min_chunk_lenght = 15000  # minumum chunk lenght in ms
        try:
            audio = pydub.AudioSegment.from_file(file_path, "wav")  # Import audio as pydub audio obj
            audio = audio.set_channels(1)  # convert audio to mono (use first channel)
        except Exception as e:
            print_red("Unexpected error occurs while importing wav file as pydub audio -> {}".format(e))

        audio = py_eff.normalize(audio)  # normalize audio
        audio_len = len(audio)  # lenght of audio in ms
        chunk_index = 0  # stores index of chunk

        assert "wav" == file_path.split(".")[-1].lower(), "File extension is not WAV"  # checkes if file is WAV
        assert audio_len > 0, "Lenght of audio is 0"

        min_silence_len = 100  # start value of minimum silence lenght
        silence_thresh = -20  # start value of silence threshold
        min_silence_len_step = -10  # correction of minimum silnece lenght if start value didn't give correct results
        silence_thresh_step = -3  # correction of silence threshold if start value didn't give correct results

        # if audio is long enough to split it into chunks and as long as action is not canceled
        while audio_len > max_chunk_lenght and self.file_recognition_run:
            # while there is still chunk to make

            # detect best slice point for this chunk
            final_slice_point = None
            temp_min_silence_len = min_silence_len
            temp_silence_thresh = silence_thresh
            while final_slice_point == None:

                # detect silence within max_chunk_lenght
                silence_time_stamps_arr = detect_silence(audio[:max_chunk_lenght], min_silence_len=temp_min_silence_len,
                                                         silence_thresh=temp_silence_thresh)

                slice_points_arr = []  # array that contains potential time stamps of slide points for chunk
                if len(silence_time_stamps_arr) > 1:
                    for x in range(len(silence_time_stamps_arr) - 1):
                        # generate slice points between end of one silence and start of another
                        slice_points_arr.append(int(silence_time_stamps_arr[x][1] + (
                                    (silence_time_stamps_arr[x + 1][0] - silence_time_stamps_arr[x][1]) / 2)))
                else:
                    # the only slice point is the end of first detected silence
                    slice_points_arr.append(silence_time_stamps_arr[0][1])

                slice_points_arr.reverse()
                for slice_point in slice_points_arr:
                    if slice_point > min_chunk_lenght and slice_point < max_chunk_lenght:
                        final_slice_point = slice_point
                        break
                temp_min_silence_len = temp_min_silence_len + min_silence_len_step
                temp_silence_thresh = temp_silence_thresh + silence_thresh_step

            # chunkArr.append(audio[:final_slice_point+16]) #append slicepoint (add 16 ms to conpensate the cut)
            self.process_file_chunk(audio[:final_slice_point + 16], chunk_index)
            chunk_index += 1

            audio = audio[-(audio_len - final_slice_point):]
            audio_len = len(audio)
        if self.file_recognition_run:
            # add final chunk
            self.process_file_chunk(audio, chunk_index)
        self.numer_of_chunks = chunk_index + 1

    def start_microphone_voice_recognition(self, microphone_ID=None, lang_code=None):
        '''
        Function that is used to start voice recognition using microphone
        :param microphone_ID: optional variable used to select used microphone
        :param lang_code: optional language argument
        :return: None
        '''

        if lang_code != None:
            self.transcription_lang = lang_code

            self.m = sr.Microphone()

        self.stop_listening = self.r.listen_in_background(self.m, self.callback,phrase_time_limit=4)


        # set get audio level run flag to True
        self.audio_level_run = True

        # Thread that saves audio volume
        def get_volume(microphone):

            # while thread is not killed
            while self.audio_level_run:
                try:
                    mic_data = microphone.stream.read(128)
                    data = np.fromstring(mic_data, dtype=np.int16)
                    peak = np.abs(int((np.max(data) - np.min(data) / 2 ** 16) / 327))
                    self.audio_level = [peak, peak]
                except Exception:
                    DEB and print_grey("Waiting for microphone data")
                time.sleep(0.05)

            # If thread is killed set audio level back to 0
            self.audio_level = [0, 0]

        # Start volume thread
        self.volume_thread = threading.Thread(target=get_volume, daemon=True, args=(self.m,))
        self.volume_thread.start()

    def stop_voice_recognition(self):
        # Stop volume thread, stop voice recognition
        self.stop_listening(wait_for_stop=False)
        self.audio_level_run = False
        self.stream = None


if __name__ == '__main__':
    DEB=False


    print_green("Przetwarzanie mowy na tekst || Speech to text")
    print_grey("Wybierz tryb || Select Mode")
    print_grey("1. Przetwarznaie mowy na żywo || Live voice recognition")
    print_grey("2. Przetwarzanie mowy z pliku || File voice recognition")
    mode=int(input())
    assert isinstance(mode,int)
    print_grey("Wpisz kod języka || Write down language code")
    print_grey("'pl-PL' dla języka polskiego || 'en-EN' for english")
    lang = str(input())

    r=RecognizeVoice()
    if mode==1:
        print_grey("Zacznij mówić || Please start talking")
        print_grey("Aby zakończyć wpisz cokolwiek || Write anything to stop")
        r.start_microphone_voice_recognition(lang_code=lang)

        def runner():
            out=""
            while run:
                temp_out=""
                for element in r.transcription_array:
                    if element!=-1:
                        temp_out+=element[0][0]+" "

                if out!=temp_out:
                    out=temp_out
                    print_green(out)

                time.sleep(1)
        run=True
        thread=threading.Thread(target=runner,args=())
        thread.start()
        input()
        run=False
    if mode==2:
        print_grey("Wpisz ścieżke do pliku audio WAV || Please paste path to a WAV file")
        path=input()
        r.start_file_voice_recognition(file_path=path,lang_code=lang)

        out=""
        for element in r.transcription_array:
            if element != -1:
                out += element[0][0] + " "

        while len(r.transcription_array) != r.numer_of_chunks and r.file_recognition_run:
            # count % of progresss
            progressPercent = round(len(
                r.transcription_array) / r.numer_of_chunks * 100) if r.numer_of_chunks != -1 else 0

            print_grey("Przetwarzanie... || Processing... {}%".format(progressPercent))

            time.sleep(1)

        # sort array (it's needed because every thread can finish at any moment, you need to sort output)
        sorted_transcription_arr = sorted(r.transcription_array, key=lambda x: x[1], reverse=False)
        print_grey("Przetwarzanie... || Processing... {}%".format(100))
        # for every element
        for element in sorted_transcription_arr:

            # if element is not -1. It's -1 when voice was not recognized
            if element[0] != -1:
                out += element[0][0][0] + " "

        print_green(out)




