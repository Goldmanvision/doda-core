# Consolidated Wiki Audit

---
## File: wiki/b92_pistols.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - B92 Pistols</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="b92_pistols.html">B92 Pistols</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>B92 Pistols</h2>
        <p>The B92 pistols are gameplay-distinct weapons, not mirrored art. Each instance retains independent magazine and chamber state.</p>

        <h3>Ownership</h3>
        <ul>
            <li><code>DoDAB92Left</code> and <code>DoDAB92Right</code> inherit from <code>DoDAPistol</code>.</li>
            <li>Magazine and chamber state are independent for each hand.</li>
            <li><code>Clip</code> is the shared loose-reserve pool.</li>
        </ul>

        <h3>Reload Logic</h3>
        <ul>
            <li>Reload is controlled by <code>DoDAWeapon.RequestLowestLoadedPistolReload()</code>.</li>
            <li>Reloading must not be manually triggered in the weapon class to avoid bypassing the selection logic.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/character_classes.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Character Classes</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Character Classes</h2>
        <p>The player character classes manage character attributes, starting inventory, and special ability state, such as Deadzone Aim.</p>

        <h3>Active Files</h3>
        <ul>
            <li><code>DoDA/CharacterClasses/FieldAgent.zs</code></li>
            <li><code>DoDA/CharacterClasses/Analyst.zs</code></li>
            <li><code>DoDA/CharacterClasses/SAC.zs</code></li>
        </ul>

        <h3>FieldAgent (FieldAgent.zs)</h3>
        <p>The active deadzone authority for the current MAPINFO player class. Manages Deadzone Aim state, lean offsets, and starting inventory.</p>
        <ul>
            <li><code>DeadzoneAimActive</code>: State tracking for Deadzone Aim mode.</li>
            <li><code>ReticleYawOffset</code>, <code>ReticlePitchOffset</code>: Angular gaps between aim and reticle.</li>
            <li><code>LeanOffset</code>: Lateral lean camera translation offset.</li>
            <li><code>ResetDeadzoneAim()</code>: Resets all deadzone aim state and raw mouse CVars.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/deadzone_aim.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Deadzone Aim</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Deadzone Aim</h2>
        <p>Deadzone Aim is owned by <code>FieldAgent</code>, not weapons.</p>
        
        <h3>Aim Contract</h3>
        <ul>
            <li><code>GetDeadzoneYawGap()</code> and <code>GetDeadzonePitchGap()</code> are the fire-trace offset contract.</li>
            <li>Yaw convention: Negative yaw moves the reticle right on screen.</li>
            <li>Pitch convention: Positive pitch moves it down (matches active deadzone HUD implementation).</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/debugging_playbook.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Debugging Playbook</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="b92_pistols.html">B92 Pistols</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Debugging Playbook</h2>
        <p>This playbook outlines procedures for investigating common DoDA issues.</p>
        
        <h3>Common Issues</h3>
        <ul>
            <li><strong>Compile Failures</strong>: Check <code>console_log.txt</code> for script parsing errors. Ensure <code>zscript.txt</code> includes are in the correct order.</li>
            <li><strong>Weapon Issues</strong>: Verify independent magazine/chamber state for B92 pistols. Check shotgun rack state machine.</li>
            <li><strong>Aim Issues</strong>: Verify <code>FieldAgent</code> owns deadzone state and is not being overridden by weapon code.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/hud_weapon.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - HUD Weapon Readout</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>HUD Weapon Readout</h2>
        <p>The HUD displays weapon state. It is strictly read-only and must not own or mutate weapon gameplay state.</p>

        <h3>Readout Contract</h3>
        <h4>B92 Pistols</h4>
        <pre>
LEFT B92 / RIGHT B92
MAG xx/xx
CH 0 or 1
RESERVE xxx
        </pre>

        <h4>Shotgun</h4>
        <pre>
SHOTGUN
TUBE xx/07
CH LIVE
CH SPENT / UNRACKED
CH EMPTY
SHELLS xxx
        </pre>
    </div>
</body>
</html>

