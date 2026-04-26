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

DOCUMENT_TYPE_CHOICES = [
    ("CHECKLIST", "CHECKLIST：チェックリスト"),
    ("NOTICE", "NOTICE：通知文"),
    ("CONTRACT", "CONTRACT：契約書"),
    ("MINUTES", "MINUTES：議事録"),
    ("EVIDENCE", "EVIDENCE：証跡"),
    ("REPORT", "REPORT：レポート"),
    ("TEMPLATE", "TEMPLATE：テンプレート"),
    ("OTHER", "OTHER：その他"),
]

ACCESS_LEVEL_CHOICES = [
    ("INTERNAL", "INTERNAL：社内"),
    ("CONFIDENTIAL", "CONFIDENTIAL：機密"),
    ("PUBLIC", "PUBLIC：公開可"),
]


class DocumentUploadForm(forms.Form):
    """
    案件に紐づく資料・証跡アップロード用フォーム。
    """

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

    document_title = forms.CharField(
        label="資料タイトル",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：Day1従業員向け通知文案"}),
    )

    document_type = forms.ChoiceField(
        label="資料種別",
        required=True,
        choices=DOCUMENT_TYPE_CHOICES,
        initial="EVIDENCE",
    )

    category = forms.CharField(
        label="カテゴリ",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：Day1 / 人事 / 法務"}),
    )

    subcategory = forms.CharField(
        label="サブカテゴリ",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：通知 / 承認 / 証跡"}),
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    access_level = forms.ChoiceField(
        label="アクセスレベル",
        required=True,
        choices=ACCESS_LEVEL_CHOICES,
        initial="INTERNAL",
    )

    linked_task_id = forms.ChoiceField(
        label="関連タスク",
        required=False,
        choices=[],
    )

    linked_raid_id = forms.CharField(
        label="関連RAID ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：RAID-000001"}),
    )

    tags = forms.CharField(
        label="タグ",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：Day1,HR,通知"}),
    )

    document_purpose = forms.CharField(
        label="資料の目的",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "この資料を何のために使うかを入力してください。",
            }
        ),
    )

    is_template_flag = forms.BooleanField(
        label="テンプレートとして扱う",
        required=False,
    )

    is_evidence_flag = forms.BooleanField(
        label="証跡として扱う",
        required=False,
        initial=True,
    )

    is_report_flag = forms.BooleanField(
        label="レポートとして扱う",
        required=False,
    )

    file = forms.FileField(
        label="アップロードファイル",
        required=True,
    )

    def __init__(self, *args, deal_choices=None, task_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [
            ("", "案件がありません。先に案件を登録してください。")
        ]

        self.fields["linked_task_id"].choices = task_choices or [
            ("", "関連タスクなし")
        ]


class TemplateUploadForm(forms.Form):
    """
    テンプレートライブラリ登録専用フォーム。
    案件・担当者・関連タスク・証跡項目は表示しない。
    """

    document_title = forms.CharField(
        label="テンプレート名",
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：Day1全社アナウンス / 支配権変更条項（COC）・重要契約確認表"
            }
        ),
    )

    phase_id = forms.ChoiceField(
        label="主に使うフェーズ",
        required=True,
        choices=PHASE_CHOICES,
    )

    workstream_id = forms.ChoiceField(
        label="主に使うワークストリーム",
        required=True,
        choices=WORKSTREAM_CHOICES,
    )

    category = forms.CharField(
        label="カテゴリ",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：Communication / HR / IT / Finance / Legal / PMO"
            }
        ),
    )

    subcategory = forms.CharField(
        label="サブカテゴリ",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：FAQ / 通知文 / 契約確認 / 議事録 / 報告"
            }
        ),
    )

    tags = forms.CharField(
        label="タグ",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：Day1,FAQ,COC,支配権変更,RACI,SteerCo"
            }
        ),
    )

    document_purpose = forms.CharField(
        label="目的・使い方",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "このテンプレートをどの場面で使うか、使い方や注意点を入力してください。",
            }
        ),
    )

    access_level = forms.ChoiceField(
        label="アクセスレベル",
        required=True,
        choices=ACCESS_LEVEL_CHOICES,
        initial="INTERNAL",
    )

    file = forms.FileField(
        label="テンプレートファイル",
        required=True,
    )


class DocumentFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "資料名・ファイル名・タグで検索",
            }
        ),
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

    document_type = forms.ChoiceField(
        label="資料種別",
        required=False,
        choices=[("", "すべて")] + DOCUMENT_TYPE_CHOICES,
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[
            ("", "すべて"),
            ("DRAFT", "DRAFT"),
            ("ACTIVE", "ACTIVE"),
            ("APPROVED", "APPROVED"),
            ("DELETED", "DELETED"),
        ],
    )

    access_level = forms.ChoiceField(
        label="アクセスレベル",
        required=False,
        choices=[
            ("", "すべて"),
            ("INTERNAL", "INTERNAL"),
            ("CONFIDENTIAL", "CONFIDENTIAL"),
            ("PUBLIC", "PUBLIC"),
        ],
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    template_only = forms.BooleanField(
        label="テンプレートのみ",
        required=False,
        initial=False,
    )

    evidence_only = forms.BooleanField(
        label="証跡のみ",
        required=False,
        initial=False,
    )

    report_only = forms.BooleanField(
        label="レポートのみ",
        required=False,
        initial=False,
    )

    show_deleted = forms.BooleanField(
        label="削除済みも表示",
        required=False,
        initial=False,
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [("", "すべて")]