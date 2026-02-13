import os
import requests
import time

# 설정
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def get_abstract(doi):
    """DOI를 이용해 개별 논문의 초록을 가져옵니다."""
    if not doi:
        return ""
    
    url = f"https://api.elsevier.com/content/abstract/doi/{doi}"
    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # 초록 필드 추출
            abstract = data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("dc:description", "")
            return abstract
        return ""
    except:
        return ""

def fetch_all_scopus_data():
    all_entries = []
    start = 0
    count = 25
    
    # 1. 논문 목록 가져오기
    while True:
        url = "https://api.elsevier.com/content/search/scopus"
        headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
        params = {
            "query": f"AU-ID({AUTHOR_ID})",
            "view": "STANDARD",
            "sort": "coverDate",
            "start": start,
            "count": count
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200: break
        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        if not entries: break
        all_entries.extend(entries)
        total_results = int(data.get("search-results", {}).get("opensearch:totalResults", 0))
        if len(all_entries) >= total_results: break
        start += count
        time.sleep(0.5)

    # 2. 개별 논문 상세 정보(초록) 통합 및 BibTeX 저장
    if all_entries:
        with open(FILENAME, "w", encoding="utf-8") as f:
            for i, entry in enumerate(all_entries):
                title = entry.get("dc:title", "No Title")
                doi = entry.get("prism:doi", "")
                
                print(f"🔄 초록 가져오는 중 ({i+1}/{len(all_entries)}): {title[:30]}...")
                abstract_text = get_abstract(doi)
                
                # 저자명 처리
                authors_raw = entry.get("author", [])
                if isinstance(authors_raw, list) and len(authors_raw) > 0:
                    author_list = [au.get("authname", au.get("dc:creator", "Unknown")) for au in authors_raw]
                    authors = " and ".join(author_list)
                else:
                    authors = entry.get("dc:creator", "Unknown")

                journal = entry.get("prism:publicationName", "Unknown Journal")
                year = entry.get("prism:coverDate", "0000").split("-")[0]
                volume = entry.get("prism:volume", "")
                issue = entry.get("prism:issueIdentifier", "")
                pages = entry.get("prism:pageRange", "")
                
                # BibTeX 생성
                bib_id = doi.replace("/", "_") if doi else title[:10].replace(" ", "")
                bib_entry = f"@article{{{bib_id},\n"
                bib_entry += f"  title = {{{title}}},\n"
                bib_entry += f"  author = {{{authors}}},\n"
                bib_entry += f"  journal = {{{journal}}},\n"
                bib_entry += f"  year = {{{year}}},\n"
                if volume: bib_entry += f"  volume = {{{volume}}},\n"
                if issue: bib_entry += f"  number = {{{issue}}},\n"
                if pages: bib_entry += f"  pages = {{{pages}}},\n"
                if abstract_text: bib_entry += f"  abstract = {{{abstract_text}}},\n"
                if doi: bib_entry += f"  doi = {{{doi}}}\n"
                bib_entry += "}\n\n"
                f.write(bib_entry)
                
                time.sleep(0.2) # API 제한 방지
        print(f"✅ 완료: 총 {len(all_entries)}개의 논문과 초록을 저장했습니다.")

if __name__ == "__main__":
    fetch_all_scopus_data()
