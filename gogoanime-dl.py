import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import compile
import concurrent.futures

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}


def make_path(filename):
  return os.path.join(os.path.dirname(__file__), filename)


def save_res_text(res, filename):
  with open(make_path(filename), mode='w', encoding='utf-8') as f:
    f.write(res)


def get_saved_res_text(filename):
  with open(make_path(filename), mode='r', encoding='utf-8') as f:
    return f.read()


def get_url_for_mp4(url_to_ep, resolution):

  res = requests.get(url=url_to_ep, headers=headers).text
  link = BeautifulSoup(res, 'html.parser').find("li", class_="dowloads").find('a').get('href', None)
  
  # https://gogoplay1.com/download?id=MTA4MzY2&typesub=Gogoanime-DUB&title=Toriko+%28Dub%29+Episode+1
  if not link or 'gogo' not in link or 'download' not in link: raise ValueError(link)

  res = requests.get(url=link, headers=headers).text
  link = BeautifulSoup(res, 'html.parser').find(class_='dowload', text=compile('.*' + resolution + 'P.*')).find('a').get('href', None)

  # https://vidstreamingcdn.com/cdn23/42af3549e7b9a129b2bd0bd84a5505df/EP.1.v1.720p.mp4?mac=diPDSnLMzpQbwZ%2Fscejy2qqr3KX%2F1%2Fp4i3EcU97s%2BBo%3D&expiry=1641184365227
  if not link or resolution not in link or 'mp4' not in link: raise ValueError(link)

  return link


def download_mp4(mp4_url, save_as):
  res = requests.get(mp4_url, stream=True, headers=headers)
  with open(save_as, 'wb') as f:
      for chunk in tqdm(res.iter_content(chunk_size=1024), desc=save_as):
          if chunk:
              f.write(chunk)


def get_episode(url_to_ep, resolution, save_as):
  mp4_link = get_url_for_mp4(url_to_ep, resolution)
  download_mp4(mp4_link, save_as)


def main():
  # --- config --- #

  # replace the episode number with {nth_ep}
  # e.g.
  # https://www2.gogoanime.cm/girls-und-panzer-dub-episode-1
  # https://www2.gogoanime.cm/girls-und-panzer-dub-episode-{nth_ep}

  url_to_nth_ep = 'https://www2.gogoanime.cm/girls-und-panzer-dub-episode-{nth_ep}'
  min_ep = 1
  max_ep = 12
  resolution = 720
  save_directory = r"D:\girls_und_panzer"

  multithreading = True
  workers = 5

  # --- do not modify below here --- #

  resolution = str(resolution)

  if not multithreading:
    for i in range(min_ep, max_ep + 1):
      url_to_ep = url_to_nth_ep.format(nth_ep=i)
      filename = url_to_ep.split('/')[-1] + '-' + resolution + 'p.mp4'
      save_as = os.path.join(save_directory, filename)

      if os.path.exists(save_as):
        continue

      get_episode(url_to_ep, resolution, save_as)

  else:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
      future_to_url = {}

      for i in range(min_ep, max_ep + 1):
        url_to_ep = url_to_nth_ep.format(nth_ep=i)
        filename = url_to_ep.split('/')[-1] + '-' + resolution + 'p.mp4'
        save_as = os.path.join(save_directory, filename)

        if os.path.exists(save_as):
          continue

        future_to_url[executor.submit(get_episode, url_to_ep, resolution, save_as)] = url_to_ep
        
      for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        print('Downloaded: ' + url + '\n')


if __name__=='__main__':
  main()

