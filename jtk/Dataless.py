from jtk import Pretty
import string

# TODO: Revamp how we parse the Dataless text file
#
# The previous assumption I made about lines with a range of blocks is false
#
# The parser is probably going to need to know more about the structure of
# the data. If we know which are counts, and to which fields they refere,
# we can easily pair them in a cleaner fashion...
#
# We can also more easily handle the process of storing epochs if we know
# which fields contain epoch dates.
#
# We need to assemle a Map of rules for how to parse various types, and 
# aslo contain descriptions of relationships.
#

"""
Dataless.map {
    'volume-info' : Blockette (10),
    'stations' :
    {
        'NN_SSSS' :
        {
            'comments' :
            {
                'YYYY,DDD,HH:MM:SS' : Blockette (51),
                ...
            },
            'epochs' :
            {
                'YYYY,DDD,HH:MM:SS' : Blockette (50),
                ...
            },
            'channels' :
            {
                'LL-CCC' :
                {
                    'comments' :
                    {
                        'YYYY,DDD,HH:MM:SS' : Blockette (59),
                        ...
                    }
                    'epochs' :
                    {
                        'YYYY,DDD,HH:MM:SS' :
                        {
                            'format' : Blockette (30),
                            'info' : Blockette (52),
                            'misc' : [Blockette, Blockette, ...] (ALL-OTHER-BLOCKETTES),
                            'stages' :
                            {
                                <INT-STAGE-INDEX> :
                                {
                                    <INT-BLOCKETTE-NUMBER> : Blockette (53-58,61),
                                    ...
                                }
                                ...
                            }
                        }
                        ...
                    },
                },
                ...
            },
        },
        ...
    },
}
"""

stages = {
    53 : 4,
    54 : 4,
    55 : 3,
    56 : 3,
    57 : 3,
    58 : 3,
    61 : 3,
}

def parse_epoch(epoch):
    hour,minute,second,tmsec = 0,0,0,0
    parts = epoch.split(',')
    year,day = map(int, parts[0:2])
    if len(parts) > 2:
        parts = parts[2].split(':')
        hour = int(parts[0])
        if len(parts) > 1:
            minute = int(parts[1])
        if len(parts) > 2:
            s_parts = parts[2].split('.')
            if len(s_parts) > 1:
                tmsec = int(s_parts[1])
            second = int(s_parts[0])
    return year,day,hour,minute,second,tmsec

def epoch_string(epoch):
    return "%04d,%03d,%02d:%02d:%02d.%04d" % epoch


class Blockette:
    def __init__(self, number):
        self.number = number
        self.fields = {}

        self.last_start_id = 0

    def add_field_data(self, id, data):
        ids = map(int,id.split('-'))
        if (self.last_start_id > ids[0]) and ((((self.number != 52) or (self.last_start_id > 4)) and (ids[0] == 3)) or ((self.number == 52) and (ids[0] == 4))):
            return False
            #raise Exception("Blockette field out of order [last=%d -> current=%d]" % (self.last_start_id, ids[0]))
        self.last_start_id = ids[0]
        if len(ids) > 1:
            ids = range(ids[0], ids[1]+1)
            data_items = data.split()
            if len(data_items) > (len(ids) + 1):
                raise Exception("Too many parts for multi-field entry")
            if len(data_items) > (len(ids)):
                data_items = data_items[1:]
            for i in range(0, len(ids)):
                if not self.fields.has_key(ids[i]):
                    self.fields[ids[i]] = {
                        'description' : '',
                        'values' : [],
                    }
                self.fields[ids[i]]['values'].append(data_items[i])
        else:
            id = ids[0]
            parts = map(string.strip, data.split(':', 1))
            description = ''
            if len(parts) == 2:
                description,data = parts
            else:
                data = parts[0]
            if not self.fields.has_key(id):
                self.fields[id] = {
                    'description' : description,
                    'values' : [],
                }
            self.fields[id]['values'].append(data)
        return True

    def get_values_complex(self, *args):
        results = []
        for field in args:
            if not self.fields.has_key(field):
                values = (None,)
            else:
                values = self.fields[field]['values']
            if len(values) == 1:
                results.append(values[0])
            else:
                results.append(values)
        return tuple(results)

    def get_values(self, *args):
        results = []
        for field in args:
            if not self.fields.has_key(field):
                values = (None,)
            else:
                values = self.fields[field]['values']
            results.append(values)
        return tuple(results)

    def get_field(self, arg):
        results = None
        if self.fields.has_key(arg):
            results = self.fields[arg]['values']
        return results

    def get_descriptions(self, *args):
        results = []
        for field in args:
            results.append[self.fields[field]['description']]
        return tuple(results)

