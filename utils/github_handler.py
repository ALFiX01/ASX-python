import requests
import os

class GitHubHandler:
    def __init__(self, github_token=None): # Добавили параметр github_token
        self.download_folder = "downloads"
        self.github_token = github_token # Сохраняем токен

    def download_release(self, github_repo_url, filename):
        os.makedirs(self.download_folder, exist_ok=True)
        filepath = os.path.join(self.download_folder, filename)

        try:
            release_info = self._get_latest_release_info(github_repo_url)
            if not release_info:
                print(f"Error: No release info found for {github_repo_url}")
                return None

            download_url = None
            for asset in release_info['assets']:
                if filename.lower() in asset['name'].lower(): # Ищем файл по имени
                    download_url = asset['browser_download_url']
                    break

            if not download_url:
                print(f"Error: File '{filename}' not found in release assets for {github_repo_url}")
                return None

            headers = {}
            if self.github_token: # Если токен есть, добавляем в headers
                headers['Authorization'] = f'token {self.github_token}'

            print(f"DEBUG: download_release() - Request Headers: {headers}") # *** Debug output ***

            response = requests.get(download_url, stream=True, headers=headers) # Передаем headers в request
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return filepath

        except requests.exceptions.RequestException as e:
            print(f"Error downloading from GitHub: {e}")
            return None

    def _get_latest_release_info(self, github_repo_url):
        api_url = github_repo_url.replace("github.com", "api.github.com/repos") + "/releases/latest"
        headers = {}
        if self.github_token: # Если токен есть, добавляем в headers
            headers['Authorization'] = f'token {self.github_token}'

        print(f"DEBUG: _get_latest_release_info() - Request Headers: {headers}") # *** Debug output ***

        try:
            response = requests.get(api_url, headers=headers) # Передаем headers в request
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching release info: {e}")
            return None