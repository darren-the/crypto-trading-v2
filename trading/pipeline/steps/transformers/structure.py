from pipeline.base_classes.task import Task


class Structure(Task):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        self.struct_top = -1
        self.struct_bottom = -1
        self.equil_top = -1
        self.equil_bottom = -1
        self.struct_start_timestamp = -1
        self.struct_end_timestamp = -1
        self.struct = {}
        super().__init__()
        
    def process(self, element):
        self.struct = {
            'timestamp': element['timestamp'],
            'candle_timestamp': element['candle_timestamp'],
            'struct_start_timestamp': self.struct_start_timestamp,
            'struct_top': self.struct_top,
            'equil_top': self.equil_top,
            'struct_end_timestamp': self.struct_end_timestamp,
            'struct_bottom': self.struct_bottom,
            'equil_bottom': self.equil_bottom,
            'is_complete': element['is_complete'],
        }

        if element['high_timestamp'] != -1 and element['low_timestamp'] != -1:
            if element['high_timestamp'] < element['low_timestamp']:
                self._update_top(element)
                self._update_bottom(element)
            elif element['low_timestamp'] < element['high_timestamp']:
                self._update_bottom(element)
                self._update_top(element)
            elif element['high_colour'] == 'green':
                self._update_bottom(element)
                self._update_top(element)
            else:
                self._update_top(element)
                self._update_bottom(element)
        elif element['high_timestamp'] != -1:
            self._update_top(element)
        elif element['low_timestamp'] != -1:
            self._update_bottom(element)
            
        return self.struct
    
    def _reset_struct(self):
        self.struct['struct_top'] = -1
        self.struct['struct_bottom'] = -1
        self.struct['equil_top'] = -1
        self.struct['equil_bottom'] = -1
        self.struct['struct_start_timestamp'] = -1
        self.struct['struct_end_timestamp'] = -1
    
    def _save_struct(self):
        self.struct_start_timestamp = self.struct['struct_start_timestamp']
        self.struct_top = self.struct['struct_top']
        self.equil_top = self.struct['equil_top']
        self.struct_end_timestamp = self.struct['struct_end_timestamp']
        self.struct_bottom = self.struct['struct_bottom']
        self.equil_bottom = self.struct['equil_bottom']

    def _update_top(self, element):
        if element['high_timestamp'] < self.struct['struct_start_timestamp'] or \
            (element['high_timestamp'] == self.struct['struct_start_timestamp'] and element['high_colour'] == 'red'):
            return
        if self.struct['struct_top'] == -1:
            self.struct['struct_top'] = self.struct['equil_top'] = element['high_top']
            if self.struct['struct_start_timestamp'] == -1:
                self.struct['struct_start_timestamp'] = element['high_timestamp']
        elif self.struct['struct_top'] < element['high_bottom']:
            self._reset_struct()
            self.struct['struct_top'] = self.struct['equil_top'] = element['high_top']
            self.struct['struct_start_timestamp'] = element['high_timestamp']
        elif self.struct['struct_top'] < element['high_top']:
            self.struct['struct_top'] = self.struct['equil_top'] = element['high_top']
        else:
            self.struct['equil_top'] = element['high_top']
        self.struct['struct_end_timestamp'] = element['high_timestamp']
        if element['is_high']:
            self._save_struct()

    def _update_bottom(self, element):
        if element['low_timestamp'] < self.struct['struct_start_timestamp'] or \
            (element['low_timestamp'] == self.struct['struct_start_timestamp'] and element['low_colour'] == 'green'):
            return
        if self.struct['struct_bottom'] == -1:
            self.struct['struct_bottom'] = self.struct['equil_bottom'] = element['low_bottom']
            if self.struct['struct_start_timestamp'] == -1:
                self.struct['struct_start_timestamp'] = element['low_timestamp']
        elif self.struct['struct_bottom'] > element['low_top']:
            self._reset_struct()
            self.struct['struct_bottom'] = self.struct['equil_bottom'] = element['low_bottom']
            self.struct['struct_start_timestamp'] = element['low_timestamp']
        elif self.struct['struct_bottom'] > element['low_bottom']:
            self.struct['struct_bottom'] = self.struct['equil_bottom'] = element['low_bottom']
        else:
            self.struct['equil_bottom'] = element['low_bottom']
        self.struct['struct_end_timestamp'] = element['low_timestamp']
        if element['is_low']:
            self._save_struct()