---
## File: wiki/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="b92_pistols.html">B92 Pistols</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                    <a href="debugging_playbook.html">Debugging Playbook</a>
                    <a href="zscript_scope_rules.html">ZScript Scope Rules</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Welcome</h2>
        <p>This is the official documentation for DoDA.</p>
    </div>
</body>
</html>

---
## File: wiki/testing.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Testing</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Testing</h2>
        <p>Testing is performed in-game within GZDoom.</p>
        <ul>
            <li>Launch GZDoom by loading the <code>doda-core</code> directory or creating a PK3 file from it.</li>
            <li>Use <code>DebugTrigger.zs</code> for mission-related debugging.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/ui.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - UI</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>UI</h2>
        <p>Handles HUD and user interface elements, including deadzone aim indicators and weapon HUDs.</p>

        <h3>HUDDeadzoneBridge (UI/FieldAgent/HUDDeadzoneBridge.zs)</h3>
        <p>Bridge class for HUD components to access Deadzone Aim data safely.</p>
        <ul>
            <li><code>GetLeanOffset(PlayerPawn owner)</code>: Retrieves the current lateral lean offset for UI presentation.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/mission_system.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Mission System</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Mission System & Evidence</h2>
        <p>Handles mission management, campaign state, objective tracking, and evidence ledger processing.</p>

        <h3>Active Files</h3>
        <h4>Core</h4>
        <ul>
            <li><code>DoDA/MissionSystem/MissionIds.zs</code></li>
            <li><code>DoDA/MissionSystem/ObjectiveIds.zs</code></li>
            <li><code>DoDA/MissionSystem/MissionDefs.zs</code></li>
            <li><code>DoDA/MissionSystem/MissionState.zs</code></li>
            <li><code>DoDA/MissionSystem/CampaignState.zs</code></li>
            <li><code>DoDA/MissionSystem/Evidence/EvidenceLedger.zs</code></li>
            <li><code>DoDA/MissionSystem/LastMissionReport.zs</code></li>
            <li><code>DoDA/MissionSystem/MissionManager.zs</code></li>
            <li><code>DoDA/MissionSystem/MissionDirector.zs</code></li>
            <li><code>DoDA/MissionSystem/DebugTrigger.zs</code></li>
        </ul>
        <h4>Interactables/Things</h4>
        <ul>
            <li><code>DoDA/MissionSystem/Things/MissionPickupMarkers.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/ObjectivePickup.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/MissionPickup.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/MissionInteractable.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/MissionTerminal.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/ExtractionInteractable.zs</code></li>
            <li><code>DoDA/MissionSystem/Things/DeployMissionInteractable.zs</code></li>
        </ul>

        <h3>DoDAEvidenceLedger (Evidence/EvidenceLedger.zs)</h3>
        <p>Data structure for tracking evidence points acquired during an operation.</p>
        <ul>
            <li><code>WeaponEvidencePoints</code>: Points from recovered weapons.</li>
            <li><code>AmmoEvidencePoints</code>: Points from field ammunition.</li>
            <li><code>RecordResource(category, value)</code>: Adds points for a given evidence category.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/weapon_system.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Weapon System</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Weapon System</h2>
        <p>The weapon system handles weapon logic, animation, and implementation for all weapons, including the B92 pistols and the DoDA shotgun.</p>

        <h3>Active Files</h3>
        <ul>
            <li><code>DoDA/WeaponSystem/HandSwapController.zs</code></li>
            <li><code>DoDA/WeaponSystem/SpriteAnimator.zs</code></li>
            <li><code>DoDA/WeaponSystem/WeaponBase.zs</code></li>
            <li><code>DoDA/WeaponSystem/Weapons/Pistols/PistolBase.zs</code></li>
            <li><code>DoDA/WeaponSystem/Weapons/Pistols/B92Left.zs</code></li>
            <li><code>DoDA/WeaponSystem/Weapons/Pistols/B92Right.zs</code></li>
            <li><code>DoDA/WeaponSystem/Weapons/Shotguns/Shotgun.zs</code></li>
            <li><code>DoDA/WeaponSystem/Ammo/AmmoDispenser.zs</code></li>
        </ul>

        <h3>DoDAWeapon (WeaponBase.zs)</h3>
        <p>The base class for all DoDA weapons. Handles lean, deadzone, and sprite animation pipelines.</p>
        <ul>
            <li><code>yawGap</code>, <code>pitchGap</code>: Deadzone aim offsets.</li>
            <li><code>leanInput</code>, <code>leanController</code>: Lean ability components.</li>
            <li><code>handSwapController</code>: Manages weapon hand swapping.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/structure.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Structure</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Project Structure</h2>
        <p>The project is organized into several key modules defined in <code>zscript.txt</code>:</p>
        <ul>
            <li><code>Aim</code>: Aiming mechanics and input handling.</li>
            <li><code>CharacterClasses</code>: Player classes (FieldAgent, Analyst, SAC).</li>
            <li><code>UI</code>: HUD and user interface elements.</li>
            <li><code>Abilities</code>: Character abilities like leaning.</li>
            <li><code>WeaponSystem</code>: Weapon logic, animation, and pistol implementation.</li>
            <li><code>MissionSystem</code>: Mission management, campaign state, and mission objects.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/zscript_scope_rules.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - ZScript Scope Rules</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="b92_pistols.html">B92 Pistols</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>ZScript Scope Rules</h2>
        <p>This page documents DoDA-specific ZScript scope and interaction rules.</p>
        
        <h3>Action Scope</h3>
        <ul>
            <li>State actions use <code>invoker</code>.</li>
            <li>Action methods must validate <code>invoker</code> and <code>invoker.owner</code>.</li>
            <li>Action methods must not rely on <code>self.owner</code>.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/introduction.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Introduction</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Introduction</h2>
        <p>DoDA implements custom weapon systems, mission management, and advanced character mechanics (like leaning and deadzone aiming) to the GZDoom engine.</p>
    </div>
