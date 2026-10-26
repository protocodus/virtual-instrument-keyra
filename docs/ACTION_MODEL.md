# Reduced action and contact candidate

`physics::Action` is a separate mechanical research module. It is not part of
the default recording-calibrated live renderer and is not a measured recreation
of a manufacturer's action. All quantities use metres, seconds, kilograms and
newtons. The effective masses, travel, lever ratio, springs and contact losses
are authored starting values. Wool composition or key-wood density alone cannot
identify a hammer's nonlinear stiffness or a finger's contact/friction law.

## Finger, key and bed

MIDI press/release controls a bounded, finite-speed **kinematic finger proxy**.
An explicit finger target API also permits isolated experiments. A unilateral
finger/key spring with non-adhesive viscous loss pushes an effective key mass.
The key has a return spring, damping and a separate unilateral keybed cushion.
Their implicit discrete-gradient step accounts for finger work and each loss.
No MIDI event teleports the key or resets vibrating mechanical state.

When the ideal jack is engaged, hammer travel is `r * key travel` and its
reciprocal reflected inertia is `m_key + r² m_hammer`. The hammer return potential
and damping are reflected by the same ratio. Thus key and hammer do not receive
independent one-way launch forces. Escapement preserves hammer position and
velocity and disconnects the ideal jack before impact. This simplified jack is
not a multi-link grand/upright action or a measured escapement-friction model.

## Hammer/string contact and release

The free hammer follows an exact harmonic return oscillator with positive
velocity damping. The mechanical string network supplies its previous/free
contact displacements and exact constant-force compliance. Both systems then
solve one scalar non-adhesive nonlinear contact:

```text
Phi(delta) = K max(delta,0)^(p+1)/(p+1)
F = [Phi(delta_new)-Phi(delta_old)]/(delta_new-delta_old)
    * max(0,1+alpha*(delta_new-delta_old)/dt)
delta_new = delta_free - (C_hammer + C_string) F
```

The conservative force's work cancels the contact-potential change. Positive
Hunt-Crossley loss dissipates energy, including its non-adhesive clipped branch.
The bracket is bounded because the force target decreases as force increases;
the solver has a finite iteration limit and exposes its residual. At nearly
equal compression it uses the analytic derivative limit to avoid cancellation.
The string force must be applied **once** through the network's compatible
constant-force response. An arbitrary impulse or a pressure-scaled audio sample
does not satisfy this work identity.

A passive backcheck captures a returning hammer while the key remains down.
Key release withdraws the finger, releases the backcheck and allows the hammer
and key to return. Rest stops remove residual mechanical energy; they do not
restore a fresh strike's momentum. The prototype does not yet include individual
felt relaxation memory, detailed jack repetition/escapement geometry or action
noise radiation. Stulov's hereditary felt model is a different, unimplemented
constitutive law ([1995](https://doi.org/10.1121/1.411912)).

## Isolation and connection

The offline configuration can independently disable finger contact, the bed,
jack drive, hammer/string contact and backcheck. Diagnostics expose finger,
keybed and hammer forces; key travel/velocity; hammer travel/velocity; jack state;
and driven, escaped, contact, returning, backchecked and rest stages. The energy
ledger separates finger work, key/hammer viscous loss, finger loss, bed loss,
backcheck/rest-stop loss and nonlinear contact loss. `active(note)` permits
skipping idle keys and contact probes. Configuration resets state and must not be
used as an unaccounted live material switch.

One frame is `Action::beginFrame()`, mechanical-network free step, per-active-key
`solveStringContact()` followed by the matching network force application, then
`Action::endFrame()` and the network's bridge/observation step. The nonlinear
contact may be tested alone with two masses or a harmonic string port; the
action may be tested against a rigid string. The integrated instrument must also
include contact potential in its whole-system energy bookkeeping while the felt
is compressed.

The action tests check conservative and dissipative two-mass impact at six
sample rates, harmonic-port force work, a complete press/bed/strike/backcheck/
release/rest cycle with an independent energy ledger, component ablations,
malformed inputs, state-preserving repeated presses and C++ allocation traps.
They do not establish perceptual realism, Reason acceptance or finger/action
agreement with recordings. In particular, driving a finger before impact creates
physical action latency; an ordinary MIDI note-on convention usually denotes
the intended audible strike. No DAW latency or compensation policy is claimed.
