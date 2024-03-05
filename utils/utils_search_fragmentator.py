from models.item_model import Item


class SearchFragmentator:
    @staticmethod
    def get_search_item_fragment_and_page(item: Item, text_search: str):
        for page in range(item.pages_count()):
            page_text = item.get_text(page)
            index = page_text.lower().find(text_search.lower())
            if index != -1:
                if index == 0 or (len(page_text) < 50 and index < 36):
                    return page_text, page
                else:
                    while (index > 0
                           and (not page_text[index:].startswith(' ')
                                and not page_text[index:].startswith('\n'))
                    ):
                        index -= 1
                    fragment = page_text[index:]
                    if index > 0 and fragment.startswith(' '):
                        fragment = f'...{fragment.replace(' ', '', 1)}'
                    elif index > 0 and fragment.startswith('\n'):
                        fragment = f'...{fragment.replace('\n', '', 1)}'
                    return fragment, page
        return None

    @staticmethod
    def get_search_file_caption_fragment(caption, text_search: str):
        index = caption.lower().find(text_search.lower())
        if index != -1:
            if index == 0 or (len(caption) < 50 and index < 36):
                return caption
            else:
                while (index > 0
                       and (not caption[index:].startswith(' ')
                            and not caption[index:].startswith('\n'))
                ):
                    index -= 1
                fragment = caption[index:]
                if index > 0 and fragment.startswith(' '):
                    fragment = f'...{fragment.replace(' ', '', 1)}'
                elif index > 0 and fragment.startswith('\n'):
                    fragment = f'...{fragment.replace('\n', '', 1)}'
                return fragment
