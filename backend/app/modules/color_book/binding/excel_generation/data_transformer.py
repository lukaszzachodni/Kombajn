import os


class DataTransformer:
    def __init__(self, messenger):
        self.messenger = messenger

    def prepare_excel_data(self, project_data, output_dir):
        """
        Prepares project data for KDP Excel generation.
        """
        self.messenger.info(
            f"DEBUG: prepare_excel_data - project_data received: {project_data}"
        )

        try:

            transformed_data = {
                "project_name": project_data["coloringBook"]["mainProjectDetails"][
                    "title"
                ],
                "languages": list(
                    project_data["coloringBook"]["languageVersions"].keys()
                ),
                "cover_path_template": os.path.join(
                    output_dir,
                    f"{{lang}}_{project_data["coloringBook"]["mainProjectDetails"]["title"]}.pdf",
                ),
                "interior_path": os.path.join(output_dir, "manuscript.pdf"),
                "titles": {},
                "subtitles": {},
                "author_first_name": project_data["coloringBook"]["mainProjectDetails"][
                    "suggestedUniversalAuthorName"
                ]["firstName"],
                "author_last_name": project_data["coloringBook"]["mainProjectDetails"][
                    "suggestedUniversalAuthorName"
                ]["lastName"],
                "minimum_age": project_data["coloringBook"]["languageVersions"]["en"][
                    "uploaderData"
                ]["Minimum age"],
                "maximum_age": project_data["coloringBook"]["languageVersions"]["en"][
                    "uploaderData"
                ]["Maximum age"],
                "Primary Marketplace": "",
                "Low-Content Book": "",
                "Large print": "",
                "ISBN": "",
                "Imprint": "",
                "Interior & paper type": "",
                "Width (in)": "",
                "Height (in)": "",
                "Bleed Settings": "",
                "Paperback cover finish": "",
                "Cover include barcode": "",
                "AI-Generated": "",
                "AI-Texts": "",
                "AI-Texts-Tool": "",
                "AI-Images": "",
                "AI-Images-Tools": "",
                "AI-Translations": "",
                "AI-Translations-Tool": "",
                "Base all prices on Primary Marketplace price": "",
                "Expanded Distribution": "",
                "Amazon.com": "",
                "Amazon.co.uk": "",
                "Amazon.de": "",
                "Amazon.fr": "",
                "Amazon.es": "",
                "Amazon.it": "",
                "Amazon.co.jp": "",
                "Amazon.ca": "",
                "Amazon.com.au": "",
                "Amazon.nl": "",
                "Amazon.pl": "",
                "Amazon.se": "",
                "descriptions": {},
                "keywords": {},
                "categories": {},
            }

            for lang_code, lang_data in project_data["coloringBook"][
                "languageVersions"
            ].items():
                uploader_data = lang_data.get("uploaderData", {})

                transformed_data["titles"][lang_code] = uploader_data.get("Title", "")
                transformed_data["subtitles"][lang_code] = uploader_data.get(
                    "Subtitle", ""
                )
                transformed_data["descriptions"][lang_code] = uploader_data.get(
                    "Description", ""
                )

                keywords = []
                for i in range(1, 8):  # Keywords 1 to 7
                    keyword = uploader_data.get(f"Keywords {i}", "")
                    if keyword:
                        keywords.append(keyword)
                transformed_data["keywords"][lang_code] = keywords

                categories = []
                for i in range(1, 4):  # Category 1 to 3
                    category = uploader_data.get(f"Category {i}", "")
                    if category:
                        categories.append(category)
                transformed_data["categories"][lang_code] = categories

            self.messenger.info(
                f"DEBUG: prepare_excel_data - transformed_data: {transformed_data}"
            )
            return transformed_data
        except Exception as e:
            self.messenger.error(f"Error in prepare_excel_data: {e}")
            return None
