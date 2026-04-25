from django import forms


class DocumentUploadForm(forms.Form):
    deal_id = forms.CharField(
        label="案件ID",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：DEAL-000001"}),
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=True,
        choices=[
            ("PRE_CLOSE", "PRE_CLOSE：クロージング前"),
            ("DAY1", "DAY1：Day1対応"),
            ("DAY30", "DAY30：30日以内"),
            ("DAY100", "DAY100：100日計画"),
            ("TSA", "TSA：TSA対応"),
            ("POST100", "POST100：100日後"),
        ],
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=True,
        choices=[
            ("PMO", "PMO：全体管理"),
            ("HR", "HR：人事・労務"),
            ("IT", "IT：IT・システム"),
            ("FINANCE", "FINANCE：財務・会計"),
            ("LEGAL", "LEGAL：法務・契約"),
            ("SALES", "SALES：営業・顧客"),
            ("OPS", "OPS：業務・オペレーション"),
            ("COMMS", "COMMS：社内外コミュニケーション"),
        ],
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
        choices=[
            ("CHECKLIST", "CHECKLIST：チェックリスト"),
            ("NOTICE", "NOTICE：通知文"),
            ("CONTRACT", "CONTRACT：契約書"),
            ("MINUTES", "MINUTES：議事録"),
            ("EVIDENCE", "EVIDENCE：証跡"),
            ("REPORT", "REPORT：レポート"),
            ("TEMPLATE", "TEMPLATE：テンプレート"),
            ("OTHER", "OTHER：その他"),
        ],
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
        choices=[
            ("INTERNAL", "INTERNAL：社内"),
            ("CONFIDENTIAL", "CONFIDENTIAL：機密"),
            ("PUBLIC", "PUBLIC：公開可"),
        ],
        initial="INTERNAL",
    )

    linked_task_id = forms.CharField(
        label="関連タスクID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：TASK-000001"}),
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
    )

    is_report_flag = forms.BooleanField(
        label="レポートとして扱う",
        required=False,
    )

    file = forms.FileField(
        label="アップロードファイル",
        required=True,
    )