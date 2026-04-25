from django import forms


class QuestionnaireAnswerForm(forms.Form):
    """
    questionnaire_questions シートをもとに動的にフォームを作る。
    """

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.questions = questions or []

        for question in self.questions:
            question_id = question.get("question_id")
            question_text = question.get("question_text") or question.get("question_code")
            question_type = str(question.get("question_type") or "TEXT").upper()
            option_values = question.get("option_values") or ""
            default_value = question.get("default_value") or ""
            required_flag = str(question.get("required_flag", "0")) in ["1", "TRUE", "True", "true"]
            help_text = question.get("help_text") or ""
            beginner_guidance = question.get("beginner_guidance") or ""

            field_name = f"question_{question_id}"

            label = question_text
            if beginner_guidance:
                label = f"{question_text}"

            if question_type in ["YESNO", "BOOLEAN", "BOOL"]:
                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required_flag,
                    choices=[
                        ("YES", "はい"),
                        ("NO", "いいえ"),
                    ],
                    initial=default_value or "NO",
                    help_text=help_text or beginner_guidance,
                )

            elif question_type in ["SELECT", "CHOICE"]:
                choices = []
                for option in str(option_values).split(","):
                    option = option.strip()
                    if option:
                        choices.append((option, option))

                if not choices:
                    choices = [("", "選択してください")]

                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required_flag,
                    choices=choices,
                    initial=default_value,
                    help_text=help_text or beginner_guidance,
                )

            elif question_type in ["NUMBER", "INTEGER", "INT"]:
                self.fields[field_name] = forms.IntegerField(
                    label=label,
                    required=required_flag,
                    initial=default_value or None,
                    help_text=help_text or beginner_guidance,
                )

            else:
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=required_flag,
                    initial=default_value,
                    help_text=help_text or beginner_guidance,
                    widget=forms.Textarea(attrs={"rows": 2}),
                )