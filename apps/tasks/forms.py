from django import forms


PHASE_CHOICES = [
    ("PRE_CLOSE", "PRE_CLOSE：クロージング前"),
    ("DAY1", "DAY1：Day1対応"),
    ("DAY30", "DAY30：30日以内"),
    ("DAY100", "DAY100：100日計画"),
    ("TSA", "TSA：TSA対応"),
    ("POST100", "POST100：100日後"),
]

WORKSTREAM_CHOICES = [
    ("PMO", "PMO：全体管理"),
    ("HR", "HR：人事・労務"),
    ("IT", "IT：IT・システム"),
    ("FINANCE", "FINANCE：財務・会計"),
    ("LEGAL", "LEGAL：法務・契約"),
    ("SALES", "SALES：営業・顧客"),
    ("OPS", "OPS：業務・オペレーション"),
    ("COMMS", "COMMS：社内外コミュニケーション"),
]

PRIORITY_CHOICES = [
    ("HIGH", "HIGH：高"),
    ("MEDIUM", "MEDIUM：中"),
    ("LOW", "LOW：低"),
]

TASK_STATUS_CHOICES = [
    ("TODO", "TODO：未着手"),
    ("IN_PROGRESS", "IN_PROGRESS：対応中"),
    ("DONE", "DONE：完了"),
    ("BLOCKED", "BLOCKED：停止中"),
    ("CANCELLED", "CANCELLED：中止"),
]


class TaskCreateForm(forms.Form):
    deal_id = forms.ChoiceField(
        label="案件",
        required=True,
        choices=[],
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=True,
        choices=PHASE_CHOICES,
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=True,
        choices=WORKSTREAM_CHOICES,
    )

    title = forms.CharField(
        label="タスク名",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：Day1向け従業員通知文の確認"}),
    )

    description = forms.CharField(
        label="説明",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "タスクの内容、背景、完了条件などを入力してください。",
            }
        ),
    )

    priority = forms.ChoiceField(
        label="優先度",
        required=True,
        choices=PRIORITY_CHOICES,
        initial="MEDIUM",
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    due_date = forms.CharField(
        label="期限",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：2026-04-30"}),
    )

    template_source_id = forms.CharField(
        label="テンプレート元ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：TPL-000001"}),
    )

    regulation_flag = forms.BooleanField(
        label="規制対応タスク",
        required=False,
    )

    why_this_task = forms.CharField(
        label="このタスクが必要な理由",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "なぜこのタスクが必要かを入力してください。",
            }
        ),
    )

    beginner_guidance = forms.CharField(
        label="初心者向け説明",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "PMI経験が少ない人向けに、確認ポイントを簡単に記載します。",
            }
        ),
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [
            ("", "案件がありません。先に案件を登録してください。")
        ]


class TaskEditForm(TaskCreateForm):
    status = forms.ChoiceField(
        label="ステータス",
        required=True,
        choices=TASK_STATUS_CHOICES,
        initial="TODO",
    )

    completion_note = forms.CharField(
        label="完了・更新メモ",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "完了理由、更新内容、次の対応などを入力してください。",
            }
        ),
    )


class TaskFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "タスク名・説明で検索",
            }
        ),
    )

    deal_id = forms.ChoiceField(
        label="案件",
        required=False,
        choices=[],
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[("", "すべて")] + TASK_STATUS_CHOICES,
    )

    priority = forms.ChoiceField(
        label="優先度",
        required=False,
        choices=[("", "すべて")] + PRIORITY_CHOICES,
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=False,
        choices=[("", "すべて")] + PHASE_CHOICES,
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=False,
        choices=[
            ("", "すべて"),
            ("PMO", "PMO"),
            ("HR", "HR"),
            ("IT", "IT"),
            ("FINANCE", "FINANCE"),
            ("LEGAL", "LEGAL"),
            ("SALES", "SALES"),
            ("OPS", "OPS"),
            ("COMMS", "COMMS"),
        ],
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：u001",
            }
        ),
    )

    show_cancelled = forms.BooleanField(
        label="CANCELLEDも表示",
        required=False,
        initial=False,
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [("", "すべて")]