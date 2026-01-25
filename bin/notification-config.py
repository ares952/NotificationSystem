import yaml
import os

def merge_dicts(default, override):
    """Recursively merge two dictionaries."""
    result = default.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def read_config(path, defaults=None):
    """
    Read YAML configuration and merge it with defaults.
    
    :param path: Path to YAML file
    :param defaults: Optional dict with default configuration
    :return: Merged configuration dict
    """
    if defaults is None:
        defaults = {}

    try:
        with open(path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file) or {}
            merged = merge_dicts(defaults, config)
            print(f"'{path}' configuration was loaded.")
            return merged
    except FileNotFoundError:
        print(f"Warning: File '{path}' not found. Using defaults.")
        return defaults
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{path}': {e}")
        return defaults

def load_config():
    """
    Load configuration from various sources.

    :return: Merged configuration dict
    """
    config = read_config("/etc/NotificationSystem.yaml")
    config = read_config("/usr/local/etc/NotificationSystem.yaml", config)
    config = read_config("/opt/etc/NotificationSystem.yaml", config)
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    config = read_config(f"{current_dir}/../etc/NotificationSystem.yaml", config)
    config = read_config(f"{current_dir}/NotificationSystem.yaml", config)
    return config

if __name__ == "__main__":
    config = load_config()
    config = read_config("../etc/NotificationSystem.yaml", config)
    if (config is not None) and (len(config) >= 0):
        print("Configuration loaded successfully:")
        print(yaml.dump(config, sort_keys=False, allow_unicode=True, indent=4))
    else:
        print("Failed to load configuration.")
