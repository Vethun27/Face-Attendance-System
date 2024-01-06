import pygame.mixer
from gtts import gTTS

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("end_working.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("end_working.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == "__main__":
    text_to_convert = "Great Work, see you again"
    text_to_speech(text_to_convert)
