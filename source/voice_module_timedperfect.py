import pyttsx3
import os
import torch
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time as sec

from faster_whisper import WhisperModel

Model = 'base.en'   # Whisper model size (tiny, base, small, medium, large)
English = True      # Use English-only model?
Translate = False   # Translate non-English to English?
SampleRate = 44100  # Stream device recording frequency
BlockSize = 30      # Block size in milliseconds
Threshold = 0.5     # Minimum volume threshold to activate listening
Vocals = [50, 1000] # Frequency range to detect sounds that could be speech
EndBlocks = 40      # Number of blocks to wait before sending to Whisper
AIname = "arjun"    # Name to call the assistant, such as "computer" or "jarvis". Activates further commands.

# Timer Module
class Timer:
    """
    A simple timer class that counts in seconds.
    """
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0

    def start(self):
        """
        Starts the timer.
        """
        if self.start_time is None:
            self.start_time = sec.time()

    def get_time(self):
        """
        Returns the elapsed time in seconds since the timer was started, 
        or 0 if not started.
        """
        if self.start_time is None:
            return 0
        else:
            self.elapsed_time = sec.time() - self.start_time
            return self.elapsed_time

    def reset(self):
        """
        Resets the timer to 0.
        """
        self.start_time = None
        self.elapsed_time = 0

    def countdown(self, duration, message="Try again in"):
        """
        Starts a countdown for the specified duration and prints a message
        along with a countdown timer until the duration ends
        """
        
        # Print countdown message in same line
        for i in range(duration, 0, -1):
            print(f"{message} {i}...\r",end="")
            sec.sleep(1)
        print(f"{' '*17}\r",end="") # clear the prev line
        print("\033[32mListening.. \033[37m(Ctrl+C to Quit)\033[0m")


