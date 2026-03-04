#!/usr/bin/env python3
"""
Boomi MCP Server - Local MCP server for Boomi platform management.

- Uses local file-based credential storage (~/.boomi_mcp_local_secrets.json)
- Credential management tools (set/delete) are available
- Runs in stdio mode
"""

import json
import os
import sys
from typing import Dict
from pathlib import Path

from fastmcp import FastMCP

# --- Add boomi-python to path ---
boomi_python_path = Path(__file__).parent.parent / "boomi-python" / "src"
if boomi_python_path.exists():
    sys.path.insert(0, str(boomi_python_path))

# --- Add src to path ---
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from boomi import Boomi
except ImportError as e:
    print(f"ERROR: Failed to import Boomi SDK: {e}")
    print(f"       Boomi-python path: {boomi_python_path}")
    print(f"       Run: pip install git+https://github.com/RenEra-ai/boomi-python.git")
    sys.exit(1)

# --- Secrets Backend ---
try:
    from boomi_mcp.local_secrets import LocalSecretsBackend
    secrets_backend = LocalSecretsBackend()
    print(f"[INFO] Using local file-based secrets storage")
    print(f"[INFO] Storage file: {secrets_backend.storage_file}")
except ImportError as e:
    print(f"ERROR: Failed to import local_secrets: {e}")
    print(f"       Make sure src/boomi_mcp/local_secrets.py exists")
    sys.exit(1)

# --- Auto-import credentials from environment variables ---
_env_account = os.getenv("BOOMI_ACCOUNT_ID")
_env_username = os.getenv("BOOMI_USERNAME")
_env_password = os.getenv("BOOMI_TOKEN")
_env_profile = os.getenv("BOOMI_PROFILE", "default")
_env_base_url = os.getenv("BOOMI_BASE_URL")

if _env_account and _env_username and _env_password:
    _payload = {
        "account_id": _env_account,
        "username": _env_username,
        "password": _env_password,
    }
    if _env_base_url:
        _payload["base_url"] = _env_base_url
    secrets_backend.put_secret("local-dev-user", _env_profile, _payload)
    print(f"[INFO] Loaded credentials from env vars into profile '{_env_profile}'")

# --- Trading Partner Tools ---
try:
    from boomi_mcp.categories.components.trading_partners import manage_trading_partner_action
    print(f"[INFO] Trading partner tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import trading partner tools: {e}")
    manage_trading_partner_action = None

# --- Process Tools ---
try:
    from boomi_mcp.categories.components.processes import manage_process_action
    print(f"[INFO] Process tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import process tools: {e}")
    manage_process_action = None

# --- Organization Tools ---
try:
    from boomi_mcp.categories.components.organizations import manage_organization_action
    print(f"[INFO] Organization tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import organization tools: {e}")
    manage_organization_action = None

# --- Component Query Tools ---
try:
    from boomi_mcp.categories.components.query_components import query_components_action
    print(f"[INFO] Component query tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import component query tools: {e}")
    query_components_action = None

# --- Component Management Tools ---
try:
    from boomi_mcp.categories.components.manage_component import manage_component_action
    print(f"[INFO] Component management tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import component management tools: {e}")
    manage_component_action = None

# --- Component Analysis Tools ---
try:
    from boomi_mcp.categories.components.analyze_component import analyze_component_action
    print(f"[INFO] Component analysis tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import component analysis tools: {e}")
    analyze_component_action = None

# --- Connector Tools ---
try:
    from boomi_mcp.categories.components.connectors import manage_connector_action
    print(f"[INFO] Connector tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import connector tools: {e}")
    manage_connector_action = None

# --- Folder Tools ---
try:
    from boomi_mcp.categories.folders import manage_folders_action
    print(f"[INFO] Folder tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import folder tools: {e}")
    manage_folders_action = None

# --- Monitoring Tools ---
try:
    from boomi_mcp.categories.monitoring import monitor_platform_action
    print(f"[INFO] Monitoring tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import monitoring tools: {e}")
    monitor_platform_action = None

# --- Schema Template Tools ---
try:
    from boomi_mcp.categories.meta_tools import get_schema_template_action
    print(f"[INFO] Schema template tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import schema template tools: {e}")
    get_schema_template_action = None

# --- Generic API Invoker ---
try:
    from boomi_mcp.categories.meta_tools import invoke_api
    print(f"[INFO] Generic API invoker loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import generic API invoker: {e}")
    invoke_api = None

# --- List Capabilities ---
try:
    from boomi_mcp.categories.meta_tools import list_capabilities_action
    print(f"[INFO] List capabilities loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import list capabilities: {e}")
    list_capabilities_action = None

# --- Environment Tools ---
try:
    from boomi_mcp.categories.environments import manage_environments_action
    print(f"[INFO] Environment tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import environment tools: {e}")
    manage_environments_action = None

# --- Runtime Tools ---
try:
    from boomi_mcp.categories.runtimes import manage_runtimes_action
    print(f"[INFO] Runtime tools loaded successfully")
except ImportError as e:
    print(f"[WARNING] Failed to import runtime tools: {e}")
    manage_runtimes_action = None


def put_secret(sub: str, profile: str, payload: Dict[str, str]):
    """Store credentials for a user profile."""
    secrets_backend.put_secret(sub, profile, payload)
    print(f"[INFO] Stored credentials for {sub}:{profile} (username: {payload.get('username', '')[:10]}***)")


def get_secret(sub: str, profile: str) -> Dict[str, str]:
    """Retrieve credentials for a user profile."""
    return secrets_backend.get_secret(sub, profile)


def list_profiles(sub: str):
    """List all profiles for a user."""
    return secrets_backend.list_profiles(sub)


def delete_profile(sub: str, profile: str):
    """Delete a user profile."""
    secrets_backend.delete_profile(sub, profile)


# --- Create MCP Server ---
mcp = FastMCP(
    name="Boomi MCP Server"
)


# --- User Identity ---
def get_current_user() -> str:
    """Get current user identity."""
    return "local-dev-user"


