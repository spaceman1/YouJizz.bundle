import re, time

NAME = 'YouJizz'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

YJ_BASE = 'http://www.youjizz.com'
YJ_POPULAR = 'http://www.youjizz.com/most-popular/%s.html'
YJ_NEWEST = 'http://www.youjizz.com/newest-clips/%s.html'
YJ_TOPRATED = 'http://www.youjizz.com/top-rated/%s.html'
YJ_RANDOM = 'http://www.youjizz.com/random.php'
YJ_SEARCH = 'http://www.youjizz.com/search/%s-%s.html'

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'


####################################################################################################

def Start():
	Plugin.AddPrefixHandler('/video/youjizz', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
	Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')

	MediaContainer.title1 = NAME
	MediaContainer.art = R(ART)

	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)

	HTTP.CacheTime = 3600
	HTTP.Headers['User-Agent'] = USER_AGENT


####################################################################################################

def Thumb(url):
	try:
		data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))

def GetDurationFromString(duration):
	try:
		durationArray = duration.split(":")
		if len(durationArray) == 3:
			hours = int(durationArray[0])
			minutes = int(durationArray[1])
			seconds = int(durationArray[2])
		elif len(durationArray) == 2:
			hours = 0
			minutes = int(durationArray[0])
			seconds = int(durationArray[1])
		elif len(durationArray)	==	1:
			hours = 0
			minutes = 0
			seconds = int(durationArray[0])
		return int(((hours)*3600 + (minutes*60) + seconds)*1000)
	except:
		return 0


####################################################################################################

def MainMenu():
	dir = MediaContainer()
	dir.Append(Function(DirectoryItem(MovieList, L('Most Popular')), url=YJ_POPULAR))
	dir.Append(Function(DirectoryItem(MovieList, L('Newest')), url=YJ_NEWEST))
	dir.Append(Function(DirectoryItem(MovieList, L('Top Rated')), url=YJ_TOPRATED))
	dir.Append(Function(DirectoryItem(MovieList, L('Random')), url=YJ_RANDOM))
	dir.Append(Function(DirectoryItem(CategoriesMenu, L('Categories')), url=YJ_SEARCH))
	dir.Append(Function(InputDirectoryItem(Search, L('Search'), L('Search'), thumb=R(ICON)), url=YJ_SEARCH))
	return dir

def CategoriesMenu(sender,url):
	dir = MediaContainer(title2 = sender.itemTitle)
	keywords = ['amateur','anal','asian','bbw','big-butt','big-tits','bisexual','blonde','blowjob','brunette','coed','compilation','couples','creampie','cumshots','cunnilingus','dildos','dp','ebony','european','facial','fantasy','fetish','fingering','funny','gay','german','gonzo','group','hairy','handjob','hentai','instructional','interracial','interview','kissing','latina','lesbian','masturbate','mature','milf','old','panties','pantyhose','pov','public','redhead','rimming','romantic','shaved','shemale','solo-girl','solo-male','squirting','strt-sex','swallow','teen','threesome','toys','vintage','voyeur','webcam','young']
	for x in keywords:
		xCapitalized = x.capitalize()
		dir.Append(Function(DirectoryItem(SearchMovieList, L(xCapitalized)), url=url, SearchQuery=x, SearchType='categories'))
	return dir

