# Refactor Suggestions

The project is well-structured. The core patterns — typed settings dataclasses, per-environment config directories, golden file testing, and inventory-driven deployment — are all solid and work together cleanly. Here are the issues found, ranked by impact.

---

## 1. Empty environment subclasses should be eliminated (high impact)

### How it works today

`inventory.py` defines a base `Inventory` class and three environment subclasses that each set one class variable:

```python
class Inventory:
    SIMPLE_ASG_IDS: ClassVar[tuple[str, ...]] = ()
    TERMINATION_PROTECTION: ClassVar[bool] = False
    ...
    def deploy_stacks(self, app, cdk_env):
        self.app_vpc_stack(...)
        for stack_id in self.SIMPLE_ASG_IDS:   # reads class variable
            self.simple_asg_stack(...)

class DevInventory(Inventory):
    SIMPLE_ASG_IDS = SIMPLE_ASG_IDS_BY_ENV["dev"]       # only line

class StagingInventory(Inventory):
    SIMPLE_ASG_IDS = SIMPLE_ASG_IDS_BY_ENV["staging"]   # only line

class ProductionInventory(Inventory):
    SIMPLE_ASG_IDS = SIMPLE_ASG_IDS_BY_ENV["production"] # only line

INVENTORY_MAP: dict[str, type[Inventory]] = {
    "dev": DevInventory,
    "staging": StagingInventory,
    "production": ProductionInventory,
}

def get_inventory(app_env: str) -> Inventory:
    if app_env in INVENTORY_MAP:
        return INVENTORY_MAP[app_env](app_env=app_env)
    raise ValueError(...)
```

`discover.py` has the identical structure with `DevDiscoveryRunner`, `StagingDiscoveryRunner`, and `ProductionDiscoveryRunner`.

The `SIMPLE_ASG_IDS_BY_ENV` dict that each subclass reads from is already loaded from `template_defaults.json` — it already has the right value for every environment. The subclasses are just forwarding that value as a class variable. They hold no logic.

Note also that `TERMINATION_PROTECTION` is defined in the base class as `False` and is **not overridden in any subclass**. It doesn't differentiate the subclasses at all in the current code.

### What extending looks like today

To add a new environment (e.g. `sandbox`), a contributor must touch **four places** in three files:

1. **`config/template_defaults.json`** — add `sandbox` to `supported_app_envs`, `app_env_to_aws_account`, and `simple_asg_ids_by_env`
2. **`config/inventory.py`** — add `SandboxInventory(Inventory)` class and add `"sandbox": SandboxInventory` to `INVENTORY_MAP`
3. **`config/discover.py`** — add `SandboxDiscoveryRunner(DiscoveryRunner)` class and add `"sandbox": SandboxDiscoveryRunner` to `DISCOVERY_MAP`
4. **`config/<sandbox>/`** — add the environment config JSON files

Steps 2 and 3 are mechanical — they carry no information not already present in `template_defaults.json`. They exist only because the current design requires it.

### What it looks like after the fix

Move the `SIMPLE_ASG_IDS` lookup into `__init__` as an instance variable, and delete the subclasses and maps:

```python
class Inventory:
    TERMINATION_PROTECTION: ClassVar[bool] = False

    def __init__(self, app_env: str):
        check_app_env(app_env)
        check_aws_account(app_env)
        self.data_path = get_actual_path(app_env)
        self.app_env = app_env
        self.simple_asg_ids = SIMPLE_ASG_IDS_BY_ENV[app_env]  # was class var on subclass
        self.unique_stacks: dict[str, AppVpcStack] = {}
        self.multi_stacks: dict[str, dict[str, SimpleAsgStack]] = {}
        self.environment_setting = EnvironmentSetting.from_data_path(self.data_path)

    def deploy_stacks(self, app, cdk_env):
        self.app_vpc_stack(...)
        for stack_id in self.simple_asg_ids:   # now reads instance variable
            self.simple_asg_stack(...)

def get_inventory(app_env: str) -> Inventory:
    check_app_env(app_env)
    return Inventory(app_env=app_env)
```

The same change applies to `DiscoveryRunner` in `discover.py`. `check_app_env` already raises `ValueError` for unknown environments, so `get_inventory` still rejects invalid input — the `INVENTORY_MAP` lookup was just duplicating that guard.

### What extending looks like after the fix

To add `sandbox`, a contributor touches **two places** in two files:

1. **`config/template_defaults.json`** — same as before
2. **`config/<sandbox>/`** — same as before

`inventory.py` and `discover.py` require no changes.

### What to do about `TERMINATION_PROTECTION`

If production should eventually have `TERMINATION_PROTECTION = True`, it can be driven from config rather than a subclass override. Add a `termination_protection_by_env` map to `template_defaults.json`:

```json
"termination_protection_by_env": {
  "dev": false,
  "staging": false,
  "production": true
}
```

Then in `Inventory.__init__`:

```python
self.termination_protection = TERMINATION_PROTECTION_BY_ENV[app_env]
```

This keeps the environment-specific behavior in the same config file as every other environment-specific value, which is consistent with the project's philosophy.

