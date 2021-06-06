from django.shortcuts import render, HttpResponse
import time
from django.core.paginator import Paginator
from selenium import webdriver
from dergi.models import Dergi, AbstractnIndex, Editors, Volume, ArticlesInPress, PublishedArticles


def getData():  # programın çalıştığı ana fonksiyon
    html_content = ""
    page1link = []  # linkleri diziye atıyoruz
    for x in range(0, 1):  # 0 to 139 # sayfadaki linkleri geziyoruz.
        import requests
        USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        LANGUAGE = "en-US,en;q=0.5"
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        session.headers['Accept-Language'] = LANGUAGE
        session.headers['Content-Language'] = LANGUAGE
        if x == 0:
            html_content = session.get(
                f'https://www.elsevier.com/catalog?producttype=journal').text  # başlangıç sayfası
        else:
            k = x + 1
            html_content = session.get(f"https://www.elsevier.com/catalog?page=" + str(
                k) + "&cat0=&cat1=&cat2=&exclude=aggregations&exclude=categories&producttype=journal&series=&size=20&sort=datedesc").text  # pagenatör ile sayfanın değişen linkleri

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # tüm dergilerin ayrintili bağlanti linklerini aldik
        for data in soup.find_all('h5', class_='listing-products-info-text-title'):
            for a in data.find_all('a'):
                # print(a.get('href'))
                page1link.append(a.get('href'))  # for getting link
            # print(a.text)
    # print(page1link)
    veriAl(page1link)
    return html_content