def MovieList(sender,url,page=1):
	if url == YJ_POPULAR:
		dir = MediaContainer(title2 = 'Most Popular - Page: '+str(page))
	elif url == YJ_NEWEST:
		dir = MediaContainer(title2 = 'Newest - Page: '+str(page))
	elif url == YJ_TOPRATED:
		dir = MediaContainer(title2 = 'Top Rated - Page: '+str(page))
	else:
		dir = MediaContainer(title2 = sender.itemTitle+' - Page: '+str(page))
	if page > 1:
		pagem = page-1
		dir.Append(Function(DirectoryItem(MovieList, L('+++Previous Page ('+str(pagem)+')+++')), url=url, page=pagem))
	if url == YJ_RANDOM:
		pageContent = HTML.ElementFromURL(url, cacheTime=0)
	else:
		pageContent = HTML.ElementFromURL(url % str(page))
	for videoItem in pageContent.xpath('//span[@id="miniatura"]'):
		videoItemTitle = videoItem.xpath('span[@id="title1"]')[-1].text.strip()
		videoItemLink  = YJ_BASE + videoItem.xpath("span/a")[0].get('href')
		videoItemThumb = videoItem.xpath('span/img')[0].get('src')
		duration = videoItem.xpath('span[@id="title2"]/span[@class="thumbtime"]/span')[-1].text.strip()
		videoItemViews = videoItem.xpath('span[@id="title2"]/span[@class="thumbviews"]/span')[-1].text.strip()
		videoItemRating = round(((float(videoItem.xpath('span[@id="title2"]/span[@class="thumbrating"]/span')[0].get('style').strip('width: ').strip('px;')))/17*2),2)
		videoItemSummary = 'Duration: ' + duration
		videoItemSummary += '\r\nViews: ' + videoItemViews
		videoItemSummary += '\r\nRating: ' + str(videoItemRating)
		videoItemDuration = GetDurationFromString(duration)
		dir.Append(Function(VideoItem(PlayVideo, title=videoItemTitle, summary=videoItemSummary, duration=videoItemDuration, rating=videoItemRating, thumb=Function(Thumb, url=videoItemThumb)), url=videoItemLink))
	if len(pageContent.xpath('//div[@id="pagination"]/a[contains(text(),"Next")]')) == 1:
		pagep = page+1
		dir.Append(Function(DirectoryItem(MovieList, title='+++Next Page ('+str(pagep)+')+++'), url=url, page=pagep))
	return dir

def SearchMovieList(sender,url,SearchQuery='anal',SearchType='categories',page=1):
	SearchQueryCapitalized = SearchQuery.capitalize()
	SearchTypeCapitalized = SearchType.capitalize()
	dir = MediaContainer(title2 = SearchTypeCapitalized+' - '+SearchQueryCapitalized+' - Page: '+str(page))
	if page > 1:
		pagem = page-1
		dir.Append(Function(DirectoryItem(SearchMovieList, L('+++Previous Page ('+str(pagem)+')+++')), url=url, page=pagem))
	pageContent = HTML.ElementFromURL(url % (SearchQuery,str(page)))
	for videoItem in pageContent.xpath('//span[@id="miniatura"]'):
		videoItemTitle = videoItem.xpath('span[@id="title1"]')[-1].text.strip()
		videoItemLink  = YJ_BASE + videoItem.xpath("span/a")[0].get('href')
		videoItemThumb = videoItem.xpath('span/img')[0].get('src')
		duration = videoItem.xpath('span[@id="title2"]/span[@class="thumbtime"]/span')[-1].text.strip()
		videoItemViews = videoItem.xpath('span[@id="title2"]/span[@class="thumbviews"]/span')[-1].text.strip()
		videoItemRating = round(((float(videoItem.xpath('span[@id="title2"]/span[@class="thumbrating"]/span')[0].get('style').strip('width: ').strip('px;')))/17*2),2)
		videoItemSummary = 'Duration: ' + duration
		videoItemSummary += '\r\nViews: ' + videoItemViews
		videoItemSummary += '\r\nRating: ' + str(videoItemRating)
		videoItemDuration = GetDurationFromString(duration)
		dir.Append(Function(VideoItem(PlayVideo, title=videoItemTitle, summary=videoItemSummary, duration=videoItemDuration, rating=videoItemRating, thumb=Function(Thumb, url=videoItemThumb)), url=videoItemLink))
	if len(pageContent.xpath('//div[@id="pagination"]/a[contains(text(),"Next")]')) == 1:
		pagep = page+1
		dir.Append(Function(DirectoryItem(SearchMovieList, title='+++Next Page ('+str(pagep)+')+++'), url=url, page=pagep))
	return dir


def Search(sender,url,query='',SearchType='search'):
	dir = MediaContainer()
	SearchQueryCorrect = query.replace(' ','-')
	dir = SearchMovieList(sender=None, url=url, SearchQuery=SearchQueryCorrect, SearchType=SearchType)
	return dir


####################################################################################################

def PlayVideo(sender, url):
	# we need to get the video file
	content = HTTP.Request(url).content
	vidurl = re.compile('so.addVariable\("file","(.+?)"\)').findall(content, re.DOTALL)
	if len(vidurl) > 0:
		Log(vidurl[0])
		return Redirect(vidurl[0])
	else:
		return None
