import os
import yaml
import subprocess
from tkinter import *
from gtts import gTTS


from PIL import Image, ImageTk
from urllib.request import urlopen
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    output = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for name, value in attrs:
                if str(value).endswith("jpg") and name == 'src':
                    self.output.append(value)
                    return


class Actions:
    photoImg=[]
    ON_CUSTOM_RESPONDING_OPEN = []
    ROOT_PATH = os.path.realpath(os.path.join(__file__, '..'))

    def getURL(self, text):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls and len(urls[0]) > 4:
            response = urlopen(urls[0])
            imgName = urls[0].split('/')
            html = response.read()
            parser = MyHTMLParser()
            parser.feed(str(html))
            try:
                imgurl = 'http:' + parser.output[0]
                print("\n\ndownload url:"+imgurl, len(self.photoImg))

                # Save image file
                img = urlopen(imgurl)
                imgFile = '{}/resource/temp/image.jpg'.format(Actions.ROOT_PATH)
                with open(imgFile, 'wb') as localFile:
                    localFile.write(img.read())
                localFile.close()
                parser.output.clear()

                # print image
                image1 = Image.open(imgFile)
                os.remove(imgFile)
                image1 = image1.resize((250, 250), Image.ANTIALIAS)
                self.photoImg.append(ImageTk.PhotoImage(image1))
                Actions.chatBox.image_create('end', image=self.photoImg[-1])
                Actions.chatBox.insert('end', ' '+imgName[-1].replace('_', ' ')+"\n", ('g', 'tag_def'))
            except Exception as error:
                print(error)

    def chatUpdate(chat, per):
        chat = (chat+'\n').encode()
        Actions.chatBox.configure(state='normal')
        Actions.chatBox.tag_config("tag_def", foreground="black", lmargin1=10, lmargin2=10, spacing3=5)

        # http://effbot.org/tkinterbook/text.htm
        if per == 2:
            Actions.chatBox.tag_config("g", justify='left', background="yellow")
            Actions().getURL(str(chat))
            Actions.chatBox.insert('end', chat, ('g', 'tag_def'))
        elif per == 1:
            Actions.chatBox.tag_config("b", justify='right', background="pink", foreground="black", rmargin=10,
                                       lmargin1=10, lmargin2=10)
            Actions.chatBox.insert('end', chat, ('b', 'tag_def'))

        Actions.chatBox.configure(state='disabled')
        Actions.chatBox.see('end')


with open('{}/resource/yaml/Open.yaml'.format(Actions.ROOT_PATH), 'r') as conf:
    application_list = yaml.load(conf)


# ------------------------------Start Text to speech converter---------------------
def speakOut(words):
    sayFile='{}/resource/temp/say.mp3'.format(Actions.ROOT_PATH)
    language='en'
    print(' ', {"text": words})
    tts = gTTS(text=words, lang=language)
    tts.save(sayFile)
    os.system('mpg123 '+sayFile)
    os.remove(sayFile)
# ------------------------------End Text to speech converter---------------------


# ------------------------------Start of Open Application Functions-------------------------------
def openFileOption(fileLoc = [], tst=0):
    cmd = 'xdg-open \"' + str(fileLoc[tst]) + '\"'
    print('shell command:', cmd)
    subprocess.call(cmd, shell=True)
    fileName = fileLoc[0].split('/')[-1]
    print('opened \"' + fileName + '\" from \"' + fileLoc[0] + '\"')
    # speakOut('opened ' + fileName)
# ------------------------------End of Open File Functions-------------------------------


# ------------------------------Start of Open Application Functions-------------------------------
def openFun(query,uassistant):
    print('ON_CUSTOM_RESPONDING_STARTED')
    query=str(query).lower()
    sidx=query.index('open')+len('open')
    eidx=query.index("'}")
    query=query[sidx:eidx]

    if 'from' in query:
        tmp = query.split('from')
        fileName = tmp[0].strip()
        userLoc = tmp[1].strip()
        userLoc = userLoc.replace(' / ', '/')

        if os.path.isdir('/' + userLoc) and len(userLoc) > 1:
            userLoc = '/' + userLoc + '/'
        else:
            print('File not found:', fileName, 'in /'+userLoc)
            # speakOut("Sorry can't open " + query)
            print('ON_CUSTOM_RESPONDING_FINISHED')
            return
        # cmd="find '/loc/' -type f -iname *'file'*"
        cmd = 'find ' + userLoc + " -type f -iname *'" + fileName.strip() + "'*"
        print('shell command:', cmd)
        return_value = str(subprocess.check_output(cmd, shell=True))[2:-1]
        fileLoc = return_value.split('\\n')
        Actions.ON_CUSTOM_RESPONDING_OPEN = fileLoc

        if len(fileLoc) > 6:
            print('there are ' + str(len(fileLoc) - 1) + ' files with the the search key name')
            # speakOut('many files found with search key ')

        elif len(fileLoc) > 2 and len(fileLoc) <= 6:
            # speakOut('There are ' + str(len(fileLoc)-1) + ' files. Say which one you chose to open, example: first one')
            print("\n\nOption\tDetail")
            for loc in fileLoc:
                fileName = loc.split('/')[-1]
                print(str(fileLoc.index(loc) + 1) + '\t\t' + fileName.strip())

            uassistant.start_conversation()
            return

        elif len(fileLoc) > 1:
            openFileOption(fileLoc)
        else:
            print('file not found')
            # speakOut('file not found')

        Actions.ON_CUSTOM_RESPONDING_OPEN = []

    else:
        appName = str(query.strip())
        keys = [key for key, value in (application_list['Open']['Application']).items() if appName in value]
        if keys:
            appCmd=keys[0]

            # cmd="'app' & disown"
            cmd = appCmd+' & disown'
            try:
                subprocess.call(cmd, shell=True)
                print('shell command:', cmd)
                # speakOut('opening '+query)
            except Exception as error:
                print('Error Command:', cmd)
                # speakOut("Sorry can't open "+query)
        else:
            print('Application not found: ', appName)
            # speakOut(appName+' not found: ')

    print('ON_CUSTOM_RESPONDING_FINISHED')

# ------------------------------End of Open Application Functions-------------------------------

# ------------------------------Start of Close Application Functions-------------------------------
def closeFun(query):
    print('ON_CUSTOM_RESPONDING_STARTED')
    query=str(query).lower()
    sidx=query.index('close')+len('close')
    eidx=query.index("'}")
    query=query[sidx:eidx]
    appName = str(query.strip())

    keys = [key for key, value in (application_list['Open']['Application']).items() if appName in value]

    if (keys):
        appCmd=keys[0]
        # cmd="killall 'app'"
        cmd='killall '+appCmd
        try:
            t=subprocess.call(cmd, shell=True)
            if t == 0:
                print('shell command:', cmd)
                # speakOut('closed ' + query)
            else:
                print('Error Command:', cmd)
                # speakOut(appName + ' not opened')

        except Exception:
            print('Error Command:', cmd)
            # speakOut(appName+' not opened')
    else:
        print('Application not found: ', appName)
        # speakOut(appName+' not found')

    print('ON_CUSTOM_RESPONDING_FINISHED')

# ------------------------------End of Close Application Functions-------------------------------
