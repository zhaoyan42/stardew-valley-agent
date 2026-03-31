import os
import json
import glob

class WikiLoader:
    def __init__(self, wiki_root="data/wiki/"):
        self.wiki_root = wiki_root
        if not os.path.exists(self.wiki_root):
            os.makedirs(self.wiki_root)

    def get_l0_summary(self):
        """
        Returns a high-level summary of the available wiki categories.
        """
        categories = [d for d in os.listdir(self.wiki_root) if os.path.isdir(os.path.join(self.wiki_root, d))]
        return f"Wiki contains information about the following categories: {', '.join(categories)}."

    def get_l1_toc(self, category):
        """
        Returns a table of contents for a specific category.
        """
        category_path = os.path.join(self.wiki_root, category)
        if not os.path.exists(category_path):
            return f"Category '{category}' not found."
        
        files = glob.glob(os.path.join(category_path, "*.md")) + glob.glob(os.path.join(category_path, "*.json"))
        topics = [os.path.basename(f).split('.')[0] for f in files]
        return f"Category '{category}' contains: {', '.join(topics)}."

    def get_l2_details(self, category, topic):
        """
        Returns the full content of a specific topic in a category.
        """
        # Try both .md and .json
        for ext in ['.md', '.json']:
            file_path = os.path.join(self.wiki_root, category, f"{topic}{ext}")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return f"Topic '{topic}' in category '{category}' not found."

if __name__ == "__main__":
    # Test script
    loader = WikiLoader()
    print("L0:", loader.get_l0_summary())
    print("L1 (crops):", loader.get_l1_toc("crops"))
    print("L2 (parsnip):", loader.get_l2_details("crops", "parsnip"))
