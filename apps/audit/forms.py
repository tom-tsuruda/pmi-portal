from django import forms


OBJECT_TYPE_CHOICES = [
    ("DEAL", "DEAL：案件"),
    ("TASK", "TASK：タスク"),
    ("RAID", "RAID：RAID"),
    ("DOCUMENT", "DOCUMENT：資料"),
    ("DECISION", "DECISION：意思決定"),
    ("APPROVAL", "APPROVAL：承認"),
    ("QUESTIONNAIRE", "QUESTIONNAIRE：質問票"),
]


ACTION_TYPE_CHOICES = [
    ("CREATE", "CREATE：作成"),
    ("UPDATE", "UPDATE：更新"),
    ("STATUS_UPDATE", "STATUS_UPDATE：ステータス更新"),
    ("DELETE", "DELETE：削除"),
    ("SOFT_DELETE", "SOFT_DELETE：削除済み化"),
    ("UPLOAD", "UPLOAD：アップロード"),
    ("GENERATE", "GENERATE：自動生成"),
    ("APPROVE", "APPROVE：承認"),
    ("REJECT", "REJECT：却下"),
    ("RETURN", "RETURN：差し戻し"),
    ("CANCEL", "CANCEL：取消"),
]


class AuditLogFilterForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "変更前・変更後・メモで検索"}
        ),
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

    action_type = forms.ChoiceField(
        label="操作種別",
        required=False,
        choices=[("", "すべて")] + ACTION_TYPE_CHOICES,
    )

    acted_by_user_id = forms.CharField(
        label="操作者ID",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例：u001"}),
    )