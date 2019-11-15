from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Optional
from cjwkernel.types import I18nMessage, QuickFix, QuickFixAction, make_i18nMessage


class UnneededExecution(Exception):
    """A render would produce useless results."""

    pass


class TabCycleError(Exception):
    """The chosen tab exists, and it depends on the output of this tab."""

    pass


class TabOutputUnreachableError(Exception):
    """The chosen tab exists, and it is empty or has an error."""

    pass


class PromptingError(Exception):
    """
    Workbench found an error in the module parameters+dataframe; ask the user.

    This type of error will lead to user-visible error messages with Quick
    Fixes. Workbench won't invoke render(): it doesn't need to because it knows
    render() isn't ready for this input.

    Example: "calculate module expects numbers but you selected text columns.
    [convert to numbers]."
    """

    @dataclass(frozen=True)
    class WrongColumnType:
        """The chosen columns exist, but they have the wrong types."""

        # Even if there are multiple wanted_types, let's only show the user
        # a single QuickFix. It's less noisy that way. (Revisit later if
        # this becomes an issue.)

        column_names: List[str]

        found_type: Optional[str]
        """
        (Wrong) type of columns.

        Iff `wanted_types` contains "text", `found_type is None`. That's
        because we allow converting from _multiple_ column types to "text" all
        at the same time. (Converting to text is a special case: it has no
        options, because all options are in the input columns' formats.)
        """

        wanted_types: FrozenSet[str]
        """
        Required types of columns.
        """

        def __post_init__(self):
            assert (self.found_type is None) == ("text" in self.wanted_types)

        @property
        def best_wanted_type_id(self):
            if "text" in self.wanted_types:
                return "text"
            elif "number" in self.wanted_types:
                return "number"
            elif "datetime" in self.wanted_types:
                return "datetime"
            else:
                raise RuntimeError(f"Unhandled wanted_types: {self.wanted_types}")

        @property
        def should_be_text(self):
            return self.found_type is None

        def as_error_message(self) -> I18nMessage:
            """Build a message to prompt the user to use a quick fix."""
            # TODO make each quick fix get its own paragraph. (For now, quick
            # fixes are nothing but buttons.)

            icu_args = {
                "columns": len(self.column_names),
                **{
                    str(i): f"“{self.column_names[i]}”"
                    for i in range(0, len(self.column_names))
                },
            }

            if self.should_be_text:
                # Convert to Text
                # i18n: The parameter {columns} will contain the total number of columns that need to be converted; you will also receive the column names as {0}, {1}, {2}, etc.
                return make_i18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.shouldBeText",
                    "{ columns, plural, offset:2"
                    " =1 {The column {0} must be converted to Text.}"
                    " =2 {The columns {0} and {1} must be converted to Text.}"
                    " one {The columns {0}, {1} and {2} must be converted to Text.}"
                    " other {The columns {0}, {1} and # others must be converted to Text.}}",
                    icu_args,
                )
            else:
                icu_args["found_type"] = self.found_type
                icu_args["best_wanted_type"] = self.best_wanted_type_id
                # i18n: The parameter {columns} will contain the total number of columns that need to be converted; you will also receive the column names: {0}, {1}, {2}, etc. The parameters {found_type} and {best_wanted_type} will have values among "text", "number", "datetime"; however, including a (possibly empty) "other" case is mandatory.
                return make_i18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.general",
                    "{ columns, plural, offset:2"
                    " =1 {The column {0} must be converted from { found_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}} to {best_wanted_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}}.}"
                    " =2 {The columns {0} and {1} must be converted from { found_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}} to {best_wanted_type, select, text {Text} number {Numbers} datetime {Dates & Times}  other{}}.}"
                    " one {The columns {0}, {1} and {2} must be converted from { found_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}} to {best_wanted_type, select, text {Text} number {Numbers} datetime {Dates & Times} other{}}.}"
                    " other {The columns {0}, {1} and # others must be converted from { found_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}} to {best_wanted_type, select, text {Text} number {Numbers} datetime {Dates & Times} other{}}.}}",
                    icu_args,
                )

        def as_quick_fix(self):
            """Build a QuickFix that would resolve this error."""
            if self.should_be_text:
                message = make_i18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.shouldBeText",
                    "Convert to Text.",
                )
            else:
                # i18n: The parameters {found_type} and {best_wanted_type} will have values among "text", "number", "datetime"; however, including an (possibly empty) "other" case is mandatory.
                message = make_i18nMessage(
                    "py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.general",
                    "Convert { found_type, select, text {Text} number {Numbers} datetime {Dates & Times} other {}} to {best_wanted_type, select, text {Text} number {Numbers} datetime {Dates & Times} other{}}.",
                    {
                        "found_type": self.found_type,
                        "best_wanted_type": self.best_wanted_type_id,
                    },
                )

            params = {"colnames": self.column_names}

            if "text" in self.wanted_types:
                module_id = "converttotext"
            elif "number" in self.wanted_types:
                module_id = "converttexttonumber"
            elif "datetime" in self.wanted_types:
                module_id = "convert-date"
            else:
                raise RuntimeError(f"Unhandled wanted_types: {self.wanted_types}")

            return QuickFix(message, QuickFixAction.PrependStep(module_id, params))

    def __init__(self, errors: List[PromptingError.WrongColumnType]):
        super().__init__("user must change something before we render")
        self.errors = errors

    def __eq__(self, other):
        return isinstance(other, self.type) and other.errors == self.errors

    def as_error_message(self) -> List[I18nMessage]:
        return [err.as_error_message() for err in self.errors]

    def as_quick_fixes(self) -> List[QuickFix]:
        """Build a List of QuickFix: one per error."""
        return [err.as_quick_fix() for err in self.errors]
