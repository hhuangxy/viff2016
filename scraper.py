from selenium import webdriver
from datetime import datetime
from lxml import etree
import csv
import re
import omdb


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


def getNextUrl (html):
  """Get next URL
  """

  nextUrl = ''

  # Get current page
  raw = html.xpath('//li[@class="av-paging-links active"]/span[@class="current"]/text()')
  if raw:
    currPage = int(raw[0])
    nextPage = currPage + 1

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

  newLine = ''.join(c if (32 <= ord(c) and ord(c) <= 255) else ' ' for c in line)
  newLine = ' '.join(newLine.strip(',').split())

  return newLine


def isDuringWork (dateObj):
  """Determine if this is during work
  """

  afterFive = dateObj.hour >= 18
  weekend  = dateObj.weekday() >= 5
  if (weekend or afterFive):
    return 'N'
  else:
    return 'Y'


def compileListMovies (chrome, baseUrl, fName):
  """Traverse site for list of movies
  """

  dictMovies = {}
  nextUrl = baseUrl
  pageCnt = 0
  while True:
    # Get page
    page = getPage(chrome, nextUrl)
    pageCnt += 1

    # Get list of movies
    movies = page.xpath('//div[@class="item-name"]/a')

    # Add title and url to movie dictionary
    for movie in movies:
      title = stripChar(movie.text)
      url   = movie.attrib['href']
      if title not in dictMovies:
        dictMovies[title] = url

    # Get next URL
    nextUrl = getNextUrl(page)
    if nextUrl == '':
      break
    nextUrl = baseUrl + '/' + nextUrl

  # Write dictMovies to file
  keys = sorted(dictMovies.keys())
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)
    for key in keys:
      if baseUrl in dictMovies[key]:
        plink = dictMovies[key]
      else:
        plink = baseUrl + '/article/' + dictMovies[key].split('permalink=')[-1]

      # Title can be inconsistent so only save the link
      row = [plink]
      cwr.writerow(row)

  return 'compileListMovies: %d page(s)' % pageCnt


def compileListGenres (chrome, baseUrl, fName):
  """Traverse site for genres
  """

  currYear = str(datetime.today().year)
  genres = {
    "Action, Thrills & Suspense"   : currYear + '-genre-action',
    "Comedy"                       : currYear + '-genre-comedy',
    "Documentary"                  : currYear + '-genre-documentary',
    "Drama"                        : currYear + '-genre-drama',
    "Experimental & Avant Garde"   : currYear + '-genre-experimental',
    "Fantasy, Sci-fi & Horror"     : currYear + '-genre-fantasy',
    "Romance"                      : currYear + '-genre-romance',
    "Shorts"                       : currYear + '-shorts'
  }

  pageCnt = compileListGeneric(chrome, baseUrl, fName, genres)

  return 'compileListGenres: %s page(s)' % pageCnt


def compileListSeries (chrome, baseUrl, fName):
  """Traverse site for series
  """

  currYear = str(datetime.today().year)
  series = {
    "Altered States"              : currYear + '-series-altered-states',
    "BC Spotlight"                : currYear + '-series-bcspotlight',
    "Contemporary World Cinema"   : currYear + '-series-contemporaryworldcinema',
    "Dragons & Tigers"            : currYear + '-series-dragonsandtigers',
    "Focus on Italy"              : currYear + '-series-focusonitaly',
    "Future//Present"             : currYear + '-series-future-present',
    "Galas"                       : currYear + '-series-galas',
    "Gateway"                     : currYear + '-series-gateway',
    "High School Outreach"        : currYear + '-education',
    "Impact"                      : currYear + '-series-impact',
    "Insights"                    : currYear + '-series-insights',
    "MODES"                       : currYear + '-series-modes',
    "Shorts Programs"             : 'shorts-' + currYear,
    "Special Presentations"       : currYear + '-series-specialpresentations',
    "Spotlight on France"         : currYear + '-series-spotlightfrance',
    "True North"                  : currYear + '-series-true-north',
    "Vanguard"                    : currYear + '-series-vanguard'
  }

  pageCnt = compileListGeneric(chrome, baseUrl, fName, series)

  return 'compileListSeries: %s page(s)' % pageCnt


