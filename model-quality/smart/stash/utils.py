
from pmkoalas._logging import info, debug, enable_logging
from pmkoalas.complex import ComplexTrace, ComplexEvent, ComplexEventLog
from pmkoalas.read import read_xes_complex
from pmkoalas.export import export_to_xes_complex

from os import path
from shutil import rmtree
from xml.etree.ElementTree import Element, parse
from typing import Set, Tuple, List
from datetime import datetime
from dataclasses import dataclass

XMLNS_TAG = "{http://code.deckfour.org/xes}"
DATASTREAM_TAG = "{https://cpee.org/datastream/datastream.xesext}"

def _extract_value(value:str, element:Element) -> object:
    """
    Trys to find a approperiate convertion of the string of a point value. 
    """
    # find the type
    type = element.attrib[f"{DATASTREAM_TAG}procedure_type"]

    if "binary" in type:
        return True if float(value) == 1 else False
    elif "continuous" in type:
        return float(value)
    else:
        return value

def _create_tmp_file(subprocess_id:str) -> str:
    """
    extracts the subprocess event log from the zip and returns a filepath for use.
    """
    import zipfile
    zipfile.ZipFile(path.join(".", "Cleaned Event Log.zip")).extract("Cleaned Event Log/"+subprocess_id+".xes", path.join(".", "tmp"))
    filepath = path.join(".", "tmp", "Cleaned Event Log", subprocess_id+".xes")
    return filepath

def _clean_tmp():
    """
    cleans tmp.
    """
    rmtree( path.join(".", "tmp") )

def _extract_subprocess_events(subprocess_id:str) -> List[Element]:
    """
    Trys to find all elements of the tree that relate to the subprocesses events.
    """

    info("working on :: "+subprocess_id)
    filepath = _create_tmp_file(subprocess_id)

    # check that file exists
    if not path.exists(filepath):
        raise FileNotFoundError("subprocess log file not found at :: "+filepath)
    
    # parse traces
    xml_tree = parse(filepath)
    log = xml_tree.getroot()

    if (log == None):
        raise ValueError("Unable to find root element in xml structure")
    
    # find subprocess id
    subprocess = log.find(f"{XMLNS_TAG}trace")
    subprocess_id = subprocess.find(".*[@key='SubProcessID']")
    info(f"looking at subprocess :: {subprocess_id.attrib['value']}")

    # find events
    sub_events = subprocess.findall(f"{XMLNS_TAG}event")
    info(f"contains #events :: {len(sub_events)}")

    _clean_tmp()

    return sub_events

def extract_observation_keys(subprocess_id:str) -> Set[Tuple[str,str]]:
    """
    extracts all observation keys in a subprocess log and collects their 
    type as well.
    """

    # find events
    sub_events = _extract_subprocess_events(subprocess_id)
    info(f"contains #events :: {len(sub_events)}")

    # for each event, find the list of iot events
    for event in sub_events:
        # get concept:name for event
        concept = event.find(".*[@key='concept:name']")
        info(f"working on event :: {concept.attrib['value']}")

        # find streams
        iot_stream = event.findall(".*[@key='stream:datastream']")
        info(f"found #streams :: {len(iot_stream)}")

        # for each stream, extract point
        keys = set()
        for stream in iot_stream:
            info(f"stream contains : {len(stream)}")
            for point in stream:
                keys.add(
                    (
                        point.attrib[DATASTREAM_TAG+'observation'],
                        point.attrib[DATASTREAM_TAG+'procedure_type']
                    )
                )

    # shout keys
    info(f" found observation keys and types :: {keys}")
    return keys

@dataclass
class Point:
    time:datetime
    value:object

    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return self.__str__()

def extract_time_series_from_subprocess(subprocess_id:str, observation:str) -> List[Point]:
    """
    extracts a list of points from the given subprocess log file and observation key.
    """
    series = []

    # find subprocess events
    sub_events = _extract_subprocess_events(subprocess_id)

    # for each event, find the list of iot events
    for event in sub_events:
        # get concept:name for event
        concept = event.find(".*[@key='concept:name']")
        info(f"working on event :: {concept.attrib['value']}")

        # find streams
        iot_stream = event.findall(".*[@key='stream:datastream']")
        info(f"found #streams :: {len(iot_stream)}")

        for stream in iot_stream:
            stream = stream.findall(f".*[@{DATASTREAM_TAG}observation='{observation}']")
            info(f"stream contains : {len(stream)}")
            for point in stream:
                time = point.find(f"{XMLNS_TAG}date").attrib[f"{DATASTREAM_TAG}timestamp"]
                value = point.find(f"{XMLNS_TAG}string").attrib[f"{DATASTREAM_TAG}value"]

                # process time 
                time = datetime.fromisoformat(time)

                # process value
                value = _extract_value(value, point)

                series.append(Point(time, value))
    # sort and return
    info(f"returning series of size :: {len(series)=}")
    series = sorted(series, key=lambda p: p.time)
    return series

