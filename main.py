# -*- coding: UTF-8 -*-
'''
---IMPORT---
--EXTERNAL LIBRARIES--
kivy - used for GUI
time - only used time.sleep function
threading - used for thread managment
os - to get path of script running

--OTHER PYTHON FILES--
recognition - handling speech recognition
languages - stores and gives access to strings in different languages
'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
import time
import threading
from os import path
import recognition

import read_config as l

DEB = True  # Should I print debugging info

'''
print_green, print_red, print_grey, print_yellow are used only for debugging 
'''


def print_green(string):
    print('\x1b[1;30;42m' + str(string) + '\x1b[0m')


def print_red(string):
    print('\x1b[1;30;41m' + str(string) + '\x1b[0m')


def print_gray(string):
    print('\x1b[0;30;47m' + str(string) + '\x1b[0m')


def print_yellow(string):
    print('\x1b[6;30;43m' + str(string) + '\x1b[0m')


class LiveVoiceRecognition(BoxLayout):
    '''
    Class used for live audio transcription
    '''

    # Language variables
    l_live_main_title = StringProperty(l.get_key_for_live("mainTitle"))
    l_live_start_button_normal = StringProperty(l.get_key_for_live("mainButton")[0])
    l_live_start_button_pressed = StringProperty(l.get_key_for_live("mainButton")[1])
    l_live_text_hint = StringProperty(l.get_key_for_live("defTextInput"))
    l_live_alternatives = StringProperty(l.get_key_for_live("alts"))

    # Set volume bar variables to 0 (Max is 100)
    live_volume_left, live_volume_right = NumericProperty(0), NumericProperty(0)

    def __init__(self, **kwargs):
        super(LiveVoiceRecognition, self).__init__(**kwargs)
        self.r = recognition.RecognizeVoice()  # Set voice recognizer variable
        self.text_array_alternatives, self.text_array_full = [], []  # altTextArr - array with alternative transcriptions, fullTextAtArr - array with full transcription
        self.text_array_initialization = ["",
                             ""]  # Array that saves text before and after cursor, used when starting live transcription

    # Update Language variables
    def update_gui(self):
        self.l_live_main_title = l.get_key_for_live("mainTitle")
        self.l_live_start_button_normal = l.get_key_for_live("mainButton")[0]
        self.l_live_start_button_pressed = l.get_key_for_live("mainButton")[1]
        self.l_live_text_hint = l.get_key_for_live("defTextInput")
        self.l_live_alternatives = l.get_key_for_live("alts")

    def recognition_button_pressed(self, state):
        # Live recognition button was pressed

        def get_text_initialization(input_text_obj):
            '''
            Function that returns text before and after cursor
            :param input_text_obj: kivy.TextInput object
            :return [before,after]:  before - text before cursor, after - text after cursor
            '''
            col = input_text_obj.cursor[0]  # current cursor column
            row = input_text_obj.cursor[1]  # current cursor row
            step = 0
            while col != 0 or row != 0:
                # count how many steps untill cursor will be at position 0,0 (at start)
                input_text_obj.do_cursor_movement('cursor_left')
                step += 1
                col = input_text_obj.cursor[0]
                row = input_text_obj.cursor[1]
            # return text before and after cursor
            return [input_text_obj.text[:step] + " ", input_text_obj.text[step:]]

        def start_recognition_thread(self):
            '''
            Live recognition thread
            :param self: import self to thread
            '''

            self.r = recognition.RecognizeVoice()  # Set voice recognizer to live recognition
            self.r.start_microphone_voice_recognition(l.get_config("curr_mic"), l.get_config(
                "curr_transcription_lang"))  # Start microphone voice recognition

            while not self.kill_recognition_thread:
                # Loop until thread is killed

                # Read volume bar data
                self.live_volume_left = int(self.r.audio_level[0])
                self.live_volume_right = int(self.r.audio_level[1])
                time.sleep(0.03)  # update data every 33 milliseconds

                assert isinstance(self.r.transcription_array, list), "self.r.transcriptionArr is not list -{}".format(
                    self.r.transcription_array)

                # If there's a new transcription to show
                if len(self.r.transcription_array) > 0:
                    # For every new transciption to show
                    for index, element in enumerate(self.r.transcription_array):

                        # If there are alternatives in that transcription
                        if isinstance(element,
                                      list):  # checks if it's instance of list. Can happend only when sound was not recognised.
                            if len(element) > 1:
                                # Append alternatives to alternatives array queue
                                self.text_array_alternatives.append([self.r.transcription_array[index], len(self.text_array_full)])

                            # Appends this transcription to full transcription array
                            self.text_array_full.append(self.r.transcription_array[index][0][0])

                            # Sends new transcription to GUI
                            self.ids.full_text.text = self.text_array_initialization[0] + " ".join(self.text_array_full) + " " + \
                                                      self.text_array_initialization[1]

                            # Pop transcription element that was alread shown
                            self.r.transcription_array.pop(index)

                # If there's any alternative transcription to show
                if len(self.text_array_alternatives) > 0:

                    # alternative transcription array split into variables
                    element = self.text_array_alternatives[0][0]
                    id = self.text_array_alternatives[0][1]

                    # For every alternative that is avaliable show button
                    for ind, alts in enumerate(element):
                        exec("self.ids.alt" + str(ind) + '.text ="""' + str(alts[0]) + '''"""''')
                        exec("self.ids.alt" + str(ind) + ".opacity=1")
                        exec("self.ids.alt" + str(ind) + ".disabled=False")

                    # Show other GUI elements
                    self.ids.alttext.opacity, self.ids.gridAlt.opacity = 1, 1
                    self.ids.gridAlt.disabled = False

                    # text before is a str with a text before alternative
                    textBefore = self.text_array_initialization[0] + " ".join(self.text_array_full[0:self.text_array_alternatives[0][1]])
                    textBefore += " " if self.text_array_alternatives[0][1] > 0 else ""

                    # select (mark) alternative in full text
                    self.ids.full_text.select_text(len(textBefore),
                                                   len(textBefore) + len(self.text_array_full[self.text_array_alternatives[0][1]]))

                else:
                    # Hide GUI elements for alternatives
                    self.ids.alttext.opacity, self.ids.gridAlt.opacity = 0, 0
                    self.ids.gridAlt.disabled = True
                    for i in range(6):
                        exec("self.ids.alt" + str(i) + ".opacity = 0")
                        exec("self.ids.alt" + str(i) + ".disabled=True")

                    self.ids.full_text.cancel_selection()  # Cancel text selection

            # Set volume bars back to 0 (no signal)
            self.live_volume_left, self.live_volume_right = 0, 0

        if state == 'down':
            # If live recognition was triggered
            self.text_array_full = []
            self.kill_recognition_thread = False  # set kill thread flag to False
            self.text_array_initialization = get_text_initialization(self.ids.full_text)  # save text before and after cursor
            self.recognition_thread = threading.Thread(target=start_recognition_thread,
                                                       args=(self,))
            # start live recognition thread
            self.recognition_thread.start()
        else:
            # If live recognition was stopped
            '''
            Check if stop listening function exists. 
            If it doesn't exist program will wait until it's created
            It can not exists only in very specific situation.
            In order to trigger this situation user needs to click 
            start live and stop live recognition within less than 1 sec.
            '''
            stop = None
            while stop is None:
                try:
                    stop = self.r.stop_listening
                except:
                    pass

            # Stop voice recognition
            self.r.stop_voice_recognition()
            self.kill_recognition_thread = True
            self.text_array_initialization = None
            self.text_array_alternatives = []

    def altenative_button_pressed(self, button_text):
        # Alternative button was pressed

        # variables with text before and after alternative
        text_before = self.text_array_initialization[0] + " ".join(self.text_array_full[0:self.text_array_alternatives[0][1]])
        text_before += " " if self.text_array_alternatives[0][1] > 0 else ""

        text_after = " ".join(self.text_array_full[self.text_array_alternatives[0][1] + 1:len(self.text_array_full)])
        text_after += " " if len(text_after) > 0 else ""
        text_after += self.text_array_initialization[1]

        self.text_array_full[self.text_array_alternatives[0][1]] = button_text  # change element in full text array into alternative
        self.ids.full_text.text = text_before + button_text + " " + text_after  # show alternative in text_input gui
        self.text_array_alternatives.pop(0)  # pop used alternative


class FileVoiceRecognition(BoxLayout):
    '''
    Class used for transcription of audio files
    '''

    # Language variables
    side_title_state = 0  # default state of side title
    l_side_title = StringProperty(l.get_key_for_file("sideTitle")[side_title_state])
    l_enable_start = BooleanProperty(False)
    l_main_title = StringProperty(l.get_key_for_file("mainTitle"))
    l_def_text_input = StringProperty(l.get_key_for_file("defTextInput"))
    l_main_button = StringProperty(l.get_key_for_file("mainButton")[0])

    side_title_state = 0  # default state of side title
    script_path = path.realpath(__file__)  # path of script used to know where to open file explorer

    def __init__(self, **kwargs):
        super(FileVoiceRecognition, self).__init__(**kwargs)
        self.r = recognition.RecognizeVoice()  # Set voice recognizer to file recognition
        self.text_array_full = []  # altTextArr - array with alternative transcriptions, fullTextAtArr - array with full transcription
        self.file_path = None  # Path to file to do transcripiton

    # Update Language variables
    def update_gui(self):
        self.l_main_title = l.get_key_for_file("mainTitle")
        self.l_def_text_input = l.get_key_for_file("defTextInput")
        self.l_main_button = l.get_key_for_file("mainButton")[0]
        self.l_side_title = l.get_key_for_file("sideTitle")[self.side_title_state]

    def file_is_selected(self, file_path):
        '''
        Function that is activated when file is selected
        :param file_path: path to file
        '''

        supported_formats_array = ["wav"]  # list of supported formats

        '''
        checks if filePath is longer than 0 - kivy has a bug that sometimes results in len(filePath)==0
        '''
        if len(file_path) > 0:
            # checks if file is supported
            if str(str(file_path[0]).split(".")[-1:][0]).lower() in supported_formats_array:
                # shows in GUI that file is supported, and enables to start transciption
                self.l_side_title = l.get_key_for_file("sideTitle")[1]
                self.side_title_state = 1
                self.l_enable_start = True

                # set self filePath to selected file path
                self.file_path = file_path
            else:
                # shows in GUI that file is not supported, and disables button to start transciption
                self.l_side_title = l.get_key_for_file("sideTitle")[2]
                self.side_title_state = 2
                self.l_enable_start = False

                # supported file is not selected so set self filePath to None
                self.file_path = None

    def start_transcription(self, state):
        '''
        Function that is activated when start file transcription button was pressed
        :param state: state of button 
        '''

        def start_recognition_thread(self):
            '''
            File recognition thread
            :param self: import self to thread
            '''

            assert len(self.file_path) > 0, "FilePath is len 0"

            self.r = recognition.RecognizeVoice()  # Set voice recognizer to file recognition

            # makes a new thread to start file voice regonition (otherwise it will block updating GUI)
            self.thread_file_rec = threading.Thread(target=self.r.start_file_voice_recognition,
                                                    args=(self.file_path[0], l.get_config("curr_transcription_lang")))
            self.thread_file_rec.start()  # start file recognition thread then look for output

            # clears out text field
            self.ids.full_text2.text, showText = "", ""

            # while not all chunks are processed
            while len(self.r.transcription_array) != self.r.numer_of_chunks and self.r.file_recognition_run:
                # count % of progresss
                progressPercent = round(len(
                    self.r.transcription_array) / self.r.numer_of_chunks * 100) if self.r.numer_of_chunks != -1 else 0

                # save progress with % mark
                self.l_side_title = "{}%".format(progressPercent)

                # Display info about progress and chunks if debugging is Enabled
                DEB and print_yellow("All chunks {}, ready chunks {}, percent progress {}".format(self.r.numer_of_chunks,
                                                                                                  len(
                                                                                                     self.r.transcription_array),
                                                                                                  progressPercent))

                # update ~10 times every second
                time.sleep(0.1)

            # sort array (it's needed because every thread can finish at any moment, you need to sort output)
            sorted_transcription_arr = sorted(self.r.transcription_array, key=lambda x: x[1], reverse=False)

            # for every element
            for element in sorted_transcription_arr:

                # if element is not -1. It's -1 when voice was not recognized
                if element[0] != -1:
                    showText += element[0][0][0] + " "

            # send final text to be shown in GUI
            self.ids.full_text2.text = showText

            # enable text field (so user could edit it or copy)
            self.ids.full_text2.disabled = False

            # change text of buttons to indicate that process is over, and that user can process another file
            self.side_title_state = 3
            self.l_side_title = l.get_key_for_file("sideTitle")[self.side_title_state]
            self.l_main_button = l.get_key_for_file("mainButton")[2]

        def state_gui(show, self):
            '''
            Function used to show and hide elements of gui
            :param show: True- hide filechooser,show big text box, False - small text box, show filechooser
            '''
            if show:
                # hide & disable filechooser and show text field
                self.ids.filechooser.size_hint = (1, 0.01)
                self.ids.filechooser.opacity = 0
                self.ids.filechooser.size = (0.01, 0.01)
                self.ids.filechooser.disabled = True

                self.ids.full_text2.disabled = True
                self.ids.full_text2.size_hint = (1, 1)
                self.ids.full_text2.opacity = 1
            else:
                # show & enable filechooser and hide and enable text field
                self.ids.filechooser.size_hint = (1, 1)
                self.ids.filechooser.opacity = 1
                self.ids.filechooser.disabled = False
                self.ids.filechooser.cancel()
                self.ids.full_text2.disabled = False
                self.ids.full_text2.size_hint = (1, 0.01)
                self.ids.full_text2.opacity = 0

        if state != "normal":
            # print debbinging info
            DEB and print_gray("File recognition process was started")

            # hide & disable filechooser and show text field
            state_gui(True, self)

            # change GUI text to indicate that processing was started
            self.l_main_button = l.get_key_for_file("mainButton")[1]

            # make & start recognition thread
            self.r.file_recognition_run = True
            self.start_file_rec_thread = threading.Thread(target=start_recognition_thread, args=(self,))
            self.start_file_rec_thread.start()
        else:
            # sideTitleState only when processing was done
            if self.side_title_state == 3:
                # show user info that he can start processing another file
                self.side_title_state = 0
                self.l_side_title = l.get_key_for_file("sideTitle")[self.side_title_state]

            # print debbinging info
            DEB and print_yellow("Zakończenie procesu")

            # show & enable filechooser and hide and enable text field
            state_gui(False, self)

            # show user info that he can start transcription
            self.l_main_button = l.get_key_for_file("mainButton")[0]

            # shut down file recognition thread and clear transcription Array
            self.r.file_recognition_run = False
            self.r.transcription_array = []


class SettingsScreen(BoxLayout):
    '''
    Class used for Settings
    '''

    # Language variables
    l_settings_main_title = StringProperty(l.get_key_for_settings("panelName"))
    l_settings_app_language = StringProperty(l.get_key_for_settings("selectAppLang"))
    l_settings_transcription_lang = StringProperty(l.get_key_for_settings("selectTranscriptionLang"))

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    # Update Language variables
    def update_gui(self):
        self.l_settings_main_title = l.get_key_for_settings("panelName")
        self.l_settings_app_language = l.get_key_for_settings("selectAppLang")
        self.l_settings_transcription_lang = l.get_key_for_settings("selectTranscriptionLang")


    # function to app language
    def set_app_lang(self, button):
        # update config
        l.update_config("curr_lang", str(button.id))

        # print debbinging info
        DEB and print_green("I set language to {} with code {}".format(button.text, button.id))

        # reload GUI elements
        self.load_options()

        # reload all GUI language elements because app lanuage was updated
        self.parent.parent.ids.liveVoiceRecognition.update_gui()
        self.parent.parent.ids.fileVoiceRecognition.update_gui()
        self.parent.parent.ids.settingsScreen.update_gui()
        self.parent.parent.update_gui()

    # function to set transription language
    def set_trans_lang(self, button):
        # update config
        l.update_config("curr_transcription_lang", str(button.id))

        # print debbinging info
        DEB and print_green("I set transcription language to {} - {}".format(button.text, button.id))

        # reload GUI elements
        self.load_options()

    def load_options(self):
        def add_button(id, butText, onPress=None, butID=None, padX=10, padY=10, sizeAddX=50, sizeAddY=50, isBold=False):
            btn = Button(text=str(butText), size_hint=(None, None), bold=isBold)
            btn.size = [btn.texture_size[0] + sizeAddX, btn.texture_size[1] + sizeAddY]
            btn.halign = 'center'
            btn.bind(texture_size=btn.setter('size'))
            btn.padding_x = padX
            btn.padding_y = padY
            if onPress != None:
                btn.bind(on_press=onPress)
            if butID != None:
                btn.id = butID

            id.add_widget(btn)

        self.ids.settbox2.clear_widgets()
        self.ids.settbox3.clear_widgets()

        for code, ogName, enName in zip(l.get_list_of_languages(0), l.get_list_of_languages(1), l.get_list_of_languages(2)):
            isBold = True if code == l.get_config("curr_lang") else False
            add_button(self.ids.settbox2, "{}  {} {}".format(code, ogName, enName), self.set_app_lang, butID=code,
                       isBold=isBold)

        for lang in l.get_key_for_settings("supportedLang"):
            assert len(
                lang) == 2, "every language should have lenght of 2 - [language code,language name], lang here -> {}".format(
                lang)
            isBold = True if lang[0] == l.get_config("curr_transcription_lang") else False
            add_button(self.ids.settbox3, lang[1], self.set_trans_lang, isBold=isBold, butID=lang[0])


class MotherScreen(TabbedPanel):
    '''
    Class of mother screen
    '''

    # Language variables
    l_app_window_title = StringProperty(l.get_key_for_mother_screen("AppName"))
    l_app_tabbed_tab_name1 = StringProperty(l.get_key_for_mother_screen("Live"))
    l_app_tabbed_tab_name2 = StringProperty(l.get_key_for_mother_screen("File"))
    l_app_tabbed_tab_name3 = StringProperty(l.get_key_for_mother_screen("Settings"))

    def __init__(self, **kwargs):
        super(MotherScreen, self).__init__(**kwargs)
        self.title = self.l_app_window_title
        self.id = "motherScreen"

    # Update Language variables
    def update_gui(self):
        self.l_app_window_title = l.get_key_for_mother_screen("AppName")
        self.l_app_tabbed_tab_name1 = l.get_key_for_mother_screen("Live")
        self.l_app_tabbed_tab_name2 = l.get_key_for_mother_screen("File")
        self.l_app_tabbed_tab_name3 = l.get_key_for_mother_screen("Settings")


class App(App):
    def build(self):
        self.title="Praca Dyplomowa"

    def stop(self):
        import os
        os._exit(1)






App().run()
