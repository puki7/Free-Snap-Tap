## V1.1.5 changelog

241028-1323
bugfix:
- when active window returned empty the script crashed 
  - fixed
- evaluations with python code that hat spaces in it like (not is_set('var')) were not recognized correctly 
  - fixed
- if a line in the config file started with whitespaces and could lead to wrong recognition of start arguments and commented out lines
  - leading whitespaces will now be removed
  - fixed
- automatic shortening of active window name removed the name of e.g. the game because of some versioning info following it. So if the last part of the window name is not the game name, then it could happen that the game name would be removed
  - now it will always check the full name for the focus name 
  - removed shortening due to many possible naming schemes
  - fixed 

added:
- eval `|(is_repeat_active('aliasname'))` -> True or False dependent on if a repeat is active


changed
- changed default value of set to 1 and clear to 0 (in python 0 -> False and 1 -> True)
  - to always work in variables with numbers and not mix numbers and boolean values
- status_indicator now starts with red as default and only changes when focus name is recognized
- cleaned up some code for the drawing of the status_indicator

## V1.1.4 main_testing branch Changelog
241023-1055
- removed some debug output

- None ke can have manual delays - no default delays will be applied in any case
  - if a delay is given it will be played
  - if no delay is given the default delays will not be applied and no delay will be played
- None can now also have hte key_string `reset` and `delay`
  - no functionality in itself, but for better readability
  - `reset|(macroname)` or `delay|100` is easier to read
- empty ke in trigger group might not correctly be handled as only a release key_event
  - preventive fix to make sure the release ke will be added also to a trigger group
- simplified release_all_keys() underlying function to not be as aggressiv and only release currently pressed simulated keys
- `|(type('text to write'))` and `|(write('text to write'))` eval added
- variables can now be set, checked and cleared
  - `|(set('variable'))` to set it to True
  - can be checked by `|(is_set('variable'))`: will return True or False
  - can be cleared by `|(clear('variable'))`
  - and all variables can be cleared by `|(clear_all_variables())`
  - variables will be reset on change of focus app
- variables with a bit more control over there content can be used by:
  - can be used to adjust delays of key_events or 
  - to create costum sequences or keysets with more than 2 layers (before only True and False possible)
  - `|(set('variable',*value*))` to set a variable to e.g. a number
  - `|(get('variable'))` will just return the content of the variable - a check has to be done seperately or it will be interpreted as a delay
  - `|(check('variable',*value*))` to get the variable and check against the given value - will return True or False
  - `|(incr('variable'))` increases by 1: will set to 0 if not set before
  - `|(decr('variable'))` decreases by 1: will set to 0 if not set before
- added `-macrodelay` as future replacement for `-aliasdelay`
  - I do not know why I choose this misleading name first - maybe I thought aliases are the same as macros
  - both now usable and will replace -aliasdelay step by step

bugfix:
- key combinations did not reset when used and retriggered itself on resuming - fixed
- if option 0 was activated before the first time start of the listener, then an error stopped the listener - fixed
- rebind will be executed despide some of the constraints of the trigger result in False 
  - the constraints will not even checked when replacement key is None, because they will not be saved in the trigger key_event
  - the constraints are stripped when the conversion to a set of key_events takes place because of None being recognised as a Key instead of a key_event as it should
  - None key now works correctly as key_event, but constraints wil still be stripped if key_event is converted to Key 
  - on conversion to set of key_events now also copies the constraints 
  - fixed

ideas:
- on initializing macros - when Key as trigger used then create a macro for -ke of Key and a supress Rebind for +ke of Key
- alias on a focus group basis?
