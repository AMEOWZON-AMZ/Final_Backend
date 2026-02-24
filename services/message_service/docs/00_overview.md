# 00_overview

친구 관계는 Friends 테이블에서 (user_id, friend_user_id) 존재 여부로 확인

메시지/하트 전송 시 친구 여부 검증은 **현재 코드상 주석 처리됨** (is_accepted 체크 비활성화)

실제 배포 시에는 is_accepted() 체크를 활성화하여 ACCEPTED 상태인 친구만 전송하도록 설정 가능

현재는 from_user_id와 to_user_id만 있으면 전송됨