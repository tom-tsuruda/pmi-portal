from django import forms


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

SYNERGY_TYPE_CHOICES = [
    ("COST_REDUCTION", "COST_REDUCTION：コスト削減"),
    ("REVENUE_UPSIDE", "REVENUE_UPSIDE：売上拡大"),
    ("PROCUREMENT", "PROCUREMENT：購買条件改善"),
    ("IT_RATIONALIZATION", "IT_RATIONALIZATION：システム統合効果"),
    ("WORKFORCE_OPTIMIZATION", "WORKFORCE_OPTIMIZATION：人員配置最適化"),
    ("WORKING_CAPITAL", "WORKING_CAPITAL：運転資本改善"),
    ("CAPEX_OPTIMIZATION", "CAPEX_OPTIMIZATION：設備投資最適化"),
    ("OTHER", "OTHER：その他"),
]

STATUS_CHOICES = [
    ("PLANNED", "PLANNED：計画中"),
    ("IN_PROGRESS", "IN_PROGRESS：実行中"),
    ("ACHIEVED", "ACHIEVED：達成"),
    ("AT_RISK", "AT_RISK：注意"),
    ("CANCELLED", "CANCELLED：中止"),
]


class SynergyCreateForm(forms.Form):
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

    synergy_type = forms.ChoiceField(
        label="シナジー種別",
        required=True,
        choices=SYNERGY_TYPE_CHOICES,
    )

    initiative_name = forms.CharField(
        label="施策名",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：購買条件統一による原価低減"}),
    )

    description = forms.CharField(
        label="内容",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "このシナジー施策の内容を入力してください。",
            }
        ),
    )

    baseline_amount = forms.FloatField(
        label="基準額",
        required=False,
        initial=0,
        help_text="統合前の基準額です。例：現状コスト、現状売上など。",
    )

    target_amount = forms.FloatField(
        label="目標額",
        required=False,
        initial=0,
    )

    actual_amount = forms.FloatField(
        label="実績額",
        required=False,
        initial=0,
    )

    one_time_cost_amount = forms.FloatField(
        label="一時費用",
        required=False,
        initial=0,
        help_text="実現のために一度だけ発生する費用です。",
    )

    run_rate_amount = forms.FloatField(
        label="Run-rate効果額",
        required=False,
        initial=0,
        help_text="年間換算した継続効果額です。",
    )

    confidence_percent = forms.FloatField(
        label="確度％",
        required=False,
        initial=50,
        min_value=0,
        max_value=100,
    )

    planned_start_date = forms.DateField(
        label="計画開始日",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    planned_end_date = forms.DateField(
        label="計画終了日",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    actual_start_date = forms.DateField(
        label="実績開始日",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    actual_end_date = forms.DateField(
        label="実績終了日",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=True,
        choices=STATUS_CHOICES,
        initial="PLANNED",
    )

    slippage_flag = forms.BooleanField(
        label="遅延あり",
        required=False,
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
                "placeholder": "この施策の意味や確認ポイントを簡単に記載します。",
            }
        ),
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [
            ("", "案件がありません。先に案件を登録してください。")
        ]


class SynergyFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "施策名・内容で検索"}),
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

    synergy_type = forms.ChoiceField(
        label="シナジー種別",
        required=False,
        choices=[("", "すべて")] + SYNERGY_TYPE_CHOICES,
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[("", "すべて")] + STATUS_CHOICES,
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    slippage_only = forms.BooleanField(
        label="遅延ありのみ",
        required=False,
    )

    def __init__(self, *args, deal_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["deal_id"].choices = deal_choices or [("", "すべて")]