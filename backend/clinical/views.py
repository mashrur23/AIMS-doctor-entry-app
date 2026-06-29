import json
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from openpyxl import Workbook

from .models import (
    Advice,
    AllergicHistory,
    ChiefComplaint,
    ClinicalExam,
    Consultation,
    Diagnosis,
    FamilyHistory,
    GynaeObsHistory,
    HealthScreening,
    Investigation,
    Medication,
    Patient,
    PersonalHistory,
)


PATIENT_SECTION_FIELDS = {
    "family_history": (FamilyHistory, "patient", ["father", "mother", "siblings", "others"]),
    "allergic_history": (
        AllergicHistory,
        "patient",
        ["food", "medicine", "pollen", "dust", "mites", "others"],
    ),
    "personal_history": (
        PersonalHistory,
        "patient",
        ["smoking", "alcohol", "activity_level", "food_preferences", "others"],
    ),
    "gynae_obs_history": (
        GynaeObsHistory,
        "patient",
        [
            "lmp",
            "edd",
            "para",
            "gravida",
            "alc",
            "delivery_history",
            "contraceptives_history",
            "pv_examination",
        ],
    ),
}

CONSULTATION_ONE_TO_ONE_FIELDS = {
    "health_screening": (
        HealthScreening,
        "consultation",
        ["blood_pressure", "pulse_rate", "temperature", "respiratory_rate", "weight", "height", "bmi"],
    ),
    "clinical_exam": (
        ClinicalExam,
        "consultation",
        ["anaemia", "jaundice", "cyanosis", "edema", "systemic_examination_notes"],
    ),
    "advice": (Advice, "consultation", ["advice_notes"]),
}

CONSULTATION_MANY_FIELDS = {
    "chief_complaints": (ChiefComplaint, ["complaint", "duration"]),
    "investigations": (Investigation, ["investigation_name"]),
    "diagnoses": (Diagnosis, ["diagnosis_name", "diagnosis_note"]),
    "medications": (Medication, ["medicine_name", "dosage", "frequency", "duration", "instruction"]),
}


def _text(value):
    return "" if value is None else str(value).strip()


def _date_value(value):
    if not value:
        return None
    if hasattr(value, "isoformat"):
        return value
    return parse_date(str(value))


def _datetime_value(value):
    if not value:
        return timezone.now()
    if hasattr(value, "isoformat"):
        return value
    parsed = parse_datetime(str(value))
    if parsed is None:
        parsed_date = parse_date(str(value))
        if parsed_date:
            parsed = timezone.datetime.combine(parsed_date, timezone.datetime.min.time())
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed)
    return parsed


def _clean_payload(payload, fields):
    cleaned = {}
    for field in fields:
        if field in {"lmp", "edd"}:
            cleaned[field] = _date_value(payload.get(field))
        else:
            cleaned[field] = _text(payload.get(field))
    return cleaned


def _has_value(values):
    return any(value not in ("", None) for value in values.values())


def _model_payload(instance, fields):
    data = {}
    for field in fields:
        value = getattr(instance, field)
        data[field] = value.isoformat() if hasattr(value, "isoformat") else value
    return data


def _optional_related(instance, name):
    try:
        return getattr(instance, name)
    except ObjectDoesNotExist:
        return None


def _serialize_consultation(consultation):
    patient = consultation.patient
    payload = {
        "id": str(consultation.id),
        "file_name": consultation.file_name,
        "patient_identifier": patient.patient_identifier,
        "transcript": consultation.transcript,
        "consultation_date": consultation.consultation_date.isoformat(),
        "patient_sections": {},
        "consultation_sections": {},
    }

    for section, (_, _, fields) in PATIENT_SECTION_FIELDS.items():
        related = _optional_related(patient, section)
        payload["patient_sections"][section] = _model_payload(related, fields) if related else {}

    for section, (_, _, fields) in CONSULTATION_ONE_TO_ONE_FIELDS.items():
        related = _optional_related(consultation, section)
        payload["consultation_sections"][section] = _model_payload(related, fields) if related else {}

    for section, (_, fields) in CONSULTATION_MANY_FIELDS.items():
        related_manager = getattr(consultation, section)
        payload["consultation_sections"][section] = [
            _model_payload(item, fields) for item in related_manager.all()
        ]

    return payload


def _upsert_one_to_one(model, link_name, parent, payload, fields):
    values = _clean_payload(payload or {}, fields)
    if not _has_value(values):
        return
    model.objects.update_or_create(**{link_name: parent}, defaults=values)


def _replace_many(model, consultation, items, fields):
    model.objects.filter(consultation=consultation).delete()
    rows = []
    for item in items or []:
        values = _clean_payload(item, fields)
        if _has_value(values):
            rows.append(model(consultation=consultation, **values))
    if rows:
        model.objects.bulk_create(rows)


