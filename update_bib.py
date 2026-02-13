import os
import requests

# 교수님 정보 설정
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def fetch_scopus_data():
    # Scopus Search API 호출
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/x-bibtex"
    }
    params = {
        "query": f"AU-ID({AUTHOR_ID})",
        "view": "COMPLETE"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        with open(FILENAME, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ publications.bib 파일이 성공적으로 갱신되었습니다.")
    else:
        print(f"❌ 오류 발생: {response.status_code}")

if __name__ == "__main__":
    fetch_scopus_data()
