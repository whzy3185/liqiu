import unittest

from research_core.experiment import ConfigurationError, _validate_config


def base_config():
    return {
        "algorithm": "x", "dataset": "y", "pool": "exploration",
        "seed": 1, "runner": "experiments.runners.smoke:run",
    }


class ProtocolTests(unittest.TestCase):
    def test_initial_seed_is_valid(self):
        _validate_config(base_config())


    def test_confirmation_rejects_search(self):
        config = base_config()
        config.update({
            "pool": "confirmation", "confirmation_rationale": "frozen candidate",
            "search": {"enabled": True},
        })
        with self.assertRaises(ConfigurationError):
            _validate_config(config)


if __name__ == "__main__":
    unittest.main()
