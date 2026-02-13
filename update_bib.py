import os
import requests
import time

# 설정
AUTHOR_ID = "55773731500"
API_KEY = os.getenv("SCOPUS_API_KEY")
FILENAME = "publications.bib"

def fetch_detailed_data(eid):
    """EID를 사용하여 모든 저자, 초록, Article Number를 가져옵니다."""
    url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200: return None
        
        core = resp.json().get("abstracts-retrieval-response", {})
        item = core.get("item", {}).get("bibrecord", {}).get("head", {})
        
        # 1. 모든 저자명 추출 (Full Name)
        author_group = item.get("author-group", [])
        if isinstance(author_group, dict): author_group = [author_group]
        
        all_authors = []
        for group in author_group:
            authors = group.get("author", [])
            if isinstance(authors, dict): authors = [authors]
            for au in authors:
                preferred = au.get("preferred-name", {})
                name = f"{preferred.get('ce:surname', '')}, {preferred.get('ce:given-name', '')}"
                if name.strip() == ",": name = au.get("ce:indexed-name", "Unknown")
                all_authors.append(name)
        
        # 2. 초록 추출
        abstract = core.get("coredata", {}).get("dc:description", "")
        
        # 3. Article Number (Item Number) 추출
        article_num = core.get("coredata", {}).get("prism:number", "")
        
        return {
            "authors": " and ".join(all_authors),
            "abstract": abstract,
            "article_number": article_num
        }
    except:
        return None

def main():
    all_entries = []
    start = 0
    
    # 목록 검색
    while True:
        url = "https://api.elsevier.com/content/search/scopus"
        headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
        params = {"query": f"AU-ID({AUTHOR_ID})", "view": "STANDARD", "start": start, "count": 25}
        
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200: break
        entries = res.json().get("search-results", {}).get("entry", [])
        if not entries: break
        all_entries.extend(entries)
        if len(all_entries) >= int(res.json()["search-results"]["opensearch:totalResults"]): break
        start += 25
        time.sleep(0.3)

    # 상세 정보 통합 및 저장
    with open(FILENAME, "w", encoding="utf-8") as f:
        for i, entry in enumerate(all_entries):
            eid = entry.get("eid")
            title = entry.get("dc:title")
            print(f"🔄 처리 중 ({i+1}/{len(all_entries)}): {title[:40]}...")
            
            detail = fetch_detailed_data(eid)
            
            # 기본 정보
            journal = entry.get("prism:publicationName", "")
            year = entry.get("prism:coverDate", "").split("-")[0]
            vol = entry.get("prism:volume", "")
            iss = entry.get("prism:issueIdentifier", "")
            pages = entry.get("prism:pageRange", "")
            doi = entry.get("prism:doi", "")
            
            # 상세 정보 적용
            authors = detail["authors"] if detail else entry.get("dc:creator", "Unknown")
            abstract = detail["abstract"] if detail else ""
            art_num = detail["article_number"] if detail else ""

            # BibTeX 쓰기
            bib_id = doi.replace("/", "_") if doi else eid
            f.write(f"@article{{{bib_id},\n")
            f.write(f"  title = {{{title}}},\n")
            f.write(f"  author = {{{authors}}},\n")
            f.write(f"  journal = {{{journal}}},\n")
            f.write(f"  year = {{{year}}},\n")
            if vol: f.write(f"  volume = {{{vol}}},\n")
            if iss: f.write(f"  number = {{{iss}}},\n")
            if art_num: f.write(f"  note = {{Article Number: {art_num}}},\n")
            elif pages: f.write(f"  pages = {{{pages}}},\n")
            if abstract: f.write(f"  abstract = {{{abstract}}},\n")
            if doi: f.write(f"  doi = {{{doi}}}\n")
            f.write("}\n\n")
            time.sleep(0.2) # API 속도 제한 준수

    print(f"✅ 모든 정보가 포함된 {len(all_entries)}개의 논문을 저장했습니다.")

if __name__ == "__main__":
    main()
