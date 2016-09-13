from selenium import webdriver
from datetime import datetime
from lxml import etree
import csv
import re


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

  newLine = ''.join(c if (32 <= ord(c) && ord(c) <= 255) else ' ' for c in line)
  newLine = ' '.join(newLine.strip(',').split())

  return newLine


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
  listMovies = uniqify(listMovies)
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


def compileListSeries (chrome, baseUrl, fName):
  """Traverse site for series
  """

  series = {
    "Altered States"	             : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=EC7D5A6D-EC4D-4568-AF93-ABF27E20250F",
    "Arts and Letters"	           : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=D2E30BE6-23B6-4BB4-8A5B-A7FD48ED472B",
    "BC Spotlight"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=0A1CA5AA-123C-4410-B537-E279E4FF7E41",
    "Canadian Images"	             : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=8D2D6389-CF61-4D41-B41B-73E214257660",
    "Contemporary World Cinema"	   : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=3607CE49-AD16-4E9C-B969-3D69C842B243",
    "Creator Talks"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=08C03402-5156-4F53-9097-5641F8F92A08",
    "Documentaries"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=A976ADB5-1503-4059-9CDF-C7A5BB9CE90C",
    "Dragons and Tigers"	         : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=7443AFF9-DF25-4D7C-9A07-FC86AC40690D",
    "Episodic"	                   : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=C8AFF6CA-0C79-427F-9A8E-3CDFCA2FF90F",
    "Future//Present"	             : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=57318F0D-9744-4610-BF84-A0B5D4DDD313",
    "Galas"	                       : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=F2FD677F-5A35-4D89-82AF-E6CC4F593154",
    "High School Outreach"	       : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=ABC13DAA-FD73-46A4-B1F6-4ED6D0513418",
    "Industry Exchange"	           : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=C6056084-0F08-46FD-988E-2C3FA8AA07FB",
    "Nights at Hub"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=A8F16792-0D9D-4855-9F3F-F6DD05939097",
    "Shorts Programs"	             : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=91103A7D-A395-4E7B-BE9D-C0BCE7E0F362",
    "Special Presentations"	       : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=9B8D6AB5-9AD6-4F4D-8135-1EFD2AAE3793",
    "Spotlight on France"	         : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=9051B2CF-2D6F-45A0-ABCB-D0658D5CB757",
    "Style in Film"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=B5AFC27E-5C46-4F94-AF19-4ED18CFECB91",
    "Sustainable Production Forum" : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=57E3A7F5-A41A-42F2-B8FB-0880E26DE67A",
    "Totally Indie Day"	           : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=24517DB3-F73C-4640-A405-02B8589F67B7",
    "VIFF Impact"	                 : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=DFF45979-84C0-47B0-A630-F48FA61FDF76",
    "Virtual Reality"	             : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=91C31DA9-49AB-4A9C-91BC-7B1FE1829D3D",
    "VIFF Repeats"	               : "default.asp?doWork::WScontent::loadArticle=Load&BOparam::WScontent::loadArticle::article_id=18F35588-7839-47CE-B7AF-119CB661FE8B"
  }

  dictMovies = {}
  for ser in series:
    nextUrl = baseUrl + '/' + series[ser]

    while True:
      # Get page
      page = getPage(chrome, nextUrl)

      # Get list of movies
      movies = page.xpath('//div[@class="item-name"]/text()')
      movies = [stripChar(m) for m in movies]

      # Add series to movie
      for movie in movies:
        if movie in dictMovies:
          dictMovies[movie].append(ser)
        else:
          dictMovies[movie] = [ser]

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
      s = sorted(uniqify(dictMovies[key]))
      s = [stripChar(z) for z in s]
      row = [key, ' | '.join(s)]
      cwr.writerow(row)

  return 'Ok!'


def parseMovieInfo (html, genres, series):
  """Parse webpage for movie info
  """

  movieInfo = []

  # Look for the title
  title = html.xpath('//h1[@class="movie-title"]/text()')
  if title:
    title = stripChar(title[0])
  else:
    title = 'NA'

  # Look for movie description
  desc = html.xpath('//div[@class="movie-description"]')
  if desc:
    desc = desc[0]
    etree.strip_tags(desc , '*')
    desc = stripChar(desc.text)
  else:
    desc = 'NA'

  # Look for category
  cat = html.xpath('//h1[@class="movie-title"]/../h5/text()')
  if cat:
    cat = cat[0]
    cat = stripChar(cat).split('|')
    cat = [c.strip() for c in cat]
    cat = ' | '.join(sorted(cat))
  else:
    cat = 'NA'

  # Look for run time
  runtime = html.xpath('//div[@class="movie-information"]')
  if runtime:
    runtime = runtime[0]
    etree.strip_tags(runtime , '*')
    runtime = runtime.text
  else:
    runtime = 'NA'

  m = re.search(r'(\d+ mins?)', runtime, re.I)
  if m:
    runtime = m.group(0)

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

    if title in genres:
      miniInfo['Genre'] = genres[title]
    else:
      miniInfo['Genre'] = 'NA'

    if title in series:
      miniInfo['Series'] = series[title]
    else:
      miniInfo['Series'] = 'NA'

    movieInfo.append(miniInfo)

  return movieInfo


def writeCsv (fName, listDict):
  """Write to csv
  """

  keys = [
    'Title',
    'Description',
    'Category',
    'Running Time',
    'Date',
    'Time',
    'Genre',
    'Series'
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


def traverseMovies (chrome, baseUrl, fList, fGenre, fSeries, fOut):
  """Get get movie info from list of URL
  """

  # Load list
  listMovies = []
  with open(fList, 'r') as f:
    for line in f:
      line == line.strip()
      if line == '':
        break

      listMovies.append(line)

  # Load genres
  genres = {}
  with open(fGenre, 'r') as csvfile:
    crd = csv.reader(csvfile)

    for line in crd:
      line = [l.strip() for l in line]
      if line[0] == '':
        break

      genres[line[0]] = line[1]

  # Load series
  series = {}
  with open(fSeries, 'r') as csvfile:
    crd = csv.reader(csvfile)

    for line in crd:
      line = [l.strip() for l in line]
      if line[0] == '':
        break

      series[line[0]] = line[1]

  # Parse for movie info
  listDictMovies = []
  for url in listMovies:
    page = getPage(chrome, baseUrl + '/' + url)
    listDictMovies += parseMovieInfo(page, genres, series)

  # Write to csv
  writeCsv(fOut, listDictMovies)

  return 'Ok!'


baseUrl = 'https://www.viff.org/Online'

