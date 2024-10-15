'''
Free-Snap-Tap V1.1.3
last updated: 241015-1300
'''

from threading import Thread, Event # to play aliases without interfering with keyboard listener
from time import sleep # sleep(0.005) = 5 ms
import pygetwindow as gw # to get name of actual window for focusapp function



alias_thread_logging = []
   
class Macro_Thread(Thread):
    '''
    execute macros/alias in its own threads so the delay is not interfering with key evaluation
    '''
    def __init__(self, key_group, stop_event, alias_name, fst_keyboard):
        Thread.__init__(self)
        self.daemon = True
        self.key_group = key_group
        self.stop_event = stop_event
        self.alias_name = alias_name
        self._fst = fst_keyboard
        
    # def run(self): 
    #     to_be_played_key_events = []
    #     try:   
    #         # Key_events ans Keys here ...
    #         if self._fst.arg_manager.DEBUG2:
    #             print(f"D2: > playing macro: {self.alias_name} :: {self.key_group}")
    #         for key_event in self.key_group:
                
    #             # check all constraints at start!
    #             constraint_fulfilled, delay_times = self._fst.output_manager.check_constraint_fulfillment(key_event, get_also_delays=True)
    #             if constraint_fulfilled:
    #                 to_be_played_key_events.append([key_event, delay_times])
    #                 if self._fst.arg_manager.DEBUG2:
    #                     print(f"D2: >> will play '{key_event}' with delays: {delay_times}")

    #         for key_event, delay_times in to_be_played_key_events:
    #             # alias_thread_logging.append(f"{time() - starttime:.5f}: Send virtual key: {key_event.key_string}")
    #             if self.stop_event.is_set():
    #                 self.stop_event.clear()
    #                 break
    #             else:
    #                 if key_event.is_toggle:
    #                     key_event = self._fst.output_manager.get_next_toggle_state_key_event(key_event)
    #                 # send key event and handles interruption of delay
    #                 self._fst.output_manager.execute_key_event(key_event, delay_times, with_delay=True, stop_event=self.stop_event)
        
    def run(self): 

        try:   
            if self._fst.arg_manager.DEBUG2:
                print(f"D2: > playing macro: {self.alias_name} :: {self.key_group}")
            for key_event in self.key_group:
                
                # check all constraints at start!
                constraint_fulfilled, delay_times = self._fst.output_manager.check_constraint_fulfillment(key_event, get_also_delays=True)
                if constraint_fulfilled:
                    if self.stop_event.is_set():
                        self.stop_event.clear()
                        break
                    else:
                        if key_event.is_toggle:
                            key_event = self._fst.output_manager.get_next_toggle_state_key_event(key_event)
                        # send key event and handles interruption of delay
                        self._fst.output_manager.execute_key_event(key_event, delay_times, with_delay=True, stop_event=self.stop_event)
                       
        except Exception as error:
            print(error)
            alias_thread_logging.append(error)

class Alias_Repeat_Thread(Thread):
    '''
    repeatatly execute a key event based on a timer
    '''
    def __init__(self, alias_name, repeat_time, stop_event, fst_keyboard, time_increment=100):
        Thread.__init__(self)
        self.daemon = True
        self.alias_name = alias_name
        self.repeat_time = repeat_time
        self.stop_event = stop_event
        self.time_increment = time_increment
        self.number_of_increments = self.repeat_time // time_increment
        self._fst = fst_keyboard
        self.reset = False
        self.macro_stop_event = Event()        
         
    def run(self): 
        print(f"START REPEAT: {self.alias_name} with interval of {self.repeat_time} ms")

        while not self.stop_event.is_set():
            if self.reset:
                self.macro_stop_event = Event()
                self.reset = False
                #print(f"D4: Repeat: {self.alias_name} reset")
            else:
                #print(f"D4: Repeat: {self.alias_name} execute")
                self._fst.start_macro_playback(self.alias_name, self._fst.key_group_by_alias[self.alias_name], self.macro_stop_event)
            for index in range(self.number_of_increments):
                if self.stop_event.is_set():
                    self.macro_stop_event.set()
                    break
                elif self.reset:
                    break
                else:
                    sleep(self.time_increment / 1000)
        # if stopped also stop the macro if it is still running
        print(f"STOP REPEAT: {self.alias_name} with interval of {self.repeat_time} ms")
                
    def reset_timer(self):
        self.macro_stop_event.set()
        self.reset = True
        
            
