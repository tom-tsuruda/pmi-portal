from django import forms


class RaidCreateForm(forms.Form):
    deal_id = forms.CharField(
        label="案件ID",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：DEAL-000001"}),
    )

    raid_type = forms.ChoiceField(
        label="RAID種別",
        required=True,
        choices=[
            ("RISK", "RISK：リスク"),
            ("ASSUMPTION", "ASSUMPTION：前提条件"),
            ("ISSUE", "ISSUE：発生済み課題"),
            ("DEPENDENCY", "DEPENDENCY：依存関係"),
        ],
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

    title = forms.CharField(
        label="タイトル",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：給与支払が遅れるリスク"}),
    )

    description = forms.CharField(
        label="内容",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "リスク・課題・前提・依存関係の内容を入力してください。",
            }
        ),
    )

    probability = forms.ChoiceField(
        label="発生可能性",
        required=True,
        choices=[
            (1, "1：低い"),
            (2, "2：やや低い"),
            (3, "3：中程度"),
            (4, "4：高い"),
            (5, "5：非常に高い"),
        ],
        initial=3,
    )

    impact = forms.ChoiceField(
        label="影響度",
        required=True,
        choices=[
            (1, "1：小さい"),
            (2, "2：やや小さい"),
            (3, "3：中程度"),
            (4, "4：大きい"),
            (5, "5：非常に大きい"),
        ],
        initial=3,
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    due_date = forms.CharField(
        label="対応期限",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：2026-04-30"}),
    )

    mitigation_plan = forms.CharField(
        label="対応策・軽減策",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "例：事前に関係部門へ確認し、代替手段を準備する。",
            }
        ),
    )

    trigger_condition = forms.CharField(
        label="発動条件・注意条件",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "例：期日までに承認が下りない場合、エスカレーションする。",
            }
        ),
    )


class RaidFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "タイトル・内容・対応策で検索",
            }
        ),
    )

    deal_id = forms.CharField(
        label="案件ID",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：DEAL-000001",
            }
        ),
    )

    raid_type = forms.ChoiceField(
        label="RAID種別",
        required=False,
        choices=[
            ("", "すべて"),
            ("RISK", "RISK"),
            ("ASSUMPTION", "ASSUMPTION"),
            ("ISSUE", "ISSUE"),
            ("DEPENDENCY", "DEPENDENCY"),
        ],
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[
            ("", "すべて"),
            ("OPEN", "OPEN"),
            ("IN_PROGRESS", "IN_PROGRESS"),
            ("WATCH", "WATCH"),
            ("CLOSED", "CLOSED"),
        ],
    )

    phase_id = forms.ChoiceField(
        label="フェーズ",
        required=False,
        choices=[
            ("", "すべて"),
            ("PRE_CLOSE", "PRE_CLOSE"),
            ("DAY1", "DAY1"),
            ("DAY30", "DAY30"),
            ("DAY100", "DAY100"),
            ("TSA", "TSA"),
            ("POST100", "POST100"),
        ],
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

    escalation_level = forms.ChoiceField(
        label="重要度",
        required=False,
        choices=[
            ("", "すべて"),
            ("CRITICAL", "CRITICAL"),
            ("HIGH", "HIGH"),
            ("MEDIUM", "MEDIUM"),
            ("LOW", "LOW"),
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

    show_closed = forms.BooleanField(
        label="CLOSEDも表示",
        required=False,
        initial=False,
    )