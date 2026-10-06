# Validated Full Mod UI fixes

The four fixes were tested on a physical TempoTec V3 Blaze using `V3-Blaze-v1.3-Full-Mod-UI-Fixes-Test.upt`, SHA-256 `6bd0c1bf1973241efe6985d6da63572197f502b190851883876d82e8255017e8`. The v1.1.2 Full Mod build reproduces those exact bytes. Physical results were reported by the maintainer after the original investigation/build record; its initial “pending” checklist remains historical evidence.

Exactly six payload files differ from v1.1.1 Full Mod:

| Payload | Change |
|---|---|
| `/usr/bin/hiby_player` | Scoped header, theme-navigation and Settings repaint hooks |
| `/usr/resource/layout/theme1/dialog/shutdown_timer.dlg` | Full-display coverage |
| `/usr/resource/layout/theme1/dialog/playmenu_song_info.dlg` | Properties spacing and bounded rows |
| `/usr/resource/layout/theme1/ui_sub_back.view` | Added fullscreen list header |
| `/usr/resource/layout/theme1/ui_set_sub_back.view` | Added fullscreen Add header |
| `/usr/resource/layout/theme1/ui_eq_title.view` | Added fullscreen EQ title |

## Low-battery indicator (v1.2.1)

Full Mod draws the battery as two widgets: a static frame (`topbar_iv_battery_frame`, 14x20) and, inside its 10x11 opening, the widget the player drives (`topbar_iv_battery`). The driven widget's state image (`img_path_0/1/2`: normal, charging, low) is drawn whole and its fill (`img_focus_path`) is cropped by charge level. The v1.0 artwork made the low state a solid red 10x11 block, so below 16 % the opening turned red and the level disappeared. Giving the opening per-state fills (`img_focus_path_1/2`) was tried on hardware and made the level vanish; it is not used.

The topbar refresh (`0x50c020`, every 500 ms) reads the charge (system query `0xe`) and charging state (`0xb`); below 16 % it selects state 2 unless charging. It resolves the opening with `0x4a1b80(view, name, "imageview")` and sets the image through the object's setter at `+0x180`: at `0x50c208` for states 1 and 2 (`s3` = state, stored to `+0xc4` afterwards) and at `0x50cb18` for state 0.

Both `jalr $25` instructions become calls to `battery_state` / `battery_normal`. Each makes the original call with the original arguments, then `battery_frame` resolves `topbar_iv_battery_frame` the same way and sets its image of the same index. The frame layout gains `img_path_1` (white) and `img_path_2` (`battery_bg_low.png`, red, excluded from accent tinting). A missing view, widget, image, object or setter leaves only the original call. The opening's low-state image is now transparent, so the level keeps the theme color. Frame corners and cap are fully opaque.

A framebuffer capture in the low state confirmed the red frame, a 2-pixel border on each side and a fill spanning x=304–313 at the bottom of the opening. An apparent one-pixel gap seen in photos is the panel's RGB subpixel layout: red frame and teal fill light different subpixels.

The pull-down menu's battery is updated by other code and keeps its white frame.

## Low-battery notice

The notice (`power_low` / `please_charge`, 3 s) uses `dialog/notice_second.dlg`. The v1.0 port placed an empty `vg_notice_second` group before the two text rows; the notice then showed an empty grey card. The rows are again the dialog's first children, as in the official layout, with Full Mod's card styling.

## Coverage and header geometry

Now Playing moves `vg_topbar` offscreen. Normal Full Mod headers occupy physical Y=30–67 and list bodies begin at Y=68. Stock uses a 20-pixel inset; inherited fullscreen code still subtracts that amount.

Shutdown previously used a dialog surface starting at Y=20 with height 460. Its revised root covers Y=0–479. The existing background is a child at Y=20; message/count coordinates remain physically unchanged at Y=186/240. Only the resource changes: power-button handling and countdown instructions/callbacks remain intact.

Generic header construction (`0x4dfb00`) forces fullscreen header origins to zero through `0x4e09e0`. List geometry at `0x4b49a8` branches to `0x4b5130` to subtract 20 from body Y and add 20 to height. Short Full Mod templates then leave controls at the screen edge and can expose the preceding page.

The hooks select opaque 68-pixel variants only for the proven fullscreen child paths. Direct header children and touch areas move down 30 pixels. Original names, widget contracts, styles and theme-directory prefixes remain. Ordinary Settings/library entry keeps the original templates. No global status-bar transition or fullscreen flag is introduced.

| Now Playing menu entry | Dispatch / child code | Scope |
|---|---|---|
| List | `0x5236a4 → 0x522300 → 0x4b3860` | current-song list, type `0x13` |
| Add | `0x5236b4 → 0x5223e0 → 0x4c9f80` | local playlist-add list, type `0x0b` |
| Equalizer | `0x5236c4 → 0x4b5980 → 0x50ffe0` | title constructor `0x50dc40` |
| Album | `0x5236e8 → 0x5224e0`, lookup/new paths `0x522724/0x522738` | album list, type `0x14` |
| Properties | `0x5236f8 → 0x522760`, requests `0x5227fc/0x522818` | local metadata dialog |
| Audio Quality | `0x523654/0x523708` | quality list, type `0x6e` |
| Remove | `0x523690 → 0x523260 → 0x521840` | existing confirmation/action, unchanged |

The generic list correction covers types `0x0b/0x13/0x14/0x61/0x6e`. The list-type table is at `0x82e220` with 60-byte records; geometry dispatch is at `0x82ff00`. Add's settings-header override is further restricted to owner `vg_listview_add_m3u`. Its hidden-bar header move changes −20 to 0.

