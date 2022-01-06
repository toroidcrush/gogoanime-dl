import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import compile
import concurrent.futures

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}


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
  try:
    dl_selection_link = BeautifulSoup(res, 'html.parser').find("li", class_="dowloads").find('a').get('href', None)
  except:
    return None
  
  # https://gogoplay1.com/download?id=MTA4MzY2&typesub=Gogoanime-DUB&title=Toriko+%28Dub%29+Episode+1
  if not dl_selection_link or 'gogo' not in dl_selection_link or 'download' not in dl_selection_link:
    with open(make_path('error.log'), mode='w') as f:
      f.write(dl_selection_link + '\n\n' + res)
    raise ValueError(f"Check {make_path('error.log')} for details")

  res = requests.get(url=dl_selection_link, headers=headers).text
  try:
    link = BeautifulSoup(res, 'html.parser').find(class_='dowload', text=compile('.*' + resolution + 'P.*')).find('a').get('href', None)
  except:
    return None

  # https://vidstreamingcdn.com/cdn23/42af3549e7b9a129b2bd0bd84a5505df/EP.1.v1.720p.mp4?mac=diPDSnLMzpQbwZ%2Fscejy2qqr3KX%2F1%2Fp4i3EcU97s%2BBo%3D&expiry=1641184365227
  if not link or resolution not in link or '.mp4?' not in link:
    with open(make_path('error.log'), mode='w') as f:
      f.write(dl_selection_link + '\n\n' + link + '\n\n' + res)
    raise ValueError(f"Check {make_path('error.log')} for details")

  return link


def download_mp4(mp4_url, save_as):
  res = requests.get(mp4_url, stream=True, headers=headers)
  with open(save_as, 'wb') as f:
      for chunk in tqdm(res.iter_content(chunk_size=1024), desc=save_as):
          if chunk:
              f.write(chunk)
  return f'Downloaded: {mp4_url}'

def get_episode(url_to_ep, resolution, save_as):
  mp4_link = get_url_for_mp4(url_to_ep, resolution)
  if mp4_link is None:
    return f'Couldn\'t get link for {url_to_ep}'
  return download_mp4(mp4_link, save_as)


def main():
  # --- config --- #

  # replace the episode number with {nth_ep}
  # e.g.
  # https://www2.gogoanime.cm/girls-und-panzer-dub-episode-1
  # https://www2.gogoanime.cm/girls-und-panzer-dub-episode-{nth_ep}

  url_to_nth_ep = 'https://www3.gogoanime.cm/kakegurui-dub-episode-{nth_ep}'
  min_ep = 0
  max_ep = 2
  resolution = 720
  save_directory = r"D:\kakegurui"

  multithreading = True
  workers = 5

  # --- do not modify below here --- #

  resolution = str(resolution)
  os.makedirs(save_directory, exist_ok=True)

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
        # url = future_to_url[future]
        print(future.result() + '\n')


if __name__=='__main__':
  main()
