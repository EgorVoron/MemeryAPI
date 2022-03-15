from fuzzywuzzy import fuzz

MINIMAL_TEXT_SIMILARITY_INDEX = 50


def compare_texts(text_a, text_b):
    ratio = fuzz.ratio(text_a, text_b)
    partial_ratio = fuzz.partial_ratio(text_a, text_b)
    mean_ratio = (ratio + partial_ratio) / 2
    return mean_ratio


def sort_results(results):
    sorted_results = sorted(results, key=lambda x: -results[x])
    return sorted_results


def find_photos_by_text(pic_names, descriptions, search_text, similarity_index=MINIMAL_TEXT_SIMILARITY_INDEX):
    results = {}
    for idx, description in enumerate(descriptions):
        similarity = compare_texts(search_text, description)
        if similarity >= similarity_index:
            results[pic_names[idx]] = similarity
    return sort_results(results)
