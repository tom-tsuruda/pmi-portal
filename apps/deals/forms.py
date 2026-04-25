from django import forms


class DealCreateForm(forms.Form):
    deal_name = forms.CharField(
        label="案件名",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：A社 PMI支援案件"}),
    )

    target_company_name = forms.CharField(
        label="対象会社名",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：株式会社サンプル"}),
    )

    deal_type = forms.CharField(
        label="案件種別",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：買収後統合 / 事業承継 / 再建支援"}),
    )

    region_main = forms.CharField(
        label="主な地域",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：大阪 / 東京 / 九州"}),
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    description = forms.CharField(
        label="説明",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "案件の概要、背景、注意点などを入力してください。",
            }
        ),
    )


class DealFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "案件名・対象会社名・説明で検索",
            }
        ),
    )

    deal_status = forms.ChoiceField(
        label="案件ステータス",
        required=False,
        choices=[
            ("", "すべて"),
            ("DRAFT", "DRAFT：下書き"),
            ("ACTIVE", "ACTIVE：進行中"),
            ("ON_HOLD", "ON_HOLD：保留"),
            ("COMPLETED", "COMPLETED：完了"),
            ("CANCELLED", "CANCELLED：中止"),
            ("ARCHIVED", "ARCHIVED：アーカイブ"),
        ],
    )

    deal_type = forms.CharField(
        label="案件種別",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：買収後統合"}),
    )

    region_main = forms.CharField(
        label="地域",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：大阪"}),
    )

    owner_user_id = forms.CharField(
        label="担当者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    show_archived = forms.BooleanField(
        label="アーカイブも表示",
        required=False,
        initial=False,
    )


class DealStatusUpdateForm(forms.Form):
    deal_status = forms.ChoiceField(
        label="案件ステータス",
        required=True,
        choices=[
            ("DRAFT", "DRAFT：下書き"),
            ("ACTIVE", "ACTIVE：進行中"),
            ("ON_HOLD", "ON_HOLD：保留"),
            ("COMPLETED", "COMPLETED：完了"),
            ("CANCELLED", "CANCELLED：中止"),
            ("ARCHIVED", "ARCHIVED：アーカイブ"),
        ],
    )