</body>
</html>

---
## File: wiki/lean_system.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Lean System</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Lean System</h2>
        <p>The Lean System is responsible for view translation and hand-locking behavior.</p>

        <h3>Ownership</h3>
        <ul>
            <li><code>LeanInput</code>: Owned by the input system. Responsible for Q/E button reading and edge detection.</li>
            <li><code>LeanController</code>: Owned by the ability controller. Responsible for direction, smoothing, and lateral view offset.</li>
        </ul>

        <h3>Requirements</h3>
        <ul>
            <li>Q held: left view translation and left-hand lock.</li>
            <li>E held: right view translation and right-hand lock.</li>
            <li>Q+E: no lean target, no hand lock.</li>
            <li>Release: smooth return to center.</li>
            <li>Lean lock has priority over manual swap.</li>
            <li>Camera roll is not included.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/shotgun.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Shotgun</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Shotgun</h2>
        <p>The DoDA shotgun implements a realistic tube-fed, pump-action state machine.</p>

        <h3>State Machine Model</h3>
        <ul>
            <li>Tube capacity: 7</li>
            <li>Chamber capacity: 1</li>
            <li>Starting condition: 7 tube + 1 live chamber</li>
            <li>Reserve shells: Shell inventory</li>
        </ul>

        <h3>State Table</h3>
        <table>
            <tr>
                <th>State</th>
                <th>Tube</th>
                <th>Chamber</th>
                <th>Player action</th>
                <th>Result</th>
            </tr>
            <tr>
                <td>Ready live</td>
                <td>0–7</td>
                <td>LIVE</td>
                <td>Fire</td>
                <td>Chamber becomes spent; V required</td>
            </tr>
            <tr>
                <td>Unracked</td>
                <td>0–7</td>
                <td>SPENT/UNRACKED</td>
                <td>Fire</td>
                <td>Dry fire</td>
            </tr>
            <tr>
                <td>Unracked</td>
                <td>1–7</td>
                <td>SPENT/UNRACKED</td>
                <td>V</td>
                <td>Tube −1; chamber becomes LIVE</td>
            </tr>
            <tr>
                <td>Empty</td>
                <td>0</td>
                <td>EMPTY</td>
                <td>Fire</td>
                <td>Dry fire</td>
            </tr>
            <tr>
                <td>Empty tube</td>
                <td>0–6</td>
                <td>EMPTY</td>
                <td>R with reserve Shell</td>
                <td>Tube +1</td>
            </tr>
            <tr>
                <td>Live chamber</td>
                <td>0–7</td>
                <td>LIVE</td>
                <td>V</td>
                <td>Chambered round discarded; next tube shell chambers if available</td>
            </tr>
        </table>
    </div>
