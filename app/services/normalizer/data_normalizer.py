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
        크롤링된 원시 content 문자열에서 영업시간 데이터를 파싱하고 정규화합니다.
        """
        if not raw_content:
            return []

        normalized_list = []
        hours_section_match = re.search(r'\*\*영업시간\*\*(.*?)(\*\*|$)', raw_content, re.DOTALL)
        if not hours_section_match:
            return []
        content = hours_section_match.group(1)

        days_map = {'월': 'MON', '화': 'TUE', '수': 'WED', '목': 'THU', '금': 'FRI', '토': 'SAT', '일': 'SUN'}
        
        if '연중무휴' in content:
            close_time = "21:30"
            close_match = re.search(r'(\d{1,2}:\d{2})에 영업 종료', content)
            if close_match:
                close_time = close_match.group(1)
            
            for day_code in days_map.values():
                 normalized_list.append(Hour(day=day_code, open="00:00", close=close_time))
        
        return normalized_list
