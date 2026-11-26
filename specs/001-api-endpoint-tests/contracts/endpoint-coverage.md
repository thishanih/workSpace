# Endpoint Coverage Contract

All paths start with `/api`. The scenarios below map each application endpoint
to concrete tests. For every protected endpoint, the authentication-matrix
test is parameterized for missing and invalid credentials and verifies that
collection state is unchanged.

| Method and path | Successful scenario | Negative, credential, and ownership scenarios |
|-----------------|---------------------|-----------------------------------------------|
| GET `/health` | `tests/integration/test_health.py::test_health_check_returns_ok` | Public; credentials, validation, and ownership do not apply |
| POST `/auth/register` | `tests/integration/test_auth_endpoints.py::test_register_returns_user_and_token_pair` | `tests/integration/test_auth_errors.py::test_registration_rejects_invalid_account_fields`; `tests/integration/test_api.py::test_registration_rejects_duplicate_email`; public |
| POST `/auth/login` | `tests/integration/test_auth_endpoints.py::test_login_returns_user_and_token_pair` | `tests/integration/test_auth_errors.py::test_login_rejects_invalid_credentials`; public |
| POST `/auth/refresh` | `tests/integration/test_api.py::test_refresh_rotates_tokens_and_rejects_reuse` | `tests/integration/test_auth_errors.py::test_refresh_rejects_invalid_refresh_token`, `test_refresh_rejects_expired_token`, `test_refresh_rejects_access_purpose_token`; public route, refresh credential required in body |
| GET `/users/me` | `tests/integration/test_user_endpoints.py::test_user_profile_can_be_read_and_updated` | Auth matrix `GET-users-me`; `tests/integration/test_authentication_matrix.py::test_protected_endpoint_requires_valid_access_token`, `test_protected_endpoint_rejects_expired_access_token`; `tests/integration/test_user_errors.py::test_profile_is_scoped_to_authenticated_user` |
| PATCH `/users/me` | `tests/integration/test_user_endpoints.py::test_user_profile_can_be_read_and_updated` | Auth matrix `PATCH-users-me`; `tests/integration/test_user_errors.py::test_profile_update_rejects_invalid_name`, `test_profile_is_scoped_to_authenticated_user` |
| GET `/todos` | `tests/integration/test_todo_endpoints.py::test_todo_can_be_created_listed_read_updated_and_deleted` | Auth matrix `GET-todos`; `tests/integration/test_pagination.py::test_list_endpoints_support_empty_results_and_page_boundaries`, `test_todo_comment_and_activity_lists_reject_invalid_pagination`; `tests/integration/test_todo_errors.py::test_other_user_cannot_read_update_or_delete_todo` |
| POST `/todos` | `tests/integration/test_todo_endpoints.py::test_todo_can_be_created_listed_read_updated_and_deleted` | Auth matrix `POST-todos`; `tests/integration/test_todo_errors.py::test_todo_creation_rejects_invalid_fields`; `test_other_user_cannot_read_update_or_delete_todo` verifies ownership of resulting resource |
| GET `/todos/{todo_id}` | `tests/integration/test_todo_endpoints.py::test_todo_can_be_created_listed_read_updated_and_deleted` | Auth matrix `GET-todo`; `tests/integration/test_todo_errors.py::test_todo_operations_reject_missing_resource`, `test_other_user_cannot_read_update_or_delete_todo` |
| PATCH `/todos/{todo_id}` | `tests/integration/test_todo_endpoints.py::test_todo_can_be_created_listed_read_updated_and_deleted` | Auth matrix `PATCH-todo`; `tests/integration/test_todo_errors.py::test_todo_update_rejects_invalid_fields_without_mutation`, `test_todo_operations_reject_missing_resource`, `test_other_user_cannot_read_update_or_delete_todo` |
| DELETE `/todos/{todo_id}` | `tests/integration/test_todo_endpoints.py::test_todo_can_be_created_listed_read_updated_and_deleted` | Auth matrix `DELETE-todo`; `tests/integration/test_todo_errors.py::test_todo_operations_reject_missing_resource`, `test_other_user_cannot_read_update_or_delete_todo`; comment cascade: `tests/integration/test_comment_endpoints.py::test_deleting_todo_removes_its_comments` |
| GET `/todos/{todo_id}/comments` | `tests/integration/test_comment_endpoints.py::test_comment_can_be_created_listed_updated_and_deleted` | Auth matrix `GET-comments`; `tests/integration/test_comment_errors.py::test_comment_operations_reject_missing_resources`, `test_other_user_cannot_access_todo_comments`; pagination tests |
| POST `/todos/{todo_id}/comments` | `tests/integration/test_comment_endpoints.py::test_comment_can_be_created_listed_updated_and_deleted` | Auth matrix `POST-comment`; `tests/integration/test_comment_errors.py::test_comment_creation_rejects_invalid_body`, `test_comment_operations_reject_missing_resources`, `test_other_user_cannot_access_todo_comments` |
| PATCH `/todos/{todo_id}/comments/{comment_id}` | `tests/integration/test_comment_endpoints.py::test_comment_can_be_created_listed_updated_and_deleted` | Auth matrix `PATCH-comment`; `tests/integration/test_comment_errors.py::test_comment_update_rejects_invalid_body_without_mutation`, `test_comment_mutations_reject_missing_comment`, `test_other_user_cannot_access_todo_comments` |
| DELETE `/todos/{todo_id}/comments/{comment_id}` | `tests/integration/test_comment_endpoints.py::test_comment_can_be_created_listed_updated_and_deleted` | Auth matrix `DELETE-comment`; `tests/integration/test_comment_errors.py::test_comment_mutations_reject_missing_comment`, `test_other_user_cannot_access_todo_comments` |
| GET `/activities` | `tests/integration/test_activity_endpoints.py::test_activities_can_be_listed_filtered_and_read` | Auth matrix `GET-activities`; `tests/integration/test_activity_errors.py::test_activity_list_and_read_are_scoped_to_owner`, `test_activity_filter_rejects_invalid_or_missing_todo`; pagination tests |
| GET `/activities/{activity_id}` | `tests/integration/test_activity_endpoints.py::test_activities_can_be_listed_filtered_and_read` | Auth matrix `GET-activity`; `tests/integration/test_activity_errors.py::test_activity_read_rejects_missing_resource`, `test_activity_list_and_read_are_scoped_to_owner` |

Auth matrix test identifier prefix:
`tests/integration/test_authentication_matrix.py::test_protected_endpoint_rejects_missing_or_invalid_credentials`
with the credential parameter ID first and endpoint parameter ID second
(for example, `[missing-bearer-GET-users-me]` or
`[invalid-bearer-GET-users-me]`).

The suite uses isolated in-memory test data. It does not claim to verify real
MongoDB TTL timing, database concurrency, or performance behavior.
