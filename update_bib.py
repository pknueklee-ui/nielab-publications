import requests
import time
import json

# ==========================================
# [설정] ORCID ID
ORCID_ID = "0000-0001-5727-5716" 
OUTPUT_FILE = "publications.bib"
# ==========================================

def get_works_ids(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    # [중요] 브라우저인 척 속이는 헤더 추가
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"📡 ORCID 서버에 접속 시도: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ 접속 실패! 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return []
    
    data = response.json()
    works = data.get("group", [])
    print(f"✅ 발견된 논문 그룹 수: {len(works)}개")
    
    put_codes = []
    for work_group in works:
        summaries = work_group.get("work-summary", [])
        if summaries:
            # 가장 최신 버전(첫번째)의 ID 가져오기
            put_codes.append(summaries[0]["put-code"])
            
    return put_codes

def get_bibtex(orcid_id, put_code):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    headers = {
        "Accept": "application/x-bibtex",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"⚠️ 논문 ID {put_code} 변환 실패 (Code: {response.status_code})")
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        
    return None

def main():
    print(f"🚀 업데이트 시작: {ORCID_ID}")
    
    put_codes = get_works_ids(ORCID_ID)
    
    if not put_codes:
        print("🛑 가져올 논문이 없습니다. ORCID 공개 설정(Everyone)을 확인해주세요!")
        # 빈 파일이라도 생성해서 에러 방지
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("") 
        return

    print(f"📥 총 {len(put_codes)}편의 논문 정보를 다운로드합니다...")
    
    all_bibtex = []
    for i, code in enumerate(put_codes):
        bib = get_bibtex(ORCID_ID, code)
        if bib:
            all_bibtex.append(bib)
            print(f"  - [{i+1}/{len(put_codes)}] 완료")
        else:
            print(f"  - [{i+1}/{len(put_codes)}] 실패")
        time.sleep(0.5)
        
    # 결과 저장
    if all_bibtex:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_bibtex))
        print(f"🎉 성공! {OUTPUT_FILE}에 {len(all_bibtex)}편 저장 완료.")
    else:
        print("⚠️ 데이터는 찾았으나 BibTeX 변환에 실패했습니다.")

if __name__ == "__main__":
    main()