def _save_consultation(payload):
    file_name = _text(payload.get("file_name"))
    if not file_name:
        raise ValueError("file_name is required.")

    patient_identifier = _text(payload.get("patient_identifier")) or file_name
    patient, _ = Patient.objects.get_or_create(patient_identifier=patient_identifier)

    consultation, _ = Consultation.objects.update_or_create(
        file_name=file_name,
        defaults={
            "patient": patient,
            "transcript": _text(payload.get("transcript")),
            "consultation_date": _datetime_value(payload.get("consultation_date")),
        },
    )

    patient_sections = payload.get("patient_sections") or {}
    for section, (model, link_name, fields) in PATIENT_SECTION_FIELDS.items():
        _upsert_one_to_one(model, link_name, patient, patient_sections.get(section), fields)

    consultation_sections = payload.get("consultation_sections") or {}
    for section, (model, link_name, fields) in CONSULTATION_ONE_TO_ONE_FIELDS.items():
        _upsert_one_to_one(model, link_name, consultation, consultation_sections.get(section), fields)

    for section, (model, fields) in CONSULTATION_MANY_FIELDS.items():
        _replace_many(model, consultation, consultation_sections.get(section), fields)

    return consultation


@require_GET
def health_check(_request):
    return JsonResponse({"status": "ok"})


@require_GET
def form_schema(_request):
    return JsonResponse(
        {
            "root_fields": ["file_name", "patient_identifier", "consultation_date", "transcript"],
            "patient_sections": {key: fields for key, (_, _, fields) in PATIENT_SECTION_FIELDS.items()},
            "consultation_sections": {
                **{key: fields for key, (_, _, fields) in CONSULTATION_ONE_TO_ONE_FIELDS.items()},
                **{key: fields for key, (_, fields) in CONSULTATION_MANY_FIELDS.items()},
            },
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def consultations(request):
    if request.method == "GET":
        rows = [
            {
                "id": str(item.id),
                "file_name": item.file_name,
                "patient_identifier": item.patient.patient_identifier,
                "consultation_date": item.consultation_date.isoformat(),
            }
            for item in Consultation.objects.select_related("patient")[:50]
        ]
        return JsonResponse({"results": rows})

    try:
        payload = json.loads(request.body or "{}")
        with transaction.atomic():
            consultation = _save_consultation(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"result": _serialize_consultation(consultation)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def consultation_detail(request, consultation_id):
    try:
        consultation = Consultation.objects.select_related("patient").get(id=consultation_id)
    except Consultation.DoesNotExist:
        return JsonResponse({"error": "Consultation not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"result": _serialize_consultation(consultation)})

    try:
        payload = json.loads(request.body or "{}")
        payload["file_name"] = payload.get("file_name") or consultation.file_name
        with transaction.atomic():
            consultation = _save_consultation(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"result": _serialize_consultation(consultation)})


@require_GET
def consultation_json(_request, consultation_id):
    try:
        consultation = Consultation.objects.select_related("patient").get(id=consultation_id)
    except Consultation.DoesNotExist:
        return JsonResponse({"error": "Consultation not found."}, status=404)

    return JsonResponse(_serialize_consultation(consultation))


def _excel_workbook(consultations):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "consultations_json"
    columns = [
        "id",
        "file_name",
        "patient_identifier",
        "consultation_date",
        "transcript",
        "family_history",
        "allergic_history",
        "personal_history",
        "gynae_obs_history",
        "health_screening",
        "clinical_exam",
        "advice",
        "chief_complaints",
        "investigations",
        "diagnoses",
        "medications",
        "full_json",
    ]
    sheet.append(columns)

    for consultation in consultations:
        payload = _serialize_consultation(consultation)
        patient_sections = payload["patient_sections"]
        consultation_sections = payload["consultation_sections"]
        sheet.append(
            [
                payload["id"],
                payload["file_name"],
                payload["patient_identifier"],
                payload["consultation_date"],
                payload["transcript"],
                json.dumps(patient_sections.get("family_history", {}), ensure_ascii=False),
                json.dumps(patient_sections.get("allergic_history", {}), ensure_ascii=False),
                json.dumps(patient_sections.get("personal_history", {}), ensure_ascii=False),
                json.dumps(patient_sections.get("gynae_obs_history", {}), ensure_ascii=False),
                json.dumps(consultation_sections.get("health_screening", {}), ensure_ascii=False),
                json.dumps(consultation_sections.get("clinical_exam", {}), ensure_ascii=False),
                json.dumps(consultation_sections.get("advice", {}), ensure_ascii=False),
                json.dumps(consultation_sections.get("chief_complaints", []), ensure_ascii=False),
                json.dumps(consultation_sections.get("investigations", []), ensure_ascii=False),
                json.dumps(consultation_sections.get("diagnoses", []), ensure_ascii=False),
                json.dumps(consultation_sections.get("medications", []), ensure_ascii=False),
                json.dumps(payload, ensure_ascii=False),
            ]
        )

    return workbook


def _excel_response(consultations, filename):
    workbook = _excel_workbook(consultations)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


@require_GET
def consultation_excel(_request, consultation_id):
    consultations_qs = Consultation.objects.select_related("patient").filter(id=consultation_id)
    if not consultations_qs.exists():
        return JsonResponse({"error": "Consultation not found."}, status=404)
    return _excel_response(consultations_qs, "consultation_export.xlsx")


@require_GET
def all_consultations_excel(_request):
    consultations_qs = Consultation.objects.select_related("patient").all()
    return _excel_response(consultations_qs, "aims_consultations_export.xlsx")


@require_GET
def save_all_consultations_excel_to_downloads(_request):
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    filename = "aims_consultations_export.xlsx"
    output_path = downloads_dir / filename

    consultations_qs = Consultation.objects.select_related("patient").all()
    workbook = _excel_workbook(consultations_qs)
    workbook.save(output_path)

    return JsonResponse(
        {
            "filename": filename,
            "path": str(output_path),
            "rows": consultations_qs.count(),
        }
    )
