#!/usr/bin/env python3
"""Apply firefox-reverse changes to upstream source files."""
import os

UPSTREAM = "/workspace/upstream"

# ---- firefox.js ----
f = os.path.join(UPSTREAM, "browser/app/profile/firefox.js")
with open(f) as fh: data = fh.read()

data = data.replace(
    '\npref("sidebar.position_start", true);\n',
    '\npref("sidebar.position_start", false);\n',
    1
)
data = data.replace(
    '#ifdef NIGHTLY_BUILD\npref("sidebar.revamp", true);\n#else\npref("sidebar.revamp", false);\n#endif\n',
    'pref("sidebar.revamp", true);\n'
)
data = data.replace(
    'pref("sidebar.main.tools", "");\n',
    'pref("sidebar.main.tools", "agent");\npref("sidebar.newTool.migration.agent", "{}");\n'
)
if 'pref("frx.forceHorizontalTabs", true);' not in data:
    data = data.replace(
        'pref("sidebar.visibility", "always-show");\n',
        'pref("sidebar.visibility", "always-show");\npref("frx.forceHorizontalTabs", true);\npref("frx.hideRemoteControlCue", true);\n'
    )
data = data.replace(
    'pref("browser.ml.chat.enabled", true);',
    'pref("browser.ml.chat.enabled", false);'
)
if 'security.sandbox.content.level' not in data:
    data = data.replace(
        'pref("distribution.mozillaonline.ignore", true);\n',
        'pref("distribution.mozillaonline.ignore", true);\n\n// firefox-reverse: disable content sandbox so JSVMP trace can write from content process (reverse-only)\npref("security.sandbox.content.level", 0);\n'
    )
with open(f, "w") as fh: fh.write(data)
print("OK: firefox.js")

# ---- browser.js ----
f = os.path.join(UPSTREAM, "browser/base/content/browser.js")
with open(f) as fh: data = fh.read()
if "frx.hideRemoteControlCue" not in data:
    old = """    // Disable updating the remote control cue for performance tests,
    // because these could fail due to an early initialization of Marionette.
    const disableRemoteControlCue = Services.prefs.getBoolPref("""
    new = """    const hideFrxRemoteControlCue =
      Services.prefs.getBoolPref("frx.hideRemoteControlCue", false) ||
      Services.env.get("MOZ_FRX_HIDE_REMOTE_CONTROL_CUE") === "1";
    if (hideFrxRemoteControlCue) {
      document.documentElement.removeAttribute("remotecontrol");
      return;
    }

    // Disable updating the remote control cue for performance tests,
    // because these could fail due to an early initialization of Marionette.
    const disableRemoteControlCue = Services.prefs.getBoolPref("""
    data = data.replace(old, new, 1)
with open(f, "w") as fh: fh.write(data)
print("OK: browser.js")

# ---- SidebarManager.sys.mjs ----
f = os.path.join(UPSTREAM, "browser/components/sidebar/SidebarManager.sys.mjs")
with open(f) as fh: data = fh.read()
data = data.replace(
    'const DEFAULT_LAUNCHER_TOOLS = "aichat,syncedtabs,history,bookmarks";',
    'const DEFAULT_LAUNCHER_TOOLS = "agent";'
)
with open(f, "w") as fh: fh.write(data)
print("OK: SidebarManager.sys.mjs")

# ---- browser-sidebar.js ----
f = os.path.join(UPSTREAM, "browser/components/sidebar/browser-sidebar.js")
with open(f) as fh: data = fh.read()
data = data.replace(
    'viewGenaiChatSidebar: "aichat",',
    'viewGenaiChatSidebar: "aichat",\n  viewAgentSidebar: "agent",'
)
old = """    // Initialize global state manager.
    this.SidebarManager;
"""
new = """    // Initialize global state manager.
    this.SidebarManager;

    if (
      Services.prefs.getBoolPref("frx.forceHorizontalTabs", true) &&
      Services.prefs.getBoolPref("sidebar.verticalTabs", false)
    ) {
      Services.prefs.setBoolPref("sidebar.verticalTabs", false);
    }
"""
data = data.replace(old, new, 1)
old2 = """  toggleVerticalTabs() {
    Services.prefs.setBoolPref("""
new2 = """  toggleVerticalTabs() {
    if (Services.prefs.getBoolPref("frx.forceHorizontalTabs", true)) {
      return;
    }
    Services.prefs.setBoolPref("""
data = data.replace(old2, new2, 1)
with open(f, "w") as fh: fh.write(data)
print("OK: browser-sidebar.js")

# ---- sidebar-customize.mjs ----
f = os.path.join(UPSTREAM, "browser/components/sidebar/sidebar-customize.mjs")
with open(f) as fh: data = fh.read()
data = data.replace(
    '["viewGenaiPageAssistSidebar", "sidebar-menu-genai-page-assist-label"],',
    '["viewGenaiPageAssistSidebar", "sidebar-menu-genai-page-assist-label"],\n  ["viewAgentSidebar", "sidebar-menu-agent-label"],'
)
with open(f, "w") as fh: fh.write(data)
print("OK: sidebar-customize.mjs")

# ---- sidebar.ftl ----
f = os.path.join(UPSTREAM, "browser/locales/en-US/browser/sidebar.ftl")
with open(f) as fh: data = fh.read()
data = data.replace(
    '.label = Agent',
    '.label = Firefox-Reverse-Agent'
)
with open(f, "w") as fh: fh.write(data)
print("OK: sidebar.ftl")

print("\nAll changes applied!")
