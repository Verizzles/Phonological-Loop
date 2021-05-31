import ccm
import pyttsx3
from speech import *
from ccm.lib.actr import * 

"""
This program will hopefully allow people to run experiments using a phonological loop in python ACT-R
Words should be presented in a list form ala: list = ["word1", "word2" , "word3".......etc]
The speech feels a bit gimmicky but it's a fun gimmick and I'm sticking to it
I also name my variables wildly because I am making this up as I go along and I like to use cusswords when I'm frustrated
"""

"""
SOME LISTS THAT WE NEED TO BE GLOBALLY AVAILABLE BECAUSE PYTHON IS HARD AND I DON'T KNOW WHAT I'M DOING
these lists will be used further down to manage the words
"""
liz=[]  #this list is just to cycle through words intially. It's probably superfluous but whatever
lizz = [] #this list will contain chunks to be added to the declarative memory
lizzz = [] #this list will contain chunks to cue recall from the declarative memory


class Taint():
  
          
    
  def __init__(self):
    self.busy=False
   
      
         
  def speak(self,text, ate = 50, voice = 1):           
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - ate)
    engine.setProperty('voice', voice) 
    engine.say(text) #comment out if you don't want to hear Wall-E read to you
    engine.runAndWait()
    engine.runAndWait()
    
  """
  very ugly method to get words in a form that they can be added to the declarative memory and later recalled
  remove the #'s from the print statements to make sure the strings look like some good shit ACT-R chunks
  """  
  def word(self, text):
    p = text
    word = ("isa:word" + " word:"+ p)
    return word
    

  
  


    
    
class Loop(ccm.Model):
   
  
  

  def __init__(self):    
    self.huff = Taint()
    
    
    
  """
  This will just say everything and append the words to liz[]
  """
  #def speaks(self,text):
  #  self.huff.speak(text)
  """
  This will say everything and add the words to the declarative memory
  """
  def words(self, text):
    
    com = self.huff.word(text)
    
    return com
    
  
    


    
    