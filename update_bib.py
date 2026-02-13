import requests
import time
import sys

# ==========================================
# [설정] ORCID ID
ORCID_ID = "0000-0001-5727-5716" 
OUTPUT_FILE = "publications.bib"
# ==========================================

# 사람인 척 속이는 헤더 (User-Agent)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_works_ids(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    
    print(f"Checking URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"Error accessing ORCID! Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}") # 에러 메시지 앞부분 출력
            return []
        
        data = response.json()
        works = data.get("group", [])
        print(f"Found {len(works)} work groups.")
        
        put_codes = []
        for work_group in works:
            summaries = work_group.get("work-summary", [])
            if summaries:
                # 가장 최신 버전의 ID(put-code) 가져오기
                code = summaries[0]["put-code"]
                put_codes.append(code)
                
        return put_codes
        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def get_bibtex(orcid_id, put_code):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    # BibTeX 요청용 헤더 설정
    bib_headers = HEADERS.copy()
    bib_headers["Accept"] = "application/x-bibtex"
    
    try:
        response = requests.get(url, headers=bib_headers, timeout=15)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch BibTeX for code {put_code}. Status: {response.status_code}")
            return None
    except:
        return None

def main():
    print(f"--- Starting Update for {ORCID_ID} ---")
    
    # 1. 논문 목록 가져오기
    put_codes = get_works_ids(ORCID_ID)
    
    if not put_codes:
        print("No works found. Please check ORCID visibility again.")
        # 빈 파일이라도 생성 (에러 방지)
        with open(OUTPUT_FILE, "w") as f: f.write("")
        return

    print(f"Downloading {len(put_codes)} papers...")
    
    # 2. 각 논문 상세 정보 다운로드
    all_bibtex = []
    count = 0
    
    for code in put_codes:
        bib = get_bibtex(ORCID_ID, code)
        if bib:
            all_bibtex.append(bib)
            count += 1
            print(f"Download success: {code}")
        time.sleep(0.2) # 너무 빠르면 차단될 수 있으므로 대기
        
    # 3. 파일 저장
    if all_bibtex:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_bibtex))
        print(f"--- SUCCESS! Saved {count} papers to {OUTPUT_FILE} ---")
    else:
        print("--- FAILED: Papers found but no BibTeX downloaded ---")

if __name__ == "__main__":
    main()
