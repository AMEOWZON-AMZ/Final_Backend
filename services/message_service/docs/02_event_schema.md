# 02_event_schema

SQS job schema (minimal):
{
  "event_type": "MESSAGE|HEART",
  "from_user_id": "string",
  "to_user_id": "string",
  "ref_id": "string",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ"
}
