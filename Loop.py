import ccm

from ccm.lib.actr import *
from Speak import *
from speech import *


log=ccm.log(html=True)



class MyEnvironment(ccm.Model):
    pass


#



class MyAgent(ACTR):
    focus=Buffer()
    yolo= Buffer()
    nus= Loop()
    speeky = SpeechVerbalModule()
    thinky = SpeechThinkModule(volume=0.1, rate= 400)
    reca = SpeechVerbalModule(volume=0.9, rate=200)
    memory = Buffer()
    DM = Memory(memory, latency=0.05, threshold=0, maximum_time=20, finst_size=5, finst_time=60.0)
    
    
    
    list = ["dorota", "blair", "chuck", "jenny", "serena"]
    wordly = list[0]
    #u=len(list)
    i = 0

    def init():
        focus.set('read')



    def read1(focus = 'read'):
        word1 = list[0]
        print "foxy mama"
        speeky.say(word1)        
        g=nus.words(word1)
        t = (g + " position:one")
        yolo.set(t)
              
        DM.add(yolo)
        focus.set('read2')
    
    def read2(focus = 'read2'):
        word2 = list[1]
        speeky.say(word2)
        g=nus.words(word2)
        print "jive cats"
        t = (g + " position:two")
        yolo.set(t)
              
        DM.add(yolo)
        focus.set('read3')
    
    def read3(focus = 'read3'):
        l = list[2]
        print "rockabillies"
        speeky.say(l)
        g=nus.words(l)
        t = (g + " position:three")
        yolo.set(t)
               
        DM.add(yolo)
        focus.set('read4')
    def read4(focus = 'read4'):
        l = list[3]
        speeky.say(l)
        print "greasers"
        g=nus.words(l)
        t = (g + " position:four")
        yolo.set(t)
               
        DM.add(yolo)
        focus.set('read5')
    def read5(focus = 'read5'):
        l = list[4]
        print "jesus take the wheel"
        speeky.say(l)
        g=nus.words(l)
        t = (g + " position:five")
        yolo.set(t)
               
        DM.add(yolo)
        focus.set('rehearse')

    def rehearse1a(focus='rehearse'):
        DM.request('isa:word position:one')
        print "requesting"
        focus.set('rehearse0')

    def rehearse1b(focus='rehearse0', memory = 'isa:word position:one word:?word'):
        DM.add(memory)
        thinky.say(word)
        print word
        DM.request('isa:word position:two')
        focus.set('rehearse2')
        
    def rehearse2(focus='rehearse2', memory = 'isa:word position:two word:?word'):
        DM.add(memory)
        thinky.say(word)
        print word
        DM.request('isa:word position:three')
        focus.set('rehearse3')
    
    def rehearse3(focus='rehearse3', memory = 'isa:word position:three word:?word'):
        DM.add(memory)
        thinky.say(word)
        print word
        DM.request('isa:word position:four')
        focus.set('rehearse4')

    def rehearse4(focus='rehearse4', memory = 'isa:word position:four word:?word'):
        DM.add(memory)
        thinky.say(word)
        print word
        DM.request('isa:word position:five')
        focus.set('rehearse5')
    
    def rehearse5(focus='rehearse5', memory = 'isa:word position:five word:?word'):
        DM.add(memory)
        thinky.say(word)
        print word
        focus.set('retrieve')

    def retrieve(focus='retrieve'):
        DM.request('isa:word')
        print "remembering"
        focus.set('recall')

    def recall(focus='recall', memory = 'isa:word word:?word'):
        print word
        reca.say(word)
        #DM.add(memory)
        DM.request('isa:word', require_new=True)
        focus.set('recall1')

    def recall1(focus='recall1', memory = 'isa:word word:?word'):
        print word
        reca.say(word)
        #DM.add(memory)
        DM.request('isa:word', require_new=True)
        focus.set('recall3')
    def recall3(focus='recall3', memory = 'isa:word word:?word'):
        print word
        reca.say(word)
        #DM.add(memory)
        DM.request('isa:word', require_new=True)
        focus.set('recall4')
    def recall4(focus='recall4', memory = 'isa:word word:?word'):
        print word
        reca.say(word)
        #DM.add(memory)
        DM.request('isa:word', require_new=True)
        focus.set('recall2')

    def recall2(focus='recall2', memory = 'isa:word word:?word'):
        print word
        reca.say(word)
        #DM.add(memory)
        focus.set('stop')
    
       
    
    def Iforgotfam(DM='error:True'):
        print "fuck"
        #DM.add(memory)
        focus.set('stop')
      
        
    def stop_production(focus='stop'):
        #print word
        speeky.dump()
        thinky.dump()
        reca.dump()
        self.stop()
GossipGirl=MyAgent()                              # name the agent
online=MyEnvironment()                     # name the environment
online.agent=GossipGirl                           # put the agent in the environment
ccm.log_everything(online)                 # print out what happens in the environment

online.run()                               # run the environment
ccm.finished()       