</body>
</html>

---
## File: wiki/weapon_base.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Weapon Base</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="weapon_base.html">Weapon Base</a>
                    <a href="shotgun.html">Shotgun</a>
                    <a href="hud_weapon.html">HUD Weapon</a>
                    <a href="deadzone_aim.html">Deadzone Aim</a>
                    <a href="lean_system.html">Lean System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Weapon Base</h2>
        <p>The <code>DoDAWeapon</code> class serves as the shared gameplay base for all DoDA weapons.</p>

        <h3>DoDAWeapon</h3>
        <table>
            <tr>
                <th>Field</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Kind</td>
                <td>Class</td>
            </tr>
            <tr>
                <td>Active source path</td>
                <td><code>DoDA/WeaponSystem/WeaponBase.zs</code></td>
            </tr>
            <tr>
                <td>Owner</td>
                <td>WeaponSystem</td>
            </tr>
            <tr>
                <td>Status</td>
                <td>IMPLEMENTED</td>
            </tr>
            <tr>
                <td>Source evidence</td>
                <td><code>DoDA/WeaponSystem/WeaponBase.zs</code></td>
            </tr>
            <tr>
                <td>Runtime evidence</td>
                <td>Not human-verified</td>
            </tr>
            <tr>
                <td>Engine documentation</td>
                <td>Not documented</td>
            </tr>
        </table>

        <p>Description: Base class responsible for weapon FOV, deadzone offsets, sprite positioning, lean interaction, hand swap, fire locking, and generic manual-control dispatch.</p>

        <p>Contracts:</p>
        <ul>
            <li>Responsibilities: Weapon FOV, deadzone offsets, sprite positioning, lean interaction, hand swap, fire locking, generic manual-control dispatch.</li>
            <li>Non-responsibilities: Weapon-specific chamber/magazine/tube logic, shotgun states, B92 reload internals, HUD state storage.</li>
            <li>Action methods must validate <code>invoker</code> and <code>invoker.owner</code>; they must not rely on <code>self.owner</code>.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/aim_abilities.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Aim & Abilities</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Aim & Abilities</h2>
        <p>Covers aiming mechanics, deadzone aiming, and character abilities like leaning.</p>

        <h3>Active Files</h3>
        <h4>Aim</h4>
        <ul>
            <li><code>DoDA/Aim/AimInput.zs</code></li>
        </ul>
        <h4>Abilities</h4>
        <ul>
            <li><code>DoDA/Abilities/Lean/LeanInput.zs</code></li>
            <li><code>DoDA/Abilities/Lean/LeanController.zs</code></li>
        </ul>

        <h3>DoDALeanController (Abilities/Lean/LeanController.zs)</h3>
        <p>Manages lean state, camera translation, and lean locking.</p>
        <ul>
            <li><code>LeanLock</code>: Boolean state for hand locking during a lean.</li>
            <li><code>Update()</code>: Updates camera lean translation.</li>
            <li><code>IsLeanLocked()</code>: Returns lean lock status.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/architecture.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DoDA Wiki - Architecture</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="introduction.html">Introduction</a></li>
            <li class="dropdown">
                <a href="#">Architecture</a>
                <div class="dropdown-content">
                    <a href="architecture.html">Architecture Overview</a>
                    <a href="structure.html">Structure</a>
                </div>
            </li>
            <li class="dropdown">
                <a href="#">Systems</a>
                <div class="dropdown-content">
                    <a href="weapon_system.html">Weapon System</a>
                    <a href="mission_system.html">Mission System</a>
                    <a href="aim_abilities.html">Aim & Abilities</a>
                </div>
            </li>
            <li><a href="character_classes.html">Character Classes</a></li>
            <li><a href="ui.html">UI</a></li>
            <li><a href="testing.html">Testing</a></li>
        </ul>
    </nav>
    <div id="content">
        <h2>Architecture Overview</h2>
        <ul>
            <li>Weapon system refactoring (moving lean logic out of WeaponBase).</li>
            <li>Deadzone Aim System (requires C++ patterns or improved ZScript implementation).</li>
            <li>Configuration files (CVARINFO, KEYCONF, MENUDEFS) organization.</li>
            <li>Camera and Aim System locking functionality.</li>
        </ul>
    </div>
