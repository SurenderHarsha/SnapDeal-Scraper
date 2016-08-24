from bs4 import BeautifulSoup
import re
import MySQLdb
import pip._vendor.requests as r
import sqlite3


def scrape(a):
    try:
        quer=""
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        for i in a.split():
            quer+=i+"+"
        print "Number of results:"
        no_r=raw_input()
        quer=quer[:-1]
        q=r.get("http://www.snapdeal.com/search?keyword="+quer+"&santizedKeyword=&catId=&categoryId=0&suggested=false&vertical=&noOfResults="+no_r+"&searchState=&clickSrc=go_header&sort=rlvncyf",headers=headers)
        if q.status_code!=200:
            q.close()
            q=r.get("http://www.snapdeal.com/search?keyword="+quer+"&santizedKeyword=&catId=&categoryId=0&suggested=false&vertical=&noOfResults=48&searchState=&clickSrc=go_header&sort=rlvncyf",headers=headers)
        if q.status_code!=200:
            print "Could not connect to SnapDeal servers,Check your internet connection and try again!"
            return
        soup=BeautifulSoup(q.text,"html.parser")
        db=sqlite3.connect('my_sql')
        cur=db.cursor()
        name="snapdeal0"
        k=0
        while 1:
            try:
                cur.execute('create table '+name+'(name text,price real,rating real,image text)')
                break
            except:
                k+=1
                name=name[:-1]+str(int(name[-1])+k)
        n=soup.find_all('p')
        span=soup.find_all('span')
        names=[]
        for i in n:
            s=re.findall('.*class="product-title".*',str(i))
            if s!=[]:
                names.append(s)
        tname=[]
        for i in names:
            s=re.findall('title="(.*)"',str(i))
            tname.append(s)
        rat=[]
        for i in range(len(n)):
            s=re.findall('.*class="product-rating-count">(.*)<.*',str(n[i]))
            if re.findall('.*class="product-title".*',str(n[i-1]))!=[]:
                rat.append(s)
        pric=[]
        for i in span:
            s=re.findall('.*class="product-price" data-price="(.*)".*',str(i))
            if s!=[]:
                pric.append(s)
        img=soup.find_all('img')
        images=[]
        for i in img:
            s=re.findall('.*class="product-image.*" .*src="(.*)".*',str(i))
            if s!=[]:
                images.append(s)
        for i in range(len(rat)):
            j=images[i][0].split()
            if rat[i]==[]:
                cur.execute("insert into "+name+" values(?,?,?,?)",(tname[i][0],float(pric[i][0]),-1,j[0][:-1]))
                continue
            cur.execute("insert into "+name+" values(?,?,?,?)",(tname[i][0],float(pric[i][0]),float(rat[i][0][1:-1]),j[0][:-1]))
        db.commit()
        print "Sort By:\n1.Name\n2.Price\n3.Rating\n"
        t=['','name','price','rating']
        p=int(raw_input())
        print "1.Ascending Order\n2.Descending Order\n"
        f=['','asc','desc']
        l=int(raw_input())
        curs=db.execute('select * from '+name+' order by '+t[p]+' '+f[l])
        file=open(name+".html", "w")
        file.write('<p>Search for:'+quer+'</p>')
        file.write('<h1>Format=Name,Price,Rating,ImageLink</h1>')
        file.write('<table>')
        for row in curs:
            file.write('<tr><td>'+row[0]+'</td><td><h3>Rs.'+str(row[1])+'</h3></td><td>'+str(row[2])+'')
            file.write('<td><img src='+row[-1]+'></td></tr>')
        file.write('</table>')
        db.close()
        file.close()
        k=0
        name="snapdeal0"
        while 1:
            try:
                cur.execute('drop table '+name)
                name=name[:-1]+str(int(name[-1])+k)
                k+=1
            except:
                break
        return
    except:
        print "Please give a correct input!"
        return
a=raw_input("Name of the Product:")
scrape(a)