> **Full design:** The complete redesign — including the `StackFactory` dataclass,
> `STACKS_BY_ENV` eligibility dict, updated `Inventory` and `DiscoveryRunner` classes,
> module structure, graduation workflow, and ADO pipeline example — is in
> `STACK_MANAGEMENT_DESIGN.md` and `azure-pipelines.yml`.

---

## 2. `get_logger` accumulates duplicate handlers (correctness)

`config/helper.py:37` — `get_logger()` calls `logging.getLogger()` (which returns the same logger instance on repeated calls) and then unconditionally calls `addHandler()`. Every import that calls `get_logger()` with the same module name adds another handler, producing duplicated log lines.

Fix: guard with `if not my_logger.handlers:` before adding the handler.

---

## 3. `unique_stacks["app_vpc"]` magic string is a silent failure point

`inventory.py:47,79,98` — the string `"app_vpc"` is used as a dict key in two places with no shared constant. If one is renamed, the runtime guard (`if app_vpc_stack is None: raise RuntimeError(...)`) silently stops working.

Fix: replace the `unique_stacks` dict with a typed instance attribute:
```python
self.app_vpc_stack: AppVpcStack | None = None
```
This is also more expressive — it makes it clear that there's exactly one AppVpc stack per inventory, not an arbitrary named collection.

---

## 4. `INVENTORY_MAP` has no coverage validation

`project.py:102-112` validates that `APP_ENV_TO_AWS_ACCOUNT` and `SIMPLE_ASG_IDS_BY_ENV` cover all `SUPPORTED_APP_ENVS`, but `INVENTORY_MAP` in `inventory.py` has no equivalent check. If recommendation #1 isn't taken, at minimum add this at the bottom of `inventory.py`:

```python
for _env in SUPPORTED_APP_ENVS:
    if _env not in INVENTORY_MAP:
        raise RuntimeError(f"INVENTORY_MAP missing entry for environment: {_env}")
```

---

## 5. `APP_ENVS` in test `_shared.py` duplicates `SUPPORTED_APP_ENVS`

`tests/unit/config/settings/_shared.py:12` hardcodes `APP_ENVS = ("dev", "staging", "production")`. Adding a new environment to `template_defaults.json` won't automatically update the test coverage. It should import from `config.project`:

```python
from config.project import SUPPORTED_APP_ENVS as APP_ENVS
```

---

## 6. Golden file `FileNotFoundError` gives no guidance

`tests/helper.py:59` raises a bare `FileNotFoundError`. When a developer adds a new test case and runs it, the error message gives no hint that they should run `make unit-update_golden`. The message should read something like: `"... does not exist. Run 'make unit-update_golden' to generate it."` — this is especially important for template users who haven't internalized the workflow yet.

---

## 7. `EnvironmentSetting` is loaded N+2 times per deploy

`Inventory.__init__` loads `environment_setting`. `AppVpcInput.from_config_directory` loads it again. Each call to `SimpleAsgInput.from_config_directory` loads it again. With N ASG stacks that's N+2 reads of the same file.

Easiest fix: accept an optional pre-loaded setting in the `Input.from_config_directory` class methods:
```python
@classmethod
def from_config_directory(cls, data_path: Path, env_setting: EnvironmentSetting | None = None) -> "AppVpcInput":
    return cls(
        env_setting=env_setting or EnvironmentSetting.from_data_path(data_path),
        app_vpc_setting=AppVpcSetting.from_data_path(data_path),
    )
```
Then `Inventory` passes `self.environment_setting` through. This is low-priority for correctness but good hygiene.

---

## 8. Makefile CDK targets repeat 5 lines of boilerplate (minor)

All `cdk-*` targets repeat the same find-CDK-binary + pyenv + activate shell preamble. A `define` macro would DRY this:

```makefile
define CDK_ENV
  $(eval CDK := $(shell find . -type f -name cdk))
  source scripts/enable_pyenv.sh; pyenv local $(PYTHON_VERSION); source .venv/bin/activate;
endef
```

---

## Summary

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | Empty env subclasses force multi-file changes per new env | `inventory.py`, `discover.py` | High — extensibility |
| 2 | Duplicate `get_logger` handlers cause doubled log output | `config/helper.py:37` | Correctness |
| 3 | Magic string `"app_vpc"` dict key is a silent failure point | `inventory.py:47,79,98` | Reliability |
| 4 | `INVENTORY_MAP` has no coverage assertion | `inventory.py` | Safety |
| 5 | `APP_ENVS` in tests is a duplicate of `SUPPORTED_APP_ENVS` | `tests/unit/config/settings/_shared.py:12` | Correctness |
| 6 | Golden file missing gives no `--update_golden` hint | `tests/helper.py:59` | DX for template users |
| 7 | `EnvironmentSetting` loaded N+2 times per deploy | `inventory.py`, `stack/` | Minor hygiene |
| 8 | CDK Makefile targets repeat 5-line boilerplate | `Makefile` | Minor cleanup |

Items 1–5 are the highest priority.
