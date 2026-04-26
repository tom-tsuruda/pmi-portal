from datetime import timedelta

from django.utils import timezone

from apps.core.utils.datetime_utils import now_str
from apps.core.utils.ids import next_id
from apps.deals.services import DealService
from apps.questionnaire.repositories import (
    ExcelChecklistTemplateRepository,
    ExcelQuestionRepository,
    ExcelQuestionnaireAnswerRepository,
)
from apps.tasks.dtos import TaskCreateDTO
from apps.tasks.services import TaskService


DEFAULT_QUESTIONS = [
    {
        "question_id": "Q001",
        "question_code": "TSA_EXISTS",
        "question_text": "TSA（移行サービス契約）はありますか？",
        "question_type": "YESNO",
        "default_value": "NO",
        "required_flag": 1,
        "display_order": 1,
        "help_text": "売主側から一定期間サービス提供を受ける場合は「はい」にします。",
        "beginner_guidance": "TSAがある場合、終了期限・責任分担・費用負担の管理が重要です。",
        "is_active": 1,
    },
    {
        "question_id": "Q002",
        "question_code": "PERSONAL_DATA_EXISTS",
        "question_text": "個人情報を扱いますか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 2,
        "help_text": "従業員情報、顧客情報、取引先担当者情報などを含みます。",
        "beginner_guidance": "個人情報がある場合、移管範囲・アクセス権限・保管場所の確認が必要です。",
        "is_active": 1,
    },
    {
        "question_id": "Q003",
        "question_code": "OVERSEAS_SCOPE",
        "question_text": "海外拠点・海外取引が関係しますか？",
        "question_type": "YESNO",
        "default_value": "NO",
        "required_flag": 1,
        "display_order": 3,
        "help_text": "海外子会社、海外顧客、海外サプライヤー、越境データ移転などが対象です。",
        "beginner_guidance": "海外が関係すると、法規制・税務・個人情報・契約確認が増えます。",
        "is_active": 1,
    },
    {
        "question_id": "Q004",
        "question_code": "REGULATED_INDUSTRY",
        "question_text": "規制業種に該当しますか？",
        "question_type": "YESNO",
        "default_value": "NO",
        "required_flag": 1,
        "display_order": 4,
        "help_text": "金融、医療、インフラ、化学、航空、防衛、個人情報を大量に扱う業種などです。",
        "beginner_guidance": "規制業種では、許認可・当局対応・監査証跡が重要になります。",
        "is_active": 1,
    },
    {
        "question_id": "Q005",
        "question_code": "EMPLOYEE_TRANSFER",
        "question_text": "従業員の移管・説明対応がありますか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 5,
        "help_text": "雇用条件、給与、福利厚生、説明会、FAQなどを含みます。",
        "beginner_guidance": "PMIでは従業員不安を抑える初期コミュニケーションが重要です。",
        "is_active": 1,
    },
    {
        "question_id": "Q006",
        "question_code": "IT_INTEGRATION",
        "question_text": "ITシステム統合・アカウント移行がありますか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 6,
        "help_text": "メール、ID、会計、人事、販売管理、ファイルサーバーなどです。",
        "beginner_guidance": "Day1でアクセスできないと業務停止につながるため、ITは早期確認が必要です。",
        "is_active": 1,
    },
    {
        "question_id": "Q007",
        "question_code": "BRAND_CHANGE",
        "question_text": "社名・ブランド・ロゴ変更がありますか？",
        "question_type": "YESNO",
        "default_value": "NO",
        "required_flag": 1,
        "display_order": 7,
        "help_text": "名刺、Webサイト、契約書、請求書、看板、顧客通知などに影響します。",
        "beginner_guidance": "ブランド変更は対外通知や資料差し替え漏れが起きやすい領域です。",
        "is_active": 1,
    },
    {
        "question_id": "Q008",
        "question_code": "CUSTOMER_NOTICE_REQUIRED",
        "question_text": "重要取引先への通知が必要ですか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 8,
        "help_text": "顧客、サプライヤー、金融機関、業務委託先などへの通知です。",
        "beginner_guidance": "通知漏れは信用低下につながるため、誰に何をいつ伝えるかを管理します。",
        "is_active": 1,
    },
    {
        "question_id": "Q009",
        "question_code": "PAYROLL_PAYMENT_CRITICAL",
        "question_text": "Day1で給与・支払・請求に影響がありますか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 9,
        "help_text": "給与支払、仕入支払、請求書発行、銀行口座、承認権限などです。",
        "beginner_guidance": "お金の流れが止まると業務影響が大きいため、Day1前に必ず確認します。",
        "is_active": 1,
    },
    {
        "question_id": "Q010",
        "question_code": "DAY100_PLAN_REQUIRED",
        "question_text": "100日計画を作成しますか？",
        "question_type": "YESNO",
        "default_value": "YES",
        "required_flag": 1,
        "display_order": 10,
        "help_text": "Day100までの統合方針、優先課題、KPI、体制をまとめる計画です。",
        "beginner_guidance": "Day1対応だけでなく、Day100までの計画があると統合が安定します。",
        "is_active": 1,
    },
]


