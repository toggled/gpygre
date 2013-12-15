import sys
from qt import *

class AssociativeListBox(QListBox):

    def __init__(self, *args):
        apply(QListBox.__init__,(self,)+args)
        self.text2key = {}
        self.key2text = {}
        self.connect(self, SIGNAL("selected(int)"),
                     self.slotItemSelected)

    def insertItem(self, text, key):
        QListBox.insertItem(self, text)
        self.text2key [self.count() - 1] = key
        self.key2text [key]=self.count() - 1

    def currentKey(self):
        return self.text2key[self.currentItem()]

    def setCurrentItem(self, key):
        if self.key2text.has_key(key):
            QListBox.setCurrentItem(self, self.key2text[key])

    def slotItemSelected(self, index):
        key=self.currentKey()
        self.emit(PYSIGNAL("itemSelected"),
                  (key, self.currentText()) )

    def removeItem(self, index):
        del self.text2key[self.currentItem()]
        del self.key2text[index]
        QListView.removeItem(self, index)

class MainWindow(QMainWindow):

    def __init__(self, *args):
        apply(QMainWindow.__init__, (self,) + args)
        self.listbox=AssociativeListBox(self)
        self.listbox.insertItem("Visible text 1", "key1")
        self.listbox.insertItem("Visible text 2", "key2")
        self.listbox.insertItem("Visible text 3", "key3")
        self.setCentralWidget(self.listbox)

        self.connect(self.listbox,PYSIGNAL( "itemSelected"), self.printSelection)

    def printSelection(self, key, text):
            print "Associated with", key, "is", text

def main(args):
    app=QApplication(args)
    win=MainWindow()
    win.show()
    app.connect(app, SIGNAL("lastWindowClosed()")
                                 , app
                                 , SLOT("quit()")
                                 )
    app.exec_loop()

if __name__=="__main__":
    main(sys.argv)
