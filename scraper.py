from selenium import webdriver
from lxml import etree


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

baseUrl = 'https://www.viff.org/Online'