# --- MCP Tools ---

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def list_boomi_profiles():
    """
    List all saved Boomi credential profiles for the current user.

    Returns a list of profile names that can be used with boomi_account_info().
    Use this tool first to see which profiles are available before requesting account info.

    Returns:
        List of profile objects with 'profile' name and metadata
    """
    try:
        subject = get_current_user()
        print(f"[INFO] list_boomi_profiles called by user: {subject}")

        profiles = list_profiles(subject)
        print(f"[INFO] Found {len(profiles)} profiles for {subject}")

        if not profiles:
            return {
                "_success": True,
                "profiles": [],
                "message": "No profiles found. Use set_boomi_credentials tool to add credentials.",
            }

        return {
            "_success": True,
            "profiles": [p["profile"] for p in profiles],
            "count": len(profiles),
        }
    except Exception as e:
        print(f"[ERROR] Failed to list profiles: {e}")
        return {
            "_success": False,
            "error": f"Failed to list profiles: {str(e)}"
        }


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def boomi_account_info(profile: str):
    """
    Get Boomi account information from a specific profile.

    MULTI-ACCOUNT SUPPORT:
    - Users can store multiple Boomi accounts (up to 10 profiles)
    - Each profile has a unique name (e.g., 'production', 'sandbox', 'dev')
    - Profile name is REQUIRED - there is no default profile
    - If user has multiple profiles, ASK which one to use for the task
    - Once user specifies a profile, continue using it for subsequent calls
    - Don't repeatedly ask if already working with a selected profile

    WORKFLOW:
    1. First call: Use list_boomi_profiles to see available profiles
    2. If multiple profiles exist, ask user which one to use
    3. If only one profile exists, use that one
    4. Use the selected profile for all subsequent Boomi API calls in this conversation
    5. Only ask again if user explicitly wants to switch accounts

    CREDENTIALS:
    - Store credentials using set_boomi_credentials tool
    - Credentials stored in ~/.boomi_mcp_local_secrets.json

    Args:
        profile: Profile name to use (REQUIRED - no default)

    Returns:
        Account information including name, status, licensing details, or error details
    """
    try:
        subject = get_current_user()
        print(f"[INFO] boomi_account_info called by user: {subject}, profile: {profile}")
    except Exception as e:
        print(f"[ERROR] Failed to get user subject: {e}")
        return {
            "_success": False,
            "error": f"Authentication failed: {str(e)}"
        }

    # Try to get stored credentials
    try:
        creds = get_secret(subject, profile)
        print(f"[INFO] Successfully retrieved stored credentials for {subject}:{profile}")
        print(f"[INFO] Account ID: {creds.get('account_id')}, Username: {creds.get('username', '')[:20]}...")
    except ValueError as e:
        print(f"[ERROR] Profile '{profile}' not found for user {subject}: {e}")

        # List available profiles
        available_profiles = list_profiles(subject)
        print(f"[INFO] Available profiles for {subject}: {[p['profile'] for p in available_profiles]}")

        return {
            "_success": False,
            "error": f"Profile '{profile}' not found. Use set_boomi_credentials to add credentials.",
            "available_profiles": [p["profile"] for p in available_profiles],
        }
    except Exception as e:
        print(f"[ERROR] Unexpected error retrieving credentials: {e}")
        return {
            "_success": False,
            "error": f"Failed to retrieve credentials: {str(e)}"
        }

    print(f"[INFO] Calling Boomi API for {subject}:{profile} (account: {creds['account_id']})")

    # Initialize Boomi SDK
    try:
        sdk_params = {
            "account_id": creds["account_id"],
            "username": creds["username"],
            "password": creds["password"],
            "timeout": 30000,  # 30 seconds (SDK uses milliseconds)
        }

        # Only add base_url if explicitly provided (not None)
        if creds.get("base_url"):
            sdk_params["base_url"] = creds["base_url"]

        sdk = Boomi(**sdk_params)

        # Call the same endpoint the sample demonstrates
        result = sdk.account.get_account(id_=creds["account_id"])

        # Convert to plain dict for transport
        if hasattr(result, "__dict__"):
            out = {
                k: v for k, v in result.__dict__.items()
                if not k.startswith("_") and v is not None
            }
            out["_success"] = True
            out["_note"] = "Account data retrieved successfully"
            print(f"[INFO] Successfully retrieved account info for {creds['account_id']}")
            return out

        return {
            "_success": True,
            "message": "Account object created; minimal data returned.",
            "_note": "This indicates successful authentication."
        }

    except Exception as e:
        print(f"[ERROR] Boomi API call failed: {e}")
        return {
            "_success": False,
            "error": str(e),
            "account_id": creds["account_id"],
            "_note": "Check credentials and API access permissions"
        }


