from newspaper import Article
from datetime import datetime
import docx2txt

def parseUrl(url):
    article = Article(url)
    article.download()
    article.parse()
    
    # print (article.)
    if article.publish_date is None:
        article.publish_date = datetime.utcnow().date().isoformat().strftime("%Y-%m-%d")
    
    if article.authors is None:
        article.authors.append('Aagat Pokhrel')
    
    if article.text is None:
        article.text = 'No Text'

      
    document = {
        'title': article.title,
        'author': article.authors,
        'date': article.publish_date,
        'text': article.text,
        'image': article.top_image, 
        'images': article.images,
        'html': article.html,
        'slides': {},
    }

    return document

def parseText(text):
    document = {
        'title': 'Title Page',
        'author': 'Aagat Pokhrel',
        'date': datetime.utcnow().date().isoformat().strftime("%Y-%m-%d"),
        'text': text,
        'image': None, 
        'images': [],
        'html': None,
        'slides': {},
    }
    return document

def parseUpload(upload):

    # upload = docx2txt.process(upload)
    document = {
        'title': 'Title Page',
        'author': 'Aagat Pokhrel',
        'date': datetime.utcnow().date().isoformat().strftime("%Y-%m-%d"),
        'text': upload,
        'image': None, 
        'images': [],
        'html': None,
        'slides': {},
    }
    return document