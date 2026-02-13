import os
import requests
import time

# 설정
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def fetch_all_scopus_data():
    all_entries = []
    start = 0
    count = 25 # 한 페이지당 가져올 수 있는 최대치
    
    while True:
        url = "https://api.elsevier.com/content/search/scopus"
        headers = {
            "X-ELS-APIKey": API_KEY,
            "Accept": "application/json"
        }
        params = {
            "query": f"AU-ID({AUTHOR_ID})",
            "view": "STANDARD",
            "sort": "coverDate",
            "start": start,
            "count": count
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get("search-results", {}).get("entry", [])
            
            if not entries:
                break
                
            all_entries.extend(entries)
            
            # 전체 개수 확인
            total_results = int(data.get("search-results", {}).get("opensearch:totalResults", 0))
            print(f"🔄 진행 중: {len(all_entries)} / {total_results}")
            
            if len(all_entries) >= total_results:
                break
                
            start += count
            time.sleep(0.5) # 서버 부하 방지
        else:
            print(f"❌ 오류 발생: {response.status_code}")
            break

    if all_entries:
        with open(FILENAME, "w", encoding="utf-8") as f:
            for entry in all_entries:
                title = entry.get("dc:title", "No Title")
                author = entry.get("dc:creator", "Unknown")
                journal = entry.get("prism:publicationName", "Unknown Journal")
                date = entry.get("prism:coverDate", "0000")
                year = date.split("-")[0] if "-" in date else date
                doi = entry.get("prism:doi", "")
                
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
        print(f"✅ 완료: 총 {len(all_entries)}개의 논문을 저장했습니다.")

if __name__ == "__main__":
    fetch_all_scopus_data()
