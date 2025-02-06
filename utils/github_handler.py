import os
import requests
from config import GITHUB_API_URL, GITHUB_DOWNLOAD_FOLDER

class GitHubHandler:
    def __init__(self):
        self.api_url = GITHUB_API_URL
        self.download_folder = GITHUB_DOWNLOAD_FOLDER
        
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def download_release(self, repo_url, filename):
        """Download the latest release from a GitHub repository"""
        try:
            # Extract owner and repo from URL
            _, _, owner, repo = repo_url.rstrip('/').split('/')[-4:]
            
            # Get latest release
            api_url = f"{self.api_url}/repos/{owner}/{repo}/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_data = response.json()
            download_url = None
            
            # Find the appropriate asset
            for asset in release_data['assets']:
                if filename.lower() in asset['name'].lower():
                    download_url = asset['browser_download_url']
                    break
            
            if download_url:
                # Download the file
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                file_path = os.path.join(self.download_folder, filename)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return file_path
            
            return None
            
        except Exception as e:
            print(f"Error downloading from GitHub: {str(e)}")
            return None
