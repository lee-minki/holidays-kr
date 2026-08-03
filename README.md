# 대한민국 공휴일 데이터

[![Update Holiday Data](https://github.com/lee-minki/holidays-kr/actions/workflows/update-holidays.yml/badge.svg)](https://github.com/lee-minki/holidays-kr/actions/workflows/update-holidays.yml)

한국천문연구원 특일 정보 제공 서비스의 공휴일 데이터를 ICS와 연도별 JSON으로 제공합니다.
GitHub Actions가 매일 12:15 KST에 현재·다음 해를 다시 조회해 임시공휴일과 대체공휴일 변경을 반영합니다.

## Google Calendar 구독

GitHub Pages 배포가 완료되면 다음 주소를 Google Calendar의 “URL로 추가”에 넣습니다.

```text
https://lee-minki.github.io/holidays-kr/holidays.ics
```

Google Calendar는 구독 캘린더의 새 변경사항을 자체 주기로 동기화합니다. 긴급한 임시공휴일은 원본 ICS를 갱신해도 앱에 표시되기까지 시간이 걸릴 수 있습니다.

## 운영 원칙

- `HOLIDAY_API_KEY`는 GitHub Actions Secret으로만 사용하며, 저장소와 배포 파일에는 포함하지 않습니다.
- 개인 일정·음력 기념일·알림은 이 공개 공휴일 피드와 분리합니다.
- 데이터 출처: [한국천문연구원 특일 정보 제공 서비스](https://www.data.go.kr/dataset/15012679/openapi.do)

Original project: https://github.com/DaeHyeoNi/holidays-kr