class Dataless: 
    def __init__(self, raw_dataless, progress_callback=None, cancel_callback=None, quiet=False):
        self.raw_dataless = raw_dataless
        self.blockettes = None
        self.map = {
            'volume-info' : None,
            'stations' : {},
        }

        self.progress_callback = self._print_progress
        if quiet:
            self.progress_callback = self._progress_stub
        if callable(progress_callback):
            self.progress_callback = progress_callback

        self.cancel_callback = self._cancel_stub
        if callable(cancel_callback):
            self.cancel_callback = cancel_callback

        self.total = 0
        self.count = 0
        self.skipped = 0
        self.percent = 0.0
        self.last_percent = 0.0
        self.line = ""

    def _progress_stub(self, *args):
        pass

    def _cancel_stub(self):
        pass

    def _print_progress(self, *args):
        print "%0.2f%% (%d/%d - %d lines skipped)" % (self.percent, self.count, self.total, self.skipped)

    def process(self):
        self._parse_dataless()
        self._assemble_data()

        #Pretty.pretty(self.map)

    def _parse_dataless(self):
        if self.raw_dataless is None:
            return

        self.blockettes = []

        self.total = len(self.raw_dataless)
        self.count = 0
        self.skipped = 0
        self.percent = 0.0
        self.last_percent = 0
        self.stage = "Parsing Dataless"

        blockettes = {}
        for line in self.raw_dataless:
            # Check for a cancel request
            self.cancel_callback()

            # Track our progress
            self.count += 1
            self.percent = float(int(float(self.count) / float(self.total) * 100.0))
            if self.percent > self.last_percent:
                self.last_percent = self.percent
                self.progress_callback(self.stage, self.count, self.total)

            line = line.strip()
            self.line = line

            # Assume we will skip this line
            self.skipped += 1

            if line == '':
                continue
            if line[0] == '#':
                continue
            if line[0] != 'B':
                continue

            # If we didn't skip, revert the increment
            self.skipped -= 1

            key,data = line.split(None,1)
            blockette_num,field_ids = key[1:].split('F', 1)
            blockette_num = int(blockette_num)

            # If this blockette does not exist, create it
            if not blockettes.has_key(blockette_num):
                blockette = Blockette(blockette_num)
                blockettes[blockette_num] = blockette
                self.blockettes.append(blockette)
            # If this blockette does exist, retrieve it
            else:
                blockette = blockettes[blockette_num]
            
            # If we stepped backward in the field_id value we need to start a new blockette
            if not blockette.add_field_data(field_ids, data):
                blockette = Blockette(blockette_num)
                blockettes[blockette_num] = blockette
                self.blockettes.append(blockette)
                blockette.add_field_data(field_ids, data)


    def _assemble_data(self):
        if self.blockettes is None:
            return

        self.total = len(self.blockettes)
        self.count = 0
        self.skipped = 0
        self.percent = 0.0
        self.last_percent = 0
        self.stage = "Assembling Data"

        stations = self.map['stations']
        station = None
        channel = None
        epoch = None

        for blockette in self.blockettes:
            # Track our progress
            self.count += 1
            self.percent = float(int(float(self.count) / float(self.total) * 100.0))
            if self.percent > self.last_percent:
                self.last_percent = self.percent
                self.progress_callback(self.stage, self.count, self.total)

            number = blockette.number

          # Volume Information
            if number == 10:
                if self.map['volume-info'] is not None:
                    raise Exception("Found multiple volume-info blockettes.")
                self.map['volume-info'] = blockette

          # List of Stations in Volume
            elif number == 11:
                # This information is only necessay for parsing the SEED volume
                pass

          # Station Epochs
            elif number == 50:
                key = "%s_%s" % blockette.get_values_complex(16,3)
                if not stations.has_key(key):
                    stations[key] = {
                        'comments' : {},
                        'epochs' : {},
                        'channels' : {},
                    }
                station = stations[key]
                try:
                    epoch_key = epoch_string(parse_epoch(blockette.get_values_complex(13)[0]))
                    station['epochs'][epoch_key] = blockette
                except AttributeError:
                    pass

          # Station Comments
            elif number == 51:
                epoch_key = epoch_string(parse_epoch(blockette.get_values_complex(3)[0]))
                station['comments'][epoch_key] = blockette

          # Channel Epochs
            elif number == 52:
                key = "%s-%s" % blockette.get_values_complex(3,4)
                if not station['channels'].has_key(key):
                    station['channels'][key] = {
                        'comments' : {},
                        'epochs' : {},
                    }
                channel = station['channels'][key]
                epoch_key = epoch_string(parse_epoch(blockette.get_values_complex(22)[0]))
                channel['epochs'][epoch_key] = {
                    'info' : blockette,
                    'format' : None,
                    'stages' : {},
                    'misc' : [],
                }
                epoch = channel['epochs'][epoch_key]

          # Epoch Format
            elif number == 30:
                epoch['format'] = blockette

          # Channel Comments
            elif number == 59:
                epoch_key = epoch_string(parse_epoch(blockette.get_values_complex(3)[0]))
                channel['comments'][epoch_key] = blockette

          # Channel Stages
            elif stages.has_key(number):
                stage_key = int(blockette.get_values_complex(stages[number])[0])
                if not epoch['stages'].has_key(stage_key):
                    epoch['stages'][stage_key] = {}
                epoch['stages'][stage_key][blockette.number] = blockette
          
          # All other data
            else:
                epoch['misc'].append(blockette)


