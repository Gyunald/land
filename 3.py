import json
import requests
from requests.exceptions import RequestException

def get_route_details_string_from_url(url: str) -> str:
    """
    지정된 URL에서 경로 JSON 데이터를 가져와 상세 내용을 포맷된 문자열로 반환합니다.

    Args:
        url: 경로 데이터가 포함된 JSON 파일을 제공하는 API 엔드포인트 URL.

    Returns:
        경로 요약 및 상세 정보가 포함된 포맷팅된 문자열 또는 오류 메시지.
    """
    try:
        # 1. URL 호출 및 응답 확인
        # timeout=10: 요청이 10초를 초과하면 시간 초과 오류를 발생시킵니다.
        response = requests.get(url, timeout=10)
        # HTTP 응답 코드가 4xx 또는 5xx일 경우 HTTPError 예외를 발생시킵니다.
        response.raise_for_status()

        # 2. JSON 데이터 로드
        data = response.json()
    
    except requests.exceptions.Timeout:
        return f"오류: URL 호출 시간 초과: {url}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP 오류: 요청 실패 (상태 코드 {response.status_code})"
    except RequestException as e:
        return f"요청 오류: URL을 가져올 수 없습니다: {e}"
    except json.JSONDecodeError as e:
        return f"JSON 디코딩 오류: {e}"

    # --- 기존 파일 처리 로직 시작 ---

    # 1. 경로 정보 추출
    context = data.get('res', {}).get('context', {})
    paths = data.get('res', {}).get('paths', [])
    
    if not paths:
        return "경로 정보(paths)를 찾을 수 없습니다."

    first_path = paths[0]
    
    # 2. 요약 정보 추출 (필수 항목)
    start_parts = context.get('start', '정보 없음').split(',')
    goal_parts = context.get('goal', '정보 없음').split(',')
    
    # 총 이동 시간 = 탑승 시간 + 도보 시간 + 대기 시간
    total_duration = first_path.get('duration', 0) + first_path.get('walkingDuration', 0) + first_path.get('waitingDuration', 0)
    
    summary = {
        "출발지": start_parts[2].strip() if len(start_parts) > 2 else 'N/A',
        "도착지": goal_parts[2].strip() if len(goal_parts) > 2 else 'N/A',
        "총 이동 시간(분)": total_duration,
        "walking 시간(분)": first_path.get('walkingDuration', 0), 
        "총 환승 횟수": first_path.get('transferCount', 0)
    }
    
    # 3. 상세 경로 (legs) 및 환승 정보 추출
    legs = first_path.get('legs', [])
    legs_data = []
    
    for i, leg in enumerate(legs):
        steps = leg.get('steps', [{}])
        if not steps: continue
        
        step = steps[0]
        leg_type = step.get('type', '이동')
        leg_duration_min = step.get('duration', 'N/A')
        
        detail = ""
        route_name = ""
        start_station = None
        goal_station = None 
        transfer_info = {}
        
        if leg_type == 'WALKING':
            distance = step.get('distance', 'N/A')
            instruction = step.get('instruction', '도보 이동')
            detail = f"{instruction} ({distance}m)"

            # 이전/다음 leg 정보를 기반으로 환승 정보 확인 (환승 횟수에 포함되는 도보 이동)
            if i > 0 and i < len(legs) - 1:
                prev_leg = legs_data[-1]
                next_steps = legs[i+1].get('steps', [{}])
                next_step = next_steps[0] if next_steps else {}
                
                # 이전 단계와 다음 단계가 대중교통이고 현재 단계가 도보인 경우, 환승으로 간주
                if prev_leg['수단'] in ['SUBWAY', 'BUS'] and next_step.get('type') in ['SUBWAY', 'BUS']:
                    transfer_station = prev_leg.get('도착역', 'N/A')
                    next_routes = next_step.get('routes', [{}])
                    next_route_name = next_routes[0].get('name', 'N/A') if next_routes else 'N/A'
                    
                    # 환승 정보를 WALKING 단계에 포함
                    transfer_info = {
                        "환승 수단": "도보",
                        "환승역": transfer_station,
                        "환승 노선 종류": next_route_name,
                        "환승 횟수 포함": True
                    }

        elif leg_type in ['SUBWAY', 'BUS']:
            routes = step.get('routes', [{}])
            route_name = routes[0].get('name', '노선명 없음')
            
            stations = step.get('stations', [])
            start_station = stations[0].get('name', '출발역') if stations else 'N/A'
            goal_station = stations[-1].get('name', '도착역') if len(stations) > 1 else 'N/A'
            
            if start_station != 'N/A' and goal_station != 'N/A':
                detail = f"승차: {start_station} → 하차: {goal_station}"
            elif start_station != 'N/A':
                 detail = f"승차: {start_station}"

        
        legs_data.append({
            "수단": leg_type,
            "노선": route_name,
            "시간(분)": leg_duration_min,
            "상세": detail,
            "출발역": start_station,
            "도착역": goal_station,
            "환승 정보": transfer_info
        })
        
    # 4. 결과 포맷팅 (문자열 리스트로 조합)
    output = []
    output.append(f"출발지: {summary['출발지']}")
    output.append(f"도착지: {summary['도착지']}")
    output.append("-" * 60)
    output.append(f"총 이동 시간: 약 {summary['총 이동 시간(분)']}분 (대기, 탑승, 도보 시간 포함)")
    output.append(f"총 도보 시간 (Walking): 약 {summary['walking 시간(분)']}분")
    output.append(f"환승 횟수: {summary['총 환승 횟수']}회")
    output.append("-" * 60)
    output.append("\n[단계별 경로]")

    for i, leg in enumerate(legs_data):
        time_info = f"(약 {leg['시간(분)']}분 소요)"
        
        transport_str = ""
        if leg['수단'] == 'SUBWAY':
            transport_str = f"지하철 ({leg['노선']})"
        elif leg['수단'] == 'BUS':
            transport_str = f"\ 버스 ({leg['노선']})"
        elif leg['수단'] == 'WALKING':
            transport_str = f"도보"
        else:
            transport_str = f"{leg['수단']}"
        
        output.append(f"{i+1}. {transport_str} {time_info}")
        output.append(f"   ㄴ {leg['상세']}")
        
        # 환승 정보가 있는 경우 별도 출력
        if leg['환승 정보'].get("환승 횟수 포함"):
            info = leg['환승 정보']
            output.append(f"환승 정보:")
            output.append(f"환승역: {info['환승역']}")
            output.append(f"환승 수단: {info['환승 수단']}")
            output.append(f"환승 노선 종류: {info['환승 노선 종류']} (승차)")
            output.append("-" * 30)
            
    output.append("=" * 60)
    
    return "\n".join(output)

# 함수 실행 예시
if __name__ == "__main__":
    # TODO: 경로 정보를 제공하는 실제 API URL로 교체해야 합니다.
    # 이 URL은 예시이며, 실제 경로 데이터를 반환하지 않습니다.
    EXAMPLE_URL = "https://pt.map.naver.com/cs-quick-path/api/pubtrans-route-search?phase=real&mode=TIME&departureTime=2025-10-02T18:34:54&departure=126.7671006,37.7254216,placeid%3D13543583,name%3D%25EC%259A%25B4%25EC%25A0%2595%25EC%2597%25AD%2520%25EA%25B2%25BD%25EC%259D%2598%25EC%25A4%2591%25EC%2595%2599%25EC%2584%25A0&arrival=127.1403861,37.4372518,placeid%3D13479575,name%3D%25EC%2588%2598%25EC%25A7%2584%25EC%2597%25AD%25208%25ED%2598%25B8%25EC%2584%25A0&includeDetailOperation=true&supportFerry=true&caller=cs-mo-quick-path"
    
    print("--- URL 호출 기반 경로 데이터 처리 시작 ---")
    result_string = get_route_details_string_from_url(EXAMPLE_URL)
    print(result_string)
