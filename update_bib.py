import os
import requests

# 설정 (Scopus ID와 API Key는 그대로 유지)
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def fetch_scopus_data():
    # JSON 형식으로 데이터를 요청합니다 (406 에러 방지)
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "query": f"AU-ID({AUTHOR_ID})",
        "view": "COMPLETE",
        "sort": "coverDate"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        
        with open(FILENAME, "w", encoding="utf-8") as f:
            for entry in entries:
                # 개별 논문 정보를 BibTeX 형식으로 변환하여 기록
                title = entry.get("dc:title", "No Title")
                author = entry.get("dc:creator", "Unknown")
                journal = entry.get("prism:publicationName", "")
                year = entry.get("prism:coverDate", "").split("-")[0]
                doi = entry.get("prism:doi", "")
                
                bib_entry = f"@article{{{doi if doi else title[:10]},\n"
                bib_entry += f"  title = {{{title}}},\n"
                bib_entry += f"  author = {{{author}}},\n"
                bib_entry += f"  journal = {{{journal}}},\n"
                bib_entry += f"  year = {{{year}}},\n"
                bib_entry += f"  doi = {{{doi}}}\n"
                bib_entry += "}\n\n"
                f.write(bib_entry)
        print(f"✅ {len(entries)}개의 논문을 publications.bib에 저장했습니다.")
    else:
        print(f"❌ 오류 발생: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_scopus_data()
