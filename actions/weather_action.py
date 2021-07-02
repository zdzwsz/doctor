import logging
from typing import Text, Dict, Any, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict
from utils.action_util import get_weather
from rasa_sdk.events import EventType
from utils.data_util import get_yaml

logger = logging.getLogger(__name__)

city_data = [i.strip() for i in get_yaml("./data/entity_city.yml")["nlu"][0]["examples"].split("-")]


class ValidateWeatherForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_weather_form"

    @staticmethod
    def get_date_list() -> List[Text]:
        return ["今天", "明天", "后天"]

    def validate_day(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> Dict[Text, Any]:
        if type(slot_value) == list:
            slot_value = slot_value[0]

        if slot_value in self.get_date_list():
            return {"day": slot_value}
        else:
            return {"day": None}

    @staticmethod
    def get_city_list() -> List[Text]:
        return city_data

    def validate_city(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> Dict[Text, Any]:
        if type(slot_value) == list:
            slot_value = slot_value[0]
        if slot_value == "":
            return {"city": None}

        if slot_value in self.get_city_list():
            return {"city": slot_value}
        else:
            return {"city": None}


class ActionWeatherForm(Action):
    def name(self) -> Text:
        return "action_weather_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        slots = tracker.current_slot_values()
        city = slots["city"]
        date = slots["day"]
        dispatcher.utter_message(text=get_weather(city, date))
        return []


class ActionAskWeatherFormCity(Action):
    def name(self) -> Text:
        return "action_ask_weather_form_city"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        dispatcher.utter_message(text="你想询问哪个城市的？")
        return []


class ActionAskWeatherFormDate(Action):
    def name(self) -> Text:
        return "action_ask_weather_form_day"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        dispatcher.utter_message(text="你想询问哪个日期的？[今天、明天、后天]")
        return []


class ClearWeatherFormSlot(Action):
    """清除掉上次收集的 slots"""

    def name(self) -> Text:
        return "action_clear_weather_form_slots"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        clear_slots = domain.get("forms", {})["weather_form"]["required_slots"].keys()
        slots_data = domain.get("slots")
        print(clear_slots)
        return [slot_set(slot_name, slots_data.get(slot_name)['initial_value']) for slot_name in clear_slots]


def slot_set(
        key: Text, value: Any = None, timestamp: Optional[float] = None
) -> EventType:
    return {"event": "slot", "timestamp": timestamp, "name": key, "value": value}
