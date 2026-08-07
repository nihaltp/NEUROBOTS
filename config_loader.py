import yaml
import os

def load_config(config_path="config.yaml"):
    """
    Loads configuration from a YAML file.
    Default path is 'config.yaml' in the project root.
    """
    if not os.path.exists(config_path):
        # Fallback to absolute path if running from a different directory
        root_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(root_dir, "config.yaml")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    print("Configuration loaded successfully:")
    print(config)