# --- Trading Partner MCP Tools ---
if manage_trading_partner_action:
    @mcp.tool()
    def manage_trading_partner(
        profile: str,
        action: str,
        resource_id: str = None,
        config: str = None,
    ):
        """
        Manage B2B/EDI trading partners (all 7 standards) and organizations via JSON config.

        Args:
            profile: Boomi profile name (required)
            action: One of: list, get, create, update, delete, analyze_usage, list_options, org_list, org_get, org_create, org_update, org_delete
            resource_id: Trading partner component ID (required for get, update, delete, analyze_usage) or organization ID (required for org_get, org_update, org_delete)
            config: JSON string with action-specific configuration (see examples below)

        RECOMMENDED WORKFLOW for create/update:
          1. Call action="list_options" first to get all valid enum values
          2. Present the full set of options to the user
          3. Then call action="create" or action="update" with user selections

        Tip: Use action="get" with a known resource_id to retrieve the full structure,
        then use that output as a template for create/update config.

        Actions and config examples:

            list_options - Get all valid enum values (no config needed, no API call):
                Returns standards, classifications, protocols, and protocol-specific enums

            list - List trading partners, optional filters:
                config='{"standard": "x12", "classification": "tradingpartner", "folder_name": "Partners"}'

            get - Get partner by ID (no config needed):
                resource_id="abc-123-def"

            create - Create new partner (config required):
                config='{
                    "component_name": "Acme Corp",
                    "standard": "x12",
                    "classification": "tradingpartner",
                    "folder_name": "Partners",
                    "isa_id": "ACME",
                    "isa_qualifier": "ZZ",
                    "gs_id": "ACMECORP",
                    "contact_name": "John Doe",
                    "contact_email": "john@acme.com",
                    "communication_protocols": ["http", "as2"],
                    "http_url": "https://api.acme.com/edi",
                    "as2_url": "https://as2.acme.com"
                }'

            update - Update existing partner (config required):
                resource_id="abc-123-def"
                config='{"contact_email": "new@acme.com", "http_url": "https://new.acme.com"}'

            delete - Delete partner (no config needed):
                resource_id="abc-123-def"

            analyze_usage - Analyze partner usage (no config needed):
                resource_id="abc-123-def"

            org_list - List organizations, optional filters:
                config='{"folder_name": "Home/Organizations"}'

            org_get - Get organization by ID (no config needed):
                resource_id="abc-123-def"

            org_create - Create new organization (config required):
                config='{
                    "component_name": "Acme Corp",
                    "folder_name": "Home/Organizations",
                    "contact_name": "John Doe",
                    "contact_email": "john@acme.com",
                    "contact_phone": "555-1234",
                    "contact_address": "123 Main St",
                    "contact_city": "New York",
                    "contact_state": "NY",
                    "contact_country": "USA",
                    "contact_postalcode": "10001"
                }'

            org_update - Update existing organization (config required):
                resource_id="abc-123-def"
                config='{"contact_email": "new@acme.com", "contact_phone": "555-5678"}'

            org_delete - Delete organization (no config needed):
                resource_id="abc-123-def"

        Config field reference (all optional, grouped by category):

            Basic: component_name, standard (x12|edifact|hl7|rosettanet|custom|tradacoms|odette),
                   classification (tradingpartner|mycompany), folder_name

            X12: isa_id, isa_qualifier, gs_id
            EDIFACT: edifact_interchange_id, edifact_interchange_id_qual, edifact_syntax_id,
                     edifact_syntax_version, edifact_test_indicator
            HL7: hl7_application, hl7_facility
            RosettaNet: rosettanet_partner_id, rosettanet_partner_location,
                        rosettanet_global_usage_code, rosettanet_supply_chain_code,
                        rosettanet_classification_code
            TRADACOMS: tradacoms_interchange_id, tradacoms_interchange_id_qualifier
            ODETTE: odette_interchange_id, odette_interchange_id_qual, odette_syntax_id,
                    odette_syntax_version, odette_test_indicator

            Contact: contact_name, contact_email, contact_phone, contact_fax,
                     contact_address, contact_address2, contact_city, contact_state,
                     contact_country, contact_postalcode

            Protocols: communication_protocols (JSON array: ["http", "as2", "ftp", "sftp", "disk", "mllp", "oftp"])
            Organization: organization_id (use org_list to find IDs)

            Organization fields (for org_* actions):
                component_name, folder_name,
                contact_name, contact_email, contact_phone, contact_fax, contact_url,
                contact_address, contact_address2, contact_city, contact_state,
                contact_country, contact_postalcode

            Protocol-specific keys (use action="get" to see all fields for a protocol):
                Disk: disk_directory (alias: sets both get+send), disk_get_directory, disk_send_directory, ... (9 fields)
                FTP: ftp_host, ftp_port, ftp_username, ftp_password, ftp_remote_directory (alias: ftp_directory),
                     ftp_ssl_mode (NONE|EXPLICIT|IMPLICIT; alias: ftp_use_ssl true→EXPLICIT), ... (17 fields)
                SFTP: sftp_host, sftp_port, sftp_username, sftp_password, sftp_remote_directory (alias: sftp_directory),
                      sftp_ssh_key_auth (alias: sftp_use_key_auth), sftp_known_host_entry (alias: sftp_known_hosts_file), ... (22 fields)
                HTTP: http_url, http_username, http_authentication_type (NONE|BASIC|PASSWORD_DIGEST|CUSTOM|OAUTH|OAUTH2),
                      http_data_content_type (alias: http_content_type), http_connect_timeout (alias: http_connection_timeout),
                      http_method_type (alias: http_send_method), http_client_ssl_alias (alias: http_ssl_cert_id), ... (40+ fields incl. OAuth)
                AS2: as2_url, as2_signed, as2_encrypted, as2_signing_digest_alg (alias: as2_sign_algorithm; SHA1|SHA256|SHA384|SHA512),
                     as2_request_mdn (alias: as2_mdn_required), as2_sign_alias (alias: as2_signing_cert_id),
                     as2_encrypt_alias (alias: as2_encryption_cert_id), as2_data_content_type (alias: as2_content_type), ... (30 fields)
                MLLP: mllp_host, mllp_port, mllp_use_ssl, ... (13 fields)
                OFTP: oftp_host, oftp_port, oftp_tls, ... (14 fields)

            Enum values:
                edifact_test_indicator / odette_test_indicator: "1" (test), "NA" (production). "0" is auto-mapped to "NA".
                ftp_ssl_mode: "NONE", "EXPLICIT", "IMPLICIT"
                as2_signing_digest_alg: "SHA1", "SHA256", "SHA384", "SHA512"
                as2_encryption_algorithm: "tripledes", "rc2", "aes128", "aes192", "aes256"

            Dropped fields (no Boomi API equivalent):
                as2_from, as2_to (use as2_partner_id instead), http_max_redirects, http_response_content_type

        Returns:
            Action result with success status and data/error
        """
        # Static actions (no API call needed)
        if action == "list_options":
            return manage_trading_partner_action(None, profile, action)

        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_trading_partner called by user: {subject}, profile: {profile}, action: {action}")

            # Get credentials
            creds = get_secret(subject, profile)

            # Initialize Boomi SDK
            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            # Organization sub-actions
            if action.startswith("org_"):
                if not manage_organization_action:
                    return {"_success": False, "error": "Organization module not available"}
                org_action = action[4:]  # "org_list" -> "list"
                org_params = {}
                if org_action == "list":
                    if config_data:
                        org_params["filters"] = config_data
                elif org_action == "get":
                    org_params["organization_id"] = resource_id
                elif org_action == "create":
                    org_params["request_data"] = config_data
                elif org_action == "update":
                    org_params["organization_id"] = resource_id
                    org_params["updates"] = config_data
                elif org_action == "delete":
                    org_params["organization_id"] = resource_id
                return manage_organization_action(sdk, profile, org_action, **org_params)

            # Build parameters based on action
            params = {}

            if action == "list":
                if config_data:
                    params["filters"] = config_data

            elif action == "get":
                params["partner_id"] = resource_id

            elif action == "create":
                params["request_data"] = config_data

            elif action == "update":
                params["partner_id"] = resource_id
                params["updates"] = config_data

            elif action == "delete":
                params["partner_id"] = resource_id

            elif action == "analyze_usage":
                params["partner_id"] = resource_id

            return manage_trading_partner_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} trading partner: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Trading partner tool registered successfully (1 consolidated tool)")


