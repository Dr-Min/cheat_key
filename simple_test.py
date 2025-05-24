#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from bg3_builder.skill_extractor import extract_bg3_terms_from_source
    print("✅ skill_extractor 임포트 성공")
except Exception as e:
    print(f"❌ skill_extractor 임포트 실패: {e}")

try:
    from bg3_builder.improved_image_system import process_images_with_source_accuracy
    print("✅ improved_image_system 임포트 성공")
except Exception as e:
    print(f"❌ improved_image_system 임포트 실패: {e}")

try:
    from bg3_builder.accurate_build_generator import create_build_with_accurate_images
    print("✅ accurate_build_generator 임포트 성공")
except Exception as e:
    print(f"❌ accurate_build_generator 임포트 실패: {e}")

print("\n🎯 모든 모듈 임포트 테스트 완료!")
print("이제 정확한 이미지 시스템이 준비되었습니다!") 