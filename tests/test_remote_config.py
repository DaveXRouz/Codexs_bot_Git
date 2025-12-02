from codexs_bot.localization import Language, main_menu_labels
from codexs_bot.remote_config import RemoteConfig, default_menu_rows


def _sample_payload():
    return {
        "fetched_at": "2025-01-01T00:00:00Z",
        "menu_buttons": [
            {
                "button_key": "apply",
                "en_text": "Apply Now",
                "fa_text": "ارسال درخواست",
                "emoji": "💼",
                "action_type": "start_flow",
                "action_config": {"flow_key": "application_flow"},
                "order_index": 1,
            },
            {
                "button_key": "about",
                "en_text": "About Codexs",
                "fa_text": "درباره Codexs",
                "emoji": "🏢",
                "action_type": "send_content",
                "action_config": {"content_slug": "about"},
                "order_index": 2,
            },
        ],
        "flows": [
            {"flow_key": "application_flow", "steps": [], "enabled": True},
        ],
        "questions": [
            {"question_key": "full_name", "en_text": "Name?", "fa_text": "نام؟"},
        ],
        "content": {
            "about": {"en_body": "About EN", "fa_body": "About FA"},
            "welcome": {"en_body": "Welcome EN", "fa_body": "Welcome FA"},
        },
        "settings": {"bot_name": "Codexs"},
    }


def test_remote_config_builds_keyboard_and_matches_buttons():
    rc = RemoteConfig()
    rc.update_from_payload(_sample_payload())

    rows_en = rc.build_menu_rows(Language.EN)
    assert rows_en[0][0].startswith("💼 Apply"), rows_en

    rows_fa = rc.build_menu_rows(Language.FA)
    assert rows_fa[0][0].endswith("ارسال درخواست")

    button_en = rc.find_menu_button("💼 Apply Now", Language.EN)
    assert button_en and button_en["button_key"] == "apply"

    button_fa = rc.find_menu_button("🏢 درباره Codexs", Language.FA)
    assert button_fa and button_fa["action_type"] == "send_content"


def test_remote_config_content_and_question_helpers():
    rc = RemoteConfig()
    rc.update_from_payload(_sample_payload())

    about_en = rc.get_content_text("about", Language.EN)
    about_fa = rc.get_content_text("about", Language.FA)
    assert about_en == "About EN"
    assert about_fa == "About FA"

    prompt = rc.get_question_prompt("full_name", Language.FA)
    assert prompt == "نام؟"

    flow = rc.get_flow("application_flow")
    assert flow is not None and flow["flow_key"] == "application_flow"

    assert rc.get_setting("bot_name") == "Codexs"


def test_default_menu_rows_falls_back_to_static_labels():
    # When no remote menu is configured the default rows should match localization defaults
    fallback = main_menu_labels(Language.EN)
    assert default_menu_rows(Language.EN) == fallback

