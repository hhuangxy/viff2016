from selenium import webdriver
from datetime import datetime
from lxml import etree
import csv


def startSession ():
  """Start Chrome
  """

  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--incognito')
  chrome_options.add_experimental_option('prefs', {
    "profile.managed_default_content_settings.images"        : 2,
    "profile.managed_default_content_settings.plugins"       : 2,
    "profile.managed_default_content_settings.popups"        : 2,
    "profile.managed_default_content_settings.geolocation"   : 2,
    "profile.managed_default_content_settings.notifications" : 2,
    "profile.managed_default_content_settings.media_stream"  : 2
  })

  return webdriver.Chrome(chrome_options=chrome_options)


def getPage (chrome, url):
  """Get HTML webpage
  """

  # Go get page
  chrome.get(url)

  return etree.HTML(chrome.page_source)


def getListMovies (html):
  """Get list of movie titles
  """

  listMovies = []

  # Get list of movies
  listRaw = html.xpath('//div[@class="item-name"]/a')
  for raw in listRaw:
    listMovies.append(raw.attrib)

  return listMovies


def getNextUrl (html):
  """Get next URL
  """

  nextUrl = ''

  # Get current page
  raw = html.xpath('//li[@class="av-paging-links active"]/span[@class="current"]/text()')
  if raw:
    currentPage = int(raw[0])
    nextPage = currentPage + 1

    # Find next url
    listRaw = html.xpath('//li[@class="av-paging-links"]/a')
    for raw in listRaw:
      url = raw.attrib['href']

      if ('current_page=%i' % nextPage) in url:
        nextUrl = url
        break

  return nextUrl


def uniqify (seq, idfun=None):
  """Make list unique

  Taken from: https://www.peterbe.com/plog/uniqifiers-benchmark
  """

  if idfun is None:
    def idfun(x): return x

  seen = {}
  result = []
  for item in seq:
    marker = idfun(item)
    if marker in seen:
      continue

    seen[marker] = 1
    result.append(item)

  return result


def stripChar (line):
  """Strip unwanted characters from line
  """
  newLine = [c for c in line if ord(c) < 255]
  newLine = [c if (c.isalnum() or (c in ' \'/!|:",.')) else ' ' for c in newLine]
  newLine = ''.join(newLine).split()
  newLine = ' '.join(newLine).strip(',')

  return newLine


def writeCsv (fName, listDict):
  """Write to csv
  """

  keys = [
    'Title',
    'Description',
    'Category',
    'Running Time',
    'Date',
    'Time'
  ]

  # Open file
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)

    # Get header
    cwr.writerow(keys)

    # Build/write rows
    for d in listDict:
      row = [d[k] for k in keys]
      cwr.writerow(row)

  return 'Ok!'


def compileListMovies (chrome, baseUrl, fName):
  """Traverse site for list of movies
  """

  listMovies = []
  nextUrl = baseUrl
  while True:
    # Get page
    page = getPage(chrome, nextUrl)

    # Get list of movies
    listMovies += getListMovies(page)

    # Get next URL
    nextUrl = getNextUrl(page)
    if nextUrl == '':
      break

    nextUrl = baseUrl + '/' + nextUrl

  # Write listMovies to file
  with open(fName, 'w', newline='') as f:
    for movie in listMovies:
      f.write(movie['href'] + '\n')

  return 'Ok!'


def compileListGenres (chrome, baseUrl, fName):
  """Traverse site for genres
  """

  genres = {
    "Action, Thrills and Suspense" : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=FD335D3A-2B4E-49E6-A9AD-D903211473E5",
    "Comedy"                       : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=1F714C6A-C18A-40AE-984A-7598775B7CB8",
    "Documentary"                  : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=2A3F7BA0-632A-4F2A-904A-96C5BB4F30B5",
    "Drama"                        : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=51492B66-A572-4D43-9F60-F32FBAC897D8",
    "Experimental and Avant Garde" : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=6815B00E-49C0-40E7-9FAF-81AD4642A7BB",
    "Fantasy, Sci-fi and Horror"   : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=564BF55C-2F82-47A2-9F33-109D9918B494",
    "Romance"                      : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=C5AAC588-2D02-46B4-967C-FB2B822C33A9",
    "Shorts"                       : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=6CC8110C-DA38-4FD5-86B6-36711950D7E7"
  }

  dictMovies = {}
  for genre in genres:
    nextUrl = baseUrl + '/' + genres[genre]

    while True:
      # Get page
      page = getPage(chrome, nextUrl)

      # Get list of movies
      movies = page.xpath('//div[@class="item-name"]/text()')
      movies = [stripChar(m) for m in movies]

      # Add genre to movie
      for movie in movies:
        if movie in dictMovies:
          dictMovies[movie].append(genre)
        else:
          dictMovies[movie] = [genre]

      # Get next URL
      nextUrl = getNextUrl(page)
      if nextUrl == '':
        break

      nextUrl = baseUrl + '/' + nextUrl

  # Write dictMovies to file
  keys = sorted(dictMovies.keys())
  keys = [stripChar(k) for k in keys]
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)

    for key in keys:
      g = sorted(uniqify(dictMovies[key]))
      g = [stripChar(z) for z in g]
      row = [key, ' | '.join(g)]
      cwr.writerow(row)

  return 'Ok!'


def parseMovieInfo (html):
  """Parse webpage for movie info
  """

  movieInfo = []

  # Look for the title
  title = html.xpath('//h1[@class="movie-title"]/text()')[0]
  title = stripChar(title)

  # Look for movie description
  desc = html.xpath('//div[@class="movie-description"]')[0]
  etree.strip_tags(desc , '*')
  desc = stripChar(desc.text)

  # Look for category
  cat = html.xpath('//h1[@class="movie-title"]/../h5/text()')[0]
  cat = stripChar(cat).split('|')
  cat = [c.strip() for c in cat]
  cat = ' | '.join(sorted(cat))

  # Look for run time
  runtime = html.xpath('//div[@class="movie-information"]/div[4]')[0]
  etree.strip_tags(runtime , '*')
  runtime = runtime.text.split(':')[1]

  # Look for dates
  dates = html.xpath('//span[@class="start-date"]/text()')
  for d in dates:
    miniInfo = {}
    dObj = datetime.strptime(d, '%d %B %Y %I:%M %p')

    miniInfo['Title']        = title
    miniInfo['Description']  = desc
    miniInfo['Category']     = cat
    miniInfo['Running Time'] = runtime
    miniInfo['Date']         = dObj.strftime('%d %b')
    miniInfo['Time']         = dObj.strftime('%H:%M')

    movieInfo.append(miniInfo)

  return movieInfo


def traverseMovies (chrome, baseUrl, fIn, fOut):
  """Get get movie info from list of URL
  """

  # Load log
  listMovies = []
  with open(fIn, 'r') as f:
    for line in f:
      line == line.strip()
      if line == '':
        break

      listMovies.append(line)

  # Remove duplicates
  listMovies = uniqify(listMovies)

  # Parse for movie info
  listDictMovies = []
  for url in listMovies:
    page = getPage(chrome, baseUrl + '/' + url)
    listDictMovies += parseMovieInfo(page)

  # Write to csv
  writeCsv(fOut, listDictMovies)

  return 'Ok!'


baseUrl = 'https://www.viff.org/Online'

