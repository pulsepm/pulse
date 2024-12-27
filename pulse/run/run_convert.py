import json
import tomli


def config_convert(toml_file_path: str, json_file_path: str) -> dict:
    """
    Converts configuration file from .json (pawn.json) to .toml (pulse.toml).

    Args:
        toml_file_path (str): Path to pulse.toml.
        json_file_path (str): Path to pawn.json.
    """
    with open(toml_file_path, "rb") as file:
        config = tomli.load(file)

    config_profile = config.get("runtime", {})

    json_config = {
        "announce": config_profile.get("announce", True),
        "artwork": {
            "cdn": config_profile.get("artwork", {}).get("cdn", ""),
            "enable": config_profile.get("artwork", {}).get("enable", True),
            "models_path": config_profile.get("artwork", {}).get(
                "models_path", "models"
            ),
            "port": config_profile.get("artwork", {}).get("port", 7777),
            "web_server_bind": config_profile.get("artwork", {}).get(
                "web_server_bind", ""
            ),
        },
        "banners": {
            "dark": config_profile.get("banners", {}).get("dark", ""),
            "light": config_profile.get("banners", {}).get("light", ""),
        },
        "chat_input_filter": config_profile.get("chat_input_filter", True),
        "discord": {"invite": config_profile.get("discord", {}).get("invite", "")},
        "enable_query": config_profile.get("enable_query", True),
        "exclude": config_profile.get("exclude", ["Fixes"]),
        "game": {
            "allow_interior_weapons": config_profile.get("game", {}).get(
                "allow_interior_weapons", True
            ),
            "chat_radius": config_profile.get("game", {}).get("chat_radius", 200.0),
            "death_drop_amount": config_profile.get("game", {}).get(
                "death_drop_amount", 0
            ),
            "gravity": config_profile.get("game", {}).get("gravity", 0.008),
            "group_player_objects": config_profile.get("game", {}).get(
                "group_player_objects", False
            ),
            "lag_compensation_mode": config_profile.get("game", {}).get(
                "lag_compensation_mode", 1
            ),
            "map": config_profile.get("game", {}).get("map", ""),
            "mode": config_profile.get("game", {}).get("mode", ""),
            "nametag_draw_radius": config_profile.get("game", {}).get(
                "nametag_draw_radius", 70.0
            ),
            "player_marker_draw_radius": config_profile.get("game", {}).get(
                "player_marker_draw_radius", 250.0
            ),
            "player_marker_mode": config_profile.get("game", {}).get(
                "player_marker_mode", 1
            ),
            "time": config_profile.get("game", {}).get("time", 12),
            "use_all_animations": config_profile.get("game", {}).get(
                "use_all_animations", True
            ),
            "use_chat_radius": config_profile.get("game", {}).get(
                "use_chat_radius", False
            ),
            "use_entry_exit_markers": config_profile.get("game", {}).get(
                "use_entry_exit_markers", True
            ),
            "use_instagib": config_profile.get("game", {}).get("use_instagib", False),
            "use_manual_engine_and_lights": config_profile.get("game", {}).get(
                "use_manual_engine_and_lights", False
            ),
            "use_nametag_los": config_profile.get("game", {}).get(
                "use_nametag_los", True
            ),
            "use_nametags": config_profile.get("game", {}).get("use_nametags", True),
            "use_player_marker_draw_radius": config_profile.get("game", {}).get(
                "use_player_marker_draw_radius", False
            ),
            "use_player_ped_anims": config_profile.get("game", {}).get(
                "use_player_ped_anims", False
            ),
            "use_stunt_bonuses": config_profile.get("game", {}).get(
                "use_stunt_bonuses", True
            ),
            "use_vehicle_friendly_fire": config_profile.get("game", {}).get(
                "use_vehicle_friendly_fire", False
            ),
            "use_zone_names": config_profile.get("game", {}).get(
                "use_zone_names", False
            ),
            "validate_animations": config_profile.get("game", {}).get(
                "validate_animations", True
            ),
            "vehicle_respawn_time": config_profile.get("game", {}).get(
                "vehicle_respawn_time", 10000
            ),
            "weather": config_profile.get("game", {}).get("weather", 10),
        },
        "language": config_profile.get("language", ""),
        "logging": {
            "enable": config_profile.get("logging", {}).get("enable", True),
            "file": config_profile.get("logging", {}).get("file", "log.txt"),
            "log_chat": config_profile.get("logging", {}).get("log_chat", True),
            "log_connection_messages": config_profile.get("logging", {}).get(
                "log_connection_messages", True
            ),
            "log_cookies": config_profile.get("logging", {}).get("log_cookies", False),
            "log_deaths": config_profile.get("logging", {}).get("log_deaths", True),
            "log_queries": config_profile.get("logging", {}).get("log_queries", False),
            "log_sqlite": config_profile.get("logging", {}).get("log_sqlite", False),
            "log_sqlite_queries": config_profile.get("logging", {}).get(
                "log_sqlite_queries", False
            ),
            "timestamp_format": config_profile.get("logging", {}).get(
                "timestamp_format", "[%Y-%m-%dT%H:%M:%S%z]"
            ),
            "use_prefix": config_profile.get("logging", {}).get("use_prefix", True),
            "use_timestamp": config_profile.get("logging", {}).get(
                "use_timestamp", True
            ),
        },
        "max_bots": config_profile.get("max_bots", 0),
        "max_players": config_profile.get("max_players", 50),
        "name": config_profile.get("name", "open.mp server"),
        "network": {
            "acks_limit": config_profile.get("network", {}).get("acks_limit", 3000),
            "aiming_sync_rate": config_profile.get("network", {}).get(
                "aiming_sync_rate", 30
            ),
            "allow_037_clients": config_profile.get("network", {}).get(
                "allow_037_clients", True
            ),
            "bind": config_profile.get("network", {}).get("bind", ""),
            "cookie_reseed_time": config_profile.get("network", {}).get(
                "cookie_reseed_time", 300000
            ),
            "grace_period": config_profile.get("network", {}).get("grace_period", 5000),
            "http_threads": config_profile.get("network", {}).get("http_threads", 50),
            "in_vehicle_sync_rate": config_profile.get("network", {}).get(
                "in_vehicle_sync_rate", 30
            ),
            "limits_ban_time": config_profile.get("network", {}).get(
                "limits_ban_time", 60000
            ),
            "message_hole_limit": config_profile.get("network", {}).get(
                "message_hole_limit", 3000
            ),
            "messages_limit": config_profile.get("network", {}).get(
                "messages_limit", 500
            ),
            "minimum_connection_time": config_profile.get("network", {}).get(
                "minimum_connection_time", 0
            ),
            "mtu": config_profile.get("network", {}).get("mtu", 576),
            "multiplier": config_profile.get("network", {}).get("multiplier", 10),
            "on_foot_sync_rate": config_profile.get("network", {}).get(
                "on_foot_sync_rate", 30
            ),
            "player_marker_sync_rate": config_profile.get("network", {}).get(
                "player_marker_sync_rate", 2500
            ),
            "player_timeout": config_profile.get("network", {}).get(
                "player_timeout", 10000
            ),
            "port": config_profile.get("network", {}).get("port", 7777),
            "public_addr": config_profile.get("network", {}).get("public_addr", ""),
            "stream_radius": config_profile.get("network", {}).get(
                "stream_radius", 200.0
            ),
            "stream_rate": config_profile.get("network", {}).get("stream_rate", 1000),
            "time_sync_rate": config_profile.get("network", {}).get(
                "time_sync_rate", 30000
            ),
            "use_lan_mode": config_profile.get("network", {}).get(
                "use_lan_mode", False
            ),
        },
        "password": config_profile.get("password", ""),
        "pawn": {
            "side_scripts": config_profile.get("pawn", {}).get("side_scripts", []),
        },
        "rcon": {
            "allow_teleport": config_profile.get("allow_teleport", False),
            "enable": config_profile.get("enable", False),
            "password": config_profile.get("password", "change1me"),
        },
        "sleep": config_profile.get("sleep", 5.0),
        "use_dyn_ticks": config_profile.get("use_dyn_ticks", True),
        "website": config_profile.get("website", "open.mp"),
    }

    with open(json_file_path, "w") as json_file:
        json.dump(json_config, json_file, indent=4)

    return json_config