def compileListThemes (chrome, baseUrl, fName):
  """Traverse site for themes
  """

  currYear = str(datetime.today().year)
  themes = {
    "Action, Thrills & Suspense"      : currYear + '-theme-action',
    "Adventures Outdoors"             : currYear + '-theme-adventure',
    "Animals"                         : currYear + '-theme-animals',
    "Animation"                       : currYear + '-theme-animation',
    "Architecture"                    : currYear + '-theme-architecture',
    "Art & Photography"               : currYear + '-theme-art-photography',
    "Award Winners"                   : currYear + '-theme-award-winners',
    "Biography"                       : currYear + '-theme-biography',
    "Buddhist Interest"               : currYear + '-theme-buddhist-interest',
    "Comedy"                          : currYear + '-theme-comedy',
    "Crime"                           : currYear + '-theme-crime',
    "Dance"                           : currYear + '-theme-dance',
    "Drama"                           : currYear + '-theme-drama',
    "Economics & Globalization"       : currYear + '-theme-economics',
    "Environment"                     : currYear + '-theme-environment',
    "Experimental & Avant Garde"      : currYear + '-theme-experimental',
    "Family Relations"                : currYear + '-theme-family-relations',
    "Fantasy, Sci-fi & Horror"        : currYear + '-theme-fantasy',
    "Filmmaking"                      : currYear + '-theme-filmmaking',
    "Food, Farm & Garden"             : currYear + '-theme-food',
    "Health"                          : currYear + '-theme-health',
    "Human Rights & Social Justice"   : currYear + '-theme-human-rights',
    "High School Program"             : currYear + '-education',
    "History"                         : currYear + '-theme-history',
    "Immigration"                     : currYear + '-theme-immigration',
    "Indigenous"                      : currYear + '-theme-indigenous',
    "Islamic World"                   : currYear + '-theme-islamic-world',
    "Jewish Interest"                 : currYear + '-theme-jewish-interest',
    "LGBTQ"                           : currYear + '-theme-lgbtq',
    "Literary"                        : currYear + '-theme-literary',
    "Music"                           : currYear + '-theme-music',
    "Mystery"                         : currYear + '-theme-mystery',
    "Politics"                        : currYear + '-theme-politics',
    "Religion, Spirituality & Myth"   : currYear + '-theme-religion',
    "Romance"                         : currYear + '-theme-romance',
    "Science & Technology"            : currYear + '-theme-science',
    "Sex & Eroticism"                 : currYear + '-theme-sex',
    "Theatre"                         : currYear + '-theme-theatre',
    "War & Espionage"                 : currYear + '-theme-war',
    "Women Directors"                 : currYear + '-theme-women-directors',
    "Youth Under 18 May Attend"       : currYear + '-youth'
  }

  pageCnt = compileListGeneric(chrome, baseUrl, fName, themes)

  return 'compileListThemes: %s page(s)' % pageCnt


def compileListGeneric (chrome, baseUrl, fName, srchDict):
  """Generic list compilier
  """

  dictMovies = {}
  pageCnt = []
  for crit in srchDict:
    nextUrl = baseUrl + '/article/' + srchDict[crit]
    pageCnt.append(0)
    while True:
      # Get page
      page = getPage(chrome, nextUrl)
      pageCnt[-1] += 1

      # Get list of movies
      movies = page.xpath('//div[@class="item-name"]/text()')
      movies = [stripChar(m) for m in movies]

      # Add search criteria to movie dictionary
      for movie in movies:
        if movie in dictMovies:
          dictMovies[movie].append(crit)
        else:
          dictMovies[movie] = [crit]

      # Get next URL
      nextUrl = getNextUrl(page)
      if nextUrl == '':
        break
      nextUrl = baseUrl + '/article/' + nextUrl

  # Write dictMovies to file
  keys = sorted(dictMovies.keys())
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)
    for key in keys:
      s = sorted(uniqify(dictMovies[key]))
      s = [stripChar(z) for z in s]
      row = [key, ' | '.join(s)]
      cwr.writerow(row)

  return pageCnt


