#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bg3_builder.ghost_uploader import post_to_ghost_blog

# 다양한 BG3 용어가 포함된 테스트 마크다운
test_markdown_with_bg3_terms = """
# Baldur's Gate 3 Storm Sorcerer 빌드 가이드

이 빌드는 Reddit과 Fextralife 가이드를 기반으로 작성되었음.

## 개요
**Storm Sorcerer**는 강력한 번개 마법에 특화된 클래스로, 높은 DPS와 AoE 피해를 자랑함.

## 스탯 분배
- **STR**: 8
- **DEX**: 14
- **CON**: 16
- **INT**: 10
- **WIS**: 12
- **CHA**: 17

## 추천 종족
**Dragonborn**이 가장 적합함:
- **매력 +2, 힘 +1** 보너스
- **브레스 웨폰** 추가 공격 옵션
- **용 혈통**에 따른 저항력

## 주요 주문들

### 1레벨 주문
- **Magic Missile**: 확정 피해를 주는 기본 공격 주문
- **Shield**: 방어력을 +5 증가시키는 방어 주문
- **Thunderwave**: 근거리 적들을 밀어내는 AoE 공격

### 2레벨 주문  
- **Misty Step**: 순간이동으로 전술적 이동
- **Scorching Ray**: 연속 공격으로 높은 피해

### 3레벨 주문
- **Fireball**: 강력한 AoE 폭발 피해
- **Lightning Bolt**: 직선 관통 번개 공격
- **Counterspell**: 적의 주문을 무효화

## 추천 장비

### Act 1
- **무기**: **Quarterstaff** +1
- **방어구**: **Studded Leather** Armor
- **액세서리**: **Ring** of Protection

### Act 2  
- **무기**: **Staff** of Fire
- **방어구**: **Robe** of Summer
- **액세서리**: **Amulet** of Greater Health

### Act 3
- **무기**: **Staff** of Power
- **방어구**: **Cloak** of Displacement
- **액세서리**: **Ring** of Spell Storing

## 멀티클래스 옵션
**Tempest Cleric** (2레벨)과의 멀티클래스를 고려해볼 것:
- **Channel Divinity**: 번개/천둥 피해 최대화
- **Heavy Armor** 착용 가능
- 추가 **Healing** 주문 접근

## 전투 전략

### 기본 전투 루틴
1. **Haste** 또는 **Shield** 으로 버프 시작
2. **Fireball** 또는 **Lightning Bolt** 으로 주요 딜링
3. **Misty Step** 으로 안전한 위치 확보
4. **Magic Missile** 으로 마무리

### 고급 콤보
- **Quickened Spell** + **Fireball** + **Lightning Bolt** 연계
- **Twinned Spell** 로 **Haste** 이중 적용
- **Counterspell** 로 적 마법사 무력화

## 장점과 단점

### 장점
- 높은 폭발적 피해
- 다양한 AoE 옵션
- 우수한 기동성 (**Misty Step**)
- 강력한 제어 능력

### 단점  
- 낮은 생존력
- 스펠 슬롯 의존도 높음
- 근접전에서 취약

## 팁
- 항상 **Shield** 주문을 준비해둘 것
- **Sorcery Points** 관리가 핵심
- **Concentration** 주문 보호가 중요함
- **Lightning** 저항 적들 주의

이 빌드는 패치 8 기준으로 작성되었음.
"""

def test_improved_image_accuracy():
    """개선된 이미지 정확도 테스트"""
    print("📝 개선된 이미지 정확도 테스트 시작...")
    print("🔍 BG3 용어 검증 시스템과 화이트리스트 기반 이미지 검색 테스트")
    
    # Ghost 블로그에 포스팅 (개선된 이미지 시스템 사용)
    post_url = post_to_ghost_blog(
        title="[테스트] 개선된 이미지 정확도 시스템",
        content=test_markdown_with_bg3_terms,
        build_name="Storm Sorcerer 이미지 정확도 테스트",
        tags=["테스트", "이미지정확도", "Storm Sorcerer"]
    )
    
    if post_url:
        print(f"✅ 테스트 포스트 생성 성공!")
        print(f"🔗 포스트 URL: {post_url}")
        print()
        print("📊 확인할 항목들:")
        print("  - Magic Missile, Shield, Fireball 등 주문 이미지가 정확한지")
        print("  - Studded Leather, Ring, Staff 등 장비 이미지가 맞는지") 
        print("  - 일반적인 단어들(build, level, damage)은 이미지가 없는지")
        print("  - 이미지 크기와 스타일이 적절한지")
    else:
        print("❌ 테스트 포스트 생성 실패")

if __name__ == "__main__":
    test_improved_image_accuracy() 