def veriAl(links):

    metascore = []
    editorBoard = []
    links[16] = "https://www.journals.elsevier.com/underground-space"
    print(len(links))
    for link in links:  # linkleri teker teker ayırıyoruz
        if link == "https://www.journals.elsevier.com/chem" or link == "https://www.journals.elsevier.com/cell-chemical-biology" or link == "https://www.journals.elsevier.com/heliyon":  # Bu linkler başka sayfaya yönlendirilen linkler bu linkleri ayırıyoruz.
            continue
        if link == "https://www.elsevier.com/journals/underground-space/2467-9674":
            link = "https://www.journals.elsevier.com/underground-space"
        import requests
        USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        LANGUAGE = "en-US,en;q=0.5"
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        session.headers['Accept-Language'] = LANGUAGE
        session.headers['Content-Language'] = LANGUAGE
        editorLink = link + "/editorial-board"  # editor listesinin tutulduğu linkler
        volumeName = link.split("/")[-1]
        volumeLink = "https://www.sciencedirect.com/journal/" + volumeName + "/issues"
        articlesInPressLink = "https://www.sciencedirect.com/journal/" + volumeName + "/articles-in-press"
        # print(link)
        html_content = session.get(f'{link}').text
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            dergiAdi = soup.find('div', attrs={'class': 'publication-title'}).text  # dergi adını çektiğimiz kod
            dergiAdi = dergiAdi.strip()  # dergi adı karakter isimlerini düzenlediğimiz kod
        except:
            print("Dergi başka siteye ait")
            continue
        ISSN = soup.find('div', attrs={'class': 'issn keyword'}).text  # ıssn bilgilerinin tutulduğu yeri çeken kod
        ISSN = ISSN.strip()  # ıssn bilgilerinin karakter düzenlemesini yaptık
        ISSN = ISSN[5:]
        ISSN = ISSN.strip()
        _div = soup.find('div', attrs={'class': 'menu-item-content-sticky stickyList'})
        # uls = _div.find_all('ul',attrs={'class':'not-enum'})
        spans = _div.find_all('span', attrs={'class': 'tooltip'})
        CiteScore = "null"
        SNIP = "null"
        SJR = "null"
        try:
            if len(spans) > 0:
                CiteScore = str(spans[0].text)
                CiteScore = CiteScore.strip()
                CiteScore = CiteScore.partition('\n')[0]  # string işlemleri 6.9
                SNIP = str(spans[1].text)
                SNIP = SNIP.strip()
                SNIP = SNIP.partition('\n')[0]
                SJR = str(spans[2].text)
                SJR = SJR.strip()
                SJR = SJR.partition('\n')[0]
        except:
            print("JOURNAL METRİCS ALINAMADI")
        aimNscope = soup.find('div', attrs={'class': 'full-scope'})
        dergiYazi = aimNscope.text
        link2 = "https://www.elsevier.com/journals/" + dergiAdi.lower().replace(" ",
                                                                                "-") + "/" + ISSN + "/abstracting-indexing"
        # abstract indexing bilgilerinin gösterileceği link
        list_absn = absNindexAl(link2)  # abstracting indexing listesini tutuyor.
        editorList = getEditorList(editorLink)
        volumeList = getVolumeList(volumeLink)
        publishedArticles = getDataWithSelenium(volumeLink)
        print("NEXTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        articlesInPress = getArticlesInPress(articlesInPressLink)
        # print("fonksiyon sonu")
        link_ = "https://journalinsights.elsevier.com/journals/" + ISSN + "/oapt"  # online article publication time

        last_zaman = zamanAl(link_)  # oapt ler tutuluyor.. #online article publication time
        # print(last_zaman[0])#yil first last
        img_src = "https://secure-ecsd.elsevier.com/covers/80/Tango2/large/" + ISSN.replace("-", "") + ".jpg"
        d1 = Dergi(dergiAdi=dergiAdi, aimNscope=dergiYazi, ISSN=ISSN, citeScore=CiteScore, img_src=img_src,
                   SNIP=SNIP, SJR=SJR, last_year=last_zaman[0], first_score=last_zaman[1], final_score=last_zaman[2])
        d1.save()  # çektiğimiz bilgileri veri tabanına kaydediyoruz.
        for article in publishedArticles:
            year = article.get('year')
            number = article.get('number')
            published_article_obj = PublishedArticles(ISSN=Dergi.objects.get(ISSN=ISSN), Year=year, Number=number)
            published_article_obj.save()
        for volume in volumeList:
            year = volume.get('year')
            number = volume.get('number')
            volume_obj = Volume(ISSN=Dergi.objects.get(ISSN=ISSN), Year=year, PublicationNumber=number)
            volume_obj.save()
        for editor in editorList:
            name = editor.get('name')
            info = editor.get('info')
            editor_object = Editors(ISSN=Dergi.objects.get(ISSN=ISSN), Editor=name, EditorInfo=info)
            editor_object.save()
        for eleman in list_absn:
            a1 = AbstractnIndex(ISSN=Dergi.objects.get(ISSN=ISSN), list=eleman)
            a1.save()
        print(articlesInPress, "asdasdasdasdasd")
        articlesInPressObject = ArticlesInPress(ISSN=Dergi.objects.get(ISSN=ISSN), ArticleNumber=articlesInPress)
        articlesInPressObject.save()

def zamanAl(link):
    data = []
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{link}').text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    table = soup.find('table', attrs={'class': 'count3columns'})
    if table is not None:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values
        return data[0]

    elif table is None:
        return ["null", "null", "null"]


def getEditorList(link):  # Editör listesini çektiğimiz yer
    editorDict = []  # diziye atadık
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{link}').text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        mydivs = soup.findAll("div", {"class": "publication-editor"})
        for singleEditor in mydivs:
            editorName = singleEditor.find("div", {"class": "publication-editor-name"})  # editör adını çekdik.
            _editorName = editorName.find("h3").text
            editorSubject = singleEditor.find("span", {"class": "publication-editor-affiliation"}).text
            editorDict.append({'name': _editorName, 'info': editorSubject})
    except:
        editorDict.append({'name': "None", 'info': "None"})
        print(link + 'excepte girdi')
    print("return etti")
    return editorDict

#def getArticlesInPress(link):  # yayınlanan makaleler çekilen yer
    #import requests
    #USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    #LANGUAGE = "en-US,en;q=0.5"
    #session = requests.Session()
    #session.headers['User-Agent'] = USER_AGENT
    #session.headers['Accept-Language'] = LANGUAGE
    #session.headers['Content-Language'] = LANGUAGE
    #html_content = session.get(f'{link}').text
    #from bs4 import BeautifulSoup
    #soup = BeautifulSoup(html_content, 'lxml')

    #try:
        #oList = soup.find("ol", {"class": "js-article-list article-list-items"})
        #articlesNumber = oList.findAll("li", {"class",
                                              #"js-article-list-item article-item u-padding-xs-top u-margin-l-bottom"})
        #return len(articlesNumber)
    #except:
        #return 0


def article_İn_press_Pagination(url):
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{url}').text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    list2 = []
    pages = soup.find_all('span', attrs={'class': 'pagination-pages-label'})
    for page in pages:
        a = page.text
        number = max([int(word) for word in a.split() if word.isdigit()])

        for i in range(2, number + 1): # 2 den mi başlaması gerek yoksa 1 den neden 2
            urll = (url + '?page=' + str(i))
            list2.append(urll)
    return list2

def getArticlesInPress(link):  # yayınlanan makaleler çekilen yer
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{link}').text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    list5 = []

    try:
        oList = soup.find("ol", {"class": "js-article-list article-list-items"})
        articlesNumber = oList.findAll("li", {"class",
                                              "js-article-list-item article-item u-padding-xs-top u-margin-l-bottom"})
        list5.append(len(articlesNumber))

        b = article_İn_press_Pagination(link)
        for k in b:
            html_content = session.get(f'{k}').text
            soup = BeautifulSoup(html_content, 'lxml')

            oList = soup.find("ol", {"class": "js-article-list article-list-items"})
            articlesNumber2 = oList.findAll("li", {"class",
                                                   "js-article-list-item article-item u-padding-xs-top u-margin-l-bottom"})
            list5.append(len(articlesNumber2))

        return sum(list5)
    except:
        return 0

def getVolumeList(link):  # yayınlanacak makalelerinin tarih ve adet tuttuğumuz yer
    volumeDict = []  # diziye atadık
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{link}').text
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        myList = soup.findAll("li", {"class": "accordion-panel js-accordion-panel"})

        for volumeLink in myList:
            editorName = volumeLink.find("button", {
                "class": "accordion-panel-title u-padding-s-ver u-text-left text-l js-accordion-panel-title"})
            year = editorName.find("span", {"class": "accordion-title js-accordion-title"}).text
            year = year.split('—')[0]
            number = volumeLink.findAll("div", {"class": "issue-item u-margin-s-bottom"})
            volumeDict.append({'year': year, 'number': len(number)})
            break

    except:
        volumeDict.append({'name': "None", 'info': "None"})
        print(link + 'Volume Alınamadı')
    print(" volume return etti")
    return volumeDict


def absNindexAl(link):  # abstracting indexing çekilen yer
    absIndexList = []  # bilgileri diziye atadık.
    from bs4 import BeautifulSoup

    html_content = soupInstaller(link)
    soup = BeautifulSoup(html_content, 'html.parser')
    for ultag in soup.find_all('ul', attrs={'class': 'abstr-index-list'}):
        for litag in ultag.find_all('li'):
            # print(litag.text)
            absIndexList.append(litag.text)
    return absIndexList


def soupInstaller(link):
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{link}').text
    return html_content


def getDataWithSelenium(link):  # selenium çalışan yer
    articlesByYear = []  # makale tarihlerini diziye atadık
    from bs4 import BeautifulSoup
    html_content = soupInstaller(link)
    soup = BeautifulSoup(html_content, 'html.parser')
    driver_path = "C:/Users/can_8/OneDrive/Masaüstü/Yeni klasör/chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.maximize_window()
    driver.get(link)
    drop_down_buttons = soup.find_all("li", {"class": "accordion-panel js-accordion-panel"})
    print(len(drop_down_buttons), "buton sayisi")
    for i in range(1, len(drop_down_buttons) + 1):
        print(i, "İ SAYİSİ")
        if i == 6:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            # all-issues > ol > li:nth-child(6)
            drop_down = driver.find_element_by_css_selector(f"#all-issues > ol > li:nth-child({i})")
            drop_down.click()
            time.sleep(1)
            deneme = drop_down.find_element_by_tag_name("section")
            number = deneme.find_elements_by_tag_name("div")
            button = drop_down.find_element_by_tag_name("button")
            text = button.find_element_by_tag_name("span").text
            print(len(number), "///", text)
            articlesByYear.append({'year': text, 'number': len(number)})
        except Exception as e:
            articlesByYear.append({'year': "null", 'number': "null"})
            print(str(e))
        time.sleep(3)
    driver.close()
    print("SELENİUM VERİİİİİİİİİYİ ALDIIIIIIIIIIII")
    return articlesByYear


def home_view(request):  # anasayfa
    #html_content = getData()  #getData fonkiyonunun çalıştığı yer.Programın çalıştığı ilk yer.
    #asd = getVolumeList("https://www.sciencedirect.com/journal/veterinary-and-animal-science/issues")
    #getEditorList("https://www.journals.elsevier.com/current-opinion-in-toxicology/editorial-board")
    #getArticlesInPress("https://www.sciencedirect.com/journal/veterinary-and-animal-science/articles-in-press")
    #getDataWithSelenium("https://www.sciencedirect.com/journal/veterinary-and-animal-science/issues")
    dergiModel_list = Dergi.objects.all()
    AbstractModel = AbstractnIndex.objects.all()
    paginator = Paginator(dergiModel_list, 20)

    page_number = request.GET.get('page')
    dergiModel = paginator.get_page(page_number)
    return render(request, "index.html", {"dergiModel": dergiModel, "abstractModel": AbstractModel})


#def post_detail(request, id):
    #dergiModel = Dergi.objects.get(ISSN=str(id))
    #try:
        #volumes = Volume.objects.filter(ISSN=str(id))[0]
        #articleInPress = ArticlesInPress.objects.filter(ISSN=str(id))[0]
        #publishedArticles = PublishedArticles.objects.filter(ISSN=str(id))
    #except:
        #volumes = [{'year': "None", 'number': "None"}]
        #publishedArticles = [{'year': "None", 'number': "None"}]
        #articleInPress = 0

    #dergi = dergiModel
    #return render(request, 'details.html', {"publishedArticles": publishedArticles, "dergi": dergi, "volumes": volumes,
                                            #"articleInPress": articleInPress})


def post_detail(request, id):

    import re
    dergiModel = Dergi.objects.get(ISSN=str(id))

    try:


        volumes = Volume.objects.filter(ISSN=str(id))[0]
        articleInPress = ArticlesInPress.objects.filter(ISSN=str(id))[0]
        publishedArticles = PublishedArticles.objects.filter(ISSN=str(id))


        ids = PublishedArticles.objects.filter(ISSN=str(id)).values_list('Number', flat=True) # veri tabanından id numarasına göre Number değerlerini çekiyor.
        ids = list(ids) #çekilen değerler query objesidir. İşlem yapmak için list objesine dönüştürülüyor.

        mynewlist = [s for s in ids if s.isdigit()] #List içerisinde sadece sayısal değerler alınıyor.
        mynewlist = list(map(int, mynewlist)) #Alınan sayısal değerler int e çeriliyor.
        avrlist = sum(mynewlist) / len(mynewlist)  #list deki numberlerin ortalaması alınıyor.
        avrlist = str(round(avrlist, 2))  #Hesaplanan ortalama değer stringe dönüştürülüyor. ve virgülden sonra sadece iki digit göstermesi sağlanıyor.

        aaa = (avrlist)

        text = PublishedArticles.objects.filter(ISSN=str(id)).values_list('Year', flat=True)
        text = list(text)
        list2=[]
        for i in text:
            m = len(re.findall(r'\b\d+\b', i)) - 1
            list2.append(abs(m))
        avrlist2 = sum(list2) / len(list2)

        bb=(avrlist2)

        avrlist3 = sum(mynewlist) / len(mynewlist)

        avrlist3=(avrlist3)/avrlist2

        bbb = int(avrlist3)    #1

        ee=int(articleInPress.ArticleNumber)/bbb
        ee1=("{0:.2f}".format(ee))      #2

        eee = (int(articleInPress.ArticleNumber) % bbb)  # 3
        eeee= (int(articleInPress.ArticleNumber) - round(eee)) #4
        eeeee=(int(articleInPress.ArticleNumber) - round(eeee)) #5

        import math
        eeeeee = math.ceil(ee)  # 6

        abab = 12 / avrlist2 * eeeeee
        abab = ("{0:.2f}".format(abab))  # 7

    except:
        volumes = [{'year': "None", 'number': "None"}]
        publishedArticles = [{'year': "None", 'number': "None"}]
        articleInPress = 0


    dergi = dergiModel
    return render(request, 'details.html', {"publishedArticles": publishedArticles, "dergi": dergi, "volumes": volumes,
                                            "articleInPress": articleInPress,"aaa": aaa,"bb": bb,"bbb": bbb,"ee1": ee1,"eee": eee,"eeee": eeee,"eeeee": eeeee,"eeeeee": eeeeee,"abab": abab})


def abstractNindex(request, id):
    abstractModel = list(AbstractnIndex.objects.filter(ISSN=str(id)))
    dergi_ = Dergi.objects.get(ISSN=str(id))

    return render(request, 'abstract.html', {"list": abstractModel, "dergi": dergi_})


def editor_page(request, id):
    editor_list = list(Editors.objects.filter(ISSN=str(id)))
    dergi_ = Dergi.objects.get(ISSN=str(id))

    return render(request, 'editorview.html', {"list": editor_list, "dergi": dergi_})