SMART_FACTORY_KEYS = [
    'http://iot.uni-trier.de/StreamDataAnnotationOnto#HBW_2_Crane_Jib_Property_Current_Position_X',
    'http://iot.uni-trier.de/FTOnto#MotorSpeed',
    'http://iot.uni-trier.de/StreamDataAnnotationOnto#HBW_2_Crane_Jib_Property_Current_Position_Y'
]

SHORTEN_KEYS = {
    'http://iot.uni-trier.de/StreamDataAnnotationOnto#HBW_2_Crane_Jib_Property_Current_Position_X' : 'HBW_2_CRPOSX',
    'http://iot.uni-trier.de/FTOnto#MotorSpeed' : 'MSPEED',
    'http://iot.uni-trier.de/StreamDataAnnotationOnto#HBW_2_Crane_Jib_Property_Current_Position_Y' : 'HBW_2_CRPOSY'
}

LARGE_STREAMS = [
    "9b29103a-c755-42fd-954d-efb5815f229f",
    "1e47d232-29d0-4a3f-a9d1-0e5b0af2eabe",
    "ea1baec0-9310-4d29-97c8-e8db77f1de85",
    "67fa3bec-0185-4c95-afad-3339f3b95b35"
]

def handle_factory_stream(subprocess_ids:List[str], observation:str) -> ComplexTrace:
    """
    
    """
    events = []

    # loop through subprocesses
    index = 1
    for subprocess_id in subprocess_ids:
        if subprocess_id in LARGE_STREAMS:
            info("skipping large log :: "+subprocess_id)
            continue
        try :
            series = extract_time_series_from_subprocess(subprocess_id, observation)
        except Exception as e:
            info("failed to handle :: " + subprocess_id)
            continue

        for point in series:
            events.append(
                ComplexEvent(
                    f"exogenous_data_point_{index:010d}",
                    {
                        "exogenous:value" : point.value,
                        "time:timestamp" : point.time
                    }
                )
            )
            index += 1    

    # find a nice xseries name
    if observation in SHORTEN_KEYS.keys():
        name = SHORTEN_KEYS[observation]
    else:
        name = observation.split("#")[-1]

    return ComplexTrace(events, {
        'exogenous:name' : name
    })

class LowMemStorage():

    def __init__(self) -> None:
        import tempfile
        self._tmp = tempfile.TemporaryFile("w+t")
        

    def append(self, item):
        self._tmp.write(item.__repr__().replace("\n"," ")+"\n") 

    def __iter__(self):
        import datetime
        self._tmp.flush()
        self._tmp.seek(0)
        for line in self._tmp:
            try :
                yield eval(line)
            except Exception as e:
                open("error.stderr", "w+").write(line)
                info("couldn't process repr")
                continue

@enable_logging
def work():
    # generate exogenous datasets for smart factory
    for logn, key in enumerate(SMART_FACTORY_KEYS):
        traces = LowMemStorage()
        for variant, instances in read_xes_complex(path.join(".","wf101_starts_only.xes")).__iter__():
            info(f"working on variant :: {variant}")
            for inst in instances:
                subprocesses = []
                for ev in inst.__iter__():
                    data = ev.data()
                    if "SubProcessID" in data.keys():
                        subprocesses.append(data["SubProcessID"])
                info(f"handling #subprocesses : {len(subprocesses)}")

                trace = handle_factory_stream(subprocesses, key)

                if len(trace) > 0:
                    data = trace.data()
                    data["concept:name"] = inst.data()["concept:name"]
                    trace = ComplexTrace(
                        trace,
                        data
                    )
                    traces.append(trace)
                info("!!!!! --- handled trace --- !!!!!")
        
        xlog = ComplexEventLog(traces, name="Exogenous Dataset - "+key)
        export_to_xes_complex(path.join(".", f"xlog_{logn+1}.xes"), xlog)

if __name__ == "__main__":
    work(debug=True)

    
