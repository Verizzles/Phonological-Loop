"""
Provide speech support for Python ACT-R models.

Author: David Pierre Leibovitz (C) 2019

Usage:
1: from speech import *
2: speechNote=SpeechSupport(name="Note", memorize=False, volume=0.75)
...

   speechNote - the system/debug/print/log/note speech output. NOT an ACT-R module.
                Usage: speechNote.introduction()   - to list all available voices
                       speechNote.hello(log=None)  - to introduce this speaker
                       speechNote.say("something") - to say something
README:
Windows 10
- came with only 1 voice (Zira), to add more
  * Goto: Windows Setting/Time & Language/Language/+ Add a language
    - choose ones with Text-to-speech available
    - UNCHECK: Install language pack and set as my Windows display language
  * This didn't make the languages available! See: https://apps.magicmau.nl/EliteG19s/Docs/EliteG19s-Manual.html#user-content-MoreVoices
- Only one shared voice engine - cannot have two agents talk simultaneously!
"""

##################################################################################################################################
# Import the main Text To Speech (tts) system. If it fails, fake it - simply log all utterences
##################################################################################################################################

try:
    import pyttsx3  # Text-To-Speech; see https://pypi.org/project/pyttsx3/
except:
    print """
##################################################################################################################################
# Pyton package pyttsx3 is not installed - creating a fake for logging purposes.
# - For downloading, please see: https://pypi.org/project/pyttsx3/
# - Read speech.py for README info
##################################################################################################################################"""
    class pyttsx3: # Fake TTS system if package not installed.
        @staticmethod
        def init(): return None;

import ccm
import ccm.logger

