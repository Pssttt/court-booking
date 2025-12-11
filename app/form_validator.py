"""
Google Form Schema Validator
Checks if the configured field IDs are present in the Google Form HTML.
"""

import httpx
import logging
import re
import json
from typing import Dict, Any, List
from config.settingstest import GOOGLE_FORM

logger = logging.getLogger(__name__)


async def check_form_schema() -> Dict[str, Any]:
    """
    Fetches the Google Form and checks if all configured field IDs are present
    by parsing the FB_PUBLIC_LOAD_DATA_ javascript object.
    """
    submit_url = GOOGLE_FORM["submit_url"]
    field_ids_to_check = GOOGLE_FORM["field_ids"]

    viewform_url = submit_url.replace("/formResponse", "/viewform")
    if not viewform_url.endswith("/viewform"):
        viewform_url = submit_url

    missing_fields: List[str] = []
    response_status = "success"
    message = "All configured Google Form fields found."
    found_ids = []

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(viewform_url, timeout=10)
            response.raise_for_status()
            html_content = response.text

        match = re.search(
            r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);\s*</script>",
            html_content,
            re.DOTALL,
        )

        if not match:
            match = re.search(
                r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);", html_content, re.DOTALL
            )

        if match:
            json_str = match.group(1)
            data = json.loads(json_str)

            if len(data) > 1 and len(data[1]) > 1:
                questions = data[1][1]

                for q in questions:
                    if len(q) > 4 and isinstance(q[4], list):
                        for entry in q[4]:
                            if len(entry) > 0:
                                found_ids.append(str(entry[0]))

            logger.info(f"Found {len(found_ids)} fields in form: {found_ids}")

            for field_name, full_entry_id in field_ids_to_check.items():
                entry_num = full_entry_id.replace("entry.", "")

                if entry_num not in found_ids:
                    missing_fields.append(f"{field_name} ({entry_num})")

        else:
            response_status = "failure"
            message = "Could not find form definition (FB_PUBLIC_LOAD_DATA_) in HTML. Form might be behind login."
            logger.warning(message)
            return {"status": response_status, "message": message, "missing_fields": []}

        if missing_fields:
            response_status = "failure"
            message = f"Missing fields: {', '.join(missing_fields)}"
            logger.error(message)

    except Exception as e:
        response_status = "failure"
        message = f"Error checking form schema: {str(e)}"
        logger.error(message)

    return {
        "status": response_status,
        "message": message,
        "missing_fields": missing_fields,
    }
