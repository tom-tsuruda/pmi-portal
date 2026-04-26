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


class DecisionCreateForm(forms.Form):
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
        label="意思決定タイトル",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：Day1通知方針を承認"}),
    )

    summary = forms.CharField(
        label="要約",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "意思決定の概要を入力してください。",
            }
        ),
    )

    decision_detail = forms.CharField(
        label="詳細",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "決定内容、背景、検討経緯などを入力してください。",
            }
        ),
    )

    decision_type = forms.ChoiceField(
        label="意思決定種別",
        required=True,
        choices=[
            ("GENERAL", "GENERAL：一般"),
            ("POLICY", "POLICY：方針"),
            ("APPROVAL", "APPROVAL：承認"),
            ("ESCALATION", "ESCALATION：エスカレーション"),
            ("RISK_RESPONSE", "RISK_RESPONSE：リスク対応"),
            ("BUDGET", "BUDGET：予算"),
            ("SCOPE", "SCOPE：スコープ"),
        ],
        initial="GENERAL",
    )

    decided_by_user_id = forms.CharField(
        label="決定者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    decided_on = forms.CharField(
        label="決定日",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：2026-04-25"}),
    )

    decision_meeting_name = forms.CharField(
        label="会議名",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：PMI週次会議 / SteerCo"}),
    )

    related_task_id = forms.CharField(
        label="関連タスクID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：TASK-000001"}),
    )

    related_raid_id = forms.CharField(
        label="関連RAID ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：RAID-000001"}),
    )

    related_document_id = forms.CharField(
        label="関連資料ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：DOC-000001"}),
    )

    impact_summary = forms.CharField(
        label="影響概要",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "この決定により影響を受ける業務・部門・期限などを入力してください。",
            }
        ),
    )

    followup_action_required_flag = forms.BooleanField(
        label="フォローアップ対応が必要",
        required=False,
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=True,
        choices=[
            ("DRAFT", "DRAFT：下書き"),
            ("PROPOSED", "PROPOSED：提案中"),
            ("DECIDED", "DECIDED：決定済み"),
            ("SUPERSEDED", "SUPERSEDED：後続決定で上書き"),
            ("CANCELLED", "CANCELLED：取消"),
        ],
        initial="DRAFT",
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [
            ("", "案件がありません。先に案件を登録してください。")
        ]


class DecisionFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "タイトル・要約・詳細で検索"}),
    )

    deal_id = forms.ChoiceField(
        label="案件",
        required=False,
        choices=[],
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=False,
        choices=[("", "すべて")] + PHASE_CHOICES,
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=False,
        choices=[("", "すべて")] + WORKSTREAM_CHOICES,
    )

    decision_type = forms.ChoiceField(
        label="意思決定種別",
        required=False,
        choices=[
            ("", "すべて"),
            ("GENERAL", "GENERAL"),
            ("POLICY", "POLICY"),
            ("APPROVAL", "APPROVAL"),
            ("ESCALATION", "ESCALATION"),
            ("RISK_RESPONSE", "RISK_RESPONSE"),
            ("BUDGET", "BUDGET"),
            ("SCOPE", "SCOPE"),
        ],
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[
            ("", "すべて"),
            ("DRAFT", "DRAFT"),
            ("PROPOSED", "PROPOSED"),
            ("DECIDED", "DECIDED"),
            ("SUPERSEDED", "SUPERSEDED"),
            ("CANCELLED", "CANCELLED"),
        ],
    )

    decided_by_user_id = forms.CharField(
        label="決定者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [("", "すべて")]