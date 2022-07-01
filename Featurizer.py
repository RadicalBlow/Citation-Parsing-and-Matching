import string
import random


class Featurizer():
    def __init__(self, window=2, check_punct=False, position=False,
                 check_wordlist=False, check_namelist=False,
                 check_titlelist=False, add_token=False, all=False):
        self.window = window
        self.check_punct = check_punct or all
        self.position = position or all
        self.check_wordlist = check_wordlist or all
        self.check_namelist = check_namelist or all
        self.check_titlelist = check_titlelist or all
        self.add_token = add_token or all
        self.punctuation = string.punctuation
        self.randnumbers = ["Rn", "Rdnr", "Rdn", "Rz", "RdNr", "Rdz"]
        self.standard_features = {
                "caps": "None",
                "digits": "None",
                "is_four_digits": False,
                "isAufl": False,
                "isRand": False,
                "isIn": False,
                "isPar": False,
                "isBOS": False,
                "isEOS": False,
                "hasPunct": False,
            }

        if check_wordlist or all:
            with open("/content/drive/MyDrive/Afstudeerproject/Data/Wordlists/wordlist.txt", "r") as f:
                self.wordlist = f.readlines()
                self.wordlist = [word.replace("\n", "") for word in self.wordlist]

        if check_namelist or all:
            with open("/content/drive/MyDrive/Afstudeerproject/Data/Wordlists/known_names.txt", "r") as f:
                self.namelist = f.readlines()
                self.namelist = [name.replace("\n", "") for name in self.namelist]

            with open("/content/drive/MyDrive/Afstudeerproject/Data/Wordlists/surnames.txt", "r") as f:
                self.surnames = f.readlines()
                self.surnames = [name.replace("\n", "") for name in self.surnames]

        if check_titlelist or all:
            with open("/content/drive/MyDrive/Afstudeerproject/Data/Wordlists/only_titles.txt", "r") as f:
                self.titlelist = f.readlines()
                self.titlelist = [title.replace("\n", "") for title in self.titlelist]

    def featurize_citation(self, citation, parsed=[]):
        labeling = False
        if parsed:
            labeling = True
        if citation.count("/") > 0:
            citation = citation.replace("/", " ")
        else:
            citation = citation.replace("-", " ")
        citation = citation.split(" ")
        citation = ["BOS"] * self.window + citation + ["EOS"] * self.window
        featurized = []
        for i, token in enumerate(citation):
            if token == "" or token == " ":
                continue
            elif "," in token and token != ",":
                citation.insert(i + 1, ",")
                token = token.replace(",", "")
            token_features = self.standard_features.copy()
            if labeling:
                if token == "," and random.random() < 0.25:
                    continue
                for parsed_token in parsed:
                    if token == parsed_token[0]:
                        token_features["label"] = parsed_token[1]
                        parsed.remove(parsed_token)
                        break
                if "label" not in token_features:
                    token_features["label"] = "other"

            if self.add_token:
                token_features["token"] = token

            if self.position:
                token_features["position"] = (i - self.window)/(len(citation) - self.window * 2)

            token_features["length"] = len(token)

            self.check_chars(token, token_features)
            self.check_token(token, token_features)
            self.check_lists(token, token_features)

            featurized.append(token_features)

        featurized = self.add_window(featurized)

        return featurized

    def check_chars(self, token, token_features):
        caps = 0
        digits = 0
        for char in token:
            if char.isdigit():
                digits += 1
            elif char.isupper():
                caps += 1
            elif char in self.punctuation:
                token_features["hasPunct"] = True

        if digits > 0 and digits < len(token):
            token_features["digits"] = "mixed"
        elif digits == len(token):
            token_features["digits"] = "all"
        if digits == 4:
            token_features["is_four_digits"] = True

        if token[0].isupper() and caps == 1:
            token_features["caps"] = "first"
        elif caps > 1 and caps < len(token):
            token_features["caps"] = "mixed"
        elif caps == len(token):
            token_features["caps"] = "all"

    def check_token(self, token, token_features):
        if "Aufl" in token:
            token_features["isAufl"] = True
        elif token.replace(".", "") in self.randnumbers:
            token_features["isRand"] = True
        elif token.replace(":", "") == "in":
            token_features["isIn"] = True
        elif "§" in token:
            token_features["isPar"] = True
        elif token == "BOS":
            token_features["isBOS"] = True
        elif token == "EOS":
            token_features["isEOS"] = True

        return True

    def check_lists(self, token, token_features):
        if self.check_wordlist:
            token_features["inWordlist"] = False
            if token.lower() in self.wordlist:
                token_features["inWordlist"] = True

        if self.check_namelist:
            token_features["inNamelist"] = False
            if token in self.namelist:
                token_features["inNamelist"] = True

        if self.check_titlelist:
            token_features["inTitlelist"] = False
            if token in self.titlelist:
                token_features["inTitlelist"] = True

        return True

    def add_window(self, featurized):
        windowed = []
        for i in range(self.window, len(featurized)-self.window):
            token_features = featurized[i].copy()
            for j in range(-self.window, self.window + 1):
                if j == 0:
                    continue
                window_token = featurized[i + j].copy()
                for feature in window_token:
                    if feature == "token" or feature == "label" or feature == "position":
                        continue
                    token_features[f"{j}:{feature}"] = window_token[feature]
            windowed.append(token_features)

        return windowed