Add's service paths (`0x4ce080`, types `0x39/0x41`) use geometry `0x4b3d48`, not the defective adjustment, and remain unchanged. Properties service paths (`0x522834/0x522874 → 0x555500`) also remain. They were inspected statically, not exercised with streaming services.

Properties already owns a fullscreen black root. Its back/title/artist move down 30 pixels; ten metadata rows reclaim 3-pixel gaps, reducing pitch from 35 to 32. The Path field remains Y=410/height 65; the inner group becomes height 480. Fonts, text heights, values and contracts remain.

Equalizer's graph, presets, reset/switch assets and controls remain unchanged. Variant templates retain teardown names and paths, including list destruction `0x4b5980` and EQ title destruction `0x50d820`. Physical tests confirmed child-page geometry and return to fullscreen Now Playing.

## Theme navigation

Color apply (`0x4f6580`) persists selectors `0x36/0x37/0x38` at `0x4f6660–0x4f667c` and installs close callback `0x4f56e0`. The callback at `0x4f5718` already requested the launcher through `0x44d540`.

The wrong destination came later: main init (`0x515120`) creates the launcher at `0x515568`, then the branch at `0x5157c8 → 0x515814` reconstructs Music (`0x528ec0`) and the saved list (`0x514840`), restoring playback through `0x514ec0`.

The tested hook adds transient request origin `ui_color_reload` through existing helper `0x44d360`. Only that origin skips Music/list reconstruction and follows root completion `0x51583c`; playback restoration remains. Ordinary startup and language-change branches are preserved. Color storage/application and saved navigation values are untouched.

## Settings redraw

Idle callback `0x4b7160` uses a 1000 ms timeout; its Settings branch is `0x4b72a0`. Scrollbar visibility routine `0x4e2e00` hides the existing widget rather than destroying it. Its repaint call at `0x4e2e5c → 0x46f320` invalidates a narrow strip.

The draw path `0x4bd540 → 0x7a7c40 → 0x7a7560 → 0x7a74a0` combines damage-rectangle X with child-local X (`0x7a74c8/0x7a74d0`). A card at local X=4 gets origin 4 for full damage at X=0, but origin 304 for strip damage at X=300. This explains the observed edge corruption; the hide path contained no viewport or scroll-position writes.

For Settings type `0x27` only, the hook replaces the narrow invalidation with a NULL-rectangle full repaint of the existing list surface, supported by `0x46f320/0x76e1e0`. Other types retain their arguments. Scrollbar visibility, timeout, geometry and scroll state remain; the shared renderer and album drawing are not patched. Physical tests confirmed the reported corruption no longer occurs. No separate vertical-reflow defect was established.

## Binary changes and reversal

| Player file offset | Original VA | Patched span | Purpose |
|---|---|---:|---|
| `0x0dfbf4` | `0x4dfbf4` | 4 bytes | list header resolver |
| `0x0e5990` | `0x4e5990` | 4 bytes | Add header resolver |
| `0x10dcb8` | `0x50dcb8` | 4 bytes | EQ title resolver |
| `0x0b49a8` | `0x4b49a8` | 8 bytes | scoped list geometry |
| `0x0ca0b4` | `0x4ca0b4` | 4 bytes | Add header offset |
| `0x0f5718` | `0x4f5718` | 4 bytes | color close callback |
| `0x1157c8` | `0x5157c8` | 8 bytes | color-only restore branch |
| `0x0e2e5c` | `0x4e2e5c` | 4 bytes | Settings repaint |
| `0x10c208` | `0x50c208` | 4 bytes | battery frame, charging/low (v1.2.1) |
| `0x10cb18` | `0x50cb18` | 4 bytes | battery frame, normal (v1.2.1) |
| `0x507040–0x50757e` | `0x907040–0x90757e` | 1343 bytes | hook code and strings |
| `0x0000a4–0x0000ab` | ELF program header | 8 bytes | RX filesz/memsz: `0x507030 → 0x50757f` |

The zero-filled gap ends before the next segment at file offset `0x508000`. Executable size, writable segment, entry point, section table and dynamic relocations remain. The existing metadata NOP at `0x38240` is retained.

Hook entries: list header `0x9070e0`, Add `0x907168`, EQ `0x907208`, list geometry `0x907280`, color reload `0x9072c8`, color restore `0x90732c`, Settings repaint `0x90737c`, battery state `0x9073e0`, battery normal `0x907428`, battery frame `0x907470`; shared helpers start at `0x907040/0x907074/0x9070b0`.

[hooks.S](../build/v1.3/ui/hooks.S) and [patch.py](../build/v1.3/ui/patch.py) retain the tested instructions and original-byte assertions. [validate.py](../build/v1.3/ui/validate.py) compares all 1343 bytes with LLVM and checks all 123 list types, hidden/visible topbar, resolver failure, ABI/stack preservation, color/language branches, Settings-only repaint arguments and, for the battery hooks, the unchanged original call, the frame image index per state and every missing-object case. The v1.2.1 code was inserted before the strings, so every v1.1.2 hook keeps its address. External functions are stubbed; the harness is not a GUI emulator.

Each build writes exact before/after bytes in `BINARY-PATCHES.json`. [revert.py](../build/v1.3/ui/revert.py) supports per-bug development overlays; it is not part of production packaging. The original investigation checked individual reversions and full reversal to the pinned baseline. Any altered overlay needs a fresh manifest and hardware validation before release.

Every other payload file and existing metadata record matches v1.1.1 Full Mod. The LDAC library, Bluetooth Receiver implementation, countdown logic, Balance artwork, album performance work, Now Playing appearance and EQ graph/control resources are preserved. Removed experimental Quick Settings functionality is not restored.
