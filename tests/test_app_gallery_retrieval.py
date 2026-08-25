import unittest

from studies.application_retrieval.gallery import METHODS, evaluate_gallery_retrieval


class ApplicationGalleryRetrievalTests(unittest.TestCase):
    def test_digits_end_to_end(self):
        result = evaluate_gallery_retrieval("digits", 3)
        self.assertEqual({row["method"] for row in result["frontier"]}, set(METHODS))
        self.assertTrue(all(0 <= row["map_at_10"] <= 1 for row in result["frontier"]))
        self.assertEqual(result["metadata"]["source"], "sklearn")


if __name__ == "__main__":
    unittest.main()