</body>
</html>

---
## File: wiki/content/B92Pistols.md
# B92 Pistols

## Overview
The B92 pistols (`DoDAB92Left`, `DoDAB92Right`) are gameplay-distinct weapons, each with an independent magazine and chamber state.

## State Management
- `magazineRounds`: Current rounds in the magazine.
- `chamberLoaded`: Whether a round is chambered.
- `firearmStateInitialized`: Tracks if the state has been initialized.

## Reload Behavior
- `CanReload()`: Allows reloading if reserve ammo (`Clip`) is available and the magazine is not full.
- `CommitReload()`: Returns unused magazine rounds to reserve, loads a new magazine, and chambers a round if empty.
- `QueueReload()`: Flags a reload request.
- `DoDA_BeginReload()`: Validates the request before starting the animation.
- `DoDA_CommitReload()`: Performs the `CommitReload()` call.

## Hand Swap
- `RequestHandSwap()`: Switches between left and right hands.
- `HandSwapController` lock state (`IsPistolSwapLocked()`) restricts swaps if active.

---
## File: wiki/content/WeaponAuxiliary.md
# Weapon Auxiliary Systems

## HandSwapController
Manages hand swap logic, including locking and swap restrictions.
- `Hand_Left`/`Hand_Right`: Constants for hand identification.
- `ResolveDesiredHand(...)`: Determines the desired hand based on lean, swap inputs, and deadzone aim.
- `IsPistolSwapLocked()`: Checks if the swap is locked (e.g., during active Deadzone Aim).

## SpriteAnimator
Manages procedural weapon sprite animation for sway, tilt, and lean effects.
- `Update(...)`: Calculates `FinalX`, `FinalY`, and `FinalRotation` based on yaw/pitch gap, lean amount, and hand dip amount.
- `Apply(...)`: Applies the calculated procedural offsets to the weapon sprite (`PSprite`).

## AmmoDispenser
A simple interactable actor for acquiring ammunition.
- `Used(Actor user)`: Adds 15 rounds of `Clip` ammunition to the player upon interaction.

---
## File: wiki/content/LeanAbility.md
# Lean Ability

## Overview
The lean ability allows for tactical view translation. It is composed of `DoDALeanInput` (for reading inputs) and `DoDALeanController` (for managing the lean state and view translation).

## DoDALeanInput
Responsible for reading Q (`BT_USER1`) and E (`BT_USER2`) buttons and edge detection.

### Key Methods
- `Update(PlayerPawn owner)`: Captures button states and updates `LeaningLeft`, `LeaningRight`, `LeaningLeftPressed`, and `LeaningRightPressed`.
- `IsLeaning()`: Returns true if either Q or E is held.

## DoDALeanController
Responsible for managing lean direction, smoothing, view translation, and hand locking.

### Key Methods
- `Update(...)`:
    - Handles scroll wheel inputs (`BT_USER4`) to adjust `LeanDistance` (lean amount) within [8.0, 40.0].
    - Calculates `LeanAmount` using smoothing (0.25).
    - Sets `AppliedOffset` based on `LeanAmount` and `LeanDistance`.
    - Updates `FieldAgent.LeanOffset` (if available).
    - Uses `owner.SetViewPos` to translate the camera view laterally.
