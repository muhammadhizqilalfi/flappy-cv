import threading

class SoundManager:
    def __init__(self, sounds_dict):
        self.sounds = sounds_dict
        self.looping_status = {name: False for name in sounds_dict}
        self.timeout_timers = {}
        
    def play(self, sound_name, volume = 1.0, loop = False):
        self.set_volume(sound_name, volume)

        if not self.looping_status[sound_name]:
            if loop:
                self.sounds[sound_name].play(-1)
            else:
                self.sounds[sound_name].play()
            
            self.looping_status[sound_name] = True

    def play_timeout(self, sound_name, volume = 1.0, loop = False, timeout = None):
        self.set_volume(sound_name, volume)

        if loop:
            self.sounds[sound_name].play(-1)
        else:
            self.sounds[sound_name].play()

        self.looping_status[sound_name] = True

        if timeout is not None:
            self._set_timeout(sound_name, timeout)

    def _set_timeout(self, sound_name, timeout_seconds):
        if sound_name in self.timeout_timers:
            self.timeout_timers[sound_name].cancel()
        
        timer = threading.Timer(timeout_seconds, self._on_timeout, [sound_name])
        timer.daemon = True
        timer.start()
        self.timeout_timers[sound_name] = timer
    
    def _on_timeout(self, sound_name):
        self.looping_status[sound_name] = False

        if sound_name in self.timeout_timers:
            del self.timeout_timers[sound_name]
    
    def stop(self, sound_name):
        self.sounds[sound_name].stop()

        if sound_name in self.looping_status:
            self.looping_status[sound_name] = False

        if sound_name in self.timeout_timers:
            self.timeout_timers[sound_name].cancel()
            del self.timeout_timers[sound_name]
    
    def stop_all(self):
        for sound_name in self.sounds:
            self.stop(sound_name)

    def stop_all_except(self, sound_name = []):
        for name in self.sounds:
            if name not in sound_name:
                self.stop(name)

                if name in self.looping_status:
                    self.looping_status[name] = False
    
    def set_volume(self, sound_name, volume):
        self.sounds[sound_name].set_volume(volume)
    
    def is_playing(self, sound_name):
        return self.looping_status.get(sound_name, False)