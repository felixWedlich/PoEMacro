#TODO rewrite and not copy paste
import configparser
import http

import ahkpy
import requests,sys,json

from pvrecorder import PvRecorder
from Levenshtein import distance as levenshtein_distance

gem_types = ["phantasmal", "divergent", "anomalous"]
gem_url = "https://poe.ninja/api/data/itemoverview?league={0}&type=SkillGem"



def extract_gem_info(lines, gem_names):
    results = {}
    for gem_name in gem_names:
        results[gem_name] = {}
        for l in lines:
            if l["name"].lower() == gem_name:
                if results[gem_name].get(l.get("gemLevel")):
                    results[gem_name][l.get("gemLevel")]["chaos"] = min(
                        results[gem_name][l.get("gemLevel")]["chaos"], l.get("chaosValue")
                    )
                    results[gem_name][l.get("gemLevel")]["div"] = min(
                        results[gem_name][l.get("gemLevel")]["div"], l.get("divineValue")
                    )
                else:
                    results[gem_name][l.get("gemLevel")] = {
                        "chaos": l["chaosValue"],
                        "div": l["divineValue"],
                    }
    return results


# def get_gem_price(gem_name,league, min_level=3, max_level=19):
#     data = get_gem_data(league)
#     gem_info = extract_gem_info(data, gem_name)
#     results = {}
#     for name, d in gem_info.items():
#         results[name] = {}
#         for level, data in d.items():
#             if level in range(min_level, max_level):
#                 results[name][level] = data
#     return results


class GemPricer:

    def __init__(self, config: configparser.ConfigParser):
        self.RECORD_HOTKEY = config.get('hotkeys','RECORD_AUDIO')
        self.league = config.get('poe','LEAGUE')
        self.data = None


    def _setup_gem_names(self):
        self.gem_names = open("data/heist/gem_names.txt","r").readlines()
        self.gem_names = [ (quality + gem).rstrip() for gem in self.gem_names for quality in ["Divergent ", "Anomalous ", "Phantasmal "]]



    def _get_gem_data(self):
        gem_url = f"https://poe.ninja/api/data/itemoverview?league={self.league}&type=SkillGem"
        r = requests.get(gem_url)
        if r.status_code != http.HTTPStatus.OK:
            raise Exception("Request to Poe.Ninja failed, most likely invalid league provided")

        data = json.loads(r.text)["lines"]
        gems = {}
        for l in data:
            gem_name = l["name"]
            if l.get("corrupted"):
                continue
            if gem_name not in gems:
                gems[gem_name] = [l]
            else:
                gems[gem_name].append(l)
        self.data = gems


    def _load_model(self):
        import whisper
        self.model = whisper.load_model("base.en")

    def _setup_microphone(self):
        #todo if device name is not provided in settings.cfg, ask the user (provide list of names and await the desired ID)
        self.recorder = PvRecorder(device_index=3, frame_length=512)

    # def price_gems(self):
    #     audio = []
    #     print("recording...",end="")
    #     while ahkpy.is_key_pressed(self.RECORD_HOTKEY):
    #         frame = self.recorder.read()
    #         audio.extend(frame)
    #     self.recorder.stop()
    #     print(" finished")
    #     # with wave.open(filename, 'w') as f:
    #     #     f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
    #     #     f.writeframes(struct.pack("h" * len(audio), *audio))
    #     result = self.model.transcribe(filename)
    #     transcriped_gems = []
    #     for segment in result["segments"]:
    #         text = segment["text"]
    #         text = text.replace(".",",")
    #         transcriped_gems.extend(filter(lambda t: len(t) > 8, text.split(",")))
    #
    #     best_match = {}
    #     for transcriped_gem in transcriped_gems:
    #
    #         distances = {levenshtein_distance(transcriped_gem, gem): gem for gem in self.gem_names}
    #         best_match[transcriped_gem] = distances[min(distances)].lower()
    #
    #     prices = get_gem_price(list(best_match.values()),"Sanctum")
    #     # for matched_gem,price in sorted(prices)
    #     for transcriped_gem,best_match in best_match.items():
    #         #heard:{transcriped_gem}
    #         print(f"matched:{best_match}\t\t\t price: {prices[best_match]}")
    #     print("")

    def get_gem_price(self,gem_name,min_level=3, max_level=19):
        gem_info = {}
        gem_info[gem_name] = {}

        for g in self.data[gem_name]:
            g[""]
            # if g[gem_name].get(l.get("gemLevel")):
            #     gem_info[gem_name][l.get("gemLevel")]["chaos"] = min(
            #         gem_info[gem_name][l.get("gemLevel")]["chaos"], l.get("chaosValue")
            #     )
            #     gem_info[gem_name][l.get("gemLevel")]["div"] = min(
            #         gem_info[gem_name][l.get("gemLevel")]["div"], l.get("divineValue")
            #     )
            # else:
            #     gem_info[gem_name][l.get("gemLevel")] = {
            #         "chaos": l["chaosValue"],
            #         "div": l["divineValue"],
            #     }
        results = {}
        for name, d in gem_info.items():
            results[name] = {}
            for level, data in d.items():
                if level in range(min_level, max_level):
                    results[name][level] = data
        return results