- `IsLeanLocked()`: Returns true if a lean state is locked (Q or E held).
- `GetLockedHand()`: Returns the hand restricted during lean (`DoDAHandSwapController.Hand_Left` for Q, `DoDAHandSwapController.Hand_Right` for E).

---
## File: wiki/content/CharacterClasses.md
# Character Classes

## Overview
DoDA features three playable character classes: `FieldAgent`, `Analyst`, and `SAC`. All classes inherit from `DoomPlayer` and implement a common deadzone aim system.

## Common Deadzone Aim
Each character class independently manages its deadzone state.

### Properties
- `DeadzoneAimActive`: Tracks if deadzone aim is currently active.
- `ReticleYawOffset` / `ReticlePitchOffset`: The signed angular gap between actor aim and red-dot aim.
- `DeadzoneYawLimit` / `DeadzonePitchLimit`: Constraints on how far the reticle can move.
- `SmoothedMouseX` / `SmoothedMouseY`: Smoothed per-tick deadzone input for trackball-like inertia.

### Methods
- `ResetDeadzoneAim()`: Resets all deadzone state variables and clears raw mouse CVars.
- `Tick()`: Manages deadzone activation based on `BT_ALTATTACK` (alt-fire) and debug CVars (`doda_debug_force_deadzone`).

## Class-Specific Details
- `FieldAgent`:
    - Extends deadzone activation logic to include lean states (triggered by `BT_USER1` and `BT_USER2`).
    - Starts with: `DoDAB92Left`, `DoDAB92Right`, `DoDAMP5KSD`, `DoDAHolster`, `Clip` (100).
- `Analyst`:
    - Basic deadzone implementation.
    - Starts with: `Clip` (100).
- `SAC`:
    - Basic deadzone implementation.
    - Starts with: `DoDAB92Left`, `DoDAB92Right`, `Clip` (100).

---
## File: wiki/content/WIP.md
# Open Questions / WIP

- `DoDA/Aim/DeadzoneController.zs`: Legacy/orphan. Should it be restored or deleted?
- MP5 deadzone crosshair alignment: Unverified if it reads the correct deadzone controller methods.
- Shotgun system: Under active runtime stabilization, not documented.
- `Analyst` and `SAC` player classes: Basic functional documentation complete; advanced usage/interactions pending.
- Mission System: Core components documented; specific mission flow logic requires further validation.

---
## File: wiki/content/Changelog.md
# Changelog

- Initial documentation of the DoDA weapon and aim system.
- Pages created: `WeaponArchitecture.md`, `B92Pistols.md`, `MP5KSD.md`, `InputDeadzone.md`, `TestDebugging.md`.
- Documented files: `WeaponBase.zs`, `PistolBase.zs`, `B92Left.zs`, `B92Right.zs`, `MP5KSD.zs`, `MP5ModeHandler.zs`, `AimInput.zs`, `HUDDeadzone.zs`, `HUDDeadzoneBridge.zs`.
- Documentation of character classes (`FieldAgent`, `Analyst`, `SAC`) and ability systems (`LeanInput`, `LeanController`).
- Documentation of weapon auxiliary systems (`HandSwapController`, `SpriteAnimator`, `AmmoDispenser`) and the Mission System (`MissionManager` and components).

---
## File: wiki/content/TestDebugging.md
# Test and Debugging Guide

## Test Matrix
- B92 normal fire, deadzone fire, empty/reload behavior.
- MP5 semi, burst (partial magazine), automatic fire.
- MP5 tactical reload, empty reload/cocking, dry fire.
- MP5 deadzone crosshair alignment (WIP / unverified).

## Diagnostic Markers
- `[DEBUG/RELOAD]`: `PistolBase.CanReload`, `QueueReload`, `DoDA_BeginReload`, `DoDA_CommitReload`.
- `[DODA/WEAPON]`: `PistolBase.CommitReload`.
- `HANDSWAP`: `PistolBase.RequestHandSwap`.
- `MP5`: `MP5KSD` fire modes, burst, reload, chamber loading, shot traces.
- `SPRITE`: `WeaponBase.PrintDebugSpriteOffsets`.

