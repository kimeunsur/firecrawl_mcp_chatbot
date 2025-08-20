import re
from typing import List, Optional
from ...models.place import MenuItem, Hour

class DataNormalizer:
    def normalize_menu(self, raw_content: Optional[str]) -> List[MenuItem]:
        """
        크롤링된 원시 content 문자열에서 마크다운 링크 구조를 정확히 파싱하여
        이름, 설명, 가격을 정규화합니다.
        """
        if not raw_content:
            return []

        normalized_list = []
        # 각 메뉴 항목을 나타내는 "- [text](link)" 마크다운 블록을 찾음
        item_blocks = re.findall(r'- \[(.*?)\]\(https://[^\)]+\)', raw_content, re.DOTALL)

        for block_content in item_blocks:
            price_match = re.search(r'_(?P<price>[\d,]+)_ 원', block_content)
            if not price_match:
                continue
            
            price = re.sub(r'\D', '', price_match.group('price'))
            info_part = block_content[:price_match.start()].strip()

            # 백슬래시와 공백의 조합을 기준으로 이름/설명 부분을 분리
            info_components = re.split(r'\\{2,}\s*', info_part)
            cleaned_components = [comp.strip() for comp in info_components if comp.strip()]

            if not cleaned_components:
                continue

            is_signature = "대표" in cleaned_components[0]
            name = ""
            description = None

            if is_signature:
                if len(cleaned_components) > 1:
                    name = cleaned_components[1]
                    if len(cleaned_components) > 2:
                        description = " ".join(cleaned_components[2:])
                else:
                    continue # "대표"만 있고 이름이 없는 경우는 무시
            else:
                name = cleaned_components[0]
                if len(cleaned_components) > 1:
                    description = " ".join(cleaned_components[1:])

            if description and "일시적인 오류가 발생했습니다" in description:
                description = None

            menu_item = MenuItem(
                name=name,
                price=price,
                description=description,
                is_signature=is_signature
            )
            normalized_list.append(menu_item)
            
        return normalized_list

    def normalize_hours(self, raw_content: Optional[str]) -> List[Hour]:
        """
        크롤링된 원시 content 문자열에서 다양한 형식의 영업시간 데이터를 파싱하고 정규화합니다.
        """
        if not raw_content:
            return []

        # '영업시간' 섹션의 내용을 추출 (더 넓은 패턴으로)
        hours_section_match = re.search(r'\*\*영업시간\*\*\s*\n(.*?)(?=\n\*\*|\Z)', raw_content, re.DOTALL)
        if not hours_section_match:
            return []
        
        content = hours_section_match.group(1).strip()
        
        normalized_list = []
        days_map = {'월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI', '토': 'SAT', '일': 'SUN'}
        
        # "월-금", "월,수,금" 등 요일 그룹과 시간/상태를 매칭하는 정규식
        # 예: "월-금 10:00 - 21:00", "토,일 10:00 - 22:00", "매주 월요일 정기 휴무"
        pattern = re.compile(
            r"((?:[월화수목금토일](?:,[월화수목금토일])*(?:-?[월화수목금토일])?|매일|연중무휴))\s+"  # 요일 그룹 (e.g., 월-금, 토,일, 매일)
            r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"  # 시간 (HH:MM - HH:MM)
            r"(?:\s*\((.*?)\))?"  # 괄호 안의 추가 정보 (e.g., 라스트오더)
            r"|((?:매주|매달)\s*.*?요일)\s*(정기 휴무)" # 휴무 정보 (e.g., 매주 월요일 정기 휴무)
        )

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = pattern.search(line)
            if match:
                # 영업시간 매칭 (그룹 1,2,3,4)
                if match.group(1) and match.group(2) and match.group(3):
                    day_group_str = match.group(1)
                    open_time = match.group(2)
                    close_time = match.group(3)
                    extra_info = match.group(4) # 라스트오더 등

                    # 요일 그룹 해석
                    days = self._parse_day_group(day_group_str, days_map)
                    
                    for day_code in days:
                        normalized_list.append(Hour(
                            day=day_code, 
                            open=open_time, 
                            close=close_time,
                            description=extra_info.strip() if extra_info else None
                        ))
                # 휴무일 매칭 (그룹 5,6)
                elif match.group(5) and match.group(6):
                    day_info = match.group(5)
                    status = match.group(6)
                    # '월'요일 -> 'MON'
                    for day_char, day_code in days_map.items():
                        if day_char in day_info:
                            normalized_list.append(Hour(
                                day=day_code,
                                open="00:00",
                                close="00:00",
                                description=status # "정기 휴무"
                            ))
        
        # 기존의 '연중무휴' 로직은 더 일반적인 패턴에 통합되므로 제거하거나 유지할 수 있음
        # 여기서는 새로운 패턴이 대부분을 커버하므로 단순화
        if not normalized_list and '연중무휴' in content:
            open_time = "09:00" # 기본값
            close_time = "21:00" # 기본값
            time_match = re.search(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', content)
            if time_match:
                open_time = time_match.group(1)
                close_time = time_match.group(2)

            for day_code in days_map.values():
                 normalized_list.append(Hour(day=day_code, open=open_time, close=close_time))

        return normalized_list

    def _parse_day_group(self, group_str: str, days_map: dict) -> List[str]:
        """ "월-금", "토,일" 같은 문자열을 ['MON', 'TUE', ...] 리스트로 변환 """
        days = set()
        
        if "매일" in group_str or "연중무휴" in group_str:
            return list(days_map.values())

        # "월-금" 같은 범위 처리
        range_match = re.match(r'([월화수목금토일])-([월화수목금토일])', group_str)
        if range_match:
            start_day = range_match.group(1)
            end_day = range_match.group(2)
            day_chars = list(days_map.keys())
            try:
                start_index = day_chars.index(start_day)
                end_index = day_chars.index(end_day)
                for i in range(start_index, end_index + 1):
                    days.add(days_map[day_chars[i]])
                return list(days)
            except ValueError:
                pass # 인덱스 못찾으면 아래 로직으로

        # "월,수,금" 같은 개별 요일 처리
        day_chars = re.findall(r'[월화수목금토일]', group_str)
        for char in day_chars:
            if char in days_map:
                days.add(days_map[char])
        
        return list(days)