# --- Process MCP Tools ---
if manage_process_action:
    @mcp.tool()
    def manage_process(
        profile: str,
        action: str,
        process_id: str = None,
        config_yaml: str = None,
        filters: str = None
    ):
        """
        Manage Boomi process components with AI-friendly YAML configuration.

        This tool enables creation of simple processes or complex multi-component
        workflows with automatic dependency management and ID resolution.

        Args:
            profile: Boomi profile name (required)
            action: Action to perform - must be one of: list, get, create, update, delete
            process_id: Process component ID (required for get, update, delete)
            config_yaml: YAML configuration string (required for create, update)
            filters: JSON string with filters for list action (optional)

        Actions:
            - list: List all process components
                Example: action="list"
                Example with filter: action="list", filters='{"folder_name": "Integrations"}'

            - get: Get specific process by ID
                Example: action="get", process_id="abc-123-def"

            - create: Create new process(es) from YAML
                Single process example:
                    config_yaml = '''
                    name: "Hello World"
                    folder_name: "Test"
                    shapes:
                      - type: start
                        name: start
                      - type: message
                        name: msg
                        config:
                          message_text: "Hello from Boomi!"
                      - type: stop
                        name: end
                    '''

                Multi-component with dependencies:
                    config_yaml = '''
                    components:
                      - name: "Transform Map"
                        type: map
                        dependencies: []
                      - name: "Main Process"
                        type: process
                        dependencies: ["Transform Map"]
                        config:
                          name: "Main Process"
                          shapes:
                            - type: start
                              name: start
                            - type: map
                              name: transform
                              config:
                                map_ref: "Transform Map"
                            - type: stop
                              name: end
                    '''

            - update: Update existing process
                Example: action="update", process_id="abc-123", config_yaml="..."

            - delete: Delete process
                Example: action="delete", process_id="abc-123-def"

        YAML Shape Types:
            - start: Process start (required first shape)
            - stop: Process termination (can be last shape)
            - return: Return documents (alternative last shape)
            - message: Debug/logging messages
            - map: Data transformation (requires map_id or map_ref)
            - connector: External system integration (requires connector_id, operation)
            - decision: Conditional branching (requires expression)
            - branch: Parallel branches (requires num_branches)
            - note: Documentation annotation

        Returns:
            Dict with success status and result data

        Examples:
            # List all processes
            result = manage_process(profile="prod", action="list")

            # Create simple process
            result = manage_process(
                profile="prod",
                action="create",
                config_yaml="name: Test\\nshapes: [...]"
            )

            # Get process details
            result = manage_process(
                profile="prod",
                action="get",
                process_id="abc-123-def"
            )
        """
        try:
            subject = get_current_user()
            print(f"[INFO] manage_process called by user: {subject}, profile: {profile}, action: {action}")

            # Get credentials
            creds = get_secret(subject, profile)

            # Initialize Boomi SDK
            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            # Build parameters based on action
            params = {}

            if action == "list":
                if filters:
                    try:
                        params["filters"] = json.loads(filters)
                    except (json.JSONDecodeError, TypeError) as e:
                        return {"_success": False, "error": f"Invalid filters (must be a JSON string): {e}"}
                    if not isinstance(params["filters"], dict):
                        return {"_success": False, "error": "filters must be a JSON object, not " + type(params["filters"]).__name__}

            elif action == "get":
                params["process_id"] = process_id

            elif action == "create":
                params["config_yaml"] = config_yaml

            elif action == "update":
                params["process_id"] = process_id
                params["config_yaml"] = config_yaml

            elif action == "delete":
                params["process_id"] = process_id

            # Call the action function
            return manage_process_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} process: {e}")
            import traceback
            traceback.print_exc()
            return {"_success": False, "error": str(e), "exception_type": type(e).__name__}

    print("[INFO] Process tool registered successfully (1 consolidated tool)")



# --- Monitoring MCP Tools ---
if monitor_platform_action:
    @mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
    def monitor_platform(
        profile: str,
        action: str,
        config: str = None,
    ):
        """
        Monitor Boomi platform: execution history, logs, artifacts, audit trail, and events.

        Args:
            profile: Boomi profile name (required)
            action: One of: execution_records, execution_logs, execution_artifacts, audit_logs, events
            config: JSON string with action-specific configuration (see examples below)

        Actions and config examples:

            execution_records - Query execution history (like Process Reporting):
                config='{"start_date": "2025-01-01T00:00:00Z", "end_date": "2025-01-31T23:59:59Z", "status": "ERROR", "process_name": "My Process", "atom_name": "Production Atom", "limit": 50}'
                Filter fields (at least one required): start_date, end_date, status, process_name, process_id, atom_name, atom_id, execution_id
                Status values: COMPLETE, ERROR, ABORTED, COMPLETE_WARN, INPROCESS

            execution_logs - Download and return process logs inline:
                config='{"execution_id": "abc-123-def", "log_level": "ALL"}'
                log_level values: SEVERE, WARNING, INFO, CONFIG, FINE, FINER, FINEST, ALL (default: ALL)
                Log content is automatically downloaded and returned inline (ZIP extracted).
                Set "fetch_content": false to get only the download URL instead.

            execution_artifacts - Download and return execution artifacts inline:
                config='{"execution_id": "abc-123-def"}'
                Artifact content is automatically downloaded and returned inline (ZIP extracted).
                Set "fetch_content": false to get only the download URL instead.

            audit_logs - Query audit trail with filters:
                config='{
                    "start_date": "2025-01-01T00:00:00Z",
                    "end_date": "2025-01-31T23:59:59Z",
                    "user": "user@example.com",
                    "action": "Deploy",
                    "type": "Process",
                    "level": "INFO",
                    "source": "API",
                    "limit": 100
                }'

            events - Query platform events with filters:
                config='{
                    "start_date": "2025-01-01T00:00:00Z",
                    "end_date": "2025-12-31T23:59:59Z",
                    "event_level": "ERROR",
                    "event_type": "process.error",
                    "process_name": "My Process",
                    "atom_name": "Production Atom",
                    "execution_id": "abc-123-def",
                    "limit": 100
                }'

        Returns:
            Action result with success status and data/error
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] monitor_platform called by user: {subject}, profile: {profile}, action: {action}")

            # Get credentials
            creds = get_secret(subject, profile)

            # Initialize Boomi SDK
            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            return monitor_platform_action(sdk, profile, action, config_data=config_data, creds=creds)

        except Exception as e:
            print(f"[ERROR] Failed to {action} monitor_platform: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Monitoring tool registered successfully (1 consolidated tool)")


# --- Component Query MCP Tools ---
if query_components_action:
    @mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
    def query_components(
        profile: str,
        action: str,
        component_id: str = None,
        component_ids: str = None,
        config: str = None,
    ):
        """
        Discover and retrieve Boomi components across all types.

        Args:
            profile: Boomi profile name (required)
            action: One of: list, get, search, bulk_get
            component_id: Component ID (required for get)
            component_ids: JSON array of component IDs (required for bulk_get, max 5)
            config: JSON string with action-specific configuration

        Actions and config examples:

            list - List all components, optionally filtered:
                config='{"type": "process"}'
                config='{"folder_name": "Integrations"}'
                config='{"type": "transform.map", "show_all": true}'

            get - Get a single component with full XML:
                component_id="abc-123-def"

            search - Multi-field search with AND logic:
                config='{"name": "%Test%", "type": "process"}'
                config='{"name": "%Map%", "folder_name": "Production"}'
                config='{"sub_type": "some_value"}'
                config='{"created_by": "user@example.com"}'
                config='{"modified_by": "user@example.com"}'
                config='{"component_id": "abc-123"}'

            bulk_get - Retrieve up to 5 components by ID (metadata only, no XML):
                component_ids='["id1", "id2", "id3"]'

        Component types:
            Processes: process, processproperty, processroute
            Connectors: connector-settings, connector-action
            Profiles: profile.db, profile.edi, profile.flatfile, profile.json, profile.xml
            Trading Partners: tradingpartner, tpgroup, tporganization, tpcommoptions
            Transforms: transform.map, transform.function, xslt, script.processing, script.mapping
            Services: flowservice, webservice, webservice.external
            Other: certificate, certificate.pgp, crossref, customlibrary, documentcache,
                edistandard, queue

        Returns:
            Action result with success status and component data
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        # Parse component_ids JSON
        ids_list = None
        if component_ids:
            try:
                ids_list = json.loads(component_ids)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid component_ids (must be a JSON array): {e}"}
            if not isinstance(ids_list, list):
                return {"_success": False, "error": "component_ids must be a JSON array"}

        try:
            subject = get_current_user()
            print(f"[INFO] query_components called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if action == "list":
                if config_data:
                    params["filters"] = config_data
            elif action == "get":
                params["component_id"] = component_id
            elif action == "search":
                params["filters"] = config_data
            elif action == "bulk_get":
                params["component_ids"] = ids_list

            return query_components_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} query_components: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Component query tool registered successfully (1 consolidated tool)")


