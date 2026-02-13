import os
import requests

# 설정
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def fetch_scopus_data():
    # 401 에러 방지를 위해 view를 STANDARD로 변경하고 필수 항목만 요청합니다.
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "query": f"AU-ID({AUTHOR_ID})",
        "view": "STANDARD", # 권한 문제를 피하기 위해 기본 뷰 사용
        "sort": "coverDate"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        
        if not entries:
            print("⚠️ 검색된 논문이 없습니다.")
            return

        with open(FILENAME, "w", encoding="utf-8") as f:
            for entry in entries:
                # 기본 뷰에서 제공하는 안전한 필드들만 추출
                title = entry.get("dc:title", "No Title")
                author = entry.get("dc:creator", "Unknown")
                journal = entry.get("prism:publicationName", "Unknown Journal")
                date = entry.get("prism:coverDate", "0000")
                year = date.split("-")[0] if "-" in date else date
                doi = entry.get("prism:doi", "")
                
                # BibTeX 포맷 생성
                bib_id = doi.replace("/", "_") if doi else title[:10].replace(" ", "")
                bib_entry = f"@article{{{bib_id},\n"
                bib_entry += f"  title = {{{title}}},\n"
                bib_entry += f"  author = {{{author}}},\n"
                bib_entry += f"  journal = {{{journal}}},\n"
                bib_entry += f"  year = {{{year}}},\n"
                if doi:
                    bib_entry += f"  doi = {{{doi}}}\n"
                bib_entry += "}\n\n"
                f.write(bib_entry)
        print(f"✅ 성공: {len(entries)}개의 논문 데이터를 저장했습니다.")
    else:
        print(f"❌ 오류 발생: {response.status_code}")
        print(f"상세 내용: {response.text}")

if __name__ == "__main__":
    fetch_scopus_data()
