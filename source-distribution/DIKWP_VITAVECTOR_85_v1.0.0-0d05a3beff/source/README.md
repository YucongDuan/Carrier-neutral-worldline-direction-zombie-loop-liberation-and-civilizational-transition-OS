# DIKWP VITAVECTOR-85

**Carrier-neutral worldline direction, zombie-loop liberation and civilizational transition OS.**

> Do not define who is human. Diagnose the direction of a worldline.

VITAVECTOR-85 does not classify a carrier as human, non-human, partial human, good, evil, civilized or uncivilized. It evaluates a bounded worldline window: sources, differences, decisions, affected worlds, actions, observed effects, corrections and successor options.

A complete D/I/K/W/P loop (`11111`) is necessary for semantic continuity, but it is not sufficient for vitality. A loop may be locally complete yet globally stagnant, extractive, domination-producing or closed to reality. VITAVECTOR-85 separates semantic closure from generative direction.

## Core outputs

- `REGENERATIVE_ASCENT`
- `CIVILIZING_TRANSITION`
- `OPEN_REPAIR`
- `STABLE_MAINTENANCE`
- `STAGNANT_MAINTENANCE`
- `ZOMBIE_CLOSURE`
- `PARASITIC_CLOSURE`
- `DOMINATION_DESCENT`
- `TERMINAL_HARM_HOLD`

These states apply only to the declared time/context window. They are never permanent essence labels.

## Run

Requires Python 3.10+; the reference runtime uses only the Python standard library, SQLite and vanilla JavaScript.

```bash
python start_showcase.py
```

Open `http://127.0.0.1:8781`.

CLI:

```bash
python run.py summary
python run.py compile examples/zombie_loop.json --out outputs/zombie.worldline.json
python run.py intervene outputs/zombie.worldline.json examples/zombie_intervention.json --out outputs/zombie.intervened.json
python run.py outcome outputs/zombie.intervened.json examples/zombie_outcome.json --out outputs/zombie.closed.json
python run.py successor outputs/zombie.closed.json --out outputs/zombie.successor.json
python run.py selftest
make qa
```

## Non-negotiable boundary

The system provides no `humanity_score`, personhood rank, intrinsic worth score, social credit or permanent moral label. Basic protections, contestability, appeal and freedom from irreversible harm are never gated by a direction state.

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
