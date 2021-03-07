from flask import Flask, request, render_template
import pickle

app = Flask(__name__)

model = pickle.load(open("modelim.pickle", 'rb'))
tokenizer = pickle.load(open("tokenim.pickle", 'rb'))

diller = {0:'Afrikanca',1:'Almanca',2:'Arapça',3:'Arnavutça',4:'Azerbaycan Türkçesi',5:'Belarusça'
         ,6:'Bengalce',7:'Boşnakça',8:'Bulgarca',9:'Burmaca',10:'Danca',11:'Endonezce',12:'Estonyaca'
         ,13:'Farsça',14:'Felemenkçe',15:'Filipince',16:'Fince',17:'Fransızca',18:'Gürcüce',19:'Hintçe'
         ,20:'Hırvatça',21:'Japonca',22:'Korece',23:'Lehçe',24:'Letonca',25:'Litvanca',26:'Macarca'
         ,27:'Makedonca',28:'Malezya Dili',29:'Norveççe',30:'Portekizce',31:'Romence',32:'Rusça'
         ,33:'Slovakça',34:'Slovence',35:'Sırpça',36:'Tatarca',37:'Tayca',38:'Türkmence',39:'Türkçe'
         ,40:'Ukraynaca',41:'Urduca',42:'Uygurca',43:'Vietnamca',44:'Yunanca',45:'Çekçe',46:'Çince'
         ,47:'İbranice',48:'İngilizce',49:'İspanyolca',50:'İsveççe',51:'İtalyanca',52:'İzlandaca'}

def tahmin_et(metin):
    tokenized = tokenizer.transform([metin])
    try:
        tahmin = model.predict_classes(tokenized)
    except:
        tahmin = "Hata"
    return tahmin

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/', methods=['GET','POST'])
def yazi_al():
    req = request.form['text']
    text = str(req.lower())
    if request.method == "POST":
        if text.strip() == "" or text == None:
            text = "Metin veya ses dosyası ekleyin."
            return render_template("index.html", sonuc = text)

    if not tahmin_et(text) == "Hata":
        dil = diller[tahmin_et(text)[0]]
    else:
        dil = "Dil tanımlanamadı."

    return render_template("index.html", sonuc = dil)

if __name__ == "__main__":
    app.run(debug = True)
