import pandas as pd
import json
import os
from backend.app.modules.color_book.binding import config


class KDPExcelGenerator:
    def __init__(self):
        self.processed_data = []

    def get_cover(self, project_data, lang):
        # Assuming cover path is a template that needs the language
        # e.g., "output/MyProject/cover_{lang}.pdf"
        return project_data.get("cover_path_template", "").format(lang=lang)

    def get_manuscript(self, project_data):
        # Manuscript is the same for all versions
        return project_data.get("interior_path", "")

    def get_language(self, lang):
        return lang

    def get_title(self, project_data, lang):
        return project_data.get("titles", {}).get(lang, "")

    def get_subtitle(self, project_data, lang):
        return project_data.get("subtitles", {}).get(lang, "")

    def get_series(self, project_data):
        return ""  # Placeholder

    def get_author_prefix(self, project_data):
        return ""  # Placeholder

    def get_author_first_name(self, project_data):
        return project_data.get("author_first_name", "")

    def get_author_last_name(self, project_data):
        return project_data.get("author_last_name", "")

    def get_contributor_role(self, project_data):
        return ""  # Placeholder

    def get_contributor_prefix(self, project_data):
        return ""  # Placeholder

    def get_contributor_first_name(self, project_data):
        return ""  # Placeholder

    def get_contributor_last_name(self, project_data):
        return ""  # Placeholder

    def get_description(self, project_data, lang):
        return project_data.get("descriptions", {}).get(lang, "")

    def get_public_domain(self, project_data):
        return "No"  # Placeholder

    def get_minimum_age(self, project_data):
        return project_data.get("minimum_age", "")  # Placeholder

    def get_maximum_age(self, project_data):
        return project_data.get("maximum_age", "")  # Placeholder

    def get_primary_marketplace(self, project_data):
        return "Amazon.com"  # Placeholder

    def get_categories(self, project_data, lang):
        return project_data.get("categories", {}).get(lang, [])

    def get_keywords(self, project_data, lang):
        return project_data.get("keywords", {}).get(lang, [])

    def get_low_content_book(self, project_data):
        return "Yes"  # Placeholder

    def get_large_print(self, project_data):
        return "No"  # Placeholder

    def get_isbn(self, project_data):
        return ""  # Placeholder

    def get_imprint(self, project_data):
        return ""  # Placeholder

    def get_interior_paper_type(self, project_data):
        return "white paper"  # Placeholder

    def get_width_in(self, project_data):
        return "6"  # Placeholder

    def get_height_in(self, project_data):
        return "9"  # Placeholder

    def get_bleed_settings(self, project_data):
        return "Bleed"  # Placeholder

    def get_paperback_cover_finish(self, project_data):
        return "Matte"  # Placeholder

    def get_cover_include_barcode(self, project_data):
        return "NO"  # Placeholder

    def get_ai_generated(self, project_data):
        return "YES"  # Placeholder

    def get_ai_texts(self, project_data):
        return "YES"  # Placeholder

    def get_ai_texts_tool(self, project_data):
        return "Gemini"  # Placeholder

    def get_ai_images(self, project_data):
        return "YES"  # Placeholder

    def get_ai_images_tools(self, project_data):
        return "Imagen"  # Placeholder

    def get_ai_translations(self, project_data):
        return "YES"  # Placeholder

    def get_ai_translations_tool(self, project_data):
        return "Gemini"  # Placeholder

    def get_base_all_prices_on_primary_marketplace_price(self, project_data):
        return "NO"  # Placeholder

    def get_expanded_distribution(self, project_data):
        return "YES"  # Placeholder

    def get_amazon_com_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_co_uk_price(self, project_data):
        return "7.99"  # Placeholder

    def get_amazon_de_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_fr_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_es_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_it_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_co_jp_price(self, project_data):
        return "1000"  # Placeholder

    def get_amazon_ca_price(self, project_data):
        return "13.99"  # Placeholder

    def get_amazon_com_au_price(self, project_data):
        return "13.99"  # Placeholder

    def get_amazon_nl_price(self, project_data):
        return "9.99"  # Placeholder

    def get_amazon_pl_price(self, project_data):
        return "40.99"  # Placeholder

    def get_amazon_se_price(self, project_data):
        return "119.99"  # Placeholder

    def process_project(self, project_data):
        """
        Processes a single project and creates data rows for each language version.
        """

        for lang in project_data.get("languages", []):
            keywords = self.get_keywords(project_data, lang)
            categories = self.get_categories(project_data, lang)

            record = {
                "Cover": self.get_cover(project_data, lang),
                "Manuscript": self.get_manuscript(project_data),
                "Language": self.get_language(lang),
                "Title": self.get_title(project_data, lang),
                "Subtitle": self.get_subtitle(project_data, lang),
                "Series": self.get_series(project_data),
                "Author prefix": self.get_author_prefix(project_data),
                "Author first name": self.get_author_first_name(project_data),
                "Author last name": self.get_author_last_name(project_data),
                "Contributor role": self.get_contributor_role(project_data),
                "Contributor prefix": self.get_contributor_prefix(project_data),
                "Contributor first name": self.get_contributor_first_name(project_data),
                "Contributor last name": self.get_contributor_last_name(project_data),
                "Description": self.get_description(project_data, lang),
                "Public Domain": self.get_public_domain(project_data),
                "Minimum age": self.get_minimum_age(project_data),
                "Maximum age": self.get_maximum_age(project_data),
                "Primary Marketplace": self.get_primary_marketplace(project_data),
                "Category 1": categories[0] if len(categories) > 0 else "",
                "Category 2": categories[1] if len(categories) > 1 else "",
                "Category 3": categories[2] if len(categories) > 2 else "",
                "Keywords 1": keywords[0] if len(keywords) > 0 else "",
                "Keywords 2": keywords[1] if len(keywords) > 1 else "",
                "Keywords 3": keywords[2] if len(keywords) > 2 else "",
                "Keywords 4": keywords[3] if len(keywords) > 3 else "",
                "Keywords 5": keywords[4] if len(keywords) > 4 else "",
                "Keywords 6": keywords[5] if len(keywords) > 5 else "",
                "Keywords 7": keywords[6] if len(keywords) > 6 else "",
                "Low-Content Book": self.get_low_content_book(project_data),
                "Large print": self.get_large_print(project_data),
                "ISBN": self.get_isbn(project_data),
                "Imprint": self.get_imprint(project_data),
                "Interior & paper type": self.get_interior_paper_type(project_data),
                "Width (in)": self.get_width_in(project_data),
                "Height (in)": self.get_height_in(project_data),
                "Bleed Settings": self.get_bleed_settings(project_data),
                "Paperback cover finish": self.get_paperback_cover_finish(project_data),
                "Cover include barcode": self.get_cover_include_barcode(project_data),
                "AI-Generated": self.get_ai_generated(project_data),
                "AI-Texts": self.get_ai_texts(project_data),
                "AI-Texts-Tool": self.get_ai_texts_tool(project_data),
                "AI-Images": self.get_ai_images(project_data),
                "AI-Images-Tools": self.get_ai_images_tools(project_data),
                "AI-Translations": self.get_ai_translations(project_data),
                "AI-Translations-Tool": self.get_ai_translations_tool(project_data),
                "Base all prices on Primary Marketplace price": self.get_base_all_prices_on_primary_marketplace_price(
                    project_data
                ),
                "Expanded Distribution": self.get_expanded_distribution(project_data),
                "Amazon.com": self.get_amazon_com_price(project_data),
                "Amazon.co.uk": self.get_amazon_co_uk_price(project_data),
                "Amazon.de": self.get_amazon_de_price(project_data),
                "Amazon.fr": self.get_amazon_fr_price(project_data),
                "Amazon.es": self.get_amazon_es_price(project_data),
                "Amazon.it": self.get_amazon_it_price(project_data),
                "Amazon.co.jp": self.get_amazon_co_jp_price(project_data),
                "Amazon.ca": self.get_amazon_ca_price(project_data),
                "Amazon.com.au": self.get_amazon_com_au_price(project_data),
                "Amazon.nl": self.get_amazon_nl_price(project_data),
                "Amazon.pl": self.get_amazon_pl_price(project_data),
                "Amazon.se": self.get_amazon_se_price(project_data),
            }
            self.processed_data.append(record)

    def generate_excel(self, output_path):
        """
        Generates the KDP Excel file from the processed data.
        """
        PAPERBACK_COLUMNS = [
            "Cover",
            "Manuscript",
            "Language",
            "Title",
            "Subtitle",
            "Series",
            "Author prefix",
            "Author first name",
            "Author last name",
            "Contributor role",
            "Contributor prefix",
            "Contributor first name",
            "Contributor last name",
            "Description",
            "Public Domain",
            "Minimum age",
            "Maximum age",
            "Primary Marketplace",
            "Category 1",
            "Category 2",
            "Category 3",
            "Keywords 1",
            "Keywords 2",
            "Keywords 3",
            "Keywords 4",
            "Keywords 5",
            "Keywords 6",
            "Keywords 7",
            "Low-Content Book",
            "Large print",
            "ISBN",
            "Imprint",
            "Interior & paper type",
            "Width (in)",
            "Height (in)",
            "Bleed Settings",
            "Paperback cover finish",
            "Cover include barcode",
            "AI-Generated",
            "AI-Texts",
            "AI-Texts-Tool",
            "AI-Images",
            "AI-Images-Tools",
            "AI-Translations",
            "AI-Translations-Tool",
            "Base all prices on Primary Marketplace price",
            "Expanded Distribution",
            "Amazon.com",
            "Amazon.co.uk",
            "Amazon.de",
            "Amazon.fr",
            "Amazon.es",
            "Amazon.it",
            "Amazon.co.jp",
            "Amazon.ca",
            "Amazon.com.au",
            "Amazon.nl",
            "Amazon.pl",
            "Amazon.se",
        ]

        # Create a DataFrame from the processed data with specified columns
        final_df = pd.DataFrame(self.processed_data, columns=PAPERBACK_COLUMNS)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Use ExcelWriter to write to a specific sheet
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            final_df.to_excel(writer, sheet_name="Paperbacks", index=False)
        print(f"Successfully generated KDP Excel file at: {output_path}")


def generate_kdp_excel(project_data, output_path):
    """
    Main function to generate the KDP Excel file.
    """
    generator = KDPExcelGenerator()
    generator.process_project(project_data)
    generator.generate_excel(output_path)
