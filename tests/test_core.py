import unittest

from xml_character_reference_lib import DecodeError, decode


class TestDecode(unittest.TestCase):
    def test_decimal_reference(self):
        self.assertEqual(decode("&#65;"), "A")

    def test_hexadecimal_reference_lowercase(self):
        self.assertEqual(decode("&#x41;"), "A")

    def test_hexadecimal_reference_uppercase_x_and_digits(self):
        self.assertEqual(decode("&#X41;"), "A")

    def test_multiple_references(self):
        self.assertEqual(decode("&#72;&#x69;"), "Hi")

    def test_text_around_references(self):
        self.assertEqual(decode("a&#66;c"), "aBc")

    def test_no_references_returns_unchanged(self):
        self.assertEqual(decode("plain text"), "plain text")

    def test_empty_string(self):
        self.assertEqual(decode(""), "")

    def test_ampersand_without_reference_is_passed_through(self):
        self.assertEqual(decode("a & b"), "a & b")

    def test_incomplete_reference_is_passed_through(self):
        self.assertEqual(decode("&#"), "&#")

    def test_missing_semicolon_is_passed_through(self):
        self.assertEqual(decode("&#65"), "&#65")

    def test_decoding_is_single_pass(self):
        # The replacement text is not rescanned.
        self.assertEqual(decode("&#38;#65;"), "&#65;")

    def test_tab_newline_and_carriage_return_are_legal(self):
        self.assertEqual(decode("&#9;&#10;&#13;"), "\t\n\r")

    def test_surrogate_is_rejected(self):
        with self.assertRaises(DecodeError):
            decode("&#xD800;")

    def test_null_is_rejected(self):
        with self.assertRaises(DecodeError):
            decode("&#0;")

    def test_out_of_range_is_rejected(self):
        with self.assertRaises(DecodeError):
            decode("&#x110000;")

    def test_non_character_fffe_is_rejected(self):
        with self.assertRaises(DecodeError):
            decode("&#xFFFE;")

    def test_supplementary_plane_is_accepted(self):
        self.assertEqual(decode("&#x1F600;"), "\U0001F600")

    def test_non_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            decode(65)


if __name__ == "__main__":
    unittest.main()