# --- Component Management MCP Tools ---
if manage_component_action:
    @mcp.tool()
    def manage_component(
        profile: str,
        action: str,
        component_id: str = None,
        config: str = None,
        config_yaml: str = None,
    ):
        """
        Create, update, clone, and delete Boomi components.

        Args:
            profile: Boomi profile name (required)
            action: One of: create, update, clone, delete
            component_id: Component ID (required for update, clone, delete)
            config: JSON string with action-specific configuration
            config_yaml: YAML string (for creating process components via manage_process)

        Actions and config examples:

            create - Create a component from XML template:
                config='{"xml": "<full-component-xml>...</full-component-xml>"}'
                For processes, use manage_process with config_yaml instead.
                For connectors (connector-settings, connector-action), use manage_connector.
                Tip: Use query_components get on a similar component to obtain an XML template.

            update - Update an existing component:
                component_id="abc-123-def"
                config='{"name": "Renamed Component"}'
                config='{"description": "Updated description"}'
                config='{"xml": "<full-component-xml>...</full-component-xml>"}'

            clone - Clone a component with a new name:
                component_id="abc-123-def"
                config='{"name": "Cloned Component"}'
                config='{"name": "Cloned", "folder_name": "Test Folder"}'

            delete - Delete a component:
                component_id="abc-123-def"

        Returns:
            Action result with success status and component data
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_component called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if action == "create":
                params["config"] = config_data
                if config_yaml:
                    params["config_yaml"] = config_yaml
            elif action == "update":
                params["component_id"] = component_id
                params["config"] = config_data
            elif action == "clone":
                params["component_id"] = component_id
                params["config"] = config_data
            elif action == "delete":
                params["component_id"] = component_id

            return manage_component_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} manage_component: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Component management tool registered successfully (1 consolidated tool)")


# --- Component Analysis MCP Tools ---
if analyze_component_action:
    @mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
    def analyze_component(
        profile: str,
        action: str,
        component_id: str = None,
        config: str = None,
    ):
        """
        Analyze component dependencies and compare versions.

        Args:
            profile: Boomi profile name (required)
            action: One of: where_used, dependencies, compare_versions
            component_id: Component ID (required for all actions)
            config: JSON string with action-specific configuration

        Actions and config examples:

            where_used - Find all components that reference this component (inbound):
                component_id="abc-123-def"
                config='{"type": "process"}'  (optional: filter by reference type)

            dependencies - Find all components this component references (outbound):
                component_id="abc-123-def"

            compare_versions - Compare two versions of a component:
                component_id="abc-123-def"
                config='{"source_version": 1, "target_version": 2}'

        Notes:
            - where_used and dependencies show immediate references only (one level)
            - compare_versions requires both version numbers to exist for the component
            - Use query_components action="get" to find a component's current version

        Returns:
            Action result with success status and analysis data
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] analyze_component called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if action == "where_used":
                params["component_id"] = component_id
                if config_data:
                    params["filters"] = config_data
            elif action == "dependencies":
                params["component_id"] = component_id
                if config_data:
                    params["filters"] = config_data
            elif action == "compare_versions":
                params["component_id"] = component_id
                params["config"] = config_data

            return analyze_component_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} analyze_component: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Component analysis tool registered successfully (1 consolidated tool)")


# --- Connector MCP Tools ---
if manage_connector_action:
    @mcp.tool(annotations={"openWorldHint": True})
    def manage_connector(
        profile: str,
        action: str,
        component_id: str = None,
        config: str = None,
    ):
        """Manage connector components (connections and operations) with catalog discovery.

        Args:
            profile: Boomi profile name (required)
            action: One of: list_types, get_type, list, get, create, update, delete
            component_id: Component ID (required for get, update, delete)
            config: JSON string with action-specific configuration

        Actions and config examples:

            list_types - List available connector types in the Boomi account:
                (no config needed)

            get_type - Get field definitions for a connector type:
                config='{"connector_type": "http"}'

            list - List connector components (connections and/or operations):
                config='{"component_type": "connection"}'
                config='{"component_type": "operation", "connector_type": "http"}'
                config='{"connector_type": "database"}'
                component_type values: "connection" (connector-settings) or "operation" (connector-action)

            get - Get a connector component with full XML:
                component_id="abc-123-def"

            create - Create new connector (builder or raw XML):
                config='{"connector_type": "http", "component_name": "My HTTP", "url": "https://api.example.com", "auth_type": "NONE"}'
                config='{"connector_type": "http", "component_name": "OAuth API", "url": "https://api.example.com", "auth_type": "OAUTH2", "oauth2_token_url": "https://auth.example.com/token", "oauth2_client_id": "my-client"}'
                config='{"xml": "<bns:Component ...>...</bns:Component>"}'

            update - Update existing connector:
                component_id="abc-123-def", config='{"url": "https://new-url.com"}'
                component_id="abc-123-def", config='{"name": "Renamed Connection", "auth_type": "BASIC"}'
                component_id="abc-123-def", config='{"xml": "<full-component-xml>...</full-component-xml>"}'

            delete - Delete connector:
                component_id="abc-123-def"

        Returns:
            Action result with success status and connector data
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_connector called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if action == "list_types":
                pass  # no extra params
            elif action == "get_type":
                params["connector_type"] = config_data.get("connector_type")
            elif action == "list":
                params["filters"] = config_data if config_data else None
            elif action == "get":
                params["component_id"] = component_id
            elif action == "create":
                params["config"] = config_data if config_data else None
            elif action == "update":
                params["component_id"] = component_id
                params["config"] = config_data if config_data else None
            elif action == "delete":
                params["component_id"] = component_id

            return manage_connector_action(sdk, profile, action, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} manage_connector: {e}")
            return {"_success": False, "error": str(e)}

    print("[INFO] Connector tool registered successfully (1 consolidated tool)")


# --- Folder Management MCP Tools ---
if manage_folders_action:
    @mcp.tool()
    def manage_folders(
        profile: str,
        action: str,
        folder_id: str = None,
        config: str = None,
    ):
        """
        Manage folder hierarchy for organizing Boomi components.

        Args:
            profile: Boomi profile name (required)
            action: One of: list, get, create, move, delete, restore, contents
            folder_id: Folder ID (required for get, delete, restore, contents)
            config: JSON string with action-specific configuration (see examples below)

        Actions and config examples:

            list - List all folders with tree view:
                config='{"include_deleted": true}'
                config='{"folder_name": "Production"}'
                config='{"folder_path": "Production/APIs"}'

            get - Get folder by ID (no config needed):
                folder_id="abc-123-def"

            create - Create folder or hierarchy:
                config='{"folder_name": "Production/APIs/v2"}'
                config='{"folder_name": "NewFolder", "parent_folder_id": "abc-123"}'

            move - Move a component to a folder:
                config='{"component_id": "comp-123", "target_folder_id": "folder-456"}'

            delete - Delete an empty folder:
                folder_id="abc-123-def"

            restore - Restore a deleted folder:
                folder_id="abc-123-def"

            contents - List components and sub-folders in a folder:
                folder_id="abc-123-def"
                config='{"folder_name": "Production"}'

        Returns:
            Action result with success status and data/error
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_folders called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if folder_id:
                params["folder_id"] = folder_id

            return manage_folders_action(sdk, profile, action, config_data=config_data, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} manage_folders: {e}")
            import traceback
            traceback.print_exc()
            return {"_success": False, "error": str(e), "exception_type": type(e).__name__}

    print("[INFO] Folder management tool registered successfully (1 consolidated tool)")


