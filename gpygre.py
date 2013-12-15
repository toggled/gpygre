from PySide.QtCore import *
from PySide.QtGui import *
import sys
import urllib
import re
from bs4 import BeautifulSoup as bs
import sys
import pickle
import maingui

def fetch_meaning(wordurl,word):
    wordpage = urllib.urlopen(wordurl).read()
    soupobj = bs(wordpage)
    ll = soupobj.find_all("table")
    u=None
    for i in ll:
        if word in str(i):
            u = str(i)

    if u is None:
        print "error"
        return ""

    ssp = bs(u)
    g = ssp.tr.td.font.next_sibling
    content = ""
    while g:
        if g.name != "center":
            content = content + str(g)
        g = g.next_sibling
    return content

def processurl(url,word):
    if word[0]!="a":
        url+=("/vb"+word[0])
    return url

def getword_wordurl_fromatag(url,atag):
    abc = atag['href'].split('.')[0]
    word,partsofspeech = abc.split('-')[0],abc.split('-')[1]
    return (word,partsofspeech,url+"/"+atag['href'])

class mainWindow(QMainWindow,maingui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(mainWindow,self).__init__(parent)
        self.setupUi(self)
        with open('abc.pickle','r') as f:
            self.cache = pickle.load(f)
        self.cached_wordlist= self.cache.keys()
        self.count = 0
        self.wordedit.returnPressed.connect(self.wordlist.clear)
        self.wordedit.returnPressed.connect(self.meaningtextEdit.clear)
        self.wordedit.returnPressed.connect(self.findmeaning)

        self.searchButton.clicked.connect(self.meaningtextEdit.clear)
        self.searchButton.clicked.connect(self.wordlist.clear)
        self.searchButton.clicked.connect(self.findmeaning)

        self.wordlist.currentItemChanged.connect(self.update_textedit)
        self.wordlist.itemClicked.connect(self.update_textedit)
        self.wordlist.itemActivated.connect(self.update_textedit)

        self.actionAbout_me.triggered.connect(self.showaboutdlg)
        self.actionPervious.triggered.connect(self.showprevios)
        self.actionNext.triggered.connect(self.shownext)

    def closeEvent(self,event):
        with open('abc.pickle','w') as f:
            if len(self.cache)<5:
                pickle.dump(self.cache,f)
            else:
                pickle.dump({},f)
        QMainWindow.closeEvent(self,event)

    def showprevios(self):
        if not self.cached_wordlist :
            return
        self.count -= 1
        self.count = self.count % len(self.cached_wordlist)
        word = self.cached_wordlist[self.count]
        print self.count
        self.word_meaning = self.cache[word]
        self.wordlist.clear()
        self.meaningtextEdit.clear()
        self.wordedit.setText(word)
        for key,val in self.word_meaning.items():
            self.update_listwidget(key[0],key[1])
            self.meaningtextEdit.setText(val)

    def shownext(self):
        if not self.cached_wordlist :
            return
        self.count += 1
        self.count = self.count % len(self.cached_wordlist)
        word = self.cached_wordlist[self.count]
        print self.count
        self.word_meaning = self.cache[word]
        self.wordlist.clear()
        self.meaningtextEdit.clear()
        self.wordedit.setText(word)
        for key,val in self.word_meaning.items():
            self.update_listwidget(key[0],key[1])
            self.meaningtextEdit.setText(val)


    def update_textedit(self,currentItem,previousItem=None):
        if currentItem:
            abc= currentItem.text().split('-')
            selectedword,partsofspeech = abc[0],abc[1]
            self.meaningtextEdit.setText(self.word_meaning[(selectedword,partsofspeech)])

    def showaboutdlg(self):
        import aboutgui
        class about_Dialog(QDialog,aboutgui.Ui_Dialog):
            def __init__(self,parent=None):
                super(about_Dialog,self).__init__(parent)
                self.setupUi(self)
        dlg = about_Dialog()
        dlg.exec_()

    def findmeaning(self):
        word = self.wordedit.text()
        if word == "":
            return
        self.word_meaning = get_meaning(word)
        self.count=0
        if self.word_meaning:
            self.cache[word] = self.word_meaning #build cache from each search result.
            self.cached_wordlist.append(word)
            for key,val in self.word_meaning.items():
                self.update_listwidget(key[0],key[1])

    def update_listwidget(self,word,partsofspeech):
        #QListWidgetItem(word,self.wordlist)
        self.wordlist.addItem(word+'-'+partsofspeech)

def get_meaning(word):
    url = "http://www.univsource.com/words"

    #all words except words starting with 'a' are listed in url+'/vb'+firstletter
    # suppose bolster and other words starting with 'b' are in url+'/vbb'
    wordlist_url = processurl(url,word)
    print wordlist_url
    #contents of the page containing the desired word
    content = urllib.urlopen(wordlist_url).read()
    pat=re.compile(word)
    # pat.findall(string) = finds all occurence of a pattern
    # pat.search(string) = find only one occurence
    soup = bs(content)

    #links of the words starting with the given word i.e, for 'reple', 'replenish' & 'replete' both
    #will be found
    links = soup.find_all("a",text=pat)
    if links is None:
        return None
    word_meaning={}
    for link in links:
        # if i search with reple , it will give me
        # (replenish,url+'/replenish-verb.htm')
        word,partsofspeech,wordurl = getword_wordurl_fromatag(url,link)
        print word,' ',wordurl
        meaning_usage = fetch_meaning(wordurl,word)
        word_meaning[(word,partsofspeech)] = meaning_usage
    return word_meaning
def initial_housekeeping():
    import os
    if not os.path.isfile('abc.pickle'):
        with open('abc.pickle','w') as f:
            pickle.dump({},f)

app = QApplication(sys.argv)
initial_housekeeping()
form = mainWindow()
form.show()
app.exec_()
