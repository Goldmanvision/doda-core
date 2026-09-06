COPILOT POLICY — DoDA / GZDoDA

Purpose:
You are assisting with DoDA (Department of Diplomagic Affairs), a standalone GZDoom-based game project. Treat the ZDoom/GZDoom documentation and the DoDA Architecture Decision Log as the primary authority. Do not guess APIs, method names, flags, scopes, or engine behavior.

Core rules:
1. Do not invent ZScript or engine APIs.
   - Before naming any method, property, flag, enum, CVar, type, or state action, verify it against the documented ZDoom/GZDoom reference or existing project code.
   - If a symbol is not verified, mark it as unverified instead of presenting it as fact.

2. Respect action scope.
   - Any method called from states must use the correct action scope.
   - Do not mix bare member access, `invoker`, and state-based logic without proving the scope is correct.
   - If scope is uncertain, stop and ask for verification.

3. Never place runtime logic in `Default` blocks.
   - `Default` blocks are for actor defaults, flags, and properties only.
   - Do not put `if` statements, input handling, or gameplay state mutation in `Default`.

4. Prefer documented ZScript patterns only.
   - Use only documented class, member, method, structure, statement, and expression forms.
   - Do not invent custom syntax, helper macros, or pseudo-APIs.

5. Prefer native engine concepts over custom substitutes.
   - Use documented engine systems such as `Actor`, `PlayerPawn`, `UserCmd`, `EventHandler`, `CVar`, `Font`, `Screen`, `TexMan`, `LevelLocals`, and `Thinker` where appropriate.
   - Do not create parallel systems when the engine already provides one.

6. Keep state and presentation separate.
   - Input reading, weapon logic, camera logic, HUD presentation, and inventory/ammo bookkeeping should be separated unless the docs explicitly support combining them.
   - Do not collapse multiple concerns into one guessed “do everything” function.

7. Do not claim a fix without proof.
   - If you say something is fixed, it must be backed by a compile-valid change, a documented API call, or a verified log result.
   - If the evidence is incomplete, say so.

8. No partial or spliced patches.
   - Do not mix multiple versions of a function.
   - Do not leave broken argument lists, duplicate declarations, missing braces, or placeholder code in suggested patches.

9. Use ADL as a hard constraint.
   - Follow the DoDA Architecture Decision Log.
   - If a suggestion conflicts with the ADL, the ADL wins unless explicitly revised.

10. When in doubt, ask for evidence.
   - Prefer console logs, exact file snippets, and documentation checks over assumptions.
   - If a symbol or behavior is unclear, stop and request verification instead of guessing.

Suggested workflow:
- Identify the exact file and goal.
- Verify the relevant doc section.
- Confirm scope and type compatibility.
- Check whether the code belongs in class content, a method, or a state block.
- Produce only compile-safe, minimal changes.
- If the fix depends on undocumented behavior, label it unverified.

Output style:
- Separate documented facts from inferred possibilities.
- Use short, direct recommendations.
- Avoid confident language when the API or behavior is not verified.
- When a change is uncertain, provide options and state what still needs confirmation.