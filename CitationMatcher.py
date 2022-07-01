import Levenshtein
import json


def compare_titles(title1, title2):
    abrv = ""
    titles = [title1, title2]
    for title in titles:
        if len(title.split(" ")) > 1:
            continue

        caps = 0
        for char in title:
            if char.isupper():
                caps += 1

        if caps > 1:
            abrv = title
            titles.remove(abrv)
            title = titles[0]
    
    if (abrv not in title or abrv != "") and (len(abrv) == len(title.split(" ")) or len(title.split(" ")) == 1):
        abrv = abrv.lower()
        char_between = len(title)
        for char in title.lower():
            if len(abrv) == 0:
                title1 = abrv
                title2 = abrv
                break
            elif char == abrv[0] and char_between > 1:
                abrv = abrv[1:]
                char_between = 0
            else:
                char_between += 1

    score = Levenshtein.ratio(title1, title2)

    return score


def compare_names(authors1, editors1, authors2, editors2):
    authors1 = set(authors1.split("/"))
    authors2 = set(authors2.split("/"))
    editors1 = set(editors1.split("/"))
    editors2 = set(editors2.split("/"))

    if "" in authors1:
        authors1.remove("")
    if "" in authors2:
        authors2.remove("")
    if "" in editors1:
        editors1.remove("")
    if "" in editors2:
        editors2.remove("")

    length1 = len(authors1 | editors1)
    length2 = len(authors2 | editors2)
    total_score = 0
    
    names = 0
    
    max_length = max([length1, length2])
    
    if max_length == 0:
        return 0
    elif max_length == 1:
        score_first = 1
        score_after = 0
    else:
        score_first = 0.5
        score_after = 0.5/ length1

    
    
    for author1 in authors1.copy():
        for author2 in authors2:
            name_score = Levenshtein.ratio(author1, author2)
            if name_score > 0.8:
                if names == 0:
                    total_score += score_first
                    names += 1
                else:
                    total_score += score_after
                authors1.remove(author1)
                authors2.remove(author2)
                break
    
    editors1 = editors1 | authors1
    editors2 = editors2 | authors2

    for editor1 in editors1.copy():
        for editor2 in editors2:
            name_score = Levenshtein.ratio(editor1, editor2)
            if name_score > 0.8:
                if names == 0:
                    total_score += score_first
                    names += 1
                else:
                    total_score += score_after
                editors1.remove(editor1)
                editors2.remove(editor2)
                break

    return total_score



def compare_editions(edition1, edition2):
    if type(edition1) == list:
        edition1 = " ".join(edition1)
    if type(edition2) == list:
        edition2 = " ".join(edition2)
    score = Levenshtein.ratio(edition1, edition2)

    return score


def score_citation(citation1, citation2):
    labels1 = citation1["labels"]
    labels2 = citation2["labels"]
    name_score = compare_names(labels1["author"], labels1["editor"],
                               labels2["author"], labels2["editor"])
                               
    if (labels1["title"] == "" and labels2["title"] == ""):
        title_score = 0.5
    elif name_score > 0.8 and (labels1["title"] == "" or labels2["title"] == ""):
        title_score = 0.7
    else:
        title_score = compare_titles(labels1["title"], labels2["title"])

    
    if (labels1["edition"] == "" and labels2["edition"] == ""):
        edition_score = 0.5
    elif (labels1["edition"] == "" or labels2["edition"] == ""):
        if name_score > 0.8 and title_score > 0.8:
            edition_score = 0.8
        else:
            edition_score = 0.5
    else:
        edition_score = compare_editions(labels1["edition"], labels2["edition"])
        
    if (labels1["entry"] == "" and labels2["entry"] == ""):   
        entry_score = 0.5
    elif (labels1["entry"] == "" or labels2["entry"] == ""):
        if name_score > 0.8 and title_score > 0.8:
            entry_score = 0.8
        else:
            entry_score = 0.5
    else:
        entry_score = Levenshtein.ratio(labels1["entry"], labels2["entry"])
        
    if (labels1["year"] == "" and labels2["year"] == ""):
        year_score = 0.5
    elif (labels1["year"] == "" or labels2["year"] == ""):
        if name_score > 0.8 and title_score > 0.8:
            year_score = 0.8
        else:
            year_score = 0.5
    else:
        year_score = compare_editions(labels1["year"], labels2["year"])
            
            
            
            
    total_score = name_score * 4 + title_score * 4 + edition_score * 2 + entry_score + year_score

    return total_score


def match_citation(target_citation, results=10):
    with open("/content/drive/MyDrive/Afstudeerproject/Data/labelled_data.json") as f:
        data = json.load(f)
    scored = []
    for citation in data:
        score = score_citation(target_citation, citation)
        scored.append((citation, score))
    
    scored.sort(key=lambda tup: tup[1], reverse=True)

    return scored[:results]