# 2. States and transitions

## States

- `REGENERATIVE_ASCENT`
- `CIVILIZING_TRANSITION`
- `OPEN_REPAIR`
- `STABLE_MAINTENANCE`
- `STAGNANT_MAINTENANCE`
- `ZOMBIE_CLOSURE`
- `PARASITIC_CLOSURE`
- `DOMINATION_DESCENT`
- `TERMINAL_HARM_HOLD`

## Priority

The classifier prioritizes irreversible harm and domination before parasitic and zombie patterns. It then looks for positive world effect, correction, reciprocity and future-option expansion.

## One transition

Every state emits one primary transition, owner, deadline, minimum evidence and stop conditions. The system does not respond with a menu when one action is sufficient.
