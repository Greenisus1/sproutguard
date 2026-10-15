# Sproutguard

Original fullscreen garden lane defense for Pi/Linux terminals. Plant a garden, earn glow, shoot incoming shamblers and survive ten waves. Inspired by the lane-defense idea of Plants vs. Zombies, with new code, names and custom pixel sprites. Not an official port, no PopCap/EA assets, sounds or branding.

Built with AI assistance from my design. Free, offline, no desktop, accounts, API keys, ads, paid unlocks or pip packages.

## Play

Arrows/WASD select a bed. 1-4 choose a seed; Space/Enter plants it. X removes a plant with no refund. U opens the upgrades menu. P pauses, R starts over, Q/Esc quits. Letter controls accept either casing. N starts the next wave early when the lawn is clear. First wave starts automatically after three seconds; eight seconds between waves.

- Glowflower (50 glow): produces 25 glow every eight seconds.
- Seedspitter (100): fires 25-damage seeds down its lane every 1.4 seconds when an enemy is ahead.
- Barkwall (75): 500 health, blocks enemies while shooters work.
- Burstbulb (150): explodes after one second, hitting nearby enemies in its lane and neighboring lanes.

Sky glow is collected automatically: +25 every five seconds. Seed recharge: 2/1/5/10 seconds respectively. Enemies bite plants; armored and fast enemies appear in later waves. Each lane has one emergency mower, drawn left of the lawn; once used, later enemies reaching the house cost one of five house health. Score +10 per enemy, +100 per wave. Win by clearing all ten waves.

## Lawn size

The lawn grows with your terminal: 5x9 beds on a standard 80x27 SSH window, 6x10 from about 96x34, and 7x12 from about 112x42. The size is fixed when a run starts (or restarts with R), so resizing mid-run never destroys a garden; too-small windows pause with the size they need. Mowers always match the lane count.

## Upgrades (U)

U opens the upgrades menu over the lawn; the garden keeps running while you shop. Arrows/WASD choose, Space/Enter buys, U/Esc closes. Upgrades last for the current run.

- Rich Soil (100, 3 levels): growers make +10 glow each cycle per level.
- Sharp Seeds (120, 3 levels): spitters deal +10 damage per level.
- Steel Roots (100, 2 levels): new Barkwalls gain +300 health per level.
- Quick Packets (150, 2 levels): seed packets recharge 25% faster per level.
- Spare Mowers (150, repeatable): restore every used emergency mower.
- Extra Heart (200, 3 levels): +1 house health.

## Display and setup

ANSI truecolor and Unicode half-block pixel art when the terminal advertises support (COLORTERM=truecolor/24bit or direct-color TERM). No image protocol or custom font required. V toggles pixel/text manually; `python3 sproutguard.py --ascii` starts in text mode. Terminal capabilities depend on the device displaying the SSH session. Use text mode if colors/blocks look wrong. Minimum 80x27; smaller windows pause simulation. Pixel mode waits 90ms between input frames to limit traffic; slow SSH can still feel sluggish.

Pi App Store -> Games -> Sproutguard. Installer checks Python/curses and adds Python with apt/apk/pacman if needed. Package installation needs root; Arch retains its package manager's normal confirmation. No new dependencies for graphics.

    bash app-store.sh INSTALL
    bash app-store.sh RUN
    python3 -m unittest -v
    python3 test_terminal.py

Best score saved locally at `~/.local/share/sproutguard/best.json` only on game over or victory, not on restart/quit. Saves are private, atomic and reject symlinks. Storage failures are reported. No online leaderboard or synchronized sessions.

## Scope and verification

A compact original game, not feature parity with PvZ: no campaign map, day/night/pool levels, sound, plant collection or copied characters. Local unit and PTY tests cover planting, resource/cooldown rules, shots, biting, bombs, mowers, upgrades, lawn sizes, wins/losses, saves, resizing and clean terminal exit. Version 1.1.0 adds the upgrades menu, terminal-sized lawns up to 7x12 and mower sprites. Before publication, all 28 unit tests and pixel/text PTY control/resize/exit checks passed on a real aarch64 Raspberry Pi.

MIT license, copyright 2026 Greenisus1.
