import unittest

from documentz_api import package_identity as api_identity
from documentz_application import package_identity as application_identity
from documentz_domain import package_identity as domain_identity
from documentz_infrastructure import package_identity as infrastructure_identity
from documentz_worker import package_identity as worker_identity


class PythonWorkspaceSmokeTests(unittest.TestCase):
    def test_python_workspace_smoke(self) -> None:
        identities = {
            api_identity(),
            application_identity(),
            domain_identity(),
            infrastructure_identity(),
            worker_identity(),
        }

        self.assertEqual(
            identities,
            {
                "documentz-api",
                "documentz-application",
                "documentz-domain",
                "documentz-infrastructure",
                "documentz-worker",
            },
        )


if __name__ == "__main__":
    unittest.main()
