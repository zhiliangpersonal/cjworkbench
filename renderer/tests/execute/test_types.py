import unittest
from cjwkernel.types import I18nMessage, QuickFix, QuickFixAction
from renderer.execute.types import PromptingError


class PromptingErrorTest(unittest.TestCase):
    def test_quick_fixes(self):
        err = PromptingError(
            [
                PromptingError.WrongColumnType(["A"], "text", frozenset({"number"})),
                PromptingError.WrongColumnType(
                    ["B", "C"], "datetime", frozenset({"number"})
                ),
            ]
        )
        quick_fixes_result = err.as_quick_fixes()
        self.assertEqual(
            quick_fixes_result,
            [
                QuickFix(
                    I18nMessage(
                        "py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.general",
                        {"found_type": "text", "best_wanted_type": "number"},
                    ),
                    QuickFixAction.PrependStep(
                        "converttexttonumber", {"colnames": ["A"]}
                    ),
                ),
                QuickFix(
                    I18nMessage(
                        "py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.general",
                        {"found_type": "datetime", "best_wanted_type": "number"},
                    ),
                    QuickFixAction.PrependStep(
                        "converttexttonumber", {"colnames": ["B", "C"]}
                    ),
                ),
            ],
        )

        error_result = err.as_error_message()
        self.assertEqual(
            error_result,
            [
                I18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.general",
                    {
                        "columns": 1,
                        "0": "“A”",
                        "found_type": "text",
                        "best_wanted_type": "number",
                    },
                ),
                I18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.general",
                    {
                        "columns": 2,
                        "0": "“B”",
                        "1": "“C”",
                        "found_type": "datetime",
                        "best_wanted_type": "number",
                    },
                ),
            ],
        )

    def test_quick_fixes_convert_to_text(self):
        err = PromptingError(
            [PromptingError.WrongColumnType(["A", "B"], None, frozenset({"text"}))]
        )
        quick_fixes_result = err.as_quick_fixes()
        self.assertEqual(
            quick_fixes_result,
            [
                QuickFix(
                    I18nMessage(
                        "py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.shouldBeText"
                    ),
                    QuickFixAction.PrependStep(
                        "converttotext", {"colnames": ["A", "B"]}
                    ),
                )
            ],
        )

        error_result = err.as_error_message()
        self.assertEqual(
            error_result,
            [
                I18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.shouldBeText",
                    {"columns": 2, "0": "“A”", "1": "“B”"},
                )
            ],
        )