class Focus_Thread(Thread):
    '''
    Thread for observing the active window and pause toggle the evaluation of key events
    can be manually overwritten by Controls on ALT+DEL
    '''

    def __init__(self, fst_keyboard):#, paused_lock):
        Thread.__init__(self)
        self.stop = False
        self.daemon = True
        self._fst = fst_keyboard
        self.FOCUS_THREAD_PAUSED = False
        # self.paused_lock = paused_lock

    def run(self):
        last_active_window = ''
        found_new_focus_app = False
        manually_paused = False
        while not self.stop:
            try:
                active_window = gw.getActiveWindow().title

                # shorten the active window name
                if len(active_window) >= 25:
                    reverse = active_window[::-1]
                    del1 = reverse.find('–')
                    del2 = reverse.find('-')
                    del3 = reverse.find('/')
                    del4 = reverse.find('\\')
                    del_min = 100
                    for deliminator in [del1, del2, del3, del4]:
                        if deliminator != -1 and deliminator < del_min:
                            del_min = deliminator 
                    reverse_shortened = reverse[:del_min]
                    active_window = reverse_shortened[::-1]
                    if active_window[0] == ' ':
                        active_window = active_window[1:]    
                
            except AttributeError:
                pass
            
            if active_window not in ["FST Status Indicator", "FST Crosshair"]:
                if not self.FOCUS_THREAD_PAUSED and not self._fst.arg_manager.MANUAL_PAUSED:
        
                    if active_window != last_active_window or manually_paused:
                        if active_window != last_active_window:
                            last_active_window = active_window
                        # to make sure it activates ne focus setting even if manually paused in other app than resumed

                        if manually_paused:
                            manually_paused = False
                        
                        found_new_focus_app = False
                            
                        for focus_name in self._fst.focus_manager.multi_focus_dict_keys:
                            if active_window.lower().find(focus_name) >= 0:
                                found_new_focus_app = True
                                self._fst.focus_manager.FOCUS_APP_NAME = focus_name
                                break
                                        
                        if found_new_focus_app:
                            try:
                                self._fst.update_args_and_groups(focus_name)
                                self._fst.cli_menu.update_group_display()
                                self._fst.cli_menu.display_focus_found(active_window)
                                self._fst.arg_manager.WIN32_FILTER_PAUSED = False

                            except Exception as error:
                                print('--- reloading of groups files failed - not resumed, still paused ---')
                                print(f" -> aborted reloading due to: {error}")
                        
                        else:
                            self._fst.focus_manager.FOCUS_APP_NAME = ''
                            if self._fst.arg_manager.WIN32_FILTER_PAUSED:
                                print(f"> Active Window: {active_window}")

                            else:
                                self._fst.update_args_and_groups()
                                self._fst.cli_menu.update_group_display()
                                self._fst.cli_menu.display_focus_not_found()
                                ###XXX give chance to the controller to release the pressed keys
                                sleep(0.2)
                                self._fst.arg_manager.WIN32_FILTER_PAUSED = True 
                                print(f"> Active Window: {active_window}")
                                        
                        
                else:
                    manually_paused = True
                        
            sleep(0.5)

    def pause(self):
        # with self.paused_lock:
        self.FOCUS_THREAD_PAUSED = True

    def restart(self):
        if self.FOCUS_THREAD_PAUSED:
            # with self.paused_lock:
            self.FOCUS_THREAD_PAUSED = False
            self._fst.arg_manager.MANUAL_PAUSED = False

    def end(self):
        self.stop = True
 