##################################################################################################################################
# Speech support class for use by the SpeechModule
##################################################################################################################################
import time
class SpeechSupport:
    """
Provides the interface between a text-to-specch system, and a SpeechModule.
1. say() - for the agent to say something out loud; will yield the amount of time
2. think() - for the agent to think something internally; will yield 80% of time
3. note() - for logging as an observing; no yielding

"""
    engines         = 0;    # number of engines; could have different agents with different voices
    #engine         = pyttsx3.init(); # BUG: want 1 engine per agent so they can speak at the same time without blocking each other
    voices          = None  # array of available voices

    # Python ACT-R converts inheritors of classes ACTR and ccm.Model into an interna production-like thing (not this class), BUT...
    # For example, function defitions are converted to production matchings, but the rest are deepcopied.
    # No need to deepcopy this class (from SpeechModule), a shallow reference copy will do!
    # The problem is that the engine cannot be copied!
    # CURRENT BUG: 10 modules use the same support!!!
    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self
        
    def __init__(self, name=None, voiceIndex=None, rate=None, volume=None, memorize=True, silentRecall=False, log=None):
        """Initialize myself - the constructor. Get me a new voice engine.
name:           my name, defaults to SN where N is the engine number (starting with 0)
voiceIndex:     index into the array of possible voices. Use noteSpeech.introduction() to find the one you like. Default to None (use engine number).
                If greater than the allowed possibilities, 0 will be used.
rate:           the speech rate in words per minute. Defaults to what the system assigns (200 on Windows)
volume:         0.0 - 1.0 (100%). Defaults to what the system assigns (1.0 on Windows).
memorize:       True (the default) to memorize utterences, their duration, and frequency. Use dump() to list at end.
silentRecall:   lookup memorized utterences and if found, simply adjust simulation time, but don't actualy say them- this greatly speeds up simulation.
"""
        if log is None: log=ccm.logger.log_proxy
        self.log = log
        
        self.engine = pyttsx3.init() # Because of this line. we need a __deepcopy__ as engine can't be deepcopied
        self.engineNumber = SpeechSupport.engines
        SpeechSupport.engines += 1

        if name is not None:
            self.name=name
        else:
            self.name="S%d" % self.engines
        dir(log)
        log.speech.init[self.name] = "Created in engine %d." % self.engineNumber

        if SpeechSupport.voices is None: # I assume that every engine will have the same set of voices... Do this just once - no need for a local.
            if self.engine: 
                SpeechSupport.voices=self.engine.getProperty('voices')
            else:
                SpeechSupport.voices=[]
            if len(self.voices) == 1:
                log.speech.init[self.name] = "System has only 1 voice available."
            else:
                log.speech.init[self.name] = "System has %d voices available." % len(self.voices)

        # Don't really need to know the voice index, only its id. But can't get a name without it!
        if voiceIndex is None:
            voiceIndex = self.engineNumber
        if voiceIndex >= len(SpeechSupport.voices):
            log.speech.init[self.name] = "Voice index %d too large. Use 'noteSpeech.introduction()' to find the right one. Using 0." % voiceIndex
            voiceIndex = 0  # I'm assuming there will always be at least one!
        self.voiceIndex = voiceIndex
        if self.engine:
            self.voiceId = SpeechSupport.voices[voiceIndex].id
            log.speech.init[self.name] = "Voice id is %s." % self.voiceId
            voiceName = SpeechSupport.voices[voiceIndex].name
            if voiceName is not None:
                log.speech.init[self.name] = "Technichal voice name is %s." % voiceName
        else:
            self.voiceId = None;

        self.memorize = memorize
        if memorize:
            log.speech.init[self.name] = "Memorizing utterences, their duration and their frequency of use."
            self.utterences = {}        # memorize the time it takes to say something, and the number of times said, i.e. (time, count)
        else:
            log.speech.init[self.name] = "Not memorizing utterences."
            self.utterences = None

        self.silentRecall = silentRecall
        if silentRecall:
            log.speech.init[self.name] = "Recalled utterences will be silent to quicken real time. Simulation time based on their past duration."
        else:
            log.speech.init[self.name] = "Recalled utterences will be silent to quicken real time. Simulation time based on their past duration."

        if self.engine:
            if volume is not None:
                self.voiceVolume = volume                               # Get specified volume, or
            else:
                self.voiceVolume = self.engine.getProperty('volume')    # use default volume (1.0 (100%) on Windows 10).
                
            if rate:
                self.voiceRate   = rate                                 # Get specified rate, or
            else:
                self.voiceRate   = self.engine.getProperty('rate')      # use default rate (200 words per minute on Windows 10).
        else:
            self.voiceVolume     = 1.0
            self.voiceRate       = 100
        log.speech.init[self.name] = "Volume at %d percent." % (int(100*self.voiceVolume))
        log.speech.init[self.name] = "Speed at %d words per minute." % self.voiceRate

    def _say(self, text, minVolume=0.0):
        """Say some text with created parameters, but with some minimum volume."""
        if self.engine:
            volume = self.voiceVolume
            if volume < minVolume:
                volume = minVolume
            self.engine.setProperty('voice',  self.voiceId)
            self.engine.setProperty('volume', volume)
            self.engine.setProperty('rate',   self.voiceRate)
            self.engine.say(text)
            self.engine.runAndWait()
                
    def say(self, text):
        """Say an utterence, memorize and return its time, so it can be recalled silently without pause."""
        if self.engine is None:
            print "No speech engine. %s: %s" % (self.name, text)
            return
        if self.memorize:
            dt, count = self.utterences.get(text, (0.0, 0))
        else:
            dt = 0.0; count = 0
        if count: # we have previously said it
            if self.voiceVolume and not self.silentRecall: # but volume is on so must say it again
                self._say(text)
        else: # never said it before, so time it
            dt = len(text)/10.0 # Default if no engine exists
            if self.engine:
                start_time = time.time() # Time the engine!
                self._say(text)
                end_time = time.time()
                dt=float(end_time - start_time)
        # Memorize the utterence; update the count
        if self.memorize:
            self.utterences[text]=(dt, count+1)
        self.log.speech.say[self.name] = "%7.3f: %s" % (dt, text)
        #print "Say(%s): %7.3f: %s" % (self.name, dt, text)
        return dt
       
    def introduction(self):
        """
Introduce all the voices in the speech system. Ideally only use once on global speechNote for debugging.
See also: hello().
"""
        print "-----------------------------------------------------------------------------------------------------------------"
        print "This is 'introduction()' to help you pick a system voice. Comment out its invocation if it becomes too talkative!"
        print "-----------------------------------------------------------------------------------------------------------------"
        if self.engine:
            self._say("Here are the system voices.", minVolume=1.0)
            self.engine.setProperty('rate', 200)
            n = 0
            for voice in SpeechSupport.voices:
                print "Voice number %d." % n
                print voice
                self.engine.setProperty('voice', voice.id)
                self.engine.say("Hello, I'm voice number %d. My name is %s." % (n, voice.name))
                self.engine.runAndWait()
                n+=1
            if n == 1:
                self._say("Thats it, only one voice.", minVolume=1.0)
            else:
                self._say("This engine has access to %d voices." % n, minVolume=1.0)
        else:
            print "No speech engine!"

    def hello(self):
        """
Introduce all the parameters of this speaker.
"""
        print "-----------------------------------------------------------------------------------------------------------------"
        print "This is 'hello()' to introduce voice %s. Comment out its invocation if it becomes too talkative!" % self.name
        print "-----------------------------------------------------------------------------------------------------------------"
        print SpeechSupport.voices[self.voiceIndex]
        if self.engine:
            print "Speaker Name: %s" % self.name
            self._say("Hello. My name is %s." % self.name, minVolume=0.5)
            print "Engine:       %d" % self.engineNumber
            self._say("I'm running in engine number %d." % self.engineNumber, minVolume=0.5)
            print "Number:       %d" % self.voiceIndex
            print "Voice Name:   %s" % SpeechSupport.voices[self.voiceIndex].name
            self._say("Technically, I'm voice index %d, and my voice name is %s." % (self.voiceIndex, SpeechSupport.voices[self.voiceIndex].name), minVolume=0.5)
            print "Speed:        %d (words per minute)" % self.voiceRate
            print "Volume:       %d%%" % int(100*self.voiceVolume)
            self._say("I speak %d words per minute at a volume of %d percent." % (self.voiceRate, int(100*self.voiceVolume)), minVolume=0.5)
        else:
            print "No speech engine. Hello. My name is %s." % self.name
                                                                                                                                           
    def dump(self):
        """Dump my utterences data (time, cout)"""
        print "-----------------------------------------------------------------------------------------------------------------"
        print "%s: Dumping my utterences..." % self.name
        print "-----------------------------------------------------------------------------------------------------------------"
        if self.memorize:
            n=0; totalCount=0; totalTime=0.0
            print "  N Count    Time Saying"
            for utterence in self.utterences:
                dt, count = self.utterences[utterence]
                print "%3d %5d %7.3f %s" % (n, count, dt, utterence)
                n+=1; totalCount+=count; totalTime+=count*dt
            print     "--- %5d %7.3f Totals" % (totalCount, totalTime)
        else:
            print "Nothing memorized to dump!"
            
