from django import forms


class TaskCreateForm(forms.Form):
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
        choices=[
            ("HIGH", "HIGH：高"),
            ("MEDIUM", "MEDIUM：中"),
            ("LOW", "LOW：低"),
        ],
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

    deal_id = forms.CharField(
        label="案件ID",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "例：DEAL-000001",
            }
        ),
    )

    status = forms.ChoiceField(
        label="ステータス",
        required=False,
        choices=[
            ("", "すべて"),
            ("TODO", "TODO"),
            ("IN_PROGRESS", "IN_PROGRESS"),
            ("DONE", "DONE"),
            ("BLOCKED", "BLOCKED"),
            ("CANCELLED", "CANCELLED"),
        ],
    )

    priority = forms.ChoiceField(
        label="優先度",
        required=False,
        choices=[
            ("", "すべて"),
            ("HIGH", "HIGH"),
            ("MEDIUM", "MEDIUM"),
            ("LOW", "LOW"),
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