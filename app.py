from flask import Flask, request, render_template
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests
import pickle
import time
import re

nltk.download('stopwords')

app = Flask(__name__)

model = pickle.load(open("analizmodel", 'rb'))
tokenizer = pickle.load(open("analiztokenizer", 'rb'))

def veri(adres):
        url_yeni = ""
        url = adres
        sayac = 0
        for i in url:
            url_yeni += i
            if i == "/":
                sayac += 1
            if sayac == 6:
                break
            
        url_yeni = url.replace("dp/","product-reviews/")
        url = url_yeni + "ref=cm_cr_arp_d_paging_btm_next_1?ie=UTF8&reviewerType=all_reviews""&pageNumber="
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
        liste = []
        liste_uzunlugu = []
        sayfa = 1
        sonraki_sayfa = ""
        while True:
            sonraki_sayfa = url + str(sayfa)
            req = requests.get(sonraki_sayfa, headers=headers)
            soup = BeautifulSoup(req.content,"html.parser")
            texts = soup.find_all("span", attrs={"data-hook" : "review-body"})
            for i in range(len(texts)):
                liste.append(str([texts[i].find('span').text.strip()]))
            time.sleep(0.1)
            
            if len(liste_uzunlugu) > 0 and liste_uzunlugu.count(liste_uzunlugu[len(liste_uzunlugu)-1]) > 1:
                break
            
            sayfa += 1
            liste_uzunlugu.append(len(liste))

        yorumlar_temiz = []
        etkisizler = list(stopwords.words('Turkish'))
        for text in liste:
            x = str(text)
            x = text.lower()
            x = re.sub(r'\<a href', ' ', x)
            x = re.sub(r'&amp;', '', x)
            x = re.sub(r'<br />', ' ', x)
            x = re.sub(r"^\s+|\s+$", "", x)
            x = re.sub(r'[_"\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', x)
            x = re.sub(r'\'', ' ', x)
            x = re.sub('\s{2,}', ' ', x)
            x = re.sub(r'\s+[a-zA-Z]\s+', ' ', x)
            x = re.sub(r'\^[a-zA-Z]\s+', ' ', x)
            x = re.sub(r'\s+', ' ', x, flags=re.I)
            x = re.sub(r'^b\s+', '', x)
            x = re.sub(r'\W', ' ', str(x))
            x = x.split()
            x = [word for word in x if word not in etkisizler]
            x = ' '.join(x)
            yorumlar_temiz.append(x)
        return yorumlar_temiz

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/', methods=['GET','POST'])
def get_data():
    istek = request.form['text']
    url = str(istek.lower())
    if request.method == "POST":
        if url.strip() == "" or url == None:
            sonuc = "Bir bağlantı yazın."
            return render_template("index.html", sonuc = sonuc, miktar = "")
        else:
            gorusler = veri(url)
            tokenized = tokenizer.transform(gorusler)
            tahmin = model.predict(tokenized)
            y = [1 if i > 0.5 else 0 for i in tahmin]
            oran = (int(y.count(1))/len(y))*100
            sonuc = "Olumluluk: %{}".format("%.2f" % oran)
            yorum_sayisi = "Yorum Sayısı: {}".format(str(len(gorusler)))

    return render_template("index.html", sonuc = sonuc, miktar = yorum_sayisi)

if __name__ == "__main__":
    app.run(debug = True)