# Assistant Module
class System:
    def __init__(self):
        self.silence_timer = Timer()
        self.speech_timer = Timer()
        self.silenceflag = False # flag for exit for silence for more than time limit
        self.speechflag = False # to solve the error with buffer even after reset when speech is long
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False
        self.talking = False
        self.voice_mode = False
        self.espeak = pyttsx3.init()
        self.espeak.setProperty('rate', 180) # speed of speech, 175 is terminal default, 200 is pyttsx3 default
        print("\033[96mLoading Whisper Model..\033[0m", end='', flush=True)
        # MODEL QUANTIZED TO INCREASE SPEED
        # self.model = whisper.load_model(name = f'{Model}{".en" if English else ""}', device = "cpu")
        self.model = WhisperModel(Model, device="cpu", compute_type="int8")
        # self.quantized_model = torch.quantization.quantize_dynamic(self.model, {torch.nn.Linear}, dtype=torch.qint8)
        print("\033[96m Done.\033[0m")

    def speak(self, text):
        self.talking = True # if I wanna add stop ability, I think function needs to be it's own object
        print(f"\n\033[92m{text}\033[0m\n")
        self.espeak.say(text) #call(['espeak',text]) #'-v','en-us' #without pytttsx3
        self.espeak.runAndWait()
        self.talking = False

    def exit_voice_mode(self):
        if self.voice_mode:
            self.voice_mode = False
            self.speak("voice control deactivated")

    def check_voice_mode_name(self,text):
        ''' It is understood that user is trying to say Arjun when A,J,N or L is preszent in the same order'''
        voice_mode_name = False
        word = text.split()
        if AIname in text or "origin" in text:
            voice_mode_name = True
        elif len(word) == 2:
            if "a" in word[1] and len(word[1])>3:
                if "j" in word[1]:
                    if "n" in word[1] or "l" in word[1]:
                        voice_mode_name = True            
            else:
                voice_mode_name = False
        elif len(word) == 1:
            if "a" in word[0] and len(word[0])>3:
                if "j" in word[0]:
                    if "n" in word[0] or "l" in word[0]:
                        voice_mode_name = True
            else:
                voice_mode_name = False
        else:
            voice_mode_name = False
        return voice_mode_name


    def check_commands(self,txt_analyze):       
        if len(txt_analyze.split()) in range(2,6):

            # HEADLIGHT CONTROL
            if "headlight" in txt_analyze:
                if "on" in txt_analyze:
                    print("\033[96m command 001 (HDLGT-ON) activated.\033[0m")
                elif "of" in txt_analyze:
                    print("\033[96m command 002 (HDLGT-OFF) activated.\033[0m")

            # BEEPER (HORN) CONTROL
            elif "beep" in txt_analyze or "people" in txt_analyze:
                if "on" in txt_analyze:
                    print("\033[96m command 003 (HORN-ON) activated.\033[0m")
                elif "of" in txt_analyze:
                    print("\033[96m command 004 (HORN-OFF) activated.\033[0m")
            
            # INDICATOR
            elif "indicator" in txt_analyze:
                left_found = ("left" in txt_analyze or "lift" in txt_analyze)
                right_found = ("right" in txt_analyze or "write" in txt_analyze)
                if left_found:
                    if "on" in txt_analyze:
                        print("\033[96m command 005 (LIND-ON) activated.\033[0m")
                    elif "of" in txt_analyze:
                        print("\033[96m command 006 (LIND-OFF) activated.\033[0m")
        
                elif right_found:
                    if "on" in txt_analyze:
                        print("\033[96m command 007 (RIND-ON) activated.\033[0m")
                    elif "of" in txt_analyze:
                        print("\033[96m command 008 (RIND-OFF) activated.\033[0m")
            # ENGINE
            elif "engine" in txt_analyze:
                if "on" in txt_analyze:
                    print("\033[96m command 009 (ENGN-ON) activated.\033[0m")
                elif "of" in txt_analyze:
                    print("\033[96m command 010 (ENGN-OFF) activated.\033[0m")  

            # EMERGENCY STOP
            elif "emergency" in txt_analyze and "stop" in txt_analyze:
                if "begin" in txt_analyze or "begun" in txt_analyze:
                    print("\033[96m command 011 (EMST-BEG) activated.\033[0m")
                elif "release" in txt_analyze or "relish" in txt_analyze:
                    print("\033[96m command 012 (EMST-REL) activated.\033[0m") 

            # DIRECTION CONTROL
            elif "direction" in txt_analyze:
                reverse_dir = ("reverse" in txt_analyze or "to us" in txt_analyze)
                if "neutral" in txt_analyze:
                    print("\033[96m command 013 (DIR-N) activated.\033[0m")
                elif "forward" in txt_analyze:
                    print("\033[96m command 014 (DIR-F) activated.\033[0m")
                elif reverse_dir:
                    print("\033[96m command 015 (DIR-R) activated.\033[0m")

            # IF COMMANDS NOT LISTED IN DECISION TREE
            else:
                print('\033[91mUnknown Command\033[0m')
        #IF RANDOM SENTENCES
        else:
            print('\033[91mOnly Commands are accepted\033[0m')    


    def decision_tree(self,txt):

		#CHECK VOICE MODE NAME
        voice_mode_name = self.check_voice_mode_name(txt)

    	# if inside voice_mode
        if self.voice_mode:

    		# CHECK EXIT VOICE MODE
            exits = ["bye","close","exit","terminate"]
            voice_mode_checkout = (txt.startswith(tuple(exits)) and voice_mode_name)
            if voice_mode_checkout or txt == "exit":
                self.exit_voice_mode()
                return

            #CHECK COMMANDS
            self.check_commands(txt)

        # if not inside voice mode
        else:

	    	#CHECK ENTER VOICE MODE
	        greetings = ["hi", "hey","hello"]
	        voice_mode_checkin = ((txt.startswith(tuple(greetings)) and voice_mode_name) or voice_mode_name)
	        if voice_mode_checkin:
	            self.speak("Voice mode is currently active.") 
	            self.voice_mode = True
	            return
	        else:
    	        # NOTIFY TO ENTER INTO VOICE ASSISTANT IF NOT
	            print("Call Arjun to enter into voice assistant")


    def callback(self, indata, frames, time, status):
        if self.transcription_ongoing: # waits for transcription to complete and proceed to next input
            return
            #if status: print(status) # for debugging, prints stream errors.

        # NO INPUT OR MUTED
        if not any(indata):
            print('\033[31m.\033[0m', end='', flush=True) # if no input, prints red dots
            #print("\033[31mNo input or device is muted.\033[0m") 
            return

        freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * SampleRate / frames

        #if speech within range of vocals and above threshold
        # SPEECH DETECTED
        # speech_detected = np.sqrt(np.mean(indata**2)) > Threshold and Vocals[0] <= freq <= Vocals[1] and not self.talking
        if np.sqrt(np.mean(indata**2)) > Threshold and Vocals[0] <= freq <= Vocals[1] and not self.talking:
            self.silence_timer.reset()
            self.speech_timer.start()
            # reset buffer if random speech for more than 5 seconds
            if not self.speechflag and self.speech_timer.get_time()>= 4.0:
                print("\nNoise Detected!!!")
                self.speech_timer.countdown(3)
                self.speech_timer.reset()
                self.buffer = np.zeros((0,1))
                self.speechflag = True
            else:
                if not self.speechflag: print('.', end='', flush=True) # print only when the speech is short suitable for commands
                # if self.voice_mode: print('.', end='', flush=True) # To avoid printing anything while assistant not activated
                if self.padding < 1: self.buffer = self.prevblock.copy()
                self.buffer = np.concatenate((self.buffer, indata))
                self.padding = EndBlocks
                
        else:
        # SILENCE DETECTED
            # close when silent for 30 sec
            if self.silence_timer.get_time() >= 10.0 and self.silenceflag == False and self.voice_mode == True:
                self.silence_timer.countdown(3,"closing in") # last 5 second countdown to alert user
                self.silenceflag = True
                self.exit_voice_mode()
                print("Enter voice mode to interact")

            self.padding -= 1
            if self.padding > 1:
                self.buffer = np.concatenate((self.buffer, indata))
            elif self.padding < 1 < self.buffer.shape[0] > SampleRate: # if enough silence has passed, write to file.
                self.speech_timer.reset()
                # The below if handles the problem of unwanted transcription of long speech once detected
                if self.speechflag: 
                    self.buffer = np.zeros((0,1))
                    self.speechflag = False
                    return # if long speech, do not write clear buffer and return
                write('dictate.wav', SampleRate, self.buffer) # I'd rather send data to Whisper directly..
                self.fileready = True

                self.buffer = np.zeros((0,1))
            elif self.padding < 1 < self.buffer.shape[0] < SampleRate: # if recording not long enough, reset buffer.
                self.buffer = np.zeros((0,1))
                print("\033[2K\033[0G", end='', flush=True)
            else:
                self.prevblock = indata.copy() #np.concatenate((self.prevblock[-int(SampleRate/10):], indata)) # SLOW


    def transcribe(self):
        # if self.voice_mode: print("\n\033[90mTranscribing..\033[0m") # To avoid printing anything while assistant not activated
        print("\n\033[93mTranscribing..\033[0m") #original code
        
        # trb_txt = self.quantized_model.transcribe('dictate.wav',fp16=False,language='en' if English else '',task='translate' if Translate else 'transcribe')
        segments, _ = self.model.transcribe('dictate.wav', beam_size=10)
        texts = [segment.text for segment in segments]
        if texts: 
            trb_txt = texts[0] # to handle errors for list out of range. 
            txt_preprocessed = "".join(ch for ch in trb_txt if ch not in ",.?!'").lower().strip() 
            # print(f"\n\033[90m{trb_txt}\033[0m") # output

        # if self.voice_mode: print(f"\033[1A\033[2K\033[0G{trb_txt['text']}") # To avoid printing anything while assistant not activated
        # print(f"\033[1A\033[2K\033[0G{trb_txt['text']}") #original code
        print("\n\033[93mspeak now\033[0m") #status to speak now
        self.transcription_ongoing = False
        self.silence_timer.reset()
        self.speech_timer.reset()
        self.silenceflag = False # for executing the exit for silence for only once
        self.fileready = False
        if texts: return txt_preprocessed
        else: print("None")


    def listen(self):
        self.transcription_ongoing = False
        print("\033[32mListening.. \033[37m(Ctrl+C to Quit)\033[0m")
        self.silence_timer.start()
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(SampleRate * BlockSize / 1000), samplerate=SampleRate):
            while True: 
                if self.fileready:
                    txt = self.transcribe() # print the txt to check the transcription
                    if txt: print(txt)
                    if txt: self.decision_tree(txt) # comment this if you dont want to use assistant


def main():
    try:
        module = System()
        module.listen()
    except (KeyboardInterrupt, SystemExit): pass
    finally:
        print("\n\033[93mQuitting..\033[0m")
        if os.path.exists('dictate.wav'): os.remove('dictate.wav')

if __name__ == '__main__':
    main() 

# MODEL TAKES TOO MUCH TIME FOR TRANSCRIPTION IF THE SENTENCE IS NOT PROPER OR IT IS NOISY OR JUST SILENCE