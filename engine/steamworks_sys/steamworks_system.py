import sys
import os
import time
import traceback

from steamworks import STEAMWORKS

if sys.version_info >= (3, 8) and sys.platform == 'win32':
    dll_added = False
    # Check next to executable (frozen)
    if hasattr(sys, '_MEIPASS'):
        try:
            print(f"SteamworksSystem: Adding DLL search path (Frozen): {sys._MEIPASS}")
            os.add_dll_directory(sys._MEIPASS)
            dll_added = True
        except Exception as e:
             print(f"SteamworksSystem: Warning - Failed to add MEIPASS DLL directory: {e}")
    # Fallback to current working directory (dev or if not frozen correctly)
    try:
        cwd_path = os.getcwd()
        print(f"SteamworksSystem: Adding DLL search path (CWD): {cwd_path}")
        os.add_dll_directory(cwd_path)
        dll_added = True
    except Exception as e:
         print(f"SteamworksSystem: Warning - Failed to add CWD DLL directory: {e}")

    # Optional: Add Steam Client directory if necessary (more complex)
    # steam_install_path = find_steam_client_path() # Needs implementation
    # if steam_install_path: os.add_dll_directory(steam_install_path)

    if not dll_added:
        print("SteamworksSystem: Warning - Could not add any valid DLL search paths.")


# --- Steamworks System Class ---
class SteamworksSystem:
    def __init__(self, engine):
        print("SteamworksSystem: Initializing SteamworksSystem...")
        self.engine = engine
        self.sw = None # Holds the STEAMWORKS class instance (if applicable)
        self.initialized = False
        self.user_steam_id = None
        self.user_name = None

        if not STEAMWORKS: # Check if import worked and class exists
            print("SteamworksSystem: Steamworks package not loaded or STEAMWORKS class missing.")
            return

        try:
            print("SteamworksSystem: Instantiating STEAMWORKS...")
            # Use the class provided by the installed package
            self.sw = STEAMWORKS(app_id='1547960')

            print("SteamworksSystem: Initializing Steamworks via instance...")
            if self.sw.initialize():
                self.initialized = True
                print("SteamworksSystem: Initialization SUCCESSFUL.")

                # Access APIs via the instance (assuming Goldberg-like wrapper)
                self.user_steam_id = self.sw.Users.GetSteamID()
                self.user_name = self.sw.Friends.GetFriendPersonaName(self.user_steam_id)
                print(f"SteamworksSystem: User: {self.user_name} (ID: {self.user_steam_id})")

                self.engine.events.tick.subscribe(self._run_callbacks)
                self.engine.events.quit.subscribe(self.shutdown)
                self.engine.events.steam_achievements.subscribe(self.unlock_achievement)
                # Optional: self.request_stats()
            else:
                print("SteamworksSystem: Initialization FAILED. Is Steam running? Is steam_appid.txt present/correct?")

        except Exception as e:
            print(f"SteamworksSystem: Exception during initialization: {e}")
            traceback.print_exc()
            self.sw = None

    def _run_callbacks(self, dt):
        """Called every frame to process Steam callbacks."""
        if self.initialized and self.sw:
            self.sw.run_callbacks()

    def shutdown(self):
        """Shuts down the Steamworks API via the instance."""
        if self.initialized and self.sw:
            print("SteamworksSystem: Shutting down Steamworks...")
            try:
                self.sw.shutdown()
                print("SteamworksSystem: Shutdown complete.")
            except Exception as e:
                print(f"SteamworksSystem: Exception during shutdown: {e}")
            self.initialized = False
            self.sw = None

    # --- API Wrappers (These likely remain the same if using Goldberg's wrapper) ---
    def is_initialized(self):
        return self.initialized and self.sw is not None

    def get_user_name(self):
        return self.user_name if self.is_initialized() else "Offline"

    def request_stats(self):
        if not self.is_initialized(): return False
        try:
             print("SteamworksSystem: Requesting current stats...")
             success = self.sw.UserStats.RequestCurrentStats()
             print(f"SteamworksSystem: RequestCurrentStats call status: {success}")
             return success
        except Exception as e:
             print(f"SteamworksSystem: Exception requesting stats: {e}")
             traceback.print_exc()
             return False

    def get_achievement_status(self, achievement_api_name: str):
        print(f"SteamworksSystem: Getting achievement status for '{achievement_api_name}'")
        if not self.is_initialized() or not achievement_api_name: return False
        try:
             return self.sw.UserStats.GetAchievement(achievement_api_name)
        except Exception as e:
             print(f"SteamworksSystem: Exception getting achievement status '{achievement_api_name}': {e}")
             traceback.print_exc()
             return False

    def unlock_achievement(self, achievement_api_name: str):
        if not self.is_initialized() or not achievement_api_name: return False
        try:
            print(f"SteamworksSystem: Attempting to set achievement: {achievement_api_name}")
            success_set = self.sw.UserStats.SetAchievement(achievement_api_name)
            if success_set:
                print(f"SteamworksSystem: SetAchievement successful for '{achievement_api_name}'. Calling StoreStats...")
                success_store = self.sw.UserStats.StoreStats()
                print(f"SteamworksSystem: StoreStats call status for '{achievement_api_name}': {success_store}")
                return success_store
            else:
                 print(f"SteamworksSystem: SetAchievement FAILED for '{achievement_api_name}'.")
                 return False
        except Exception as e:
            print(f"SteamworksSystem: Exception unlocking achievement '{achievement_api_name}': {e}")
            traceback.print_exc()
            return False

    def get_stat_int(self, stat_api_name: str):
         if not self.is_initialized() or not stat_api_name: return 0
         try:
             return self.sw.UserStats.GetStatInt(stat_api_name)
         except Exception as e:
             print(f"SteamworksSystem: Error getting int stat '{stat_api_name}': {e}")
             return 0

    def set_stat_int(self, stat_api_name: str, value: int):
         if not self.is_initialized() or not stat_api_name: return False
         try:
              print(f"SteamworksSystem: Setting Int Stat '{stat_api_name}' to {value}")
              success_set = self.sw.UserStats.SetStatInt(stat_api_name, value)
              if success_set:
                   success_store = self.sw.UserStats.StoreStats()
                   print(f"SteamworksSystem: StoreStats call status for '{stat_api_name}': {success_store}")
                   return success_store
              else:
                   print(f"SteamworksSystem: SetStatInt FAILED for '{stat_api_name}'.")
                   return False
         except Exception as e:
              print(f"SteamworksSystem: Error setting int stat '{stat_api_name}': {e}")
              traceback.print_exc()
              return False