DEFAULT_TEMPLATES = [
    {
        "template_code": "TPL-COMMON-001",
        "task_title": "PMIキックオフミーティングを実施する",
        "task_description": "案件関係者で目的、体制、進め方、主要論点を確認する。",
        "phase_id": "PRE_CLOSE",
        "workstream_id": "PMO",
        "default_priority": "HIGH",
        "default_due_offset_days": 3,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "",
        "trigger_answer_value": "",
        "why_this_task": "PMIでは関係者の認識を早期にそろえることが重要です。",
        "beginner_guidance": "まず誰が責任者で、何をいつまでに決めるかを明確にします。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-COMMON-002",
        "task_title": "Day1チェックリストを作成する",
        "task_description": "Day1に必要な業務継続、通知、権限、支払、問い合わせ対応を整理する。",
        "phase_id": "DAY1",
        "workstream_id": "PMO",
        "default_priority": "HIGH",
        "default_due_offset_days": 5,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "",
        "trigger_answer_value": "",
        "why_this_task": "Day1で業務を止めないための基本管理表です。",
        "beginner_guidance": "最初は完璧でなくても、漏れを見える化することが大切です。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-TSA-001",
        "task_title": "TSA一覧と終了期限を整理する",
        "task_description": "TSA対象サービス、提供者、終了期限、費用、代替手段を一覧化する。",
        "phase_id": "PRE_CLOSE",
        "workstream_id": "PMO",
        "default_priority": "HIGH",
        "default_due_offset_days": 7,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "TSA_EXISTS",
        "trigger_answer_value": "YES",
        "why_this_task": "TSA終了時に業務が止まらないようにするためです。",
        "beginner_guidance": "TSAは便利ですが、期限管理を忘れると大きなリスクになります。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-PRIVACY-001",
        "task_title": "個人情報の移管範囲とアクセス権限を確認する",
        "task_description": "従業員・顧客・取引先担当者情報の有無、保管場所、アクセス権限を整理する。",
        "phase_id": "DAY1",
        "workstream_id": "LEGAL",
        "default_priority": "HIGH",
        "default_due_offset_days": 7,
        "evidence_required_flag": 1,
        "regulation_flag": 1,
        "trigger_question_code": "PERSONAL_DATA_EXISTS",
        "trigger_answer_value": "YES",
        "why_this_task": "個人情報は漏えいや目的外利用のリスクがあるためです。",
        "beginner_guidance": "誰がどの情報にアクセスできるかを確認することから始めます。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-OVERSEAS-001",
        "task_title": "海外拠点・海外取引に関する規制論点を確認する",
        "task_description": "海外子会社、海外顧客、越境データ移転、契約、税務論点を確認する。",
        "phase_id": "PRE_CLOSE",
        "workstream_id": "LEGAL",
        "default_priority": "MEDIUM",
        "default_due_offset_days": 10,
        "evidence_required_flag": 1,
        "regulation_flag": 1,
        "trigger_question_code": "OVERSEAS_SCOPE",
        "trigger_answer_value": "YES",
        "why_this_task": "海外が関係すると法務・税務・個人情報の確認範囲が広がります。",
        "beginner_guidance": "対象国と対象業務をまず一覧化します。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-REG-001",
        "task_title": "規制業種に関する許認可・届出要否を確認する",
        "task_description": "当局対応、許認可、届出、監査証跡、契約上の制約を確認する。",
        "phase_id": "PRE_CLOSE",
        "workstream_id": "LEGAL",
        "default_priority": "HIGH",
        "default_due_offset_days": 7,
        "evidence_required_flag": 1,
        "regulation_flag": 1,
        "trigger_question_code": "REGULATED_INDUSTRY",
        "trigger_answer_value": "YES",
        "why_this_task": "規制対応を漏らすとPMI全体の遅延や法令違反につながるためです。",
        "beginner_guidance": "業種特有の届出・許認可がないかを確認します。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-HR-001",
        "task_title": "従業員向け初回説明・FAQを準備する",
        "task_description": "雇用条件、給与、福利厚生、問い合わせ先、今後の流れを整理する。",
        "phase_id": "DAY1",
        "workstream_id": "HR",
        "default_priority": "HIGH",
        "default_due_offset_days": 5,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "EMPLOYEE_TRANSFER",
        "trigger_answer_value": "YES",
        "why_this_task": "従業員の不安を減らし、離職や混乱を防ぐためです。",
        "beginner_guidance": "まず従業員が不安に思う質問をFAQにします。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-IT-001",
        "task_title": "Day1に必要なITアカウント・権限を確認する",
        "task_description": "メール、チャット、ファイル、基幹システム、承認権限の利用可否を確認する。",
        "phase_id": "DAY1",
        "workstream_id": "IT",
        "default_priority": "HIGH",
        "default_due_offset_days": 5,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "IT_INTEGRATION",
        "trigger_answer_value": "YES",
        "why_this_task": "Day1にシステムが使えないと業務停止につながるためです。",
        "beginner_guidance": "誰が何のシステムを使う必要があるかを一覧化します。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-BRAND-001",
        "task_title": "ブランド・社名変更に伴う対外資料を確認する",
        "task_description": "Web、名刺、契約書、請求書、通知文、看板、資料テンプレートの変更要否を確認する。",
        "phase_id": "DAY30",
        "workstream_id": "COMMS",
        "default_priority": "MEDIUM",
        "default_due_offset_days": 14,
        "evidence_required_flag": 0,
        "regulation_flag": 0,
        "trigger_question_code": "BRAND_CHANGE",
        "trigger_answer_value": "YES",
        "why_this_task": "対外表示の不一致は顧客混乱や信用低下につながるためです。",
        "beginner_guidance": "まず外部に見えるものを洗い出します。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-CUSTOMER-001",
        "task_title": "重要取引先への通知対象と通知文案を作成する",
        "task_description": "顧客・サプライヤー・金融機関などへの通知対象、文案、送付日を整理する。",
        "phase_id": "DAY1",
        "workstream_id": "COMMS",
        "default_priority": "HIGH",
        "default_due_offset_days": 5,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "CUSTOMER_NOTICE_REQUIRED",
        "trigger_answer_value": "YES",
        "why_this_task": "重要取引先への説明不足は信頼低下につながるためです。",
        "beginner_guidance": "誰に、何を、いつ伝えるかを決めます。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-FIN-001",
        "task_title": "Day1の支払・給与・請求への影響を確認する",
        "task_description": "給与支払、仕入支払、請求、銀行口座、承認権限、締日を確認する。",
        "phase_id": "DAY1",
        "workstream_id": "FINANCE",
        "default_priority": "HIGH",
        "default_due_offset_days": 5,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "PAYROLL_PAYMENT_CRITICAL",
        "trigger_answer_value": "YES",
        "why_this_task": "給与・支払・請求の停止は影響が大きいためです。",
        "beginner_guidance": "お金の流れが止まらないかを最優先で確認します。",
        "is_active": 1,
    },
    {
        "template_code": "TPL-DAY100-001",
        "task_title": "Day100計画を作成する",
        "task_description": "Day100までの統合テーマ、担当、期限、KPI、主要リスクを整理する。",
        "phase_id": "DAY100",
        "workstream_id": "PMO",
        "default_priority": "HIGH",
        "default_due_offset_days": 14,
        "evidence_required_flag": 1,
        "regulation_flag": 0,
        "trigger_question_code": "DAY100_PLAN_REQUIRED",
        "trigger_answer_value": "YES",
        "why_this_task": "Day1後の統合を計画的に進めるためです。",
        "beginner_guidance": "短期の火消しだけでなく、100日後の姿を決めます。",
        "is_active": 1,
    },
]


