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

KPI_CATEGORY_CHOICES = [
    ("PMI_PROGRESS", "PMI_PROGRESS：PMI進捗"),
    ("FINANCIAL", "FINANCIAL：財務"),
    ("SYNERGY", "SYNERGY：シナジー"),
    ("CUSTOMER", "CUSTOMER：顧客"),
    ("EMPLOYEE", "EMPLOYEE：従業員"),
    ("IT", "IT：IT・システム"),
    ("OPERATIONS", "OPERATIONS：業務"),
    ("RISK", "RISK：リスク"),
    ("COMPLIANCE", "COMPLIANCE：コンプライアンス"),
    ("OTHER", "OTHER：その他"),
]

MEASUREMENT_FREQUENCY_CHOICES = [
    ("DAILY", "DAILY：日次"),
    ("WEEKLY", "WEEKLY：週次"),
    ("MONTHLY", "MONTHLY：月次"),
    ("QUARTERLY", "QUARTERLY：四半期"),
    ("ADHOC", "ADHOC：随時"),
]

STATUS_COLOR_CHOICES = [
    ("GREEN", "GREEN：良好"),
    ("YELLOW", "YELLOW：注意"),
    ("RED", "RED：危険"),
]


class KpiCreateForm(forms.Form):
    deal_id = forms.ChoiceField(
        label="案件",
        required=True,
        choices=[],
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=True,
        choices=WORKSTREAM_CHOICES,
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=True,
        choices=PHASE_CHOICES,
    )

    kpi_name = forms.CharField(
        label="KPI名",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：タスク完了率 / 証跡添付率 / 顧客解約率"}),
    )

    kpi_category = forms.ChoiceField(
        label="KPIカテゴリ",
        required=True,
        choices=KPI_CATEGORY_CHOICES,
    )

    definition = forms.CharField(
        label="定義",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "このKPIをどのように計算・判断するかを入力してください。",
            }
        ),
    )

    unit = forms.CharField(
        label="単位",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：% / 件 / 千円 / 人"}),
    )

    baseline_value = forms.FloatField(
        label="基準値",
        required=False,
        initial=0,
    )

    target_value = forms.FloatField(
        label="目標値",
        required=False,
        initial=0,
    )

    actual_value = forms.FloatField(
        label="実績値",
        required=False,
        initial=0,
    )

    measurement_frequency = forms.ChoiceField(
        label="測定頻度",
        required=True,
        choices=MEASUREMENT_FREQUENCY_CHOICES,
        initial="MONTHLY",
    )

    measurement_date = forms.DateField(
        label="測定日",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    threshold_red = forms.FloatField(
        label="RED基準",
        required=False,
        initial=0,
    )

    threshold_yellow = forms.FloatField(
        label="YELLOW基準",
        required=False,
        initial=0,
    )

    threshold_green = forms.FloatField(
        label="GREEN基準",
        required=False,
        initial=0,
    )

    status_color = forms.ChoiceField(
        label="ステータスカラー",
        required=True,
        choices=STATUS_COLOR_CHOICES,
        initial="GREEN",
    )

    note = forms.CharField(
        label="メモ",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    beginner_guidance = forms.CharField(
        label="初心者向け説明",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "このKPIを見る意味や、注意すべきポイントを簡単に記載します。",
            }
        ),
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [
            ("", "案件がありません。先に案件を登録してください。")
        ]


class KpiFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "KPI名・定義で検索"}),
    )

    deal_id = forms.ChoiceField(
        label="案件",
        required=False,
        choices=[],
    )

    workstream_id = forms.ChoiceField(
        label="ワークストリーム",
        required=False,
        choices=[("", "すべて")] + WORKSTREAM_CHOICES,
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=False,
        choices=[("", "すべて")] + PHASE_CHOICES,
    )

    kpi_category = forms.ChoiceField(
        label="KPIカテゴリ",
        required=False,
        choices=[("", "すべて")] + KPI_CATEGORY_CHOICES,
    )

    measurement_frequency = forms.ChoiceField(
        label="測定頻度",
        required=False,
        choices=[("", "すべて")] + MEASUREMENT_FREQUENCY_CHOICES,
    )

    status_color = forms.ChoiceField(
        label="ステータスカラー",
        required=False,
        choices=[
            ("", "すべて"),
            ("GREEN", "GREEN"),
            ("YELLOW", "YELLOW"),
            ("RED", "RED"),
        ],
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [("", "すべて")]