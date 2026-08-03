import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main


def test_fetch_holiday_list_collects_each_month_and_filters_non_holidays(monkeypatch):
    def get(*args, **kwargs):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "response": {
                "body": {
                    "items": {
                        "item": (
                            [
                                {
                                    "locdate": 20260101,
                                    "dateName": "신정",
                                    "isHoliday": "Y",
                                },
                                {
                                    "locdate": 20260102,
                                    "dateName": "기념일",
                                    "isHoliday": "N",
                                },
                            ]
                            if kwargs["params"]["solMonth"] == "01"
                            else []
                        )
                    }
                }
            }
        }
        return response

    get = Mock(side_effect=get)
    monkeypatch.setattr(main.requests, "get", get)

    holidays = main.HolidayManager().fetch_holiday_list(2026)

    assert len(get.call_args_list) == 12
    assert [call.kwargs["params"]["solMonth"] for call in get.call_args_list] == [
        f"{month:02d}" for month in range(1, 13)
    ]
    assert holidays == [{"locdate": 20260101, "dateName": "신정", "isHoliday": "Y"}]
