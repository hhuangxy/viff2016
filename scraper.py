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


def compileListMovies (chrome, baseUrl, fName):
  """Traverse site for list of movies
  """

  listDictMovies = []
  nextUrl = baseUrl
  pageCnt = 0
  while True:
    # Get page
    page = getPage(chrome, nextUrl)
    pageCnt += 1

    # Get list of movies
    listDictMovies += getListMovies(page)

    # Get next URL
    nextUrl = getNextUrl(page)
    if nextUrl == '':
      break

    nextUrl = baseUrl + '/' + nextUrl

  # Serialize
  listMovies = []
  for dictMovies in listDictMovies:
    listMovies.append(dictMovies['href'])

  listMovies = uniqify(listMovies)

  # Write listMovies to file
  with open(fName, 'w') as f:
    for movie in listMovies:
      if baseUrl not in movie:
        pLink = movie.split('permalink=')[-1]
        movie = baseUrl + '/article/' + pLink

      f.write(movie + '\n')

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

      # Add genre to movie
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
  keys = [stripChar(k) for k in keys]
  with open(fName, 'w', newline='') as csvfile:
    cwr = csv.writer(csvfile)

    for key in keys:
      s = sorted(uniqify(dictMovies[key]))
      s = [stripChar(z) for z in s]
      row = [key, ' | '.join(s)]
      cwr.writerow(row)

  return pageCnt


def parseMovieInfo (html, bigDict):
  """Parse webpage for movie info
  """

  movieInfo = []
  miniInfo = {}

  dictXpath = {
    'Title'         : '//h1[@class="movie-title"]',
    'Description'   : '//div[@class="movie-description"]',
    'Category'      : '//h1[@class="movie-title"]/../h5',
    'Running Time'  : '//div[@class="movie-information"]'
  }
  for key in dictXpath:
    temp = html.xpath(dictXpath[key])

    # No matches
    if not temp:
      miniInfo[key] = 'NA'
      continue
    temp = temp[0]

    # Strip tags
    etree.strip_tags(temp, '*')
    if not temp.text:
      miniInfo[key] = 'NA'
      continue
    temp = temp.text

    if key == 'Running Time':
      m = re.search(r'(\d+ mins?)', temp, re.I)
      if not m:
        miniInfo[key] = 'NA'
        continue
      miniInfo[key] = m.group(0)
    else:
      miniInfo[key] = stripChar(temp)

  # Fill in genre, series, etc
  for key in bigDict:
    if miniInfo['Title'] in bigDict[key]:
      miniInfo[key] = bigDict[key][miniInfo['Title']]
    else:
      miniInfo[key] = 'NA'

  # Look for dates
  dates = html.xpath('//span[@class="start-date"]/text()')
  for d in dates:
    dObj = datetime.strptime(d, '%A, %B %d, %Y at %I:%M %p')
    miniInfo['Date'] = dObj.strftime('%d %b')
    miniInfo['Time'] = dObj.strftime('%H:%M')

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
    'Series',
    'Themes',
    'URL'
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


def traverseMovies (chrome, baseUrl, fList, fGenre, fSeries, fThemes, fOut):
  """Get get movie info from list of URL
  """

  # Load list
  listMovies = []
  with open(fList, 'r') as f:
    for line in f:
      line = line.strip()
      if line == '':
        break

      listMovies.append(line)

  bigDict = {}
  dictFiles = {
    'Genre' : fGenre,
    'Series' : fSeries,
    'Themes' : fThemes
  }
  for key in dictFiles:
    bigDict[key] = {}
    with open(dictFiles[key], 'r') as csvfile:
      crd = csv.reader(csvfile)

      for line in crd:
        line = [l.strip() for l in line]
        if line[0] == '':
          break

        bigDict[key][line[0]] = line[1]

  # Parse for movie info
  listDictMovies = []
  for url in listMovies:
    page = getPage(chrome, url)
    lm = parseMovieInfo(page, bigDict)
    for l in lm:
      l['URL'] = url
      listDictMovies.append(l)

  # Write to csv
  writeCsv(fOut, listDictMovies)

  return 'Ok!'


if __name__ == '__main__':
  baseUrl = 'https://www.viff.org/Online'
  cc = startSession()
  print(compileListMovies(cc, baseUrl, 'movies.csv'))
  #print(compileListGenres(cc, baseUrl, 'genres.csv'))
  #print(compileListSeries(cc, baseUrl, 'series.csv'))
  #print(compileListThemes(cc, baseUrl, 'themes.csv'))
  print(traverseMovies(cc, baseUrl, 'movies.csv', 'genres.csv', 'series.csv', 'themes.csv', 'output.csv'))

