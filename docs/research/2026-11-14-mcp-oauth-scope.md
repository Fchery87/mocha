# Remote MCP OAuth scope

Observed November 14, 2026. The final slice audit identified unnamed remote MCP authentication methods. The maintainer explicitly selected browser OAuth plus static keys for the MVP. This is not inferred from ChatGPT sign-in.

Both supported MCP revisions make authorization optional overall, while HTTP implementations supporting it use the documented OAuth profile and stdio uses environment credentials. Static-only support therefore cannot establish compatibility with OAuth-protected hosted services. See [2026 authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) and [2025 authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).

Current [registration guidance](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) orders pre-registration, advertised Client ID Metadata Documents, and advertised DCR fallback. DCR is deprecated compatibility behavior. [Security requirements](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations) require resource binding and secure PKCE/communication. These are version-pinned primary specifications; selected SDK conformance and live account/server compatibility remain unproved.

The [implementation contract](../contracts/providers-and-mcp.md#remote-mcp-authentication) supplies the chosen metadata URL, exact callback, authentication lifecycle, headless behavior and verification gates. No hosting, registration, login or paid request was performed during this documentation review.


A final check against [CIMD draft 03, dated November 2, 2026](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-03) supplies the current metadata/authentication/discovery details. It remains an Internet-Draft. The implementation plan chooses the repository's GitHub Pages HTTPS project endpoint for a directly served JSON document and requires HTTP 200, matching client_id, JSON MIME type and no redirect before acceptance. The metadata advertises a public client with a consistent older-server hint, never a shared secret. No Pages settings or deployment were changed during this review.
