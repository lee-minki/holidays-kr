import datetime
import glob
import json
import os
import time
import uuid
from datetime import datetime
from urllib.parse import unquote

import requests
from icalendar import Calendar, Event


class HolidayManager:
    def __init__(self):
        self.api = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_holiday_list(self, year):
        holidays = []
        service_key = unquote(os.getenv("HOLIDAY_API_KEY", ""))
        for month in range(1, 13):
            params = {
                "solYear": str(year),
                "solMonth": f"{month:02d}",
                "ServiceKey": service_key,
                "_type": "json",
                "numOfRows": "100",
            }
            for attempt in range(3):
                try:
                    response = requests.get(self.api, params=params, timeout=30)
                    response.raise_for_status()
                    break
                except (requests.ConnectionError, requests.Timeout):
                    if attempt == 2:
                        raise
                    time.sleep(2**attempt)
            items = response.json()["response"]["body"].get("items", {})
            month_items = items.get("item", []) if items else []

            if isinstance(month_items, dict):
                month_items = [month_items]
            holidays.extend(
                item for item in month_items if item.get("isHoliday") == "Y"
            )

        return holidays

    def format_holidays(self, holidays):
        formatted = {}

        for holiday in holidays:
            date_str = str(holiday["locdate"])
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

            if formatted_date not in formatted:
                formatted[formatted_date] = []
            if holiday["dateName"] not in formatted[formatted_date]:
                formatted[formatted_date].append(holiday["dateName"])

        return formatted

    def save_json(self, data, year):
        filename = os.path.join(self.data_dir, f"{year}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename

    def load_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def cleanup_old_files(self):
        current_year = datetime.now().year
        for file in glob.glob(os.path.join(self.data_dir, "*.json")):
            year = int(os.path.basename(file).split(".")[0])
            if year < current_year - 2:
                os.remove(file)

    def generate_ics(self):
        # Create calendar
        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//lee-minki//holidays-kr//KO")
        cal.add("x-wr-calname", "대한민국의 공휴일")
        cal.add("x-wr-timezone", "Asia/Seoul")
        cal.add("x-wr-caldesc", "https://github.com/lee-minki/holidays-kr")

        # Load all JSON files
        all_holidays = {}
        for file in sorted(glob.glob(os.path.join(self.data_dir, "*.json"))):
            year_data = self.load_json(file)
            all_holidays.update(year_data)

        # Sort dates and create events
        for date in sorted(all_holidays.keys()):
            date_obj = datetime.strptime(date, "%Y-%m-%d")

            for summary in all_holidays[date]:
                event = Event()
                event.add("summary", summary)
                event.add("dtstart", date_obj.date())

                # Generate a unique, deterministic UUID for each holiday
                # Using combination of date and holiday name to ensure consistency
                uid = uuid.uuid5(uuid.NAMESPACE_DNS, f"holiday-kr-{date}-{summary}")
                event.add("uid", str(uid))

                event.add("class", "PUBLIC")
                event.add("transp", "TRANSPARENT")

                cal.add_component(event)

        # Write to file
        with open("holidays.ics", "wb") as f:
            f.write(cal.to_ical())

    def process_holidays(self):
        years = [datetime.now().year, datetime.now().year + 1]
        changes_detected = False

        for year in years:
            holidays = self.fetch_holiday_list(year)
            if not holidays:
                continue

            formatted_data = self.format_holidays(holidays)
            filename = os.path.join(self.data_dir, f"{year}.json")

            # Check if file exists and compare content
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    existing_data = json.load(f)
                if existing_data != formatted_data:
                    self.save_json(formatted_data, year)
                    changes_detected = True
            else:
                self.save_json(formatted_data, year)
                changes_detected = True

        self.cleanup_old_files()

        self.generate_ics()
        return changes_detected


def main():
    manager = HolidayManager()
    changes = manager.process_holidays()
    if changes:
        print("Changes detected and new ICS file generated")
    else:
        print("No changes detected")


if __name__ == "__main__":
    main()