#from ccm.lib.actr import *

##################################################################################################################################
# Note that while these look like a Python class, they get converted to a scheduled set of productions by Python ACT-R
##################################################################################################################################
class SpeechModule(ccm.Model):  # create a speech motor module to do the speaking (in parallel with other motors commands)
    """
Despite appearences, this is NOT A CLASS, but gets converted to a set of scheduled production rules by Python ACT-R for a cognitive model
"""
    def __init__(self, name=None, voiceIndex=None, volume=None, rate=None, memorize=True, silentRecall=False, log=None):
        """Initialize myself - the constructor.
name:           my name, defaults to SN where N is the engine number (starting with 0)
voiceIndex:     index into the array of possible voices. Use noteSpeech.introduction() to find the one you like. Defaults to engineNumber.
                If greater than the allowed possibilities, 0 will be used.
rate:           the speech rate in words per minute. Defaults to what the system assigns (200 on Windows)
volume:         0.0 - 1.0 (100%). Defaults to what the system assigns (1.0 on Windows).
memorize:       True (the default) to memorize utterences, their duration, and frequency. Use dump() to list at end.
silentRecall:   lookup memorized utterences and if found, simply adjust simulation time, but don't actualy say them- this greatly speeds up simulation.
log:            can attach a loggger. But I suspect Python ACT-R fills this in with the global one?
"""
        ccm.Model.__init__(self)
        # Because of this line, Python ACT-R will try to deepcopy the SpeechSupport instance. We ensure a shallow copy.
        self.support=SpeechSupport(name=name, voiceIndex=voiceIndex, volume=volume, rate=rate, memorize=memorize, silentRecall=silentRecall, log=log) 
        
    def say(self, text):
        """Says some text over simulated time."""
        dt = self.support.say(text)
        yield dt
        #self.log.SpeechModule[self.support.name].say = text        # CCM log can figure out the ccm.Model instance
        self.log.SpeechModule.say = text

    def hello(self):
        self.support.hello()
        
    def dump(self):
        self.support.dump()

# Outer speech represent what I actually say out loud.
class SpeechVerbalModule(SpeechModule):
    def __init__(self, name='Verbal', voiceIndex=3, volume=1.0, rate=100, memorize=True, silentRecall=False, log=None):
        SpeechModule.__init__(self, name=name, voiceIndex=voiceIndex, volume=volume, rate=rate, memorize=memorize, silentRecall=silentRecall, log=log)
        
# Inner speech is what I linguistically think inside my mind.
# If used for the phonological loop, it is best to set silentRecall to True.
class SpeechThinkModule(SpeechModule):
    def __init__(self, name='Think', voiceIndex=None, volume=0.5, rate=100, memorize=True, silentRecall=True, log=None):
        SpeechModule.__init__(self, name=name, voiceIndex=voiceIndex, volume=volume, rate=rate, memorize=memorize, silentRecall=silentRecall, log=log)
        
##################################################################################################################################
# Global debug/log/print/etc. system speech output - always there.
#
# Usage: speechNote.introduction()   - to list all available voices
#        speechNote.say("something") - to say something
##################################################################################################################################
#speechNote=SpeechSupport(name="Note", memorize=False)

##################################################################################################################################
# Test the speech system
##################################################################################################################################
if __name__ == "__main__":
    speechNote=SpeechSupport(name="Note", memorize=False, volume=0.75)
    speechNote.introduction()
    speechNote.hello();
    
    speechNote.say("Hello, this is a test. How are you?")
