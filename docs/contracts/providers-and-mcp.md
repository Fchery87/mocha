# Providers and MCP contract

Specification dated November 14, 2026. Scope is settled; adapter compatibility, account access, and live inference remain verification work. [Research and source inventory](../research/2026-11-14-mocha-market-and-build-readiness.md) distinguish observed documentation from tested behavior.

## Connections and model selection

M1 ships these 12 built-in providers plus Custom. The table chooses adapter profiles, not a market ranking or a claim that every offered model supports coding tools. Presets use HTTPS. Review exact routes, auth headers, rate limits, and a coding-capable model against owner documentation when capturing adapter fixtures, before claiming support.

| Provider | M1 adapter | API-key environment reference | Owner reference |
| --- | --- | --- | --- |
| OpenAI | Responses; Chat Completions for compatible configured models | OPENAI_API_KEY | [API](https://platform.openai.com/docs/api-reference) |
| Anthropic | Messages | ANTHROPIC_API_KEY | [Messages](https://docs.anthropic.com/en/api/messages) |
| Google Gemini | Native Gemini | GEMINI_API_KEY | [API](https://aistudio.google.com/docs) |
| OpenRouter | Chat Completions | OPENROUTER_API_KEY | [API](https://openrouter.ai/docs/api-reference/overview) |
| DeepSeek | Chat Completions with DeepSeek reasoning profile | DEEPSEEK_API_KEY | [API](https://api-docs.deepseek.com/) |
| Z.ai standard API | Chat Completions, standard endpoint | ZAI_API_KEY | [Standard API](https://docs.z.ai/api-reference/introduction) |
| xAI | Responses, configured Chat compatibility | XAI_API_KEY | [API](https://docs.x.ai/docs/api-reference) |
| Mistral | Chat Completions with Mistral tool profile | MISTRAL_API_KEY | [API](https://docs.mistral.ai/api/) |
| Groq | Chat Completions | GROQ_API_KEY | [API](https://console.groq.com/docs/openai) |
| Together AI | Chat Completions | TOGETHER_API_KEY | [API](https://docs.together.ai/docs/openai-api-compatibility) |
| Fireworks AI | Chat Completions | FIREWORKS_API_KEY | [API](https://docs.fireworks.ai/tools-sdks/openai-compatibility) |
| Cerebras | Chat Completions | CEREBRAS_API_KEY | [API](https://inference-docs.cerebras.ai/) |
| Custom | Explicitly chosen supported family | User-named variable or keychain binding | User-supplied endpoint documentation |

Setup chooses provider → environment reference or protected key entry → explicit coding model → optional saved default. No paid inference occurs during catalog refresh. One saved connection per built-in provider/auth method is supported. Replace and logout are explicit. OpenAI API-key and ChatGPT sign-in are separate connections. Named Custom profiles support distinct endpoints. Multiple saved accounts per built-in method and automatic key rotation are deferred.

Metadata comes from a reviewed, bundled models.dev snapshot. Pin its upstream revision, payload hash, extraction schema, observation date, and retained MIT notice in the application release. Import only needed metadata, not upstream executable code. The research inventory is not the bundled runtime snapshot. Authenticated discovery runs where supported on connection or explicit refresh. Preserve last good data and user overrides. Distinguish catalog-listed, connected, account-discovered, fixture-verified, and live-tested states. No silent model/default changes or cross-provider fallback.

The schema is [models.schema.json](models.schema.json). The [sanitized legacy fixture](fixtures/models.legacy.sanitized.json) preserves four provider shapes and 61 model entries, including per-model API overrides and missing limits. It contains synthetic identities and invalid example endpoints. It is format evidence, not an availability test. Effective API is model override, else provider default. Missing both is invalid. Limits missing from both user data and dated catalog require input, not guessed capacity.

Unknown metadata fields warn once. Unknown API selectors, wrong known-field types, embedded credentials, or unsafe endpoint/auth fields fail validation. The loader retains extension metadata but never lets it grant permissions. `authHeader` is a legacy boolean controlling the selected adapter's header behavior, never an arbitrary header or credential value. `keyEnv` names a variable only. Separate user-owned credential bindings are not project configuration. Disallow URL userinfo and query-carried credentials. HTTPS is required except explicitly approved Custom loopback HTTP. Endpoint changes require reconnection approval before attaching credentials. Never forward credentials across redirects to another origin.

Configuration precedence is CLI/session selection → explicit user overrides → trusted project presentation/model selection → user defaults → bundled defaults. Project data cannot redefine provider endpoints, credentials, or elevate grants. Invalid updates retain the last valid saved configuration and report file/line/problem. Setup writes deliberately; startup stays read-only.

## Adapter behavior

The shared IR includes text, image references, tool calls/results, usage, and opaque adapter-owned reasoning/signatures. Preserve complete exchanges. Never dispatch partial tool arguments or forward foreign opaque state. Each profile has fixtures for text streaming, tools, fragmented arguments, reasoning, image capability, usage, cancellation, malformed streams, throttling, and unsupported fields. Unsupported model capabilities produce an explicit error before dispatch.

Native Gemini uses the current Interactions API with streaming, `store:false`, and full local history. No previous_interaction_id or hosted orchestration is required. This keeps conversation state in Mocha while following Google's recommended new-development interface. Pin the exact request/event profile and test tool/image/stateless exchanges in the adapter spike. See [migration guidance](https://aistudio.google.com/docs/migrate-to-interactions) and [GA announcement](https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/). The supported generateContent API is not an additional MVP adapter promise.

Retry at most three attempts for a pre-output transient transport failure or rate limit, honoring Retry-After up to 60 seconds within the turn deadline. Do not auto-retry after semantic output, dispatched effects, or an uncertain outcome. No automatic paid-model fallback. Provider storage controls are applied only where documented; no promise that `store:false` eliminates provider-side operational retention.

## Native ChatGPT sign-in

M2 requires the documented [open-source SIWC profile](https://developers.openai.com/siwc/token-sharing-open-source/sign-in). Prove registration, eligible access, one successful tool-capable inference, serialized refresh, logout, and revocation early. BYOK stays independent. Failure blocks M2 unless the maintainer explicitly changes scope.

Use the issued client registration and stable opaque host identity. Validate PKCE, state, nonce, identity, and granted inference permission. Use the public Responses endpoint and account-specific model list, not another client's registration or backend-api routes. Bind the callback only to 127.0.0.1 during explicit login. Browser/callback cancellation and headless absence of an interactive flow fail clearly. Secret Service failure never enables plaintext token storage.

This profile requires `store:false`, `stream:true`, and full local input history. Do not serialize unsupported ordinary BYOK fields, including HTTP previous_response_id, max_output_tokens, and temperature. Apply documented function/custom-tool namespaces. Hosted MCP and tool_search are outside this profile. Only response.completed is success; an error after streaming remains failure. See [inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference) and [limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations). Logout distinguishes local deletion from confirmed remote revocation.

## MCP profile

M2 supports tools only over stdio and Streamable HTTP, with explicit profiles for 2026-07-28 and 2025-11-25. No legacy HTTP+SSE promise, resources, prompts, sampling, or elicitation. Unsupported input-required requests return typed unsupported outcomes. Advertise only implemented capabilities.

The newer profile uses its documented stateless discovery/request rules. The older profile uses initialize negotiation. SDK support must be proven with separate version/transport fixtures. Discovery paginates with a 100-page/10,000-tool ceiling and 1 MiB per-schema limit. Exceeding limits fails discovery visibly. Cache for five minutes or the server's shorter lifetime, keyed by server identity, revision, endpoint, account profile, and schema hash. Tool changes invalidate affected cached definitions and grants. Keep deferred schemas outside the prompt until needed.

Remote credentials bind to the intended resource and origin, with no automatic cross-origin forwarding. Local servers require containment and project trust. Disconnect, authorization failure, and changed schema are visible. Transport reconnection cannot repeat an uncertain effect. Tool descriptions and read-only hints do not grant authority. Unknown effects require approval.


## Bounded input and provider IO

Before the first real inference in 003/004, resolve context/output limits, serialize a compatible model view without foreign opaque signatures, and reject a view that cannot fit. Rich compaction remains 007. Do not advertise tools before 005 can execute them. An unexpected provider tool request on an earlier text-only path ends with unsupported_tool_execution, preserves the exchange and causes no dispatch.

Initial configurable timeouts are 10 seconds to connect, 120 seconds to the first valid response event, and 120 seconds without valid stream activity. The turn deadline still bounds the whole operation. Valid documented heartbeat events can indicate transport liveness; they do not establish task completion. These timers are distinct from the 30-second blocked-client delivery timer. Report provider_timeout with the expired phase and do not auto-repeat semantic output/effects.

A parsed stream event is at most 4 MiB; a completed tool argument object is at most 1 MiB; a user config/model file is at most 4 MiB. Bound parsing before allocation and reject oversized/invalid input with input_too_large or stream_limit, not a partial dispatch. Explicit catalog refresh downloads at most 20 MiB before validated extraction; oversize failure preserves last-good data. These resource limits are configurable engineering defaults, not cumulative token caps.

## Remote MCP authentication

The maintainer confirmed browser OAuth plus static bearer credentials for the MVP on November 14, 2026. This is separate from provider API keys and ChatGPT sign-in. Authentication proves access to a server/resource; it does not grant permission to execute a tool.

Static profiles use a user-selected environment reference or protected keychain item bound to the exact canonical HTTPS MCP resource. OAuth profiles implement the authorization-code flow with S256 PKCE, state/issuer/redirect validation, protected-resource metadata discovery, OAuth authorization-server metadata and supported OIDC discovery. Verify advertised PKCE support before proceeding. OAuth authorization-server endpoints require HTTPS. Bind resource indicators, requested scopes, tokens and registrations to the selected resource/issuer/profile. Do not pass another provider/resource's token through a server or cross-origin redirect.

Select pre-registered client information first when explicitly configured for that issuer. Otherwise use a Client ID Metadata Document when the authorization server advertises support. Use Dynamic Client Registration only as the advertised compatibility fallback, with native application type. DCR is not a reason to weaken redirect/PKCE checks. If none works, return client_registration_required with a path for explicit pre-registration rather than borrow another client's identity. See [current registration](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) and [security requirements](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations). Earlier revision behavior is tested independently against its [authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).

The selected public client ID is `https://fchery87.github.io/mocha/oauth-client.json`. Its [metadata document](../oauth-client.json) declares the exact callback `http://127.0.0.1:8732/oauth/mcp/callback`. Bind only 127.0.0.1 during explicit login and expire the flow after five minutes or cancellation. A busy port produces callback_unavailable; do not silently substitute an unregistered redirect. The publishing plan is GitHub Pages serving the repository docs directory at the project path. The published URL must directly return HTTP 200 with application/json, the reviewed JSON and matching client_id, without redirects, before CIMD support passes. Enabling/configuring Pages and verifying the remote response are explicit SLICE-014 tasks, not assumed current repository settings. Server domain-trust policies can still reject that client ID; explicit pre-registration remains supported. Preparing this file is not deployment or evidence that the remote URL already serves it.

Planned host commands are `mocha mcp login <server>`, `mocha mcp logout <server>` and `mocha mcp auth status <server>`. The TUI uses the same host service. A login preview identifies issuer, resource, requested scopes and registration method before browser consent. A changed issuer/resource/scope needs reevaluation. Discovered URLs are untrusted: reject userinfo, unsafe redirects, link-local/metadata-service destinations and unauthorized private/loopback destinations. Revalidate destinations on redirects/DNS resolution; only an explicit user-owned server profile may allow a private deployment. Loopback callback access is a separate fixed exception.

Store credentials only in the protected per-resource/issuer/profile bundle, with the shared-state generation/refresh/logout locking contract. Refresh capability is optional: absence of a refresh token requires future explicit sign-in rather than fabricated refresh support. Serialize rotation and stop on uncertain persistence of a replacement token. Logout deletes local protected credentials, invalidates in-flight generations and attempts supported remote revocation; distinguish unavailable/failed remote revocation from local deletion.

Headless and Unattended runs may use current credentials and a bounded safe refresh. If fresh browser consent/scope expansion is required, stop with approval_required and headless exit 3, without launching a browser or waiting. An explicit browserless login command returns input_required and exit 2. Rejected/invalid credentials or failed refresh remain authentication failures with exit 5. At most one explicit reauthorization attempt per operation prevents consent loops. A new token never authorizes replay of an uncertain remote mutation. Only a request known not to have executed, such as a pre-execution authentication rejection, may be safely retried within the normal limits.

Required evidence includes static auth, CIMD, pre-registration and DCR fixtures; both MCP revisions; wrong/missing state and PKCE rejection; issuer/resource changes; redirect/SSRF attempts; missing refresh tokens; refresh/save/logout races; failed revocation; browser timeout; headless refusal; and a tool-policy denial after successful OAuth. Selected SDK auth support must be demonstrated; no capability follows from a version constant alone.


The current [CIMD draft 03](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-03) is a work in progress. Mocha's public-client metadata advertises token_endpoint_auth_methods_supported=[none], with a consistent legacy token_endpoint_auth_method=none for older-server interoperability. It contains no shared secret/private key. Test the supported server profiles independently and reject unsupported client authentication rather than fabricate credentials. Registration/publication verification includes response status, MIME type, identity equality and redirect absence.
