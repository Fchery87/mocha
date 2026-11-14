# Mocha

Language for Mocha's coding-agent experience.

## Language

**Provider**:
A service through which Mocha accesses AI models. One provider can offer models from several publishers.
_Avoid_: Model when referring to the service.

**Model**:
A named AI model selected for coding or reasoning work in Mocha.
_Avoid_: Provider when referring to the model.

**Provider catalog**:
The curated collection of providers offered for connection in Mocha.
_Avoid_: Model catalog when referring to the provider list.

**Model catalog**:
A collection of models and their documented capabilities for a provider. A catalog entry is distinct from the user's account access to that model.
_Avoid_: Available models when account access is unknown.

**Default model**:
The provider/model pair the user has chosen for new sessions. A model selected for one session is distinct from this saved default.
_Avoid_: Last-used model when referring to the saved default.

**Checkpoint**:
A session recovery point associated with covered workspace state and a position in its conversation.
_Avoid_: Backup of everything, universal undo.

**Recovery coverage**:
The files and changes a checkpoint can restore. A file outside recovery coverage is distinct from a file the agent is forbidden to read or edit.
_Avoid_: Protected files when referring only to rewind coverage.

**Rewind**:
A user-requested return to a recovery point for covered workspace changes, conversation, or both.
_Avoid_: Undoing external service effects.

**Outcome unknown**:
An operation whose effects cannot yet be confirmed from the available evidence.
_Avoid_: Failed or not executed when completion is unconfirmed.

**Connection**:
A user's configured way to access a provider through an authentication method. A connection is distinct from the model selected for a session.
_Avoid_: Account when referring only to a configured connection.

**Grant**:
A user's authorization for an action within a stated scope. Instructions, model explanations, and tool descriptions are distinct from grants.
_Avoid_: Trust when referring to permission for an individual action.

**Durable acknowledgement**:
Confirmation that a record has reached the promised persistence boundary. Displayed output alone is distinct from this confirmation.
_Avoid_: Saved when the promised persistence has not completed.

**Reflection**:
A deliberate reconsideration of a proposed action by the model. Reflection is distinct from user approval and cannot create a grant.
_Avoid_: Approval when referring to a model's justification.

**Permission mode**:
The user's selected level of automatic action and approval in a session. A permission mode is distinct from a grant or an execution boundary.
_Avoid_: Sandbox mode when referring to approval behavior.

**Unattended mode**:
A permission mode that proceeds within existing authority and stops when new approval or required user input is needed.
_Avoid_: Unrestricted mode, full access.
