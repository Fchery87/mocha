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
