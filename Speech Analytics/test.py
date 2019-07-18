# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:46:39 2019

@author: kpmg
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
  
def sentiment_scores(sentence): 
  
    sid_obj = SentimentIntensityAnalyzer() 
   
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
    print("Sentence Overall Rated As", end = " ") 
   
    if sentiment_dict['compound'] >= 0.05 : 
        return ("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        return ("Negative") 
  
    else : 
        return ("Neutral") 

from watson_developer_cloud import ToneAnalyzerV3
tone_analyzer = ToneAnalyzerV3(
   version='2017-09-21',
   iam_apikey='azcAYWvPk1INaDXNa-dGY0AqW6jl8qvqXAAwSqE5DtRQ',
   url='https://gateway-syd.watsonplatform.net/tone-analyzer/api'
)
#text = 'Team, I know that times are tough! Product '\
#   'sales have been disappointing for the past three '\
#   'quarters. We have a competitive product, but we '\
#   'need to do a better job of selling it!'\
#   'if you cannot sell, bugger off'



import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak Anything")
    audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print("You said: {}".format(text))
        sentiment = sentiment_scores(text)
        print(sentiment)
        tone_analysis = tone_analyzer.tone({'text': text},'application/json').get_result()
        #print(tone_analysis)
        if ( len(tone_analysis['document_tone']['tones'])>0):
            print("Below are the emotions captured:")
        for tone in tone_analysis['document_tone']['tones']:    
            print(tone['tone_name'])
            
    except:
        print("Sorry, please speak again!")


        