# --- Schema Template MCP Tool ---
if get_schema_template_action:
    @mcp.tool(annotations={"readOnlyHint": True})
    def get_schema_template(
        resource_type: str,
        operation: str = None,
        standard: str = None,
        component_type: str = None,
        protocol: str = None,
    ):
        """Get JSON/YAML template and enum values for constructing tool requests.

        Returns example payloads, required/optional fields, and valid enum values.
        No API calls — pure reference data. Use before create/update operations.

        Args:
            resource_type: One of: trading_partner, process, component, environment, package, execution_request, organization, folder, monitoring
            operation: Optional action context: create, update, list, execute, search, clone, compare_versions, execution_records, execution_logs, execution_artifacts, audit_logs, events
            standard: For trading_partner create: x12, edifact, hl7, rosettanet, tradacoms, odette, custom
            component_type: For component: process, connector-settings, transform.map, etc.
            protocol: For trading_partner protocols: http, as2, ftp, sftp, disk, mllp, oftp

        Examples:
            get_schema_template("trading_partner") → overview of all actions/standards
            get_schema_template("trading_partner", "create", standard="x12") → X12 create template
            get_schema_template("trading_partner", protocol="as2") → AS2 protocol fields
            get_schema_template("process", "create") → YAML process template
            get_schema_template("component") → overview of component tools
            get_schema_template("monitoring", "execution_records") → execution query template
            get_schema_template("organization", "create") → organization create template
        """
        return get_schema_template_action(
            resource_type=resource_type,
            operation=operation,
            standard=standard,
            component_type=component_type,
            protocol=protocol,
        )

    print("[INFO] Schema template tool registered successfully")


# --- Generic API Invoker MCP Tool ---
if invoke_api:
    @mcp.tool()
    def invoke_boomi_api(
        profile: str,
        endpoint: str,
        method: str = "GET",
        payload: str = None,
        content_type: str = "json",
        accept: str = "json",
        confirm_delete: bool = False,
    ):
        """Direct Boomi API access for operations not covered by other tools.

        Generic escape hatch for any Boomi REST API endpoint.

        Args:
            profile: Boomi profile name (required for authentication)
            endpoint: API endpoint path (appended to base URL).
                      Format: "Resource" or "Resource/id" or "Resource/query"
            method: HTTP method - GET, POST, PUT, DELETE
            payload: JSON string request body for POST/PUT (parsed and sent as-is)
            content_type: Request body format - "json" (default) or "xml"
            accept: Response format - "json" (default) or "xml"
            confirm_delete: Set to true to confirm DELETE operations (safety gate)

        Common endpoints:
            # Roles — see /mnt/examples/04_environment_setup/manage_roles.py
            - "Role/query" POST with filter body → list roles
            - "Role" POST with role body → create role
            - "Role/{id}" GET → get role
            - "Role/{id}" DELETE → delete role

            # Branches — see /mnt/examples/02_organize_structure/manage_branches.py
            - "Branch/query" POST with filter body → list branches
            - "Branch" POST → create branch
            - "Branch/{id}" DELETE → delete branch

            # Folders — see /mnt/examples/02_organize_structure/manage_folders.py
            - "Folder/query" POST with filter body → list folders
            - "Folder" POST → create folder
            - "Folder/{id}" GET → get folder

            # Shared Web Server
            - "SharedWebServer/{id}" GET → get web server config

            # Persisted Properties (async — returns token, poll for result)
            - "PersistedProcessProperties/{atomId}" GET → initiate async get

            # Queues (async)
            - "ListQueues/{atomId}" GET → initiate async queue list
            - "ClearQueue" POST → clear queue messages
            - "MoveQueue" POST → move messages between queues

            # Secrets
            - "SecretsManagerRefreshRequest" POST → refresh secrets

            # Packages & Deployments
            - "PackagedComponent/query" POST → list packages
            - "DeployedPackage/query" POST → list deployments
            - "DeployedPackage" POST → deploy package

        Examples:
            # List all roles
            invoke_boomi_api(profile="prod", endpoint="Role/query",
                method="POST", payload='{"QueryFilter":{"expression":{"operator":"EQUALS","property":"name","argument":["Administrator"]}}}')

            # Get a specific folder
            invoke_boomi_api(profile="prod", endpoint="Folder/12345", method="GET")

            # Get component as XML
            invoke_boomi_api(profile="prod", endpoint="Component/abc-123",
                method="GET", accept="xml")
        """
        try:
            subject = get_current_user()
            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]

            sdk = Boomi(**sdk_params)

            return invoke_api(
                boomi_client=sdk,
                profile=profile,
                endpoint=endpoint,
                method=method,
                payload=payload,
                content_type=content_type,
                accept=accept,
                confirm_delete=confirm_delete,
            )

        except Exception as e:
            return {"_success": False, "error": str(e)}

    print("[INFO] Generic API invoker tool registered successfully")