def getRatings (omdb, dictMovies):
  """Ratings list compilier
  """

  dictMovies['IMDB'] = 'NA'
  dictMovies['RT']   = 'NA'

  # Search IMDB and RT
  result = omdb.search(title=dictMovies['Title'])
  if result:
    result = result.json()
    if result['Response'] != 'False':
      ratings = result['Ratings']
      for r in ratings:
        if r['Source'] == 'Internet Movie Database':
          dictMovies['IMDB'] = r['Value']
        elif r['Source'] == 'Rotten Tomatoes':
          dictMovies['RT']   = r['Value']

  return 'getRatings Ok!'


def parseMovieInfo (omdb, bigDict, html, url, listDictMovies):
  """Parse webpage for movie info
  """

  miniInfo = {}

  dictXpath = {
    'Title'         : '//h1[@class="movie-title"]',
    'Description'   : '//div[@class="movie-description"]',
    'Category'      : '//h1[@class="movie-title"]/../h5',
    'Running Time'  : '//div[@class="movie-information"]'
  }
  for key in dictXpath:
    miniInfo[key] = 'NA'
    temp = html.xpath(dictXpath[key])

    # No matches
    if not temp:
      continue
    temp = temp[0]

    # Strip tags
    etree.strip_tags(temp, '*')
    if not temp.text:
      continue
    temp = temp.text

    if key == 'Running Time':
      m = re.search(r'(\d+ mins?)', temp, re.I)
      if not m:
        continue
      miniInfo[key] = m.group(0)
    else:
      miniInfo[key] = stripChar(temp)

  # Fill in genre, series, etc
  for key in bigDict:
    miniInfo[key] = 'NA'
    if miniInfo['Title'] in bigDict[key]:
      miniInfo[key] = bigDict[key][miniInfo['Title']]

  # Add ratings
  getRatings(omdb, miniInfo)

  # Add URL
  miniInfo['URL'] = url

  # Look for dates
  dates = html.xpath('//span[@class="start-date"]/text()')
  for d in dates:
    dObj = datetime.strptime(d, '%A, %B %d, %Y at %I:%M %p')
    miniInfo['Date'] = dObj.strftime('%d %b')
    miniInfo['Time'] = dObj.strftime('%H:%M')
    miniInfo['During Work'] = isDuringWork(dObj)

    listDictMovies.append(miniInfo.copy())

  return 'parseMovieInfo Ok!'


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
    'During Work',
    'IMDB',
    'RT',
    'Genre',
    'Series',
    'Themes',
    'URL'
  ]

  # Open file
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)

    # Write header
    cwr.writerow(keys)

    # Build/write rows
    for d in listDict:
      row = [d[k] for k in keys]
      cwr.writerow(row)

  return 'Ok!'


def traverseMovies (chrome, omdb, fList, fGenre, fSeries, fThemes, fOut):
  """Get get movie info from list of URL
  """

  bigDict = {}

  # Load data
  dictFiles = {
    'URL'    : fList,
    'Genre'  : fGenre,
    'Series' : fSeries,
    'Themes' : fThemes
  }
  for key in dictFiles:
    if key == 'URL':
      bigDict[key] = []
    else:
      bigDict[key] = {}
    with open(dictFiles[key], 'r') as csvfile:
      for line in csv.reader(csvfile):
        line = [l.strip() for l in line]
        if line[0] != '':
          if key == 'URL':
            bigDict[key].append(line[0])
          else:
            bigDict[key][line[0]] = line[1]

  # Parse for movie info
  listDictMovies = []
  for url in bigDict['URL']:
    page = getPage(chrome, url)
    parseMovieInfo(omdb, bigDict, page, url, listDictMovies)

  # Write to csv
  return writeCsv(fOut, listDictMovies)


if __name__ == '__main__':
  baseUrl = 'https://www.viff.org/Online'
  cc = startSession()
  oa = omdb.Api(apikey='5dcad8c4')
  print(compileListMovies(cc, baseUrl, 'movies.csv'))
  print(compileListGenres(cc, baseUrl, 'genres.csv'))
  print(compileListSeries(cc, baseUrl, 'series.csv'))
  print(compileListThemes(cc, baseUrl, 'themes.csv'))
  print(traverseMovies(cc, oa, 'movies.csv', 'genres.csv', 'series.csv', 'themes.csv', 'output.csv'))