---
## File: wiki/content/InputDeadzone.md
# Input and Deadzone

## AimInput
- `OnRegister`: Sets `RequireMouse = true` and `SetOrder(-100)`.
- `InputProcess`: Captures mouse input and updates `doda_raw_mouse_x`/`y` CVars if deadzone aim is active (`FieldAgent.IsDeadzoneAimActive()`).

## DeadzoneController
- **STATUS: LEGACY / ORPHAN.**
- Currently not included in `zscript.txt`. Do not rely on this controller for active gameplay features.

## Event Routing
- Deadzone aim input is processed by `DoDAAimInput` and consumed by `FieldAgent` (which handles math, limits, and smoothing).
- HUD components read deadzone state (e.g., `HUDDeadzoneBridge`).

---
## File: wiki/content/MP5KSD.md
# MP5KSD

## State Fields
- `MagazineCapacity`: 30
- `TotalCapacity`: 31
- `magazineRounds`, `chamberLoaded`
- `fireMode`: 0 (Semi), 1 (Burst), 2 (Auto)
- `burstShotsRemaining`, `burstInProgress`

## Fire Dispatch
- Semi: `Fire` state triggers `MP5KSD_Fire`.
- Burst: `BurstFire` state triggers `MP5KSD_BurstFire` 3 times.
- Auto: `Fire` state triggers `MP5KSD_Fire` while holding fire.

## Reload
- `TryReload()` initiates tactical or empty reload based on `IsEmpty()`.
- `PerformReloadTransfer()` transfers ammo from reserve.
- `LoadChamberFromMagazine()` chambers a round during reload.

## MP5ModeHandler
- `InputProcess()` captures 'C' to cycle fire modes and 'R' to reload.
- `NetworkProcess()` handles network events `DoDA_MP5CycleFireMode` and `DoDA_MP5Reload`.
- *Note: Not registered as a UI processor.*

---
## File: wiki/content/WeaponArchitecture.md
# Weapon Architecture

## Overview
The DoDA weapon system is based on the `DoDAWeapon` class, which extends `Weapon`. It is designed for tactical gameplay with integrated deadzone aim and lean mechanics.

## DoDAWeapon Responsibilities
- Owns weapon state, including deadzone aim variables (`yawGap`, `pitchGap`), FOV management, and fire-control locks (`fireLockTics`).
- Manages lean input and controller (`DoDALeanInput`, `DoDALeanController`).
- Manages hand swap (`DoDAHandSwapController`) and sprite animation (`DoDASpriteAnimator`).
- Provides hooks for manual fire control (`HandleManualWeaponControl`), secondary actions (`HandleSecondaryWeaponAction`), and fire-state resolution (`GetFireState`).

## Deadzone Integration
- `FieldAgent` owns deadzone activation, reset, and raw-input consumption.
- `DoDAWeapon` subclasses read and consume deadzone state for presentation, hand selection, and trace origin.
- HUD modules read deadzone state for overlay rendering (`DoDAHUDDeadzone`).
- HUD code does not modify deadzone math.

## Weapon-Base Dispatch
- `UsesManualFireDispatch()` determines if the weapon uses `GetFireState` for advanced logic (e.g., burst fire, fire-mode selection).

---
## File: wiki/content/MissionSystem.md
# Mission System

## Overview
The mission system handles mission state, progression, and objective management.

## Key Components
- `DoDAMissionManager`: Tracks `MissionResult`, `MissionIndex`, `MissionPercentComplete`, `MissionPhase`, and mission metadata.
- `DoDAMissionState` / `DoDACampaignState`: Manages the state of the current mission and campaign.
- `EvidenceLedger`: Tracks evidence gathered during missions.
- `MissionDirector`: Orchestrates mission flow and objectives.
- `MissionInteractable` / `MissionTerminal` / `ExtractionInteractable`: Specific interactable actors for mission tasks.

## Objectives and Markers
- `MissionIds` / `ObjectiveIds`: Define IDs for missions and objectives.
- `MissionPickup`: Handles objective item pickups.
- `DebugTrigger`: Used for debugging mission triggers.
