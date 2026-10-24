import unittest
from axiom.compiler import run, LexError, ParseError, RuntimeAxiomError


class CompilerPrototypeTests(unittest.TestCase):
    def test_arithmetic_precedence(self):
        self.assertEqual(run("print(2 + 3 * 4)", output=lambda _: None), [14])

    def test_immutable_binding(self):
        with self.assertRaisesRegex(RuntimeAxiomError, "immutable"):
            run("let x = 1\nx = 2")

    def test_mutable_binding(self):
        self.assertEqual(run("var x = 1\nx = x + 2\nprint(x)", output=lambda _: None), [1, 3, 3])

    def test_boolean_comparison(self):
        self.assertEqual(run("print(3 >= 2)", output=lambda _: None), [True])

    def test_string(self):
        self.assertEqual(run('print("hello")', output=lambda _: None), ["hello"])

    def test_undefined_name(self):
        with self.assertRaisesRegex(RuntimeAxiomError, "undefined name"):
            run("print(missing)", output=lambda _: None)

    def test_division_by_zero(self):
        with self.assertRaisesRegex(RuntimeAxiomError, "division by zero"):
            run("print(1 / 0)", output=lambda _: None)

    def test_lex_error(self):
        with self.assertRaises(LexError):
            run("print(@)", output=lambda _: None)

    def test_parse_error(self):
        with self.assertRaises(ParseError):
            run("let = 2")


if __name__ == "__main__":
    unittest.main()
