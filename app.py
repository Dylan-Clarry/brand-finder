import requests, sys, webbrowser, bs4, urllib, os, json
from textblob import TextBlob

# gets website links based on google search results with a given query and limit
def google_search_results(query, limit):
	url = f'https://google.com/search?q={query}&num={limit}'
	res = requests.get(url)
	print(res.status_code)
	res.raise_for_status()

	soup = bs4.BeautifulSoup(res.text, "html.parser")
	result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})

	print(len(result_div))

	websites = []
	for result in result_div:
		try:
			link = result.find('a', href=True)
			title = result.find('div', attrs={'class': 'vvjwJb'}).get_text()
			description = result.find('div', attrs={'class': 's3v9rd'}).get_text()
			print('Title:', title)

			if link != '' and title != '' and description != '':
				website = {
					'title': title,
					'link': f'https://google.com{link.get("href")}',
					'description': description,
					'social-media': []
				}
				websites.append(website)
		except:
			continue

	return websites

# check if social media link is valid
def valid_sm_link(link):
	count = link.count('/')
	if(count > 4):
		return False
	return True

# find all social media links on website
def find_social_media_links(website):
	sm_sites = ['facebook.com', 'twitter.com']

	url = website['link']
	res = requests.get(url)
	soup = bs4.BeautifulSoup(res.content, 'html.parser')
	website_links = soup.find_all('a', href=True)
	print(len(website_links))

	sm_found = []
	for sm in sm_sites:
		for link in website_links:
			link = link.attrs['href']
			if sm in link and valid_sm_link(link):
				sm_found.append(link)
	sm_found = list(set(sm_found))
	print(sm_found)
	return sm_found

# exclude websites that are known to be unwanted
def filter_websites_by_excludes(websites, excludes):
	filteredwebsites = []
	for website in websites:
		link = website['link']
		if not any(exclude in link for exclude in excludes):
			filteredwebsites.append(website)
	return filteredwebsites

# filter out websites based on keywords
def filter_website_by_keywords(websites, keywords):
	filteredwebsites = []
	for website in websites:
		words = website['description'].split()
		for keyword in keywords:
			if keyword in words:
				filteredwebsites.append(website)
				break;
	return filteredwebsites

# reads json array from file
def json_to_arr(file):
	if os.path.isfile(file):
		with open(file, 'r') as read_file:
			data = json.load(read_file)
			print(data)
	read_file.close()
	return data

# write output json file
def write_output_json(data, file):
	with open(file, 'w') as write_file:
		json.dump(data, write_file, indent=4)
	write_file.close()


if __name__ == "__main__":

	# get search queries
	file = './queries.json'
	queries = json_to_arr(file)
	print(queries)

	# get keywords
	file = './keywords.json'
	keywords = json_to_arr(file)
	print(keywords)

	# get exclude keywords
	file = './excludes.json'
	excludes = json_to_arr(file)
	print(excludes)

	limit = 25
	websites = []
	for query in queries:
		print("query:", query)
		search_results = google_search_results(query, limit)
		websites.extend(search_results)

	filteredwebsitesbyexclude = filter_websites_by_excludes(websites, excludes)
	filteredwebsites = filter_website_by_keywords(filteredwebsitesbyexclude, keywords)

	print("filtered websites:", len(filteredwebsites))

	for website in filteredwebsites:
		try:
			print(website['title'])
			sm = find_social_media_links(website)
			if len(sm) > 0:
				website['social-media'] = sm
		except:
			continue

	for website in filteredwebsites:
		print(json.dumps(website, indent=4))

	# output results to json file
	write_output_json(filteredwebsites, './output.json')