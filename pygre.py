import urllib
import re
from bs4 import BeautifulSoup as bs
import sys

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
    word = atag['href'].split('.')[0].split('-')[0]
    return (word,url+"/"+atag['href'])

def main():
    url = "http://www.univsource.com/words"
    word = sys.argv[1]
    #all words except words starting with 'a' are listed in url+'/vb'+firstletter
    # suppose bolster and other words starting with 'b' are in url+'/vbb'
    wordlist_url = processurl(url,word)

    #contents of the page containing the desired word
    content = urllib.urlopen(wordlist_url).read()

    pat=re.compile(word)
    # pat.findall(string) = finds all occurence of a pattern
    # pat.search(string) = find only one occurence
    soup = bs(content)

    #links of the words starting with the given word i.e, for 'reple', 'replenish' & 'replete' both
    #will be found
    links = soup.find_all("a",text=pat)
    for link in links:
        # if i search with reple , it will give me
        # (replenish,url+'/replenish-verb.htm')
        word,wordurl = getword_wordurl_fromatag(url,link)
        print word,' ',wordurl
        meaning_usage = fetch_meaning(wordurl,word)
        print meaning_usage

if __name__ == "__main__":
    main()
