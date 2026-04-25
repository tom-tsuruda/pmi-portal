from django import forms


OBJECT_TYPE_CHOICES = [
    ("TASK", "TASK：タスク"),
    ("RAID", "RAID：RAID"),
    ("DOCUMENT", "DOCUMENT：資料"),
    ("DECISION", "DECISION：意思決定"),
]


APPROVAL_STATUS_CHOICES = [
    ("REQUESTED", "REQUESTED：承認依頼中"),
    ("APPROVED", "APPROVED：承認済み"),
    ("REJECTED", "REJECTED：却下"),
    ("RETURNED", "RETURNED：差し戻し"),
    ("CANCELLED", "CANCELLED：取消"),
]


class ApprovalCreateForm(forms.Form):
    deal_id = forms.CharField(
        label="案件ID",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：DEAL-000001"}),
    )

    object_type = forms.ChoiceField(
        label="対象種別",
        required=True,
        choices=OBJECT_TYPE_CHOICES,
    )

    object_id = forms.CharField(
        label="対象ID",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：TASK-000001 / DOC-000001"}),
    )

    approval_step = forms.CharField(
        label="承認ステップ",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "例：一次承認 / 最終承認 / 法務確認"}),
    )

    requester_user_id = forms.CharField(
        label="依頼者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    approver_user_id = forms.CharField(
        label="承認者ID",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u002"}),
    )

    comment = forms.CharField(
        label="コメント",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "承認依頼の補足、確認してほしい点などを入力してください。",
            }
        ),
    )


class ApprovalFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "承認ステップ・コメントで検索"}),
    )

    deal_id = forms.CharField(
        label="案件ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：DEAL-000001"}),
    )

    object_type = forms.ChoiceField(
        label="対象種別",
        required=False,
        choices=[("", "すべて")] + OBJECT_TYPE_CHOICES,
    )

    object_id = forms.CharField(
        label="対象ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：TASK-000001"}),
    )

    approval_status = forms.ChoiceField(
        label="承認ステータス",
        required=False,
        choices=[("", "すべて")] + APPROVAL_STATUS_CHOICES,
    )

    requester_user_id = forms.CharField(
        label="依頼者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )

    approver_user_id = forms.CharField(
        label="承認者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u002"}),
    )