from django.contrib import messages
from django.shortcuts import redirect, render

from apps.core.exceptions import RepositoryError
from apps.questionnaire.forms import QuestionnaireAnswerForm
from apps.questionnaire.services import QuestionnaireService


questionnaire_service = QuestionnaireService()


def questionnaire_start(request, deal_id: str):
    try:
        questions = questionnaire_service.list_questions()
    except RepositoryError as e:
        messages.error(request, str(e))
        return redirect("deals:detail", deal_id=deal_id)

    if request.method == "POST":
        form = QuestionnaireAnswerForm(request.POST, questions=questions)

        if form.is_valid():
            try:
                answer_count = questionnaire_service.save_answers(
                    deal_id=deal_id,
                    questions=questions,
                    cleaned_data=form.cleaned_data,
                )

                result = questionnaire_service.generate_tasks_from_templates(
                    deal_id=deal_id,
                    questions=questions,
                    cleaned_data=form.cleaned_data,
                )

                messages.success(
                    request,
                    f"質問票を保存しました。回答 {answer_count} 件、"
                    f"新規タスク {result['created_count']} 件を生成、"
                    f"既存タスク {result['skipped_count']} 件をスキップ、"
                    f"条件不一致 {result['condition_skipped_count']} 件でした。",
                )
                return redirect("deals:detail", deal_id=deal_id)

            except RepositoryError as e:
                messages.error(request, str(e))
    else:
        form = QuestionnaireAnswerForm(questions=questions)

    return render(
        request,
        "questionnaire/questionnaire_form.html",
        {
            "form": form,
            "deal_id": deal_id,
            "questions": questions,
        },
    )