class QuestionnaireService:
    def __init__(
        self,
        question_repo: ExcelQuestionRepository | None = None,
        answer_repo: ExcelQuestionnaireAnswerRepository | None = None,
        template_repo: ExcelChecklistTemplateRepository | None = None,
        task_service: TaskService | None = None,
        deal_service: DealService | None = None,
    ):
        self.question_repo = question_repo or ExcelQuestionRepository()
        self.answer_repo = answer_repo or ExcelQuestionnaireAnswerRepository()
        self.template_repo = template_repo or ExcelChecklistTemplateRepository()
        self.task_service = task_service or TaskService()
        self.deal_service = deal_service or DealService()

    def list_questions(self) -> list[dict]:
        """
        質問票の質問を取得する。

        開発初期はExcel側に古い質問が5問だけ入っている場合があるため、
        10問未満の場合は標準質問10問を使う。
        将来、Excel側で10問以上きちんと整備したらExcelを優先する。
        """
        questions = self.question_repo.find_active()

        if len(questions) >= 10:
            return questions

        return DEFAULT_QUESTIONS

    def save_answers(self, deal_id: str, questions: list[dict], cleaned_data: dict) -> int:
        count = 0
        current_time = now_str()
        last_id = self.answer_repo.get_last_answer_id()

        for question in questions:
            question_id = question.get("question_id")
            question_code = question.get("question_code")
            field_name = f"question_{question_id}"
            answer_value = cleaned_data.get(field_name, "")

            last_id = next_id("ANS", last_id)

            record = {
                "answer_id": last_id,
                "deal_id": deal_id,
                "question_id": question_id,
                "question_code": question_code,
                "answer_value": answer_value,
                "created_at": current_time,
                "updated_at": current_time,
            }

            self.answer_repo.append_row(record)
            count += 1

        return count

    def generate_tasks_from_templates(
        self,
        deal_id: str,
        questions: list[dict] | None = None,
        cleaned_data: dict | None = None,
    ) -> dict:
        deal = self.deal_service.get_deal(deal_id)

        templates = self.template_repo.find_active()

        # 開発初期はExcel側の checklist_templates が少数だけ入っている場合がある。
        # 標準テンプレート数に満たない場合は、コード側の標準テンプレートを使う。
        if len(templates) < len(DEFAULT_TEMPLATES):
            templates = DEFAULT_TEMPLATES

        answer_map = self._build_answer_map(
            questions=questions or [],
            cleaned_data=cleaned_data or {},
        )

        created_count = 0
        skipped_count = 0
        condition_skipped_count = 0

        for template in templates:
            task_title = template.get("task_title")
            template_code = template.get("template_code")

            if not task_title:
                continue

            if not self._template_matches_answers(template, answer_map):
                condition_skipped_count += 1
                continue

            due_date = self._build_due_date(template.get("default_due_offset_days"))

            dto = TaskCreateDTO(
                deal_id=deal_id,
                phase_id=template.get("phase_id") or "DAY1",
                workstream_id=template.get("workstream_id") or "PMO",
                title=task_title,
                description=template.get("task_description") or "",
                priority=template.get("default_priority") or "MEDIUM",
                owner_user_id=deal.get("owner_user_id") or "u001",
                due_date=due_date,
                template_source_id=template_code or "",
                evidence_required_flag=self._to_int_flag(
                    template.get("evidence_required_flag")
                ),
                regulation_flag=self._to_int_flag(
                    template.get("regulation_flag")
                ),
                why_this_task=template.get("why_this_task") or "",
                beginner_guidance=template.get("beginner_guidance") or "",
            )

            created, _task_id = self.task_service.create_task_if_not_exists_by_template(dto)

            if created:
                created_count += 1
            else:
                skipped_count += 1

        return {
            "created_count": created_count,
            "skipped_count": skipped_count,
            "condition_skipped_count": condition_skipped_count,
        }

    def _build_answer_map(self, questions: list[dict], cleaned_data: dict) -> dict:
        answer_map = {}

        for question in questions:
            question_id = question.get("question_id")
            question_code = question.get("question_code")

            if not question_code:
                continue

            field_name = f"question_{question_id}"
            value = cleaned_data.get(field_name, "")

            answer_map[str(question_code).strip()] = self._normalize_answer(value)

        return answer_map

    def _template_matches_answers(self, template: dict, answer_map: dict) -> bool:
        trigger_question_code = str(
            template.get("trigger_question_code") or ""
        ).strip()

        trigger_answer_value = str(
            template.get("trigger_answer_value") or ""
        ).strip()

        if not trigger_question_code:
            return True

        expected_answer = self._normalize_answer(trigger_answer_value or "YES")
        actual_answer = answer_map.get(trigger_question_code)

        if actual_answer is None:
            return False

        return actual_answer == expected_answer

    def _normalize_answer(self, value) -> str:
        text = str(value or "").strip()
        upper_text = text.upper()

        if upper_text in ["YES", "Y", "TRUE", "1", "はい", "有", "あり"]:
            return "YES"

        if upper_text in ["NO", "N", "FALSE", "0", "いいえ", "無", "なし"]:
            return "NO"

        return text

    def _build_due_date(self, offset_days) -> str:
        try:
            days = int(offset_days or 0)
        except (TypeError, ValueError):
            days = 0

        target_date = timezone.localdate() + timedelta(days=days)
        return target_date.strftime("%Y-%m-%d")

    def _to_int_flag(self, value) -> int:
        if str(value).strip() in [
            "1",
            "TRUE",
            "True",
            "true",
            "YES",
            "Yes",
            "yes",
            "はい",
            "あり",
        ]:
            return 1

        return 0