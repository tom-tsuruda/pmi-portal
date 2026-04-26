from django import forms


YES_NO_UNKNOWN_NA_CHOICES = [
    ("YES", "はい"),
    ("NO", "いいえ"),
    ("UNKNOWN", "不明"),
    ("NA", "該当なし"),
]


class QuestionnaireAnswerForm(forms.Form):
    """
    questionnaire_questions シートをもとに動的にフォームを作る。

    YESNO / BOOLEAN / BOOL の場合も、
    PMI実務では「不明」自体が確認タスクになるため、
    はい / いいえ / 不明 / 該当なし の4択にする。
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
            required_flag = str(question.get("required_flag", "0")) in [
                "1",
                "TRUE",
                "True",
                "true",
                "YES",
                "yes",
                "はい",
            ]
            help_text = question.get("help_text") or ""
            beginner_guidance = question.get("beginner_guidance") or ""

            if not question_id:
                continue

            field_name = f"question_{question_id}"
            label = question_text

            if question_type in ["YESNO", "BOOLEAN", "BOOL"]:
                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required_flag,
                    choices=YES_NO_UNKNOWN_NA_CHOICES,
                    initial=default_value or "UNKNOWN",
                    help_text=help_text or beginner_guidance,
                    widget=forms.Select(
                        attrs={
                            "class": "question-select",
                        }
                    ),
                )

            elif question_type in ["SELECT", "CHOICE"]:
                choices = []

                for option in str(option_values).split(","):
                    option = option.strip()

                    if option:
                        choices.append((option, option))

                if not choices:
                    choices = [
                        ("", "選択してください"),
                    ]

                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required_flag,
                    choices=choices,
                    initial=default_value,
                    help_text=help_text or beginner_guidance,
                    widget=forms.Select(
                        attrs={
                            "class": "question-select",
                        }
                    ),
                )

            elif question_type in ["NUMBER", "INTEGER", "INT"]:
                self.fields[field_name] = forms.IntegerField(
                    label=label,
                    required=required_flag,
                    initial=default_value or None,
                    help_text=help_text or beginner_guidance,
                    widget=forms.NumberInput(
                        attrs={
                            "class": "question-input",
                        }
                    ),
                )

            else:
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=required_flag,
                    initial=default_value,
                    help_text=help_text or beginner_guidance,
                    widget=forms.Textarea(
                        attrs={
                            "rows": 2,
                            "class": "question-textarea",
                        }
                    ),
                )