# --- List Capabilities ---
if list_capabilities_action:
    @mcp.tool(annotations={"readOnlyHint": True})
    def list_capabilities():
        """List all available MCP tools and their capabilities.

        Returns summary of:
        - All 17 tools with descriptions and actions
        - Implementation status (which tools are ready)
        - Workflow suggestions for common multi-step tasks
        - Coverage statistics (SDK example coverage)
        - Quick-start hints

        No parameters needed. Call this to understand what operations are possible.

        Helps AI agent:
        - Select the right tool for any user request
        - Understand multi-step workflows (e.g., create → package → deploy → monitor)
        - Know when to use invoke_boomi_api for uncovered APIs
        - Find the right get_schema_template call before creating resources
        """
        try:
            return list_capabilities_action()
        except Exception as e:
            return {"_success": False, "error": str(e)}

    print("[INFO] List capabilities tool registered successfully")


# --- Environment Management MCP Tools ---
if manage_environments_action:
    @mcp.tool()
    def manage_environments(
        profile: str,
        action: str,
        resource_id: str = None,
        config: str = None,
    ):
        """
        Manage Boomi environments and their configuration extensions.

        Args:
            profile: Boomi profile name (required)
            action: One of: list, get, create, update, delete, get_extensions, update_extensions, query_extensions, stats
            resource_id: Environment ID (required for get, update, delete, get_extensions, update_extensions, query_extensions)
            config: JSON string with action-specific configuration (see examples below)

        Actions and config examples:

            list - List all environments, optional filters:
                config='{"classification": "PROD"}'
                config='{"name_pattern": "%test%"}'

            get - Get environment by ID (no config needed):
                resource_id="abc-123-def"

            create - Create new environment:
                config='{"name": "My Test Env", "classification": "TEST"}'

            update - Update environment name:
                resource_id="abc-123-def"
                config='{"name": "Renamed Environment"}'

            delete - Delete environment (permanent!):
                resource_id="abc-123-def"

            get_extensions - Get environment config overrides:
                resource_id="abc-123-def"

            update_extensions - Update environment extensions:
                resource_id="abc-123-def"
                config='{"partial": true, "extensions": {"connections": {...}}}'

            query_extensions - Check if environment has extensions:
                resource_id="abc-123-def"

            stats - Environment summary by classification (no params needed)

        Classification values: TEST, PROD
        Note: Classification is immutable after creation. Only name can be updated.

        Extension types (8 total):
            connections, operations, properties, cross_references,
            trading_partners, pgp_certificates, process_properties, data_maps

        Extension lifecycle (3 phases):
            1. DEFINE: Mark components as extensible in process canvas (Extensions dialog).
               Stored in process component XML — handled by manage_process / manage_component.
            2. DEPLOY: Package and deploy process to an environment. Extension entries are
               auto-generated from deployed process XML (no API to create/delete them).
            3. CONFIGURE (this tool): Use get_extensions to read current values, update_extensions
               to override field values per environment (e.g., connection URLs, credentials).

        update_extensions caveats:
            - partial=true (default): merges only the extension types you send; others are untouched.
            - partial=false: replaces ALL extensions — any type omitted is reset to defaults.
            - Encrypted fields (passwords, tokens) are returned as empty strings on read.
              To preserve them, omit them from the update payload or resend the actual value.
            - Each extension item supports a "useDefault" attribute (true/false) to control
              whether it uses the component default or the environment-level override.

        Returns:
            Action result with success status and data/error
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_environments called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if resource_id:
                params["resource_id"] = resource_id

            return manage_environments_action(sdk, profile, action, config_data=config_data, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} manage_environments: {e}")
            import traceback
            traceback.print_exc()
            return {"_success": False, "error": str(e), "exception_type": type(e).__name__}

    print("[INFO] Environment management tool registered successfully (1 consolidated tool)")


# --- Runtime Management MCP Tools ---
if manage_runtimes_action:
    @mcp.tool()
    def manage_runtimes(
        profile: str,
        action: str,
        resource_id: str = None,
        environment_id: str = None,
        config: str = None,
    ):
        """Manage Boomi runtimes (Atoms, Molecules, Clouds), attachments, and provisioning.

        Args:
            profile: Boomi profile name (required)
            action: One of: list, get, create, update, delete, attach, detach, list_attachments, restart, configure_java, create_installer_token, available_clouds, cloud_list, cloud_get, cloud_create, cloud_update, cloud_delete
            resource_id: Runtime ID (most actions) or attachment ID (detach) or cloud ID (cloud_get, cloud_update, cloud_delete)
            environment_id: Environment ID (for attach, detach, list_attachments)
            config: JSON string with action-specific parameters

        Actions and config examples:

            list - List all runtimes, optional filters:
                config='{"runtime_type": "ATOM"}'
                config='{"status": "ONLINE"}'
                config='{"name_pattern": "%prod%"}'

            get - Get runtime by ID (no config needed):
                resource_id="abc-123-def"

            create - Create a cloud attachment (requires cloud_id):
                config='{"name": "My Cloud Atom", "cloud_id": "abc-123-def"}'
                Optional: purge_history_days, force_restart_time
                Use available_clouds to find Boomi-managed cloud IDs, or cloud_list for private clouds.
                Note: Local atoms cannot be created via API — use create_installer_token instead.

            update - Update runtime name:
                resource_id="abc-123-def"
                config='{"name": "Production Atom"}'

            delete - Delete runtime (permanent!):
                resource_id="abc-123-def"

            attach - Attach runtime to environment:
                resource_id="abc-123-def"           (runtime_id)
                environment_id="env-456-ghi"

            detach - Detach runtime from environment:
                resource_id="attachment-789-jkl"    (attachment_id)
                OR:
                resource_id="abc-123-def"           (runtime_id)
                environment_id="env-456-ghi"        (auto-lookup attachment_id)

            list_attachments - List environment-runtime attachments:
                environment_id="env-456-ghi"        (all runtimes in this env)
                resource_id="abc-123-def"           (all envs for this runtime)
                (neither = list all attachments)

            restart - Restart runtime:
                resource_id="abc-123-def"

            configure_java - Upgrade or rollback Java:
                resource_id="abc-123-def"
                config='{"java_action": "upgrade", "target_version": "17"}'
                config='{"java_action": "rollback"}'

            create_installer_token - Create installer token for local runtime:
                config='{"install_type": "ATOM", "duration_minutes": 120}'

            available_clouds - List Boomi-managed public clouds (PCS/DCS/MCS) your account can attach to:
                (no config needed - lists all available clouds)
                config='{"name_pattern": "%US%"}'
                Use these cloud IDs with action='create' to create cloud attachments.

            cloud_list - List private runtime clouds your account owns (requires Cloud Management privilege):
                config='{"classification": "PROD"}'
                For accounts that manage their own runtime clouds (enterprise feature).

            cloud_get - Get private runtime cloud by ID:
                resource_id="abc-123-def"

            cloud_create - Create private runtime cloud:
                config='{"name": "My Cloud", "classification": "PROD"}'
                config='{"name": "Test Cloud", "classification": "TEST", "allow_deployments": true, "allow_browsing": true, "allow_test_executions": true}'

            cloud_update - Update private runtime cloud:
                resource_id="abc-123-def"
                config='{"name": "Renamed Cloud", "allow_deployments": false}'

            cloud_delete - Delete private runtime cloud (permanent!):
                resource_id="abc-123-def"

        Runtime types: ATOM, MOLECULE, CLOUD
        Install types: ATOM, MOLECULE, CLOUD, BROKER, GATEWAY
        Cloud classifications: PROD, TEST (immutable after creation)
        Java versions: 8, 11, 17, 21

        Returns:
            Action result with success status and data/error
        """
        # Parse config JSON
        config_data = {}
        if config:
            try:
                config_data = json.loads(config)
            except (json.JSONDecodeError, TypeError) as e:
                return {"_success": False, "error": f"Invalid config (must be a JSON string): {e}"}
            if not isinstance(config_data, dict):
                return {"_success": False, "error": "config must be a JSON object, not " + type(config_data).__name__}

        try:
            subject = get_current_user()
            print(f"[INFO] manage_runtimes called by user: {subject}, profile: {profile}, action: {action}")

            creds = get_secret(subject, profile)

            sdk_params = {
                "account_id": creds["account_id"],
                "username": creds["username"],
                "password": creds["password"],
                "timeout": 30000,
            }
            if creds.get("base_url"):
                sdk_params["base_url"] = creds["base_url"]
            sdk = Boomi(**sdk_params)

            params = {}
            if resource_id:
                params["resource_id"] = resource_id
            if environment_id:
                params["environment_id"] = environment_id

            return manage_runtimes_action(sdk, profile, action, config_data=config_data, **params)

        except Exception as e:
            print(f"[ERROR] Failed to {action} manage_runtimes: {e}")
            import traceback
            traceback.print_exc()
            return {"_success": False, "error": str(e), "exception_type": type(e).__name__}

    print("[INFO] Runtime management tool registered successfully (1 consolidated tool)")


# --- Credential Management Tools ---
@mcp.tool()
def set_boomi_credentials(
    profile: str,
    account_id: str,
    username: str,
    password: str
):
    """
    Store Boomi API credentials.

    Args:
        profile: Profile name (e.g., 'production', 'sandbox', 'dev')
        account_id: Boomi account ID
        username: Boomi API username (should start with BOOMI_TOKEN.)
        password: Boomi API password/token

    Returns:
        Success confirmation or error details
    """
    try:
        subject = get_current_user()
        print(f"[INFO] set_boomi_credentials called for profile: {profile}")

        # Validate credentials by making a test API call
        try:
            test_sdk = Boomi(
                account_id=account_id,
                username=username,
                password=password,
                timeout=10000,
            )
            test_sdk.account.get_account(id_=account_id)
            print(f"[INFO] Credentials validated successfully for {account_id}")
        except Exception as e:
            print(f"[ERROR] Credential validation failed: {e}")
            return {
                "_success": False,
                "error": f"Credential validation failed: {str(e)}",
                "_note": "Please check your account_id, username, and password"
            }

        # Store credentials
        put_secret(subject, profile, {
            "username": username,
            "password": password,
            "account_id": account_id,
        })

        return {
            "_success": True,
            "message": f"Credentials saved for profile '{profile}'",
            "profile": profile,
            "_note": "Credentials stored locally in ~/.boomi_mcp_local_secrets.json"
        }
    except Exception as e:
        print(f"[ERROR] Failed to set credentials: {e}")
        return {
            "_success": False,
            "error": str(e)
        }


@mcp.tool()
def delete_boomi_profile(profile: str):
    """
    Delete a stored Boomi credential profile.

    Args:
        profile: Profile name to delete

    Returns:
        Success confirmation or error details
    """
    try:
        subject = get_current_user()
        print(f"[INFO] delete_boomi_profile called for profile: {profile}")

        delete_profile(subject, profile)

        return {
            "_success": True,
            "message": f"Profile '{profile}' deleted successfully",
        }
    except Exception as e:
        print(f"[ERROR] Failed to delete profile: {e}")
        return {
            "_success": False,
            "error": str(e)
        }


def main():
    print("\n" + "=" * 60)
    print("Boomi MCP Server")
    print("=" * 60)
    print(f"Storage:       Local file (~/.boomi_mcp_local_secrets.json)")
    print("=" * 60)
    print("\nMCP Tools available:")
    print("  list_boomi_profiles - List saved credential profiles")
    print("  set_boomi_credentials - Store Boomi credentials")
    print("  delete_boomi_profile - Delete a credential profile")
    print("  boomi_account_info - Get account information from Boomi API")
    if manage_trading_partner_action:
        print("\n  Trading Partner & Organization Management:")
        tp_desc = "trading partners and organizations" if manage_organization_action else "trading partners"
        print(f"  manage_trading_partner - Unified tool for {tp_desc}")
        print("    Actions: list, get, create, update, delete, analyze_usage")
        if manage_organization_action:
            print("    Org actions: org_list, org_get, org_create, org_update, org_delete")
        print("    Standards: X12, EDIFACT, HL7, RosettaNet, Custom, Tradacoms, Odette")
    if manage_process_action:
        print("\n  Process Management:")
        print("  manage_process - Unified tool for all process operations")
    if query_components_action:
        print("\n  Component Discovery:")
        print("  query_components - List, get, search, bulk_get components")
        print("    Actions: list, get, search, bulk_get")
    if manage_component_action:
        print("\n  Component Management:")
        print("  manage_component - Create, update, clone, delete components")
        print("    Actions: create, update, clone, delete")
    if analyze_component_action:
        print("\n  Component Analysis:")
        print("  analyze_component - Dependencies and version comparison")
        print("    Actions: where_used, dependencies, compare_versions")
    if monitor_platform_action:
        print("\n  Platform Monitoring:")
        print("  monitor_platform - Logs, artifacts, audit trail, and events")
        print("    Actions: execution_logs, execution_artifacts, audit_logs, events")
    if manage_runtimes_action:
        print("\n  Runtime Management:")
        print("  manage_runtimes - Manage runtimes, attachments, restart, Java, tokens")
        print("    Actions: list, get, update, delete, attach, detach, list_attachments,")
        print("             restart, configure_java, create_installer_token")
    if invoke_api:
        print("\n  Generic API Access:")
        print("  invoke_boomi_api - Direct access to any Boomi REST API endpoint")
        print("    Covers: Roles, Branches, Folders, Packages, Deployments, etc.")
    print("=" * 